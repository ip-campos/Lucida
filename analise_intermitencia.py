from PIL import Image
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from utils import *

def analisar_intermitencia(path_arquivo, nome_arquivo):
    # ------------------------- Leitura dos arquivos --------------------------- #
    output_dir = path_arquivo.parent / "resultados" / "time_trace"
    output_dir.mkdir(parents=True, exist_ok=True)
    # Escolha do arquivo TIFF
    imagem = Image.open(path_arquivo)
    n_frames = imagem.n_frames
    fps = 1/0.03
    tempo_medida = [i / fps for i in range(n_frames)]

    # Carrega o CSV com as coordenadas das particulas
    path_centros = path_arquivo.parent / "resultados" / "centros" / f"centros_{nome_arquivo}.csv"
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

    intensidades = pd.DataFrame(np.array(intensidade_por_particula).T)

    # ------------------------ classificação de centros ---------------------------- #
    
    colunas_filtradas = []
    for coluna in intensidades:
        metricas = extrair_metricas(intensidades[coluna])
        classificacao = classificar(metricas)
        if classificacao:
            colunas_filtradas.append(intensidades[coluna])
    centros_intermitentes = pd.concat(colunas_filtradas, axis=1)

    centros_intermitentes.to_csv(output_dir / f"ictt_{nome_arquivo}.csv") # intermittent centers time trace 

    # ------------------------ graficos time trace ---------------------------- #
    output_dir_graficos = output_dir / f"{nome_arquivo}"
    output_dir_graficos.mkdir(parents=True, exist_ok=True)

    limite_inf = centros_intermitentes.to_numpy().mean() - 50
    limite_sup = centros_intermitentes.to_numpy().max() + 50
    for coluna in centros_intermitentes:
        m = extrair_metricas(centros_intermitentes[coluna])
        fig, ax = plt.subplots()
        ax.plot(tempo_medida, centros_intermitentes[coluna], linewidth=1)
        ax.set_title(f"Particula {coluna} - Coord: ({centros["X"].iloc[coluna]}, {centros["Y"].iloc[coluna]})")
        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel("Intensidade")
        ax.set_ylim(limite_inf, limite_sup)
        ax.text(
            0.95, 0.95,  # posição relativa (x, y) no sistema de coordenadas do eixo
            f"media: {m["media"]:.2f}\ndesvio: {m["desvio"]:.2f}\nvariancia: {m["variancia"]:.2f}\ncurtose: {m["curtose"]:.2f}\nrmm: {m["razao_max_mediana"]:.2f}\nn_picos: {m["num_picos"]}",
            transform=ax.transAxes,  # garante que a posição seja relativa (0 a 1)
            fontsize=9,
            verticalalignment='top',
            horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.5)  # define a caixa
        )
        fig.savefig(output_dir_graficos / f"particula{coluna}.png")
        plt.close(fig)

if __name__ == "__main__":
    analisar_intermitencia(input("Path do arquivo: "))