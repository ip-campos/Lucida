from PIL import Image
import easygui
import cv2
import numpy as np

#Carregar o arquivo tiff
arquivo_tiff = easygui.fileopenbox()
imagem = Image.open(arquivo_tiff)

#Obtém o número de frames do arquivo e as dimensões da imagem
altura, largura = imagem.size
n_frames = imagem.n_frames
print(f"O número de frames do arquivo é: {n_frames};\nAltura: {altura}, Largura: {largura}")

#Cria um arquivo de vídeo mp4
path_out = easygui.filesavebox()
fps = 20
fourcc = cv2.VideoWriter_fourcc(*"XVID")
saida_video = cv2.VideoWriter(path_out, fourcc, fps, (largura, altura), isColor=True)

#processa os frames e adiciona ao video
for i in range(n_frames):
    imagem.seek(i)
    frame = np.array(imagem)

    #Converte para 8 bits, caso seja diferente
    if frame.dtype != np.uint8:
        frame = (frame / frame.max() * 255).astype(np.uint8)

    #converte o frame para um formato suportado para opencv
    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

    #adiciona o frame ao vídeo
    saida_video.write(frame)

#Finaliza o vídeo
saida_video.release()
print(f"Vídeo salvo como {path_out}")