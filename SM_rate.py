from utils import *
import pandas as pd
from pathlib import Path

def calculate_SM_rate(path_arquivo, nome_arquivo, frate):
    ictt_csv = path_arquivo.parent / "resultados" / "time_trace" / f"ictt_{nome_arquivo}.csv"
    dados = pd.read_csv(ictt_csv, index_col=0)
    tempo = np.linspace(0, 2000*0.03, 2000)
    resultados_completos = []
    for coluna in dados:
        cnst = dados[coluna]
        thold1, thold2, avcount = calculate_threshold(cnst, 2)
        nst = apply_threshold(cnst, thold2)
        ntrans, smrate = count_transitions(nst, tempo)
        hist = compute_duration_histogram(nst, frate)
        cycle_stats = remove_long_events_and_spikes(
            hist["nfreqon"], hist["nfreqoff"],
            hist["avfreqon"], hist["avfreqoff"], 
            frate, nst, ntrans)
        
        resultado = {
        "id_centro": coluna,
        "avcount": avcount,
        "thold1": thold1,
        "thold2": thold2,
        "ntrans": ntrans,
        "smrate": smrate,
        **hist,
        **cycle_stats
        }
        resultados_completos.append(resultado)

    resultados_df = pd.DataFrame(resultados_completos)

    output_dir = path_arquivo.parent / "resultados" / "smrate"
    output_dir.mkdir(parents=True, exist_ok=True)
    resultados_df.to_csv(output_dir/ f"smr_{nome_arquivo}.csv")


if __name__ == "__main__":
    path_arquivo = Path("D:/01-08-2025-inicio-testes-novo-sistema/SM1-uzeo/filme1.tif")
    calculate_SM_rate(path_arquivo, "filme1", 30)


