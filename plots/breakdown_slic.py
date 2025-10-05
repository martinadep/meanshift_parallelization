import re
import matplotlib.pyplot as plt
import numpy as np
import os
from utils import try_read_file
from config import output_plots_dir, timing_colors, FONT_AXES, FONT_TICKS, FONT_LEGEND, breakdown_results_path_slic

print("Importing libraries...")

# Check if file exists
if not os.path.exists(breakdown_results_path_slic):
    print(f"Error: File '{breakdown_results_path_slic}' not found.")
    exit(1)

# Timing labels
timing_labels = [
    "slic_distance_calc",
    "assignment_op",
    "center_init", 
    "center_update",
    "cluster_accumulate"
]

# Data structure to store timing information
thread_counts = []
timing_data = {}

# Read the file content
file_content = try_read_file(breakdown_results_path_slic)
lines = file_content.splitlines()

execution_blocks = []
current_slic_data = {}
content_blocks = file_content.split('=============================================================')

for block_idx, block in enumerate(content_blocks):
    if not block.strip():
        continue
        
    # print(f"\nProcessing execution block {block_idx + 1}")
    
    # Reset SLIC data for this block
    current_slic_data = {}
    current_thread_count = None
    
    # Parse SLIC timing data from this block
    for line in block.splitlines():
        line = line.strip()
        
        # Look for SLIC timing data
        for label in timing_labels:
            pattern = r"{} total execution time: ([\d.]+) s".format(label)
            time_match = re.search(pattern, line)
            if time_match:
                value = float(time_match.group(1))
                current_slic_data[label] = value
                # print(f"  Found SLIC {label} = {value} seconds")
        
        # Look for thread count in the same block
        thread_match = re.search(r"Running with (\d+) threads", line)
        if thread_match:
            current_thread_count = int(thread_match.group(1))
            # print(f"  Found thread count: {current_thread_count}")
    
    # If we found both SLIC data and thread count, store them together
    if current_slic_data and current_thread_count is not None:
        if current_thread_count not in timing_data:
            timing_data[current_thread_count] = {}
            thread_counts.append(current_thread_count)
        
        # Store or update the SLIC timing data for this thread count
        for label, value in current_slic_data.items():
            timing_data[current_thread_count][label] = value
        
        # print(f"  Stored data for {current_thread_count} threads: {list(current_slic_data.keys())}")

# Sort thread counts and remove duplicates
thread_counts = sorted(list(set(thread_counts)))

# Print summary of data found
# print("\nData summary:")
for t in thread_counts:
    if t in timing_data:
        total = sum(timing_data[t].values())
        # print(f"Thread count {t}: Total time = {total:.4f}s, Components: {list(timing_data[t].keys())}")
    else:
        print(f"Thread count {t}: No timing data found")

if not thread_counts:
    print("ERROR: No thread counts detected!")
    exit(1)

if not timing_data:
    print("ERROR: No timing data detected!")
    exit(1)

# Create the stacked bar chart
fig, ax = plt.subplots(figsize=(6, 4))

bar_width = 0.6
x = np.arange(len(thread_counts))  # X positions for the bars

# Build the stacked bars
bottom = np.zeros(len(thread_counts))
for label in timing_labels:
    values = [timing_data[t].get(label, 0) for t in thread_counts]
    ax.bar(x, values, bar_width, label=label, color=timing_colors[label], bottom=bottom)
    bottom += values

# Configure the chart
# ax.set_title("SLIC Execution Time by Thread Count")
ax.set_xlabel("Number of Threads", fontsize=FONT_AXES)
ax.set_ylabel("Execution Time (seconds)", fontsize=FONT_AXES)
ax.set_xticks(x)
ax.set_xticklabels(thread_counts, fontsize=FONT_TICKS)
ax.tick_params(axis='y', labelsize=FONT_TICKS)
ax.legend(loc="upper left", fontsize=FONT_LEGEND)
ax.grid(axis="y", linestyle="--", alpha=0.7)

plt.tight_layout()

# Ensure output directory exists
if not os.path.exists(output_plots_dir):
    os.makedirs(output_plots_dir)

save_path = os.path.join(output_plots_dir, "breakdown_slic.png")
plt.savefig(save_path)
print(f"\nPlot saved as '{save_path}'")
plt.close()