import os
import re
import matplotlib.pyplot as plt
import numpy as np
import glob
from config import FONT_AXES, FONT_TICKS, FONT_LEGEND, FONT_TITLE, LANDSCAPE_INCHES, strong_scaling_dir, implementations as all_implementations, threads

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
                image_match = re.search(r"Dataset: \[\.\/data\/batch\/original_(\d+)\.csv\]", execution)
                if not image_match:
                    # Prova il pattern Windows con backslash
                    image_match = re.search(r"Dataset: \[\.\\data\\batch\\original_(\d+)\.csv\]", execution)
                
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

def extract_times_from_thread_blas_file(file_path):
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
                image_match = re.search(r"Dataset: \[\.\/data\/batch\/original_(\d+)\.csv\]", execution)
                if not image_match:
                    # Prova il pattern Windows con backslash
                    image_match = re.search(r"Dataset: \[\.\\data\\batch\\original_(\d+)\.csv\]", execution)
                
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
                                thread_number_match = re.search(r"slic_ms_blas_(\d+)_threads", file_name)
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
    
def extract_times_from_slic_ms_acc_file(file_path):
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
                image_match = re.search(r"Dataset: \[\.\/data\/batch\/original_(\d+)\.csv\]", execution)
                if not image_match:
                    # Prova il pattern Windows con backslash
                    image_match = re.search(r"Dataset: \[\.\\data\\batch\\original_(\d+)\.csv\]", execution)
                
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
    

def extract_times_from_faster_ms(file_path):
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
    results_dir = "output_pptx\output"
    
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

    # OPENBLAS
    thread_blas_files = glob.glob(os.path.join(results_dir, "slic_ms_blas_*_threads*"))
    if not thread_blas_files:
        print(f"Nessun file di thread trovato in {results_dir}")
        return
    
    thread_blas_counts = []
    for file_path in thread_blas_files:
        file_name = os.path.basename(file_path)
        thread_blas_match = re.search(r"slic_ms_blas_(\d+)_threads.txt", file_name)
        if thread_blas_match:
            thread_blas_counts.append(int(thread_blas_match.group(1)))

    thread_blas_results = {}
    for thread_blas_count in sorted(thread_blas_counts):
        file_path = os.path.join(results_dir, f"slic_ms_blas_{thread_blas_count}_threads.txt")
        print(f"Lettura del file {file_path}...")
        if os.path.exists(file_path):
            results_blas = extract_times_from_thread_blas_file(file_path)
            for image_id, data_blas in results_blas.items():
                if image_id not in thread_blas_results:
                    thread_blas_results[image_id] = []
                thread_blas_results[image_id].append(data_blas)
        else:
            print(f"File {file_path} non trovato.")
    
    # Verifica se abbiamo dati
    if not thread_blas_results:
        print("Nessun dato estratto dai file di thread blas.")
        return
    
    # MATRIX
    thread_matrix_files = glob.glob(os.path.join(results_dir, "slic_ms_matrix_*_threads*"))
    if not thread_matrix_files:
        print(f"Nessun file di thread trovato in {results_dir}")
        return

    thread_matrix_counts = []
    for file_path in thread_matrix_files:
        file_name = os.path.basename(file_path)
        thread_matrix_match = re.search(r"slic_ms_matrix_(\d+)_threads.txt", file_name)
        if thread_matrix_match:
            thread_matrix_counts.append(int(thread_matrix_match.group(1)))

    thread_matrix_results = {}
    for thread_matrix_count in sorted(thread_matrix_counts):
        file_path = os.path.join(results_dir, f"slic_ms_matrix_{thread_matrix_count}_threads.txt")
        print(f"Lettura del file {file_path}...")
        if os.path.exists(file_path):
            results_matrix = extract_times_from_thread_blas_file(file_path)
            for image_id, data_matrix in results_matrix.items():
                if image_id not in thread_matrix_results:
                    thread_matrix_results[image_id] = []
                thread_matrix_results[image_id].append(data_matrix)
        else:
            print(f"File {file_path} non trovato.")
    
    # Verifica se abbiamo dati
    if not thread_matrix_results:
        print("Nessun dato estratto dai file di thread matrix.")
        return
    
    # Leggi il file OpenACC
    acc_file_path = os.path.join(results_dir, "slic_ms_acc.txt")
    print(f"Lettura del file OpenACC {acc_file_path}...")
    if os.path.exists(acc_file_path):
        acc_results = extract_times_from_slic_ms_acc_file(acc_file_path)
        if not acc_results:
            print("Nessun dato estratto dal file OpenACC.")
    else:
        print(f"File OpenACC {acc_file_path} non trovato.")
        acc_results = {}
    
    # Leggi il file batch
    faster_ms_file_path = os.path.join(results_dir, "faster_ms.txt")
    print(f"Lettura del file batch {faster_ms_file_path}...")
    if os.path.exists(faster_ms_file_path):
        faster_ms_results = extract_times_from_faster_ms(faster_ms_file_path)
        if not faster_ms_results:
            print("Nessun dato estratto dal file batch.")
    else:
        print(f"File batch {faster_ms_file_path} non trovato.")
        faster_ms_results = {}
    
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
    
    # OPENBLAS
    best_configs_blas = {}
    for image_id, executions in thread_blas_results.items():
        if executions:
            best_exec_blas = min(executions, key=lambda x: x['total_time'])
            best_configs_blas[image_id] = best_exec_blas
    
    # Verifica se abbiamo dati validi
    if not best_configs_blas:
        print("Nessuna configurazione migliore trovata per OPENBLAS.")
        return
    
    # OPENBLAS
    best_configs_matrix = {}
    for image_id, executions in thread_matrix_results.items():
        if executions:
            best_exec_matrix = min(executions, key=lambda x: x['total_time'])
            best_configs_matrix[image_id] = best_exec_matrix

    # Verifica se abbiamo dati validi
    if not best_configs_matrix:
        print("Nessuna configurazione migliore trovata per matrix.")
        return
    
    # Prepara i dati per il grafico
    image_ids = sorted(best_configs.keys())
    best_times = [best_configs[img_id]['total_time'] for img_id in image_ids]
    best_times_blas = [best_configs_blas[img_id]['total_time'] for img_id in image_ids]
    best_times_matrix = [best_configs_matrix[img_id]['total_time'] for img_id in image_ids]
    best_threads = [best_configs[img_id]['threads'] for img_id in image_ids]
    best_threads_blas = [best_configs_blas[img_id]['threads'] for img_id in image_ids]
    best_threads_matrix = [best_configs_matrix[img_id]['threads'] for img_id in image_ids]
    batch_times = [faster_ms_results.get(img_id, 0) for img_id in image_ids]
    acc_times = [acc_results.get(img_id, {'total_time': 0})['total_time'] for img_id in image_ids]
    
    plt.rcParams.update({
        "text.usetex": False,
        "font.family": "serif",
        "font.serif": ["Times New Roman"],
    })
    # Crea il grafico
    fig, ax = plt.subplots(figsize=LANDSCAPE_INCHES)

    x = np.arange(len(image_ids))
    bar_width = 0.12  # Narrower width for 4 bars
    bar_space = 0.2

    from config import implementations
    impl_colors = {impl["name"]: impl["color"] for impl in implementations}

    # Line plot per implementazione
    ax.plot(x, batch_times, marker='o', markersize=3, label='Faster MeanShift Euc', color="#858585")
    ax.plot(x, acc_times, marker='o', markersize=3, label='SLIC + Mean Shift (OpenACC)', color="#f6ae2d")
    ax.plot(x, best_times, marker='o', markersize=3, label='SLIC + Mean Shift (OpenMP)', color=impl_colors.get('SLIC + MS (OpenMP)', '#f26419'))
    ax.plot(x, best_times_matrix, marker='o', markersize=3, label='SLIC + Mean Shift Matrix (OpenMP)', color=impl_colors.get('SLIC + MS Matrix (OpenMP)', '#4581af'))
    ax.plot(x, best_times_blas, marker='o', markersize=3, label='SLIC + Mean Shift Matrix (OpenMP + OpenBLAS)', color=impl_colors.get('SLIC + MS Matrix (OpenMP + OpenBLAS)', '#2f4858'))

    ax.set_xlabel('Image', fontsize=12)
    ax.set_ylabel('Execution Time (seconds)', fontsize=12)
    # ax.set_title('Comparison of MeanShift Implementations with Means')
    ax.set_xticks(x)
    ax.set_xticklabels([f"{img_id}" for img_id in image_ids])
    ax.legend()

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('implementation_comparison_all.pdf')
    plt.show()

    # box_data = [
    #         [t for t in batch_times if t > 0],
    #         [t for t in acc_times if t > 0],
    #         [t for t in best_times if t > 0],
    #         [t for t in best_times_matrix if t > 0],
    #         [t for t in best_times_blas if t > 0]
    #     ]
    # box_labels = [
    #         'Faster MeanShift Euc',
    #         'SLIC + Mean Shift (OpenACC)',
    #         'SLIC + Mean Shift (OpenMP)',
    #         'SLIC + Mean Shift Matrix (OpenMP)',
    #         'SLIC + Mean Shift Matrix (OpenMP + OpenBLAS)'
    #     ]

    # fig_box, ax_box = plt.subplots(figsize=(10, 6))
    # bplot = ax_box.boxplot(box_data, patch_artist=True, labels=box_labels)

    # # Colori coerenti con il grafico precedente
    # box_colors = ["#858585", "#f6ae2d", impl_colors.get('SLIC + MS (OpenMP)', '#f26419'), impl_colors.get('SLIC + MS Matrix (OpenMP)', '#4581af'), impl_colors.get('SLIC + MS Matrix (OpenMP + OpenBLAS)', '#2f4858')]
    # for patch, color in zip(bplot['boxes'], box_colors):
    #     patch.set_facecolor(color)

    # ax_box.set_ylabel('Execution Time (seconds)', fontsize=12)
    # ax_box.set_title('Execution Time Distribution per Implementation (Best Thread Config)', fontsize=14)
    # plt.xticks(rotation=20, ha='right')
    # # plt.yscale('log')  # Log scale for better visibility of distributions
    # plt.tight_layout()
    # plt.savefig('implementation_comparison_boxplot.pdf')
    # plt.show()
    
    # Stampa tabella statistica per ogni implementazione
    print("\nStatistiche per implementazione (solo best thread per immagine):")
    print("=" * 140)
    print(f"{'Implementazione':<35} {'Varianza':<12} {'Std Dev':<12} {'Img Min':<10} {'Tempo Min':<12} {'Threads Min':<12} {'Img Max':<10} {'Tempo Max':<12} {'Threads Max':<12}")
    print("=" * 140)

    stats_data = [
        ("Faster MeanShift Euc", batch_times, None),
        ("SLIC + Mean Shift (OpenACC)", acc_times, None),
        ("SLIC + Mean Shift (OpenMP)", best_times, best_threads),
        ("SLIC + Mean Shift Matrix (OpenMP)", best_times_matrix, best_threads_matrix),
        ("SLIC + Mean Shift Matrix (BLAS)", best_times_blas, best_threads_blas)
    ]

    for label, times, threads_list in stats_data:
        arr = np.array(times)
        valid = arr > 0
        arr_filt = arr[valid]
        imgs_filt = np.array(image_ids)[valid]
        threads_filt = np.array(threads_list)[valid] if threads_list is not None else None
        if arr_filt.size > 0:
            var = np.var(arr_filt)
            std = np.std(arr_filt)
            min_idx = np.argmin(arr_filt)
            max_idx = np.argmax(arr_filt)
            img_min = imgs_filt[min_idx]
            img_max = imgs_filt[max_idx]
            tempo_min = arr_filt[min_idx]
            tempo_max = arr_filt[max_idx]
            threads_min = str(threads_filt[min_idx]) if threads_list is not None else ""
            threads_max = str(threads_filt[max_idx]) if threads_list is not None else ""
            print(f"{label:<35} {var:<12.4f} {std:<12.4f} {img_min:<10} {tempo_min:<12.4f} {threads_min:<12} {img_max:<10} {tempo_max:<12.4f} {threads_max:<12}")
        else:
            print(f"{label:<35} {'-':<12} {'-':<12} {'-':<10} {'-':<12} {'':<12} {'-':<10} {'-':<12} {'':<12}")

    print("=" * 140)

    # Stampa la media delle best run per ogni implementazione
    print("\nMedia delle best run per ogni implementazione:")
    print("=" * 60)
    print(f"{'Implementazione':<35} {'Media (s)':<12}")
    print("=" * 60)
    for label, times, _ in stats_data:
        arr = np.array(times)
        valid = arr > 0
        arr_filt = arr[valid]
        if arr_filt.size > 0:
            mean_val = np.mean(arr_filt)
            print(f"{label:<35} {mean_val:<12.4f}")
        else:
            print(f"{label:<35} {'-':<12}")
    print("=" * 60)

    # Stampa un riepilogo dettagliato per ogni immagine
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