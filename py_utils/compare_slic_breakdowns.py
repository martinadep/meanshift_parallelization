import re
import matplotlib.pyplot as plt
import numpy as np
import os

print("Importing libraries...")

# Input files
input_file1 = "./breakdown_slic_naive.txt"
input_file2 = "./breakdown_slic_modified.txt"

# Check if files exist
for file in [input_file1, input_file2]:
    if not os.path.exists(file):
        print(f"Error: File '{file}' not found.")
        exit(1)

# Timing labels
timing_labels = [
    "slic_distance_calc",
    "assignment_op",
    "center_init", 
    "center_update",
    "cluster_accumulate"
]

# Colors for the different timing components
colors = {
    "slic_distance_calc": "blue",
    "assignment_op": "orange",
    "center_init": "green",
    "center_update": "red",
    "cluster_accumulate": "purple"
}

# Function to parse data from a file
def parse_timing_data(filename):
    thread_counts = []
    timing_data = {}
    
    with open(filename, "r") as file:
        lines = file.readlines()
        current_thread = None
        
        for line in lines:
            line = line.strip()
            
            # Look for thread count
            thread_match = re.search(r"Running with (\d+) threads", line)
            if thread_match:
                current_thread = int(thread_match.group(1))
                thread_counts.append(current_thread)
                timing_data[current_thread] = {}
                continue
            
            # Look for timing data
            for label in timing_labels:
                pattern = r"{} total execution time: ([\d.]+) s".format(label)
                time_match = re.search(pattern, line)
                if time_match and current_thread is not None:
                    value = float(time_match.group(1))
                    timing_data[current_thread][label] = value
    
    return sorted(list(set(thread_counts))), timing_data

print("Parsing data from files...")
thread_counts1, timing_data1 = parse_timing_data(input_file1)
thread_counts2, timing_data2 = parse_timing_data(input_file2)

# Use the union of thread counts from both files
all_thread_counts = sorted(list(set(thread_counts1 + thread_counts2)))

# Print summary of data found
print("\nData summary from file 1:")
for t in all_thread_counts:
    if t in timing_data1:
        total = sum(timing_data1[t].values())
        print(f"Thread count {t}: Total time = {total:.4f}s")
    else:
        print(f"Thread count {t}: No timing data found")

print("\nData summary from file 2:")
for t in all_thread_counts:
    if t in timing_data2:
        total = sum(timing_data2[t].values())
        print(f"Thread count {t}: Total time = {total:.4f}s")
    else:
        print(f"Thread count {t}: No timing data found")

# Create the stacked bar chart
fig, ax = plt.subplots(figsize=(14, 8))

# Width and positioning
bar_width = 0.35
x = np.arange(len(all_thread_counts))

# Build the stacked bars for file 1
bottom1 = np.zeros(len(all_thread_counts))
for label in timing_labels:
    values = [timing_data1.get(t, {}).get(label, 0) for t in all_thread_counts]
    ax.bar(x - bar_width/2, values, bar_width, label=f"{label} (Set 1)" if label == timing_labels[0] else "", 
           color=colors[label], bottom=bottom1, alpha=0.7)
    bottom1 += values

# Build the stacked bars for file 2
bottom2 = np.zeros(len(all_thread_counts))
for label in timing_labels:
    values = [timing_data2.get(t, {}).get(label, 0) for t in all_thread_counts]
    ax.bar(x + bar_width/2, values, bar_width, label=f"{label} (Set 2)" if label == timing_labels[0] else "", 
           color=colors[label], bottom=bottom2, hatch='///', alpha=0.7)
    bottom2 += values

# Add total time labels on top of each bar
for i, thread in enumerate(all_thread_counts):
    # First file
    if thread in timing_data1:
        total_time = sum(timing_data1[thread].values())
        ax.text(i - bar_width/2, total_time + 0.1, f"{total_time:.2f}s", 
                ha="center", va="bottom", fontweight="bold")
    
    # Second file
    if thread in timing_data2:
        total_time = sum(timing_data2[thread].values())
        ax.text(i + bar_width/2, total_time + 0.1, f"{total_time:.2f}s", 
                ha="center", va="bottom", fontweight="bold")

# Create a custom legend with component colors and dataset indicators
legend_elements = []
for label in timing_labels:
    legend_elements.append(plt.Rectangle((0,0), 1, 1, color=colors[label], label=label))

# Add a separator in the legend
legend_elements.append(plt.Line2D([0], [0], color='none', label=''))

# Add clearer dataset indicators
legend_elements.append(plt.Rectangle((0,0), 1, 1, fill=False, edgecolor='black', 
                                     label='standard SLIC (solid bars)'))
legend_elements.append(plt.Rectangle((0,0), 1, 1, fill=False, edgecolor='black', 
                                     hatch='///', label='modified SLIC (hatched bars)'))

# Configure the chart
ax.set_title("SLIC Execution Time Comparison by Thread Count")
ax.set_xlabel("Number of Threads")
ax.set_ylabel("Execution Time (seconds)")
ax.set_xticks(x)
ax.set_xticklabels(all_thread_counts)
ax.legend(handles=legend_elements, loc="upper right", fontsize=9)
ax.grid(axis="y", linestyle="--", alpha=0.7)

# Add a better title with file information
plt.suptitle("Comparison of Original vs. Optimized SLIC Implementation", 
             fontsize=14, fontweight='bold', y=0.98)

plt.tight_layout()
plt.savefig("./slic_comparison_performance.png")
print("\nPlot saved as 'slic_comparison_performance.png'")
plt.show()