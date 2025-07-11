import matplotlib.pyplot as plt
import os
import re
import numpy as np

# Directory contenente i risultati
results_dir = 'results_weak_scaling'

# Thread testati
threads = [1, 2, 4, 8, 16, 32, 64]

implementations = [
    {"name": "mean_shift", "color": "#BC1957", "folder": "mean_shift"},  
    {"name": "mean_shift_sqrd", "color": "#D85A1A", "folder": "mean_shift_sqrd"},    
    {"name": "mean_shift_matrix", "color": "#FFAA00DA", "folder": "mean_shift_matrix"}, 
    {"name": "mean_shift_matrix_block", "color": "#FFD900", "folder": "mean_shift_matrix_block"}, 
    {"name": "slic_ms", "color": "#1B529F", "folder": "slic_ms"},               
    {"name": "slic_ms_sqrd", "color": "#38A5D0", "folder": "slic_ms_sqrd"},
    {"name": "slic_ms_matrix", "color": "#2A7709", "folder": "slic_ms_matrix"},
    {"name": "slic_ms_matrix_block", "color": "#1BBA13", "folder": "slic_ms_matrix_block"} 
]

# Dizionario per memorizzare i tempi di esecuzione per ogni implementazione
all_execution_times = {impl["name"]: {t: {"slic": [], "mean_shift": []} for t in threads} for impl in implementations}
all_mean_times = {impl["name"]: {"slic": [], "mean_shift": []} for impl in implementations}

# Update the extract_times function to return times separately
def extract_times(file_content):
    # Extract both SLIC and mean shift times
    slic_times = re.findall(r'slic execution time: (\d+\.\d+)', file_content)
    mean_shift_times = re.findall(r'mean_shift execution time: (\d+\.\d+)', file_content)
    
    if not mean_shift_times:
        return [], []
    
    # Convert to float
    mean_shift_times = [float(time) for time in mean_shift_times]
    
    # For SLIC implementations, return both times separately
    if slic_times and "slic" in file_content.lower():
        slic_times = [float(time) for time in slic_times]
        # Return both time arrays separately
        return slic_times[:len(mean_shift_times)], mean_shift_times
    else:
        # No SLIC times or not a SLIC implementation, return empty list for SLIC and mean_shift times
        return [], mean_shift_times
    
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
                slic_times, ms_times = extract_times(content)
                
                if ms_times:
                    all_execution_times[impl["name"]][t]["slic"].extend(slic_times)
                    all_execution_times[impl["name"]][t]["mean_shift"].extend(ms_times)
                    print(f"  Thread {t}: trovate {len(ms_times)} misurazioni")
                else:
                    print(f"  Nessun tempo trovato nel file {filename}")
            else:
                print(f"  File non trovato: {filepath}")
                # Prova anche il percorso diretto senza sottocartella
                direct_filepath = os.path.join(results_dir, filename)
                if os.path.exists(direct_filepath):
                    content = try_read_file(direct_filepath)
                    slic_times, ms_times = extract_times(content)
                    
                    if ms_times:
                        all_execution_times[impl["name"]][t]["slic"].extend(slic_times)
                        all_execution_times[impl["name"]][t]["mean_shift"].extend(ms_times)
                        print(f"  Thread {t}: trovate {len(ms_times)} misurazioni (percorso diretto)")
                    else:
                        print(f"  Nessun tempo trovato nel file {filename} (percorso diretto)")
        except Exception as e:
            print(f"  Errore con il file {filepath}: {str(e)}")

# Calcola le medie per ogni implementazione
for impl_name in all_execution_times:
    for t in threads:
        ms_times = all_execution_times[impl_name][t]["mean_shift"]
        slic_times = all_execution_times[impl_name][t]["slic"]
        
        if ms_times:
            mean_ms_time = np.mean(ms_times)
            all_mean_times[impl_name]["mean_shift"].append(mean_ms_time)
            
            if slic_times:
                mean_slic_time = np.mean(slic_times)
                all_mean_times[impl_name]["slic"].append(mean_slic_time)
            else:
                all_mean_times[impl_name]["slic"].append(0)
                
            print(f"{impl_name} con {t} thread: tempo medio = {mean_ms_time+all_mean_times[impl_name]['slic'][-1]:.4f} secondi")
        else:
            all_mean_times[impl_name]["mean_shift"].append(0)
            all_mean_times[impl_name]["slic"].append(0)
            print(f"Attenzione: nessun dato disponibile per {impl_name} con {t} thread")

# Verifica se ci sono tempi validi
has_data = False
for impl_name in all_mean_times:
    if any(all_mean_times[impl_name]["mean_shift"]):
        has_data = True
        break

if not has_data:
    print("Nessun dato valido trovato nei file. Verifica i file di input.")
    exit(1)

# Prepara il grafico dei tempi di esecuzione con scala logaritmica
plt.rcParams.update({'font.size': 14})  # Set global font size
fig, ax = plt.subplots(figsize=(16, 8))

# Larghezza delle barre
bar_width = 0.11
index = np.arange(len(threads))

# Map SLIC implementations to their corresponding mean_shift implementation for color matching
slic_to_ms_map = {
    "slic_ms": "mean_shift",
    "slic_ms_sqrd": "mean_shift_sqrd",
    "slic_ms_matrix": "mean_shift_matrix",
    "slic_ms_matrix_block": "mean_shift_matrix_block"
}

# Find color for each implementation
color_map = {impl["name"]: impl["color"] for impl in implementations}

# Crea le barre per ogni implementazione
for i, impl in enumerate(implementations):
    impl_name = impl["name"]
    color = impl["color"]
    
    # Posizione delle barre
    position = index + (i - len(implementations)/2 + 0.5) * bar_width
    
    if "slic" in impl_name:
        # For SLIC implementations, show stacked bars
        slic_times = all_mean_times[impl_name]["slic"]
        ms_times = all_mean_times[impl_name]["mean_shift"]
        
        # Get corresponding mean_shift implementation color
        ms_impl = slic_to_ms_map.get(impl_name)
        ms_color = color_map.get(ms_impl, color)
        
        # Draw SLIC part (bottom)
        ax.bar(position, slic_times, bar_width, color='#38A5D0', label=f"{impl_name} (SLIC)" if i == 4 else "")
        
        # Draw mean_shift part (top)
        ax.bar(position, ms_times, bar_width, bottom=slic_times, color=ms_color, 
               label=f"{impl_name} (mean-shift)" if i == 4 else "")
    else:
        # For regular mean_shift implementations, show simple bars
        times = all_mean_times[impl_name]["mean_shift"]
        ax.bar(position, times, bar_width, color=color, label=impl_name)

# Fix legend to avoid duplicates
handles, labels = ax.get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax.legend(by_label.values(), by_label.keys(), fontsize=12)

# Configura gli assi e le etichette
ax.set_xlabel('Num of Threads', fontsize=16)
ax.set_ylabel('Mean Execution Time (seconds)', fontsize=16)
ax.set_title('Weak Scaling: Benchmark Comparison over Implementations', fontsize=18)
ax.set_xticks(index)
ax.set_xticklabels([str(t) for t in threads], fontsize=14)
ax.set_yscale('log')  # Scala logaritmica per l'asse y
plt.grid(axis='y', linestyle='--', alpha=0.7)
ax.tick_params(axis='y', labelsize=14)

plt.tight_layout()
plt.savefig('weak_scaling_all.png')
plt.show()

# Calcola e mostra anche l'efficienza per ogni implementazione (per weak scaling)
fig_efficiency, ax_efficiency = plt.subplots(figsize=(16, 8))

# Calcola l'efficienza per ogni implementazione
for i, impl in enumerate(implementations):
    impl_name = impl["name"]
    color = impl["color"]
    
    # Calculate total times (SLIC + mean_shift)
    total_times = [all_mean_times[impl_name]["slic"][j] + all_mean_times[impl_name]["mean_shift"][j] 
                  for j in range(len(threads))]
    
    # Calcola l'efficienza solo se abbiamo dati validi (tempo_1_thread / tempo_n_thread)
    if total_times[0] > 0:  # Se abbiamo un tempo valido per 1 thread
        # Per weak scaling, l'efficienza ideale è 1.0 (tempo costante)
        # L'efficienza è il rapporto tra tempo con 1 thread e tempo con n thread
        efficiency = [total_times[0]/t if t > 0 else 0 for t in total_times]
        
        # Posizione delle barre con maggiore distanziamento
        position = index + (i - len(implementations)/2 + 0.5) * bar_width
        
        ax_efficiency.bar(position, efficiency, bar_width, color=color, label=impl_name)

# Aggiungi la linea di efficienza ideale (1.0)
ax_efficiency.axhline(y=1.0, linestyle='--', color='r', label='Ideal Efficiency (1.0)')

# Configura gli assi e le etichette
ax_efficiency.set_xlabel('Num of Threads', fontsize=16)
ax_efficiency.set_ylabel('Efficiency', fontsize=16)
ax_efficiency.set_title('Weak Scaling: Efficiency Comparison over Implementations', fontsize=18)
ax_efficiency.set_xticks(index)
ax_efficiency.set_xticklabels([str(t) for t in threads], fontsize=14)
ax_efficiency.legend(fontsize=12)
ax_efficiency.set_yscale('log')  # Scala logaritmica per l'asse y
plt.grid(axis='y', linestyle='--', alpha=0.7)
ax_efficiency.tick_params(axis='y', labelsize=14)

plt.tight_layout()
plt.savefig('weak_scaling_efficiency_all.png')
plt.show()

print("Grafici generati: weak_scaling_all.png e weak_scaling_efficiency_all.png")