import re
import os
import numpy as np
import matplotlib.pyplot as plt
from utils import try_read_file
from config import timing_colors

print("Importing libraries...")

# File di input
input_file = "./results.txt"

# Check if file exists
if not os.path.exists(input_file):
    print(f"Error: File {input_file} does not exist!")
    exit(1)

# Dati da estrarre
timing_labels = [
    "coords_update",
    "kernel",
    "distance_shift",
    "distance_mode_find",
    "distance_cluster"
]

# First pass: detect all kernels and bandwidths from the file
detected_kernels = set()
detected_bandwidths = set()

content = try_read_file(input_file)
lines = content.split('\n')

for line in lines:
    line = line.strip()
    
    kernel_match = re.search(r"Kernel: (\w+)", line)
    if kernel_match:
        detected_kernels.add(kernel_match.group(1))
        
    bandwidth_match = re.search(r"Bandwidth: (\d+)", line)
    if bandwidth_match:
        detected_bandwidths.add(int(bandwidth_match.group(1)))

# Convert to sorted lists
kernels = sorted(list(detected_kernels)) if detected_kernels else ["uniform", "epanechnikov", "gaussian"]
bandwidths = sorted(list(detected_bandwidths))

print(f"Detected kernels: {kernels}")
print(f"Detected bandwidths: {bandwidths}")

# Struttura per salvare i dati
data = {kernel: {bw: {label: 0.0 for label in timing_labels} for bw in bandwidths} for kernel in kernels}

# Leggi il file e analizza i dati
current_kernel = None
current_bandwidth = None

for line in lines:
    line = line.strip()

    # Trova il kernel
    kernel_match = re.search(r"Kernel: (\w+)", line)
    if kernel_match:
        current_kernel = kernel_match.group(1)

    # Trova il bandwidth
    bandwidth_match = re.search(r"Bandwidth: (\d+)", line)
    if bandwidth_match:
        current_bandwidth = int(bandwidth_match.group(1))

    # Trova i tempi di esecuzione - FIX: using raw string for regex
    for label in timing_labels:
        time_match = re.search(r"{} total execution time: ([\d.]+)".format(label), line)
        if time_match and current_kernel is not None and current_bandwidth is not None:
            data[current_kernel][current_bandwidth][label] = float(time_match.group(1))

# Genera un unico grafico
plt.figure(figsize=(12, 10))  # Increased height to avoid layout issues
fig, ax = plt.subplots(figsize=(12, 10))
bar_width = 0.2

# If only one kernel, place it in the middle
x = np.arange(len(kernels))
x_offset = 0.25

# Check if we have one or multiple bandwidths
multiple_bandwidths = len(bandwidths) > 1

# Prepara i dati per le barre
for i, bw in enumerate(bandwidths):
    offset = (i - len(bandwidths)//2) * bar_width if multiple_bandwidths else 0
    bottom = np.zeros(len(kernels))
    
    for label in timing_labels:
        heights = [data[kernel][bw][label] for kernel in kernels]
        label_text = f"{label} (bw={bw})" if multiple_bandwidths else label
        legend_needed = i == 0 if multiple_bandwidths else True
        
        ax.bar(x + offset + x_offset, heights, bar_width, 
               label=label_text if legend_needed else "", 
               bottom=bottom, color=timing_colors[label])
        bottom += heights
    
    # Add bandwidth labels if multiple bandwidths
    if multiple_bandwidths:
        for j, kernel in enumerate(kernels):
            ax.text(x[j] + offset + x_offset, -0.5, f"bw={bw}", 
                    ha="center", va="top", fontsize=10, color="black")

# Configura il grafico
if multiple_bandwidths:
    title = "Execution Time Breakdown by Kernel and Bandwidth"
else:
    title = f"Execution Time Breakdown for {kernels[0]} kernel (bw={bandwidths[0]})"
    
ax.set_title(title)
ax.set_xlabel("Kernel")
ax.set_ylabel("Execution Time (s)")
ax.set_xticks(x + x_offset)
ax.set_xticklabels(kernels)
ax.legend(loc="upper left", bbox_to_anchor=(1, 0.5))
ax.grid(axis="y", linestyle="--", alpha=0.7)

# Adjust layout to avoid warnings
plt.tight_layout(rect=[0, 0, 0.85, 1])  # Leave space for legend

# Salva il grafico
output_dir = "./test"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    
plt.savefig(f"{output_dir}/combined_execution_time.png")
print(f"Plot saved to {output_dir}/combined_execution_time.png")
plt.close()