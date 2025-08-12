from tqdm import tqdm
import numpy as np
from scipy.signal import find_peaks
from scipy.stats import kurtosis

# ---------------------------- Particle selection functions ---------------------------- #

def adjacente(ponto1, ponto2, raio=1):
    i, j = ponto1
    i2, j2 = ponto2
    return max(abs(i - i2), abs(j - j2)) <= raio


def remover_adjacentes(lista_centros, raio=1):
    """Remove elementos adjacentes de uma lista de coordenadas."""
    filtrados = []
    for centro in tqdm(range(len(lista_centros)), desc="Removendo adjacentes"):
        if not any(adjacente(lista_centros[centro], c, raio) for c in filtrados):
            filtrados.append(lista_centros[centro])
    return filtrados

# ---------------------------- Particle selection functions ---------------------------- #

def extrair_metricas(sinal):
    sinal = np.array(sinal)
    media = np.mean(sinal)
    desvio = np.std(sinal)
    variancia = np.var(sinal)
    maximo = np.max(sinal)
    mediana = np.median(sinal)
    curt = kurtosis(sinal)
    razao_max_mediana = maximo / mediana
    picos, _ = find_peaks(sinal, height=mediana + 4 * desvio)
    num_picos = len(picos)

    return {
        "media": media,
        "desvio": desvio,
        "variancia": variancia,
        "curtose": curt,
        "razao_max_mediana": razao_max_mediana,
        "num_picos": num_picos,
    }

def classificar(metricas):
    return (
        (metricas["media"] < 850) and
        (metricas["razao_max_mediana"]>1.10) and
        (metricas["curtose"] > 5) and
        (metricas["num_picos"] > 5)
    )

def media_inten_adjacente(x, y, frame_array, n_vizinhos=8):
    """
    Calcula a média da intensidade no pixel central (x, y)
    e em até n_vizinhos adjacentes (de 1 a 8), no sentido horário.

    Parâmetros:
    - x, y: coordenadas do centro
    - frame_array: imagem como array numpy 2D
    - n_vizinhos: número de vizinhos a considerar (1 a 8)

    Retorna:
    - Média da intensidade no centro e vizinhos escolhidos.
    """
    # Coordenadas relativas dos 8 vizinhos
    offsets = [(0, 1), (0, -1), (1, 0),
               (-1, 0), (1, 1), (1, -1),
               (-1, 1), (-1, -1)]

    h, w = frame_array.shape
    intensidades = []

    # Valor do pixel central
    if 0 <= x < w and 0 <= y < h:
        intensidades.append(frame_array[y, x])
    else:
        intensidades.append(0)

    # Adicionar vizinhos (até n_vizinhos)
    for dx, dy in offsets[:n_vizinhos]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h:
            intensidades.append(frame_array[ny, nx])
        else:
            intensidades.append(0)  # valor zero se fora da imagem

    return np.mean(intensidades)

# ---------------------------- SM rate functions ---------------------------- #

def calculate_threshold(cnst, fac):
    """
    Calcula os limiares thold1 e thold2.
    """
    avcount = np.mean(cnst)
    thold1 = avcount + fac * np.sqrt(avcount)
    mask_bursts = cnst > thold1
    nburst = np.sum(mask_bursts)
    scount2 = np.sum(cnst[mask_bursts])
    thold2 = (scount2 / (nburst) + thold1) * 0.5 if nburst > 0 else thold1
    return thold1, thold2, avcount

def apply_threshold(cnst, thold2, seed=None):
    """
    Gera série binária nst (1=on, 0=off) aplicando threshold com ruído.
    """

    rng = np.random.default_rng(seed) #Gerador de números aleatórios

    random_noise = rng.standard_normal(cnst.shape) #Gera um vetor de valores aleatórios a partir de uma distribuição normal 

    fthold = thold2 + random_noise*np.sqrt(thold2) #Cria um limiar flutuante a partir de thold2 e 

    nst = (cnst > fthold).astype(int)

    return nst


def count_transitions(nst, time):
    """
    Conta transições off->on e calcula taxa média SM.
    """
    ntrans = 0
    if nst[0] == 1:
        ntrans += 1
    for i in range(len(nst) - 1):
        if nst[i] == 0 and nst[i + 1] == 1:
            ntrans += 1
    smrate = ntrans / time[-1] if time[-1] > 0 else 0.0
    return ntrans, smrate


def compute_duration_histogram(nst, frate, max_len=1000):
    """
    Gera histogramas e tempos médios das durações off/on.
    """
    nfreqoff = np.zeros(max_len, dtype=int)
    nfreqon = np.zeros(max_len, dtype=int)

    # OFF
    count = 0
    for state in nst:
        if state == 0:
            count += 1
        else:
            if 0 < count < max_len:
                nfreqoff[count] += 1
            count = 0
    if 0 < count < max_len:
        nfreqoff[count] += 1

    # ON
    count = 0
    for state in nst:
        if state == 1:
            count += 1
        else:
            if 0 < count < max_len:
                nfreqon[count] += 1
            count = 0
    if 0 < count < max_len:
        nfreqon[count] += 1

    # Médias
    sumoff = np.sum(nfreqoff)
    sumioff = np.sum(np.arange(max_len) * nfreqoff)
    avfreqoff = sumioff / sumoff if sumoff > 0 else 0
    avofftime = avfreqoff / frate if frate > 0 else 0

    sumon = np.sum(nfreqon)
    sumion = np.sum(np.arange(max_len) * nfreqon)
    avfreqon = sumion / sumon if sumon > 0 else 0
    avontime = avfreqon / frate if frate > 0 else 0

    return {
        "nfreqoff": nfreqoff,
        "nfreqon": nfreqon,
        "avfreqoff": avfreqoff,
        "avofftime": avofftime,
        "avfreqon": avfreqon,
        "avontime": avontime
    }


def remove_long_events_and_spikes(nfreqon, nfreqoff, avfreqon, avfreqoff, frate, nst, ntrans):
    """
    Calcula taxa de ciclo efetiva (descontando eventos longos e spikes).
    """
    lnon = int(round(2 * avfreqon))
    lnoff = int(round(2 * avfreqoff))

    timeon = sum(i * nfreqon[i] for i in range(lnon, len(nfreqon)))
    timeoff = sum(i * nfreqoff[i] for i in range(lnoff, len(nfreqoff)))
    nond = sum(nfreqon[lnon:])
    noffd = sum(nfreqoff[lnoff:])

    nspike = 0
    count = 0
    for state in nst:
        if state == 0:
            count += 1
        else:
            if count >= lnoff:
                nspike += 1
            count = 0

    timedis = (timeoff + timeon) / frate if frate > 0 else 0
    bunchtime = nst.size / frate - timedis if frate > 0 else 0
    bunchrate = (ntrans - nond - nspike) / bunchtime if bunchtime > 0 else 0
    desorpk = (ntrans - nond) / nond if nond > 0 else 0

    return {
        "lnon": lnon,
        "lnoff": lnoff,
        "timeon": timeon,
        "timeoff": timeoff,
        "nond": nond,
        "noffd": noffd,
        "nspike": nspike,
        "bunchrate": bunchrate,
        "desorpk": desorpk
    }