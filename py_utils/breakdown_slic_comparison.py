import os
import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from utils import try_read_file
from config import FONT_TITLE, LANDSCAPE_INCHES, FONT_AXES, FONT_LEGEND, FONT_TICKS, timing_colors

print("Importing libraries...")
# Set Times New Roman font globally and font sizes
rcParams['font.family'] = 'Times New Roman'
# rcParams['font.size'] = 22
rcParams['axes.titlesize'] = FONT_AXES
rcParams['axes.labelsize'] = FONT_AXES
rcParams['xtick.labelsize'] = FONT_TICKS
rcParams['ytick.labelsize'] = FONT_TICKS
rcParams['legend.fontsize'] = FONT_TICKS

# Input files
input_file1 = "./breakdown_slic_naive.txt"
input_file2 = "./breakdown_slic_modified.txt"

# Check if files exist
for file in [input_file1, input_file2]:
    if not os.path.exists(file):
        print(f"Error: File {file} does not exist!")
        exit(1)

# Timing labels
timing_labels = [
    "slic_distance_calc",
    "center_init", 
    "center_update",
    "assignment_op",
    "cluster_accumulate"
]

# Function to parse data from a file
def parse_timing_data(filename):
    thread_counts = []
    timing_data = {}
    
    content = try_read_file(filename)
    lines = content.split('\n')
    
    current_thread_count = None
    
    for line in lines:
        line = line.strip()
        
        # Look for thread count
        thread_match = re.search(r"Running with (\d+) threads", line)
        if thread_match:
            current_thread_count = int(thread_match.group(1))
            thread_counts.append(current_thread_count)
            timing_data[current_thread_count] = {label: 0.0 for label in timing_labels}
            print(f"  Found thread count: {current_thread_count}")
            continue
        
        # Look for timing data - FIX: Using raw string pattern
        if current_thread_count is not None:
            for label in timing_labels:
                # Check both patterns (with and without 'total')
                time_match = re.search(r"{} total execution time: ([\d.]+)".format(label), line)
                if not time_match:
                    time_match = re.search(r"{} time: ([\d.]+)".format(label), line)
                
                if time_match:
                    time_value = float(time_match.group(1))
                    timing_data[current_thread_count][label] = time_value
                    print(f"    Found {label} time: {time_value}")
    
    print(f"  Extracted data for {len(thread_counts)} thread counts from {filename}")
    return sorted(thread_counts), timing_data

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
        print(f"  {t} threads: {total:.3f}s total")
    else:
        print(f"  {t} threads: no data")

print("\nData summary from file 2:")
for t in all_thread_counts:
    if t in timing_data2:
        total = sum(timing_data2[t].values())
        print(f"  {t} threads: {total:.3f}s total")
    else:
        print(f"  {t} threads: no data")

# Check if we have any valid data
has_data = False
for t in all_thread_counts:
    if (t in timing_data1 and sum(timing_data1[t].values()) > 0) or \
       (t in timing_data2 and sum(timing_data2[t].values()) > 0):
        has_data = True
        break

if not has_data:
    print("\nWarning: No valid timing data found in the input files.")
    print("Please check that the files contain timing information in the expected format.")
    print("Example expected format: 'slic_distance_calc time: 1.234' or 'slic_distance_calc total execution time: 1.234'")
    exit(1)

# Create the stacked bar chart
fig, ax = plt.subplots(figsize=LANDSCAPE_INCHES)

# Width and positioning
bar_width = 0.35
x = np.arange(len(all_thread_counts))

# Build the stacked bars for file 1
bottom1 = np.zeros(len(all_thread_counts))
for label in timing_labels:
    values = [timing_data1.get(t, {}).get(label, 0) for t in all_thread_counts]
    ax.bar(x - bar_width/2, values, bar_width, bottom=bottom1, 
           color=timing_colors[label], label=f"{label} (1)" if label == timing_labels[0] else "")
    bottom1 += values

# Build the stacked bars for file 2
bottom2 = np.zeros(len(all_thread_counts))
for label in timing_labels:
    values = [timing_data2.get(t, {}).get(label, 0) for t in all_thread_counts]
    ax.bar(x + bar_width/2, values, bar_width, bottom=bottom2, 
           color=timing_colors[label], hatch="///", label=f"{label} (2)" if label == timing_labels[0] else "")
    bottom2 += values

# Add total time labels on top of each bar
# for i, thread in enumerate(all_thread_counts):
#     if thread in timing_data1:
#         total1 = sum(timing_data1[thread].values())
#         ax.text(x[i] - bar_width/2, total1 + 0.05, f"{total1:.2f}s", 
#                 ha='center', va='bottom', fontsize=FONT_TICKS, fontname='Times New Roman')
#     if thread in timing_data2:
#         total2 = sum(timing_data2[thread].values())
#         ax.text(x[i] + bar_width/2, total2 + 0.05, f"{total2:.2f}s", 
#                 ha='center', va='bottom', fontsize=FONT_TICKS, fontname='Times New Roman')

# Create custom legend elements
legend_elements = []
for label in timing_labels:
    legend_elements.append(plt.Rectangle((0,0), 1, 1, color=timing_colors[label], label=label))

# Add separator in the legend
legend_elements.append(plt.Line2D([0], [0], color='none', label=''))

# Add clearer dataset indicators
legend_elements.append(plt.Rectangle((0,0), 1, 1, fill=False, edgecolor='black', 
                                     label='standard SLIC (solid bars)'))
legend_elements.append(plt.Rectangle((0,0), 1, 1, fill=False, edgecolor='black', 
                                     hatch='///', label='modified SLIC (hatched bars)'))

# Configure the chart
# ax.set_title("SLIC Execution Time Comparison by Thread Count")
ax.set_xlabel("Number of Threads", fontsize=12, fontname='Times New Roman')
ax.set_ylabel("Execution Time (seconds)", fontsize=12, fontname='Times New Roman')
ax.set_xticks(x)
ax.set_xticklabels(all_thread_counts)
ax.tick_params(axis='y')
ax.legend(handles=legend_elements, loc="upper left")
ax.grid(axis="y", linestyle="--", alpha=0.7)

# Add a better title with file information
# plt.suptitle(f"SLIC Implementation Comparison\n{os.path.basename(input_file1)} vs {os.path.basename(input_file2)}", 
#            fontsize=28, fontweight='bold', y=0.98, fontname='Times New Roman')

plt.tight_layout()
plt.savefig("./slic_comparison_performance.pdf")
print("\nPlot saved as 'slic_comparison_performance.pdf'")