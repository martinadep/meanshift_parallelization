import os
import re
import matplotlib.pyplot as plt
import numpy as np
import glob

def extract_times_from_thread_file(file_path):
    """Estrae i tempi di esecuzione dal file di thread specificato."""
    results = {}
    current_image = None
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
            # Trova tutte le esecuzioni nel file
            executions = content.split("=============================================================")
            
            for execution in executions:
                if not execution.strip():
                    continue
                
                # Estrai il nome dell'immagine
                image_match = re.search(r"Dataset: \[\.\/data\/original_(\d+)\.csv\]", execution)
                if not image_match:
                    # Prova il pattern Windows con backslash
                    image_match = re.search(r"Dataset: \[\.\\data\\original_(\d+)\.csv\]", execution)
                
                if image_match:
                    current_image = image_match.group(1)
                    
                    # Estrai i tempi di esecuzione
                    slic_time_match = re.search(r"slic execution time: (\d+\.\d+)", execution)
                    ms_time_match = re.search(r"mean_shift execution time: (\d+\.\d+)", execution)
                    
                    if slic_time_match and ms_time_match:
                        slic_time = float(slic_time_match.group(1))
                        ms_time = float(ms_time_match.group(1))
                        total_time = slic_time + ms_time
                        
                        # Estrai il numero di thread
                        thread_match = re.search(r"Running with (\d+) threads", execution)
                        if thread_match:
                            threads = int(thread_match.group(1))
                            
                            # Usa il numero di thread dal nome del file se non trovato nel contenuto
                            if threads == 0:
                                file_name = os.path.basename(file_path)
                                thread_number_match = re.search(r"slic_ms_(\d+)_threads", file_name)
                                if thread_number_match:
                                    threads = int(thread_number_match.group(1))
                            
                            results[current_image] = {
                                'slic_time': slic_time,
                                'ms_time': ms_time,
                                'total_time': total_time,
                                'threads': threads
                            }
        return results
    except Exception as e:
        print(f"Errore durante la lettura del file {file_path}: {e}")
        return {}

def extract_times_from_acc_file(file_path):
    """Estrae i tempi di esecuzione dal file OpenACC specificato."""
    results = {}
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
            # Trova tutte le esecuzioni nel file
            executions = content.split("=============================================================")
            
            for execution in executions:
                if not execution.strip():
                    continue
                
                # Estrai il nome dell'immagine
                image_match = re.search(r"Dataset: \[\.\/data\/original_(\d+)\.csv\]", execution)
                if image_match:
                    image_id = image_match.group(1)
                    
                    # Estrai i tempi di esecuzione
                    slic_time_match = re.search(r"slic execution time: (\d+\.\d+)", execution)
                    ms_time_match = re.search(r"mean_shift execution time: (\d+\.\d+)", execution)
                    
                    if slic_time_match and ms_time_match:
                        slic_time = float(slic_time_match.group(1))
                        ms_time = float(ms_time_match.group(1))
                        total_time = slic_time + ms_time
                        
                        results[image_id] = {
                            'slic_time': slic_time,
                            'ms_time': ms_time,
                            'total_time': total_time
                        }
        return results
    except Exception as e:
        print(f"Errore durante la lettura del file OpenACC {file_path}: {e}")
        return {}

def extract_times_from_batch_file(file_path):
    """Estrae i tempi di esecuzione dal file batch."""
    results = {}
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
            # Trova tutte le esecuzioni nel file
            executions = content.split("----- Esecuzione per original_")
            
            for execution in executions[1:]:  # Salta il primo elemento vuoto
                if not execution.strip():
                    continue
                
                # Estrai il nome dell'immagine
                image_match = re.search(r"(\d+)\.csv", execution)
                if image_match:
                    image_id = image_match.group(1)
                    
                    # Estrai il tempo di esecuzione
                    time_match = re.search(r"MeanShiftEuc finished in (\d+\.\d+) seconds", execution)
                    
                    if time_match:
                        batch_time = float(time_match.group(1))
                        results[image_id] = batch_time
        return results
    except Exception as e:
        print(f"Errore durante la lettura del file batch {file_path}: {e}")
        return {}

def main():
    # Definisci il percorso alla directory results_strong_scaling
    results_dir = "results_strong_scaling"
    
    # Verifica che la directory esista
    if not os.path.exists(results_dir):
        print(f"Directory {results_dir} non trovata. Verificare il percorso.")
        return
    
    # Cerca i file di thread nella directory
    thread_files = glob.glob(os.path.join(results_dir, "slic_ms_*_threads*"))
    if not thread_files:
        print(f"Nessun file di thread trovato in {results_dir}")
        return
    
    # Ottieni il numero di thread dai nomi dei file
    thread_counts = []
    for file_path in thread_files:
        file_name = os.path.basename(file_path)
        thread_match = re.search(r"slic_ms_(\d+)_threads.txt", file_name)
        if thread_match:
            thread_counts.append(int(thread_match.group(1)))
    
    # Leggi i file di thread
    thread_results = {}
    for thread_count in sorted(thread_counts):
        file_path = os.path.join(results_dir, f"slic_ms_{thread_count}_threads.txt")
        print(f"Lettura del file {file_path}...")
        if os.path.exists(file_path):
            results = extract_times_from_thread_file(file_path)
            for image_id, data in results.items():
                if image_id not in thread_results:
                    thread_results[image_id] = []
                thread_results[image_id].append(data)
        else:
            print(f"File {file_path} non trovato.")
    
    # Verifica se abbiamo dati
    if not thread_results:
        print("Nessun dato estratto dai file di thread.")
        return
    
    # Leggi il file OpenACC
    acc_file_path = os.path.join(results_dir, "slic_ms_OpenACC.txt")
    print(f"Lettura del file OpenACC {acc_file_path}...")
    if os.path.exists(acc_file_path):
        acc_results = extract_times_from_acc_file(acc_file_path)
        if not acc_results:
            print("Nessun dato estratto dal file OpenACC.")
    else:
        print(f"File OpenACC {acc_file_path} non trovato.")
        acc_results = {}
    
    # Leggi il file batch
    batch_file_path = os.path.join(results_dir, "results_batch.txt")
    print(f"Lettura del file batch {batch_file_path}...")
    if os.path.exists(batch_file_path):
        batch_results = extract_times_from_batch_file(batch_file_path)
        if not batch_results:
            print("Nessun dato estratto dal file batch.")
    else:
        print(f"File batch {batch_file_path} non trovato.")
        batch_results = {}
    
    # Trova la configurazione migliore per ogni immagine
    best_configs = {}
    for image_id, executions in thread_results.items():
        if executions:
            best_exec = min(executions, key=lambda x: x['total_time'])
            best_configs[image_id] = best_exec
    
    # Verifica se abbiamo dati validi
    if not best_configs:
        print("Nessuna configurazione migliore trovata.")
        return
    
    # Prepara i dati per il grafico
    image_ids = sorted(best_configs.keys())
    best_times = [best_configs[img_id]['total_time'] for img_id in image_ids]
    best_threads = [best_configs[img_id]['threads'] for img_id in image_ids]
    batch_times = [batch_results.get(img_id, 0) for img_id in image_ids]
    acc_times = [acc_results.get(img_id, {'total_time': 0})['total_time'] for img_id in image_ids]
    
    # Crea il grafico
    fig, ax = plt.subplots(figsize=(16, 8))
    
    x = np.arange(len(image_ids))
    width = 0.25  # Riduci larghezza per far spazio a una terza barra
    
    batch_bars = ax.bar(x - width, batch_times, width, label='Faster MeanShift Euc')
    best_bars = ax.bar(x, best_times, width, label='SLIC + Mean Shift (OpenMP)')
    acc_bars = ax.bar(x + width, acc_times, width, label='SLIC + Mean Shift (OpenACC)')
    
    ax.set_xlabel('Image')
    ax.set_ylabel('Execution Time (seconds)')
    ax.set_title('Comparison of MeanShift Implementations')
    ax.set_xticks(x)
    ax.set_xticklabels([f"{img_id}" for img_id in image_ids])
    ax.legend()
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Aggiungi le etichette di tempo
    for i, (batch_time, best_time, acc_time) in enumerate(zip(batch_times, best_times, acc_times)):
        if batch_time > 0:
            ax.text(i - width, batch_time + 0.1, f"{batch_time:.2f}s", 
                    ha='center', va='bottom', fontsize=8)
        
        if best_time > 0:
            thread_text = f"{best_time:.2f}s\n({best_threads[i]} threads)"
            ax.text(i, best_time + 0.1, thread_text, 
                    ha='center', va='bottom', fontsize=8)
        
        if acc_time > 0:
            ax.text(i + width, acc_time + 0.1, f"{acc_time:.2f}s", 
                    ha='center', va='bottom', fontsize=8)
    
    # Salva e mostra il grafico
    plt.savefig('implementation_comparison.png')
    plt.show()
    
    # Stampa un riepilogo
    print("\nRiepilogo delle configurazioni per immagine:")
    print("=" * 100)
    print(f"{'Immagine':<10} {'OpenMP Threads':<15} {'OpenMP Totale':<15} {'OpenMP SLIC':<15} {'OpenMP MS':<15} "
          f"{'OpenACC Totale':<15} {'OpenACC SLIC':<15} {'OpenACC MS':<15}")
    print("=" * 100)
    
    for img_id in image_ids:
        best = best_configs[img_id]
        acc_data = acc_results.get(img_id, {'total_time': 0, 'slic_time': 0, 'ms_time': 0})
        
        print(f"{img_id:<10} {best['threads']:<15d} "
              f"{best['total_time']:<15.3f} {best['slic_time']:<15.3f} {best['ms_time']:<15.3f} "
              f"{acc_data['total_time']:<15.3f} {acc_data['slic_time']:<15.3f} {acc_data['ms_time']:<15.3f}")

if __name__ == "__main__":
    main()