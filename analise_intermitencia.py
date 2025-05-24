from PIL import Image
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from utils import *

def analisar_intermitencia(path_arquivo):
    # ------------------------- Leitura dos arquivos --------------------------- #
    path_tiff = Path(path_arquivo)
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
            intensidade = media_inten_adjacente(x, y, frame_array)
            intensidade_por_particula[idx].append(intensidade)

    # ------------------------ Aplicacao de filtros ---------------------------- #

    media_geral = centros["Intensidade media"][0]
    limiar = centros["limiar"][0]

    indices_filtrados = filtro_linha_base(
        intensidade_por_particula, media_geral, tolerancia=0.1)
    indices_filtrados = filtro_n_vezes(
        intensidade_por_particula, limiar, n_vezes=5)

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
