from identificador_particulas import identificar_particulas
from analise_intermitencia import analisar_intermitencia
from SM_rate import calculate_SM_rate
import os
import easygui
from pathlib import Path
# +-----------------   Identificador de partículas  ----------------+
# Pasta onde estão os arquivos
pasta_dados = Path(easygui.diropenbox("Escolha a pasta de arquivos a analisar"))

# Loop para processar cada arquivo
for nome_arquivo in os.listdir(pasta_dados):
    print(f"\nAnalisando arquivo: {nome_arquivo}")
    if nome_arquivo.endswith(".tif"):
        nome_arquivo = nome_arquivo.rsplit(".tif")[0]
        path_arquivo = pasta_dados / f"{nome_arquivo}.tif"
        pasta_saida = pasta_dados / "resultados"
        pasta_saida.mkdir(parents=True, exist_ok=True)
        print("Identificando partículas")
        identificar_particulas(path_arquivo, nome_arquivo)
        print("Analisando intermitência")
        analisar_intermitencia(path_arquivo, nome_arquivo)
        print("Single molecule statistics is cool")
        calculate_SM_rate(path_arquivo, nome_arquivo, 30)
