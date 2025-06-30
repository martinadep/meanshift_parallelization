import os
import numpy as np
import matplotlib.pyplot as plt
from utils import try_read_file, extract_separate_times
from config import threads, implementations, strong_scaling_dir, slic_to_ms_map

print("Analyzing strong scaling performance with SLIC breakdowns...")

# Dictionary to store execution times for each implementation
all_execution_times = {impl["name"]: {t: {"slic": [], "mean_shift": []} for t in threads} for impl in implementations}
all_mean_times = {impl["name"]: {"slic": [], "mean_shift": []} for impl in implementations}

# Read result files for each implementation
for impl in implementations:
    print(f"Analyzing implementation: {impl['name']}")
    
    for t in threads:
        filename = f"{impl['name']}_{t}_threads.txt"
        filepath = os.path.join(strong_scaling_dir, impl["folder"], filename)
        
        try:
            if os.path.exists(filepath):
                content = try_read_file(filepath)
                slic_times, mean_shift_times = extract_separate_times(content)
                
                if mean_shift_times:
                    all_execution_times[impl["name"]][t]["mean_shift"].extend(mean_shift_times)
                    if slic_times:
                        all_execution_times[impl["name"]][t]["slic"].extend(slic_times)
                    print(f"  Thread {t}: found {len(mean_shift_times)} measurements")
                else:
                    print(f"  No times found in file {filename}")
            else:
                print(f"  File not found: {filepath}")
                # Try direct path without subfolder
                direct_filepath = os.path.join(strong_scaling_dir, filename)
                if os.path.exists(direct_filepath):
                    content = try_read_file(direct_filepath)
                    slic_times, mean_shift_times = extract_separate_times(content)
                    
                    if mean_shift_times:
                        all_execution_times[impl["name"]][t]["mean_shift"].extend(mean_shift_times)
                        if slic_times:
                            all_execution_times[impl["name"]][t]["slic"].extend(slic_times)
                        print(f"  Thread {t}: found {len(mean_shift_times)} measurements (direct path)")
                    else:
                        print(f"  No times found in file {filename} (direct path)")
        except Exception as e:
            print(f"  Error with file {filepath}: {str(e)}")

# Calculate means for each implementation
for impl_name in all_execution_times:
    for t in threads:
        slic_times = all_execution_times[impl_name][t]["slic"]
        mean_shift_times = all_execution_times[impl_name][t]["mean_shift"]
        
        if mean_shift_times:
            ms_mean = np.mean(mean_shift_times)
            all_mean_times[impl_name]["mean_shift"].append(ms_mean)
        else:
            all_mean_times[impl_name]["mean_shift"].append(0)
            
        if slic_times:
            slic_mean = np.mean(slic_times)
            all_mean_times[impl_name]["slic"].append(slic_mean)
        else:
            all_mean_times[impl_name]["slic"].append(0)
            
        total = (np.mean(slic_times) if slic_times else 0) + (np.mean(mean_shift_times) if mean_shift_times else 0)
        print(f"{impl_name} with {t} threads: mean time = {total:.4f} seconds")

# Check if we have valid data
has_data = False
for impl_name in all_mean_times:
    if any(all_mean_times[impl_name]["mean_shift"]) or any(all_mean_times[impl_name]["slic"]):
        has_data = True
        break

if not has_data:
    print("No valid data found in the files. Check the input files.")
    exit(1)

# Prepare the execution time chart with stacked bars
plt.rcParams.update({'font.size': 14})
fig, ax = plt.subplots(figsize=(14, 8))

# Bar width and positioning
bar_width = 0.11
index = np.arange(len(threads))

# Find color for each implementation
color_map = {impl["name"]: impl["color"] for impl in implementations}

# Create bars for each implementation
for i, impl in enumerate(implementations):
    impl_name = impl["name"]
    position = index + (i - len(implementations)/2 + 0.5) * bar_width
    
    if "slic" in impl_name:
        # For SLIC implementations, show stacked bars
        slic_times = all_mean_times[impl_name]["slic"]
        ms_times = all_mean_times[impl_name]["mean_shift"]
        
        # Get corresponding mean_shift implementation color
        ms_impl = slic_to_ms_map.get(impl_name)
        ms_color = color_map.get(ms_impl, impl["color"])
        
        # Draw SLIC part (bottom)
        ax.bar(position, slic_times, bar_width, 
                color='#38A5D0', label=f"{impl_name} (SLIC)" if i == 4 else "")
        
        # Draw mean_shift part (top)
        ax.bar(position, ms_times, bar_width, bottom=slic_times, 
                color=ms_color, label=f"{impl_name} (mean-shift)" if i == 4 else "")
    else:
        # For regular mean_shift implementations, show simple bars
        times = all_mean_times[impl_name]["mean_shift"]
        ax.bar(position, times, bar_width, color=impl["color"], label=impl_name)

# Fix legend to avoid duplicates
handles, labels = ax.get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax.legend(by_label.values(), by_label.keys(), fontsize=12)

# Configure the chart
ax.set_xlabel('Number of Threads', fontsize=16)
ax.set_ylabel('Mean Execution Time (seconds)', fontsize=16)
ax.set_title('Strong Scaling: Execution Time Comparison with SLIC Breakdown', fontsize=18)
ax.set_xticks(index)
ax.set_xticklabels([str(t) for t in threads], fontsize=14)
ax.set_yscale('log')
ax.grid(axis='y', linestyle='--', alpha=0.7)
ax.tick_params(axis='y', labelsize=14)

plt.tight_layout()
plt.savefig('strong_scaling_slic_breakdown.png')
print("Plot generated: strong_scaling_slic_breakdown.png")
