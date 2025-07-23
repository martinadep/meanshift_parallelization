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
    "distance_kernel",
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
        
    bandwidth_match = re.search(r"Bandwidth: ([\d.]+)", line)
    if bandwidth_match:
        detected_bandwidths.add(float(bandwidth_match.group(1)))

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
    bandwidth_match = re.search(r"Bandwidth: ([\d.]+)", line)
    if bandwidth_match:
        current_bandwidth = float(bandwidth_match.group(1))

    # Trova i tempi di esecuzione - FIX: using raw string for regex
    for label in timing_labels:
        time_match = re.search(r"{} total execution time: ([\d.]+)".format(label), line)
        if time_match and current_kernel is not None and current_bandwidth is not None:
            data[current_kernel][current_bandwidth][label] = float(time_match.group(1))
# Genera un unico grafico
plt.figure(figsize=(14, 12))  # Increased size for better readability
fig, ax = plt.subplots(figsize=(14, 12))
bar_width = 0.2

# If only one kernel, place it in the middle
y = np.arange(len(kernels))
y_offset = 0.25

# Check if we have one or multiple bandwidths
multiple_bandwidths = len(bandwidths) > 1

# Prepara i dati per le barre
for i, bw in enumerate(bandwidths):
    offset = (i - len(bandwidths)//2) * bar_width if multiple_bandwidths else 0
    left = np.zeros(len(kernels))
    
    for label in timing_labels:
        widths = [data[kernel][bw][label] for kernel in kernels]
        label_text = f"{label}" if multiple_bandwidths else label
        legend_needed = i == 0 if multiple_bandwidths else True
        
        ax.barh(y + offset + y_offset, widths, bar_width, 
               label=label_text if legend_needed else "", 
               left=left, color=timing_colors[label])
        left += widths
    
    # Add bandwidth labels at the beginning of each bar (inside the plot)
    if multiple_bandwidths:
        for j, kernel in enumerate(kernels):
            # Position the text at the very beginning of the bar
            ax.text(0.06, y[j] + offset + y_offset, f"bw={bw}", 
                    ha="left", va="center", fontsize=14, color="white", 
                    weight="bold", alpha=0.7)

# Configura il grafico
if multiple_bandwidths:
    title = "Execution Time Breakdown by Kernel and Bandwidth"
else:
    title = f"Execution Time Breakdown for {kernels[0]} kernel (bw={bandwidths[0]})"
    
ax.set_title(title, fontsize=18)
ax.set_ylabel("Kernel", fontsize=16)
ax.set_xlabel("Execution Time (s)", fontsize=16)
ax.set_yticks(y + y_offset)
ax.set_yticklabels(kernels, fontsize=14)
ax.tick_params(axis='x', labelsize=14)
ax.legend(loc="upper right", bbox_to_anchor=(1, 0.5), fontsize=12)
ax.grid(axis="x", linestyle="--", alpha=0.7)

# Adjust layout to avoid warnings
plt.tight_layout(rect=[0, 0, 0.85, 1])  # Leave space for legend
# Salva il grafico
output_dir = "./"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    
plt.savefig(f"{output_dir}/breakdown_meanshift.png")
print(f"Plot saved to {output_dir}/breakdown_meanshift.png")
plt.close()