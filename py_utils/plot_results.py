import matplotlib.pyplot as plt
import os
import re
import numpy as np

# Directory contenente i risultati
results_dir = 'results'

# Thread testati
threads = [1, 2, 4, 8, 16, 32, 64]

# Numero di ripetizioni
repetitions = 5

# Dizionario per memorizzare i tempi
execution_times = {t: [] for t in threads}

# Funzione per estrarre il tempo di esecuzione dal file
def extract_time(file_content):
    # Modificare questa regex in base al formato effettivo dell'output
    # Questo è solo un esempio, assumendo che il tempo sia indicato come "Time: X.XXX seconds"
    match = re.search(r'Time:\s+(\d+\.\d+)', file_content)
    if match:
        return float(match.group(1))
    return None

# Leggi i file di risultato
for t in threads:
    for r in range(1, repetitions + 1):
        filename = f"output_{t}_threads_run_{r}.txt"
        filepath = os.path.join(results_dir, filename)
        
        try:
            with open(filepath, 'r') as file:
                content = file.read()
                time = extract_time(content)
                if time is not None:
                    execution_times[t].append(time)
        except FileNotFoundError:
            print(f"File non trovato: {filepath}")

# Calcola le medie
mean_times = [np.mean(execution_times[t]) for t in threads]

# Crea il grafico
plt.figure(figsize=(10, 6))
plt.bar([str(t) for t in threads], mean_times, color='skyblue', edgecolor='navy')
plt.xlabel('Numero di Thread')
plt.ylabel('Tempo di Esecuzione Medio (secondi)')
plt.title('Tempo di Esecuzione Medio di main_matrix per Numero di Thread')
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Aggiungi i valori sopra le colonne
for i, v in enumerate(mean_times):
    plt.text(i, v + 0.01, f"{v:.3f}", ha='center')

plt.tight_layout()
plt.savefig('execution_times.png')
plt.show()

print("Grafico generato: execution_times.png")