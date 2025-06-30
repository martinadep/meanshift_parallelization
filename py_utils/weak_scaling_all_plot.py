import os
import numpy as np
import matplotlib.pyplot as plt
from utils import try_read_file, extract_times
from config import threads, implementations, weak_scaling_dir
from plotting import create_scaling_bar_chart

print("Analyzing weak scaling performance across implementations...")

# Dictionary to store execution times for each implementation
all_execution_times = {impl["name"]: {t: [] for t in threads} for impl in implementations}
all_mean_times = {impl["name"]: [] for impl in implementations}

# Read result files for each implementation
for impl in implementations:
    print(f"Analyzing implementation: {impl['name']}")
    
    for t in threads:
        filename = f"{impl['name']}_{t}_threads.txt"
        filepath = os.path.join(weak_scaling_dir, impl["folder"], filename)
        
        try:
            if os.path.exists(filepath):
                content = try_read_file(filepath)
                times = extract_times(content)
                
                if times:
                    all_execution_times[impl["name"]][t].extend(times)
                    print(f"  Thread {t}: found {len(times)} measurements")
                else:
                    print(f"  No times found in file {filename}")
            else:
                print(f"  File not found: {filepath}")
                # Try direct path without subfolder
                direct_filepath = os.path.join(weak_scaling_dir, filename)
                if os.path.exists(direct_filepath):
                    content = try_read_file(direct_filepath)
                    times = extract_times(content)
                    
                    if times:
                        all_execution_times[impl["name"]][t].extend(times)
                        print(f"  Thread {t}: found {len(times)} measurements (direct path)")
                    else:
                        print(f"  No times found in file {filename} (direct path)")
        except Exception as e:
            print(f"  Error with file {filepath}: {str(e)}")

# Calculate means for each implementation
for impl_name in all_execution_times:
    for t in threads:
        times = all_execution_times[impl_name][t]
        if times:
            mean_time = np.mean(times)
            all_mean_times[impl_name].append(mean_time)
            print(f"{impl_name} with {t} threads: mean time = {mean_time:.4f} seconds")
        else:
            all_mean_times[impl_name].append(0)
            print(f"Warning: no data available for {impl_name} with {t} threads")

# Check if we have valid data
has_data = False
for impl_name in all_mean_times:
    if any(all_mean_times[impl_name]):
        has_data = True
        break

if not has_data:
    print("No valid data found in the files. Check the input files.")
    exit(1)

# Create execution time plot
create_scaling_bar_chart(
    implementations, 
    threads, 
    all_mean_times,
    'Weak Scaling: Execution Time Comparison between Implementations',
    'Mean Execution Time (seconds)',
    'weak_scaling_all.png',
    log_scale=True
)

# Calculate efficiency for each implementation (for weak scaling)
efficiencies = {impl["name"]: [] for impl in implementations}
for impl_name in all_mean_times:
    base_time = all_mean_times[impl_name][0]  # Time with 1 thread
    if base_time > 0:
        # For weak scaling, efficiency = T1/Tp (ideal is 1.0)
        efficiencies[impl_name] = [base_time/t if t > 0 else 0 for t in all_mean_times[impl_name]]
    else:
        efficiencies[impl_name] = [0] * len(threads)

# Create efficiency plot
plot, ax = create_scaling_bar_chart(
    implementations, 
    threads, 
    efficiencies,
    'Weak Scaling: Efficiency Comparison between Implementations',
    'Efficiency (T1/Tp)',
    'weak_scaling_efficiency_all.png'
)

# Add ideal efficiency line
ax.axhline(y=1.0, linestyle='--', color='r', label='Ideal Efficiency (1.0)')
ax.legend(fontsize=12)
plt.savefig('weak_scaling_efficiency_all.png')

print("Plots generated: weak_scaling_all.png and weak_scaling_efficiency_all.png")