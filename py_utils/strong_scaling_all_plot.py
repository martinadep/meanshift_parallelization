import matplotlib.pyplot as plt
import os
import re
import numpy as np

# Directory contenente i risultati
results_dir = 'results_strong_scaling'

# Thread testati
threads = [1, 2, 4, 8, 16, 32, 64]

#Implementazioni da confrontare
implementations = [
    {"name": "mean_shift", "color": "#BC1957", "folder": "mean_shift"},  
    {"name": "mean_shift_sqrd", "color": "#D85A1A", "folder": "mean_shift_sqrd"},    
    {"name": "mean_shift_matrix", "color": "#FFAA00DA", "folder": "mean_shift_matrix"}, 
    {"name": "mean_shift_matrix_block", "color": "#FFD900", "folder": "mean_shift_matrix_block"}, 
    {"name": "slic_ms", "color": "#1B529F", "folder": "slic_ms"},               
    {"name": "slic_ms_sqrd", "color": "#38A5D0", "folder": "slic_sqrd_ms"},
    {"name": "slic_ms_matrix", "color": "#2A7709", "folder": "slic_matrix_ms"},
    {"name": "slic_ms_matrix_block", "color": "#1BBA13", "folder": "slic_matrix_block_ms"} 
]

# Dizionario per memorizzare i tempi di esecuzione per ogni implementazione
all_execution_times = {impl["name"]: {t: [] for t in threads} for impl in implementations}
all_mean_times = {impl["name"]: [] for impl in implementations}

# Update the extract_times function
def extract_times(file_content):
    # Extract both SLIC and mean shift times
    slic_times = re.findall(r'slic execution time: (\d+\.\d+)', file_content)
    mean_shift_times = re.findall(r'mean_shift execution time: (\d+\.\d+)', file_content)
    
    if not mean_shift_times:
        return []
    
    # Convert to float
    mean_shift_times = [float(time) for time in mean_shift_times]
    
    # For SLIC implementations, add the preprocessing time
    if slic_times and "slic" in file_content.lower():
        slic_times = [float(time) for time in slic_times]
        # Return combined times (SLIC + mean_shift)
        return [slic_times[i] + mean_shift_times[i] for i in range(min(len(slic_times), len(mean_shift_times)))]
    else:
        # No SLIC times or not a SLIC implementation, return mean_shift times only
        return mean_shift_times
    
# Funzione per provare diversi encoding
def try_read_file(filepath):
    encodings = ['utf-8', 'utf-16', 'latin1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            continue
    
    # Se tutti gli encoding falliscono, prova in binario
    try:
        with open(filepath, 'rb') as file:
            return file.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Errore nella lettura binaria: {str(e)}")
        return ""

# Leggi i file di risultato per ogni implementazione
for impl in implementations:
    print(f"Analisi dell'implementazione: {impl['name']}")
    
    for t in threads:
        filename = f"{impl['name']}_{t}_threads.txt"
        filepath = os.path.join(results_dir, impl["folder"], filename)
        
        try:
            if os.path.exists(filepath):
                content = try_read_file(filepath)
                times = extract_times(content)
                
                if times:
                    all_execution_times[impl["name"]][t].extend(times)
                    print(f"  Thread {t}: trovate {len(times)} misurazioni")
                else:
                    print(f"  Nessun tempo trovato nel file {filename}")
            else:
                print(f"  File non trovato: {filepath}")
                # Prova anche il percorso diretto senza sottocartella
                direct_filepath = os.path.join(results_dir, filename)
                if os.path.exists(direct_filepath):
                    content = try_read_file(direct_filepath)
                    times = extract_times(content)
                    
                    if times:
                        all_execution_times[impl["name"]][t].extend(times)
                        print(f"  Thread {t}: trovate {len(times)} misurazioni (percorso diretto)")
                    else:
                        print(f"  Nessun tempo trovato nel file {filename} (percorso diretto)")
        except Exception as e:
            print(f"  Errore con il file {filepath}: {str(e)}")

# Calcola le medie per ogni implementazione
for impl_name in all_execution_times:
    for t in threads:
        times = all_execution_times[impl_name][t]
        if times:
            mean_time = np.mean(times)
            all_mean_times[impl_name].append(mean_time)
            print(f"{impl_name} con {t} thread: tempo medio = {mean_time:.4f} secondi")
        else:
            all_mean_times[impl_name].append(0)
            print(f"Attenzione: nessun dato disponibile per {impl_name} con {t} thread")

# Verifica se ci sono tempi validi
has_data = False
for impl_name in all_mean_times:
    if any(all_mean_times[impl_name]):
        has_data = True
        break

if not has_data:
    print("Nessun dato valido trovato nei file. Verifica i file di input.")
    exit(1)

# Prepara il grafico dei tempi di esecuzione
fig, ax = plt.subplots(figsize=(14, 8))

# Larghezza delle barre
bar_width = 0.11
index = np.arange(len(threads))

# Crea le barre per ogni implementazione
for i, impl in enumerate(implementations):
    impl_name = impl["name"]
    color = impl["color"]
    times = all_mean_times[impl_name]

    if "slic" in impl_name:
        impl_label = f"{impl_name} (preprocessing + mean-shift)"
    else:
        impl_label = impl_name
    
    # Posizione delle barre
    position = index + (i - len(implementations)/2 + 0.5) * bar_width
    
    ax.bar(position, times, bar_width, color=color, label=impl_name)

# Configura gli assi e le etichette
ax.set_xlabel('Num of Threads')
ax.set_ylabel('Mean Execution Time (seconds)')
ax.set_title('Execution Time Comparison between Implementations')
ax.set_xticks(index)
ax.set_xticklabels([str(t) for t in threads])
ax.legend()
ax.set_yscale('log') 
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('strong_scaling_all.png')
plt.show()

# Calcola e mostra anche lo speedup per ogni implementazione
fig_speedup, ax_speedup = plt.subplots(figsize=(16, 8))

# Calcola lo speedup per ogni implementazione
for i, impl in enumerate(implementations):
    impl_name = impl["name"]
    color = impl["color"]
    times = all_mean_times[impl_name]
    
    # Calcola lo speedup solo se abbiamo dati validi
    if times[0] > 0:  # Se abbiamo un tempo valido per 1 thread
        speedups = [times[0]/t if t > 0 else 0 for t in times]
        
        # Posizione delle barre
        position = index + (i - len(implementations)/2 + 0.5) * bar_width
        
        ax_speedup.bar(position, speedups, bar_width, color=color, label=impl_name)

# Aggiungi la linea di speedup ideale
ideal_speedups = threads
ax_speedup.plot(index, ideal_speedups, 'r--', label='Ideal Speedup')

# Configura gli assi e le etichette
ax_speedup.set_xlabel('Num of Threads')
ax_speedup.set_ylabel('Speedup')
ax_speedup.set_title('Speedup comparison between implementations')
ax_speedup.set_xticks(index)
ax_speedup.set_xticklabels([str(t) for t in threads])
ax_speedup.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('strong_scaling_speedup_all.png')
plt.show()

print("Grafici generati: strong_scaling_all.png e strong_scaling_speedup_all.png")