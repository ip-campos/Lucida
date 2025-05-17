from PIL import Image
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from pathlib import Path
import easygui
from tqdm import tqdm

# ---------------------------- Funcoes de filtro ---------------------------- #

def filtro_linha_base(lista_intensidade_centros, intensidade_media, tolerancia=0.1):
    """Filtra indices de particulas cuja media de intensidade esta proxima da media global."""
    return [
        i for i, centro in enumerate(lista_intensidade_centros)
        if abs(np.mean(centro) - intensidade_media) / intensidade_media < tolerancia
    ]

def filtro_n_vezes(lista_intensidade_centros, indices, limiar, n_vezes=5):
    """Filtra indices de particulas que ultrapassam o limiar mais que n vezes."""
    return [
        i for i in indices
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
    # Coordenadas relativas dos 8 vizinhos (sentido horário)
    offsets = [(0, 1), (0, -1), (1, 0),
               ( -1, 0), ( 1, 1), ( 1, -1),
               ( -1, 1), ( -1, -1)]

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

# ------------------------- Leitura dos arquivos --------------------------- #
path_tiff = Path(easygui.fileopenbox("Escolha o arquivo analisado"))
output_dir = path_tiff.parent
# Escolha do arquivo TIFF
imagem = Image.open(path_tiff)
n_frames = imagem.n_frames
fps = 1/0.04
tempo_medida = [i / fps for i in range(n_frames)]

# Carrega o CSV com as coordenadas das particulas
path_centros = output_dir / "centros.csv"
centros = pd.read_csv(path_centros)

# Inicializa estrutura para armazenar intensidades por particula
intensidade_por_particula = [[] for _ in range(len(centros))]

# ----------------------- Extracao de intensidades -------------------------- #

for frame_index in tqdm(range(n_frames), desc="Processando frames"):
    imagem.seek(frame_index)
    frame_array = np.array(imagem)

    for idx, (x, y) in enumerate(zip(centros["X"], centros["Y"])):
        intensidade = media_inten_adjacente(x, y, frame_array, 4)
        intensidade_por_particula[idx].append(intensidade)

# ------------------------ Aplicacao de filtros ---------------------------- #

media_geral = centros["Intensidade media"][0]
limiar = centros["limiar"][0]

indices_filtrados = filtro_linha_base(intensidade_por_particula, media_geral, tolerancia=0.1)
indices_filtrados = filtro_n_vezes(intensidade_por_particula, indices_filtrados, limiar, n_vezes=5)


# ---------------------------- Salvar graficos ------------------------------ #
output_dir.mkdir(parents=True, exist_ok=True)

for count, idx in enumerate(indices_filtrados):
    intensidade = intensidade_por_particula[idx]
    x = centros.loc[idx, "X"]
    y = centros.loc[idx, "Y"]

    fig, ax = plt.subplots()
    ax.plot(tempo_medida, intensidade, linewidth=1)
    ax.set_title(f"Particula {count} - Coord: ({x}, {y})")
    ax.set_xlabel("Tempo (s)")
    ax.set_ylabel("Intensidade")
    fig.savefig(output_dir / f"particula{count}-x{x}-y{y}.png")
    plt.close(fig)
