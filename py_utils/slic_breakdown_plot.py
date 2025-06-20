import re
import matplotlib.pyplot as plt
import numpy as np
import os

print("Importing libraries...")

# Input file
input_file = "./breakdown_slic2.txt"

# Check if file exists
if not os.path.exists(input_file):
    print(f"Error: File '{input_file}' not found.")
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

# Data structure to store timing information
thread_counts = []
timing_data = {}

# Print first few lines of file for debugging
print("First few lines of the file:")
with open(input_file, "r") as file:
    for i, line in enumerate(file):
        if i < 5:  # Print first 5 lines
            print(f"  {line.strip()}")
    file.seek(0)  # Reset file pointer to beginning

# Read and parse the file line by line - simpler approach
with open(input_file, "r") as file:
    lines = file.readlines()
    current_thread = None
    
    for line in lines:
        line = line.strip()
        
        # Look for thread count
        thread_match = re.search(r"Running with (\d+) threads", line)
        if thread_match:
            current_thread = int(thread_match.group(1))
            print(f"Found thread count: {current_thread}")
            thread_counts.append(current_thread)
            timing_data[current_thread] = {}
            continue
        
        # Look for timing data - use raw string for regex pattern
        for label in timing_labels:
            # Fix: Use raw string (r prefix) for regex pattern
            pattern = r"{} total execution time: ([\d.]+) s".format(label)
            time_match = re.search(pattern, line)
            if time_match and current_thread is not None:
                value = float(time_match.group(1))
                timing_data[current_thread][label] = value
                print(f"  Found {label} = {value} seconds")

# Sort thread counts
thread_counts = sorted(list(set(thread_counts)))

# Print summary of data found
print("\nData summary:")
for t in thread_counts:
    if t in timing_data:
        total = sum(timing_data[t].values())
        print(f"Thread count {t}: Total time = {total:.4f}s")
    else:
        print(f"Thread count {t}: No timing data found")

if not thread_counts:
    print("ERROR: No thread counts detected!")
    exit(1)

# Create the stacked bar chart
fig, ax = plt.subplots(figsize=(10, 8))

bar_width = 0.6
x = np.arange(len(thread_counts))  # X positions for the bars

# Build the stacked bars
bottom = np.zeros(len(thread_counts))
for label in timing_labels:
    values = [timing_data[t].get(label, 0) for t in thread_counts]
    ax.bar(x, values, bar_width, label=label, color=colors[label], bottom=bottom)
    bottom += values

# Add total time labels on top of each bar
for i, thread in enumerate(thread_counts):
    total_time = sum(timing_data[thread].get(label, 0) for label in timing_labels)
    ax.text(i, total_time + 0.05, f"{total_time:.2f}s", 
            ha="center", va="bottom", fontweight="bold")

# Configure the chart
ax.set_title("SLIC Execution Time by Thread Count")
ax.set_xlabel("Number of Threads")
ax.set_ylabel("Execution Time (seconds)")
ax.set_xticks(x)
ax.set_xticklabels(thread_counts)
ax.legend(loc="upper right")
ax.grid(axis="y", linestyle="--", alpha=0.7)

plt.tight_layout()
plt.savefig("./slic_thread_performance2.png")
print("\nPlot saved as 'slic_thread_performance.png'")
plt.show()