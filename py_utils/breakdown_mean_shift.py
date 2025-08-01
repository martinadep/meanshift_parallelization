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
    "distance_shift",
    "distance_cluster", 
    "coords_update",
    "kernel",
    "distance_kernel"
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

# Convert to sorted lists with specific kernel order
kernel_order = ["epanechnikov", "uniform", "gaussian"]
kernels = [k for k in kernel_order if k in detected_kernels] if detected_kernels else kernel_order
bandwidths = sorted(list(detected_bandwidths))

print(f"Detected kernels: {kernels}")
print(f"Detected bandwidths: {bandwidths}")

# Struttura per salvare i dati - organized by bandwidth first, then kernel
data = {bw: {kernel: {label: 0.0 for label in timing_labels} for kernel in kernels} for bw in bandwidths}
shift_calls = {bw: {kernel: 0 for kernel in kernels} for bw in bandwidths}

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
            data[current_bandwidth][current_kernel][label] = float(time_match.group(1))
    
    # Trova il numero di chiamate shift_single_point
    calls_match = re.search(r"shift_single_point total calls: (\d+)", line)
    if calls_match and current_kernel is not None and current_bandwidth is not None:
        shift_calls[current_bandwidth][current_kernel] = int(calls_match.group(1))
# Genera un unico grafico
plt.figure(figsize=(18, 12))  # Increased size for better readability
fig, ax = plt.subplots(figsize=(20, 12))
bar_width = 0.15

# Use bandwidth on y-axis
y = np.arange(len(bandwidths))
y_offset = 0.25

# Check if we have one or multiple kernels
multiple_kernels = len(kernels) > 1

# Prepara i dati per le barre
for i, kernel in enumerate(kernels):
    offset = (i - len(kernels)//2) * bar_width if multiple_kernels else 0
    left = np.zeros(len(bandwidths))
    
    for label in timing_labels:
        widths = [data[bw][kernel][label] for bw in bandwidths]
        label_text = f"{label}" if multiple_kernels else label
        legend_needed = i == 0 if multiple_kernels else True
        
        ax.barh(y + offset + y_offset, widths, bar_width, 
               label=label_text if legend_needed else "", 
               left=left, color=timing_colors[label])
        left += widths
    
    # Add kernel names inside the bars (at the beginning)
    if multiple_kernels:
        for j, bw in enumerate(bandwidths):
            # Position the text at the very beginning of the bar
            ax.text(0.06, y[j] + offset + y_offset, f"{kernel}", 
                    ha="left", va="center", fontsize=22, color="white", 
                    weight="bold", alpha=0.7)
    
    # Removed iterations count from bars - will be shown in separate plot

# Configura il grafico
# if multiple_kernels:
#     title = "Execution Time Breakdown by Bandwidth and Kernel"
# else:
#     title = f"Execution Time Breakdown for {kernels[0]} kernel"
    
# ax.set_title(title, fontsize=18)
ax.set_ylabel("Bandwidth", fontsize=27)
ax.set_xlabel("Execution Time (s)", fontsize=27)
ax.set_yticks(y + y_offset)
ax.set_yticklabels([f"{bw}" for bw in bandwidths], fontsize=22)
ax.tick_params(axis='x', labelsize=24)

# Calcola il massimo tempo totale
max_total_time = 0
for bw in bandwidths:
    for kernel in kernels:
        total_time = sum(data[bw][kernel][label] for label in timing_labels)
        max_total_time = max(max_total_time, total_time)

# Imposta i limiti dell'asse x
ax.set_xlim(0, max_total_time * 1.1)

ax.legend(loc="upper right", bbox_to_anchor=(1, 0.5), fontsize=22, title="MeanShift Components", title_fontsize=22)
ax.grid(axis="x", linestyle="--", alpha=0.7)

# Adjust layout to avoid warnings
plt.tight_layout(rect=[0, 0, 0.85, 1])  # Leave space for legend
# Salva il grafico
output_dir = "./"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    
plt.savefig(f"{output_dir}/breakdown_meanshift.pdf")
print(f"Plot saved to {output_dir}/breakdown_meanshift.pdf")
plt.close()

# Create a separate plot for iterations per pixel - using line plot to show relationship
fig2, ax2 = plt.subplots(figsize=(16, 10))

# Define colors and markers for each kernel - using provided palette
kernel_colors = {'epanechnikov': "#9a031e", 'uniform': "#003566", 'gaussian': "#386641"}
kernel_markers = {'epanechnikov': 'o', 'uniform': 's', 'gaussian': '^'}

# Get total pixels from the results (96x64 = 6144)
total_pixels = 6144

# Reverse kernel order for this plot
kernels_reversed = list(reversed(kernels))

# Define text offsets for each kernel to avoid overlapping - increased spacing
text_offsets = {'gaussian': (0, 15), 'uniform': (-25, -25), 'epanechnikov': (25, -25)}

for kernel in kernels_reversed:
    iterations_per_pixel = [shift_calls[bw][kernel] / total_pixels for bw in bandwidths]
    ax2.plot(bandwidths, iterations_per_pixel, 
             color=kernel_colors.get(kernel, '#1f77b4'), 
             marker=kernel_markers.get(kernel, 'o'),
             linewidth=3, markersize=10, 
             label=kernel, alpha=0.8)
    
    # Add value labels on each point with different offsets per kernel
    for bw, iter_per_pixel in zip(bandwidths, iterations_per_pixel):
        if iter_per_pixel > 0:  # Only show if we have data
            offset = text_offsets.get(kernel, (0, 10))
            ax2.annotate(f'{iter_per_pixel:.2f}', 
                        (bw, iter_per_pixel), 
                        textcoords="offset points", 
                        xytext=offset, 
                        ha='center', 
                        fontsize=18,  # Slightly smaller font size
                        color=kernel_colors.get(kernel, '#2f4858'),
                        weight='bold')

# Configure the iterations per pixel plot
ax2.set_xlabel("Bandwidth", fontsize=23)  # Increased font size
ax2.set_ylabel("Iterations per Pixel", fontsize=23)  # Increased font size
ax2.tick_params(axis='both', labelsize=20)  # Increased font size

# Set x-axis to show all bandwidth values
ax2.set_xticks(bandwidths)
ax2.set_xticklabels([f"{bw}" for bw in bandwidths])

ax2.legend(loc="lower right", fontsize=20, title="Kernel", title_fontsize=20)  # Increased font size
ax2.grid(True, linestyle="--", alpha=0.7)

# Add some padding to y-axis
y_max = max([shift_calls[bw][kernel] / total_pixels for bw in bandwidths for kernel in kernels if shift_calls[bw][kernel] > 0])
ax2.set_ylim(0, y_max * 1.1)

plt.tight_layout()
plt.savefig(f"{output_dir}/breakdown_meanshift_iterations.pdf")
print(f"Iterations per pixel plot saved to {output_dir}/breakdown_meanshift_iterations.pdf")
plt.close()