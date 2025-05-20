import tqdm
import numpy as np

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


def filtro_linha_base(lista_intensidade_centros, intensidade_media, tolerancia=0.1):
    """Filtra indices de particulas cuja media de intensidade esta proxima da media global."""
    return [
        i for i, centro in enumerate(lista_intensidade_centros)
        if abs(np.mean(centro) - intensidade_media) / intensidade_media < tolerancia
    ]


def filtro_n_vezes(lista_intensidade_centros, limiar, n_vezes=5):
    """Filtra indices de particulas que ultrapassam o limiar mais que n vezes."""
    return [
        i for i, centro in enumerate(lista_intensidade_centros)
        if sum(valor > limiar for valor in lista_intensidade_centros[i]) > n_vezes
    ]


def filtro_std(lista_intensidade_centros, indices, limite_superior):
    """Filtra indices de particulas com desvio padrao abaixo de um limite."""
    return [
        i for i in indices
        if np.std(lista_intensidade_centros[i]) < limite_superior
    ]


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