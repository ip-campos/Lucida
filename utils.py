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

# ---------------------------- User input functions ---------------------------- #

def get_tiff_file():
    pass