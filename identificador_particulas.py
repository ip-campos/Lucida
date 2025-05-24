from PIL import Image
import numpy as np
from matplotlib import pyplot as plt
import cv2
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from utils import *

def identificar_particulas(path_arquivo):
    # Abre o arquivo TIFF
    path_imagem = Path(path_arquivo)
    imagem = Image.open(path_imagem)
    n_frames = imagem.n_frames
    frames = []

    # Cria uma lista de frames do vídeo
    for i in tqdm(range(n_frames)):
        imagem.seek(i)
        frame_array = np.array(imagem)
        frames.append(frame_array)

    # Calcula a intensidade média do video e o limiar
    intensidade_media = np.mean(frames)
    alpha = 4
    limiar = intensidade_media + alpha * np.sqrt(intensidade_media)

    contagem_centros = dict()
    centros = []
    frames_original = []
    frames_centroide = []

    for frame_idx in tqdm(range(len(frames)), desc="Analisando frames"):
        imagem_binaria = cv2.threshold(
            frames[frame_idx], limiar, 255, cv2.THRESH_BINARY)[1].astype(np.uint8)
        centroides = cv2.connectedComponentsWithStats(imagem_binaria)[3]
        imagem_marcada = cv2.cvtColor(imagem_binaria, cv2.COLOR_GRAY2BGR)
        for pos_centro in centroides[1:].astype(int):
            centro_tuple = tuple(pos_centro)
            if centro_tuple in contagem_centros:
                contagem_centros[centro_tuple] += 1
            else:
                contagem_centros[centro_tuple] = 1
            cv2.circle(imagem_marcada,
                       (centro_tuple[0], centro_tuple[1]), 3, (0, 0, 255), 1)

        frames_centroide.append(imagem_marcada)

    for key in contagem_centros.keys():
        if contagem_centros[key] > 5:
            centros.append(key)

    # Remove centros adjacentes
    centros = np.array(remover_adjacentes(centros, raio=1))

    # Salva os centros
    output_dir = path_imagem.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(centros, columns=["X", "Y"])
    df["limiar"] = limiar
    df["Intensidade media"] = intensidade_media
    df.to_csv(output_dir / "centros.csv", index=False)

    # Animação
    # fig, ax = plt.subplots(1, 2, figsize=(10, 5))
    # ax[0].set_title("Frame Original")
    # ax[1].set_title("Com Círculos")

    # img_display_1 = ax[0].imshow(frames[0], cmap="gray", animated=True)
    # img_display_2 = ax[1].imshow(frames_centroide[0], cmap="gray", animated=True)

    # def update(frame_index):
    #    img_display_1.set_array(frames[frame_index])
    #    img_display_2.set_array(frames_centroide[frame_index])
    #    return img_display_1, img_display_2

    # ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=50, blit=True)
    # plt.show()
