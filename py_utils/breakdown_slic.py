import re
import matplotlib.pyplot as plt
import numpy as np
import os

print("Importing libraries...")

# Input file
input_file = "./data/breakdown_slic_ms.txt"

# Check if file exists
if not os.path.exists(input_file):
    print(f"Error: File '{input_file}' not found.")
    exit(1)

# Function to read file with different encodings
def read_file_with_encoding(filename):
    encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252', 'ascii']
    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"Successfully read file with encoding: {encoding}")
            return content
        except UnicodeDecodeError:
            continue
    raise Exception(f"Could not read file {filename} with any of the attempted encodings: {encodings}")

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

# Read the file content
file_content = read_file_with_encoding(input_file)
lines = file_content.splitlines()

# Print first few lines of file for debugging
print("First few lines of the file:")
for i, line in enumerate(lines[:5]):
    print(f"  {line}")

# Parse the file - handle the fact that thread count comes after SLIC timing data
execution_blocks = []
current_slic_data = {}

# Split the content into execution blocks based on separator lines
content_blocks = file_content.split('=============================================================')

for block_idx, block in enumerate(content_blocks):
    if not block.strip():
        continue
        
    print(f"\nProcessing execution block {block_idx + 1}")
    
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
                print(f"  Found SLIC {label} = {value} seconds")
        
        # Look for thread count in the same block
        thread_match = re.search(r"Running with (\d+) threads", line)
        if thread_match:
            current_thread_count = int(thread_match.group(1))
            print(f"  Found thread count: {current_thread_count}")
    
    # If we found both SLIC data and thread count, store them together
    if current_slic_data and current_thread_count is not None:
        if current_thread_count not in timing_data:
            timing_data[current_thread_count] = {}
            thread_counts.append(current_thread_count)
        
        # Store or update the SLIC timing data for this thread count
        for label, value in current_slic_data.items():
            timing_data[current_thread_count][label] = value
        
        print(f"  Stored data for {current_thread_count} threads: {list(current_slic_data.keys())}")

# Sort thread counts and remove duplicates
thread_counts = sorted(list(set(thread_counts)))

# Print summary of data found
print("\nData summary:")
for t in thread_counts:
    if t in timing_data:
        total = sum(timing_data[t].values())
        print(f"Thread count {t}: Total time = {total:.4f}s, Components: {list(timing_data[t].keys())}")
    else:
        print(f"Thread count {t}: No timing data found")

if not thread_counts:
    print("ERROR: No thread counts detected!")
    exit(1)

if not timing_data:
    print("ERROR: No timing data detected!")
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
plt.savefig("./slic_thread_breakdown.png")
print("\nPlot saved as 'slic_thread_breakdown.png'")
plt.show()