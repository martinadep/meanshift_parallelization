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
    "distance_mode_find",
    "distance_cluster"
]

# Colori per le esecuzioni
colors = {
    "coords_update": "blue",
    "kernel": "orange",
    "distance_shift": "red",
    "distance_mode_find": "green",
    "distance_cluster": "purple"
}

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

        # Trova il bandwidth
        bandwidth_match = re.search(r"Bandwidth: (\d+)", line)
        if bandwidth_match:
            current_bandwidth = int(bandwidth_match.group(1))

        # Trova i tempi di esecuzione
        for label in timing_labels:
            time_match = re.search(rf"{label} total execution time: ([\d.]+) s", line)
            if time_match and current_kernel and current_bandwidth:
                data[current_kernel][current_bandwidth][label] = float(time_match.group(1))

# Genera un unico grafico
fig, ax = plt.subplots(figsize=(12, 8))
bar_width = 0.2
x = np.arange(len(kernels))  # Posizioni dei kernel sull'asse X
x_offset = 0.25  # Margine tra i gruppi di colonne

# Prepara i dati per le barre
for i, bw in enumerate(bandwidths):
    offset = (i - 1) * bar_width  # Offset per posizionare le colonne della bandwidth
    bottom = np.zeros(len(kernels))
    for label in timing_labels:
        heights = [data[kernel][bw][label] for kernel in kernels]
        ax.bar(x + offset + x_offset, heights, bar_width, label=label if i == 0 else "", bottom=bottom, color=colors[label])
        bottom += heights

    # Aggiungi etichette delle bandwidth sotto ogni colonna
    for j, kernel in enumerate(kernels):
        ax.text(x[j] + offset + x_offset, -2, f"{bw}", ha="center", va="top", fontsize=10, color="black")

# Configura il grafico
ax.set_title("Execution Time Breakdown by Kernel and Bandwidth")
ax.set_xlabel("Kernel")
ax.set_ylabel("Execution Time (s)")
ax.set_xticks(x + x_offset)
ax.set_xticklabels(kernels)
ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
ax.grid(axis="y", linestyle="--", alpha=0.7)

# Salva il grafico
plt.tight_layout()
plt.savefig("./test/combined_execution_time.png")
plt.show()