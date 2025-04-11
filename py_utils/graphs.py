import re
import matplotlib.pyplot as plt
import numpy as np

print("Importing libraries...")

# File di input
input_file = "./test/results.txt"

# Dati da estrarre
kernels = ["uniform", "epanechnikov", "gaussian"]
bandwidths = [10, 20, 30]
timing_labels = [
    "coords_update",
    "kernel",
    "distance_shift",
    "distance_iter",
    "distance_cluster"
]

# Struttura per salvare i dati
data = {kernel: {bw: {label: 0.0 for label in timing_labels} for bw in bandwidths} for kernel in kernels}

# Leggi il file e analizza i dati
with open(input_file, "r", encoding="utf-16") as file:
    lines = file.readlines()
    current_kernel = None
    current_bandwidth = None

    for line in lines:
        line = line.strip()  # Rimuovi spazi iniziali e finali
        
        # Trova il kernel
        kernel_match = re.search(r"Kernel: (\w+)", line)
        if kernel_match:
            current_kernel = kernel_match.group(1)
            print(f"Trovato kernel: {current_kernel}")  # Debug

        # Trova il bandwidth
        bandwidth_match = re.search(r"Bandwidth: (\d+)", line)
        if bandwidth_match:
            current_bandwidth = int(bandwidth_match.group(1))
            print(f"Trovato bandwidth: {current_bandwidth}")  # Debug

        # Trova i tempi di esecuzione
        for label in timing_labels:
            time_match = re.search(rf"{label} total execution time: ([\d.]+) s", line)
            if time_match and current_kernel and current_bandwidth:
                data[current_kernel][current_bandwidth][label] = float(time_match.group(1))
                print(f"Trovato {label}: {time_match.group(1)} s")  # Debug

# Debug: stampa i dati estratti
print("Dati estratti:")
print(data)

# Genera i grafici
for kernel in kernels:
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.5
    x = np.arange(len(bandwidths))  # Posizioni delle barre

    # Prepara i dati per le barre
    bottom = np.zeros(len(bandwidths))
    for label in timing_labels:
        heights = [data[kernel][bw][label] for bw in bandwidths]
        print(f"Altezze per {label} ({kernel}): {heights}")  # Debug
        ax.bar(x, heights, bar_width, label=label, bottom=bottom)
        bottom += heights

    # Configura il grafico
    ax.set_title(f"Execution Time Breakdown for {kernel.capitalize()} Kernel")
    ax.set_xlabel("Bandwidth")
    ax.set_ylabel("Execution Time (s)")
    ax.set_xticks(x)
    ax.set_xticklabels(bandwidths)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    # Salva il grafico
    plt.savefig(f"./test/{kernel}_execution_time.png")
    plt.close()

print("Grafici generati e salvati nella directory './test'.")