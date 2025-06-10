import matplotlib.pyplot as plt
import os
import re
import numpy as np

# Directory contenente i risultati
results_dir = 'results'

# Thread testati
threads = [1, 2, 4, 8, 16, 32, 64]

# Dizionario per memorizzare i tempi
execution_times = {t: [] for t in threads}

# Funzione per estrarre i tempi di esecuzione dal file
def extract_times(file_content):
    # Cerca tutte le occorrenze di tempi nel file
    times = re.findall(r'mean_shift execution time: (\d+\.\d+)', file_content)
    if times:
        print(f"Trovati {len(times)} tempi di esecuzione")
    return [float(time) for time in times]

# Leggi i file di risultato
for t in threads:
    filename = f"main_matrix_block/main_matrix_block_{t}_threads.txt"
    filepath = os.path.join(results_dir, filename)
    
    try:
        # Leggi il file specificando l'encoding UTF-16
        with open(filepath, 'r', encoding='utf-16') as file:
            content = file.read()
            times = extract_times(content)
            if times:
                execution_times[t].extend(times)
                print(f"Thread {t}: trovate {len(times)} misurazioni")
            else:
                print(f"Nessun tempo trovato nel file {filename}")
    except FileNotFoundError:
        print(f"File non trovato: {filepath}")

# Calcola le medie
mean_times = []
for t in threads:
    if execution_times[t]:
        mean_times.append(np.mean(execution_times[t]))
        print(f"Thread {t}: tempo medio = {mean_times[-1]:.4f} secondi")
    else:
        mean_times.append(0)  # Se non ci sono dati, inserisci 0
        print(f"Attenzione: nessun dato disponibile per {t} thread")

# Verifica se ci sono tempi validi
if not any(mean_times):
    print("Nessun tempo valido trovato nei file. Verifica i file di input.")
    exit(1)

# Crea il grafico
plt.figure(figsize=(10, 6))
plt.bar([str(t) for t in threads], mean_times, color='skyblue', edgecolor='navy')
plt.xlabel('Numero di Thread')
plt.ylabel('Tempo di Esecuzione Medio (secondi)')
plt.title('Tempo di Esecuzione Medio di Mean-Shift per Numero di Thread')
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Aggiungi i valori sopra le colonne
valid_times = [t for t in mean_times if t > 0]
if valid_times:
    max_time = max(valid_times)
    for i, v in enumerate(mean_times):
        if v > 0:
            plt.text(i, v + max_time*0.01, f"{v:.3f}", ha='center')

# Aggiungi una linea che mostra il tempo sequenziale
if mean_times[0] > 0:
    plt.axhline(y=mean_times[0], color='red', linestyle='--', alpha=0.5, label='Tempo sequenziale')
    plt.legend()

plt.tight_layout()
plt.savefig('execution_times.png')
plt.show()

# Calcola e mostra anche lo speedup
if mean_times[0] > 0:
    plt.figure(figsize=(10, 6))
    speedups = [mean_times[0]/t if t > 0 else 0 for t in mean_times]
    plt.bar([str(t) for t in threads], speedups, color='lightgreen', edgecolor='darkgreen')
    plt.xlabel('Numero di Thread')
    plt.ylabel('Speedup')
    plt.title('Speedup di Mean-Shift per Numero di Thread')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Linea di speedup ideale
    ideal_speedups = [min(t/threads[0], t) for t in threads]
    plt.plot([str(t) for t in threads], ideal_speedups, 'r--', label='Speedup ideale')
    
    # Aggiungi i valori sopra le colonne
    valid_speedups = [s for s in speedups if s > 0]
    if valid_speedups:
        max_speedup = max(valid_speedups)
        for i, v in enumerate(speedups):
            if v > 0:
                plt.text(i, v + max_speedup*0.01, f"{v:.2f}", ha='center')
    
    plt.legend()
    plt.tight_layout()
    plt.savefig('speedup.png')
    plt.show()

print("Grafici generati: execution_times.png e speedup.png")