from identificador_particulas import identificar_particulas
from analise_intermitencia import analisar_intermitencia
import os
import easygui
# +-----------------   Identificador de partículas  ----------------+
# Pasta onde estão os arquivos
pasta_dados = easygui.diropenbox("Escolha a pasta de arquivos a analisar")

# Loop para processar cada arquivo
for nome_arquivo in os.listdir(pasta_dados):
    print(f"\nAnalisando arquivo: {nome_arquivo}")
    if nome_arquivo.endswith(".tif"):
        nome_arquivo = nome_arquivo.rsplit(".tif")[0]
        path_arquivo = os.path.join(pasta_dados, nome_arquivo + ".tif")
        pasta_saida = os.path.join(pasta_dados, nome_arquivo)
        novo_path_arquivo = os.path.join(pasta_saida, nome_arquivo + ".tif")
        os.mkdir(pasta_saida)
        os.rename(path_arquivo, novo_path_arquivo)
        print("Identificando partículas")
        identificar_particulas(novo_path_arquivo)
        print("Analisando intermitência")
        analisar_intermitencia(novo_path_arquivo)
