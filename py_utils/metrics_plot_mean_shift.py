import os
import re
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

def parse_perf_file(filename):
    with open(filename, "r") as f:
        content = f.read()
    runs = content.strip().split('---')
    data = []
    for run in runs:
        if not run.strip():
            continue
        # Only parse if Bandwidth and Total Points are present
        if not re.search(r'Bandwidth:', run) or not re.search(r'Total Points:', run):
            continue
        try:
            d = {}
            d['Bandwidth'] = int(re.search(r'Bandwidth: (\d+)', run).group(1))
            d['Cluster Epsilon'] = float(re.search(r'Cluster Epsilon: ([\d.eE+-]+)', run).group(1))
            d['Iteration Epsilon'] = float(re.search(r'Iteration Epsilon: ([\d.eE+-]+)', run).group(1))
            d['DataType'] = re.search(r'DataType: (\w+)', run).group(1)
            d['Total Points'] = int(re.search(r'Total Points: (\d+)', run).group(1))
            d['Total Iterations'] = int(re.search(r'Total Iterations: (\d+)', run).group(1))
            d['Iterations/sec'] = float(re.search(r'Iterations/sec: ([\d.]+)', run).group(1))
            d['Elapsed Time'] = float(re.search(r'Elapsed Time: ([\d.]+)', run).group(1))
            d['Min Iterations'] = int(re.search(r'Min Iterations: (\d+)', run).group(1))
            d['Max Iterations'] = int(re.search(r'Max Iterations: (\d+)', run).group(1))
            d['Mean Iterations'] = float(re.search(r'Mean Iterations: ([\d.]+)', run).group(1))
            d['Stddev Iterations'] = float(re.search(r'Stddev Iterations: ([\d.]+)', run).group(1))
            iters = re.search(r'Iterations per point: ([\d\s]+)', run)
            d['Iterations per point'] = np.array([int(x) for x in iters.group(1).split()]) if iters else np.array([])
            data.append(d)
        except Exception as e:
            print(f"Skipping a run due to parse error: {e}")
            continue
    return data

perf_path = "./data/metrics_mean_shift.txt"

# Carica tutte le run
all_data = parse_perf_file(perf_path)

# Raggruppa per bandwidth
bw_dict = defaultdict(list)
for d in all_data:
    bw_dict[d['Bandwidth']].append(d)

# Prepara la directory di output e il path del file
output_dir = os.path.dirname(os.path.abspath(perf_path))
output_path = os.path.join(output_dir, "metrics_plots.png")

# Crea una figura con 3 subplot
fig, axs = plt.subplots(3, 1, figsize=(10, 18))

# 1. Istogramma iterazioni per punto (media delle 3 run per bandwidth)
for bw, runs in sorted(bw_dict.items()):
    all_iters = np.stack([r['Iterations per point'] for r in runs])
    mean_iters = np.mean(all_iters, axis=0)
    hist_vals, bins = np.histogram(np.round(mean_iters), bins=np.arange(0, np.max(mean_iters)+2)-0.5)
    # Plot using the bin centers (integer values) rather than bin edges
    bin_centers = bins[:-1] + 0.5  # This makes the x-values [0, 1, 2, 3, ...]
    axs[0].plot(bin_centers, hist_vals, marker='o', label=f'Bandwidth {bw}')

axs[0].set_xlabel('Iterations per point')
axs[0].set_ylabel('Points')
axs[0].set_title('Iterations per point')
axs[0].legend()
axs[0].grid(True)

# 2. Grafico max e min iterazione per bandwidth (media delle 3 run)
bandwidths = sorted(bw_dict.keys())
min_iters = [np.mean([r['Min Iterations'] for r in bw_dict[bw]]) for bw in bandwidths]
max_iters = [np.mean([r['Max Iterations'] for r in bw_dict[bw]]) for bw in bandwidths]
x = np.arange(len(bandwidths))
width = 0.35
rects1 = axs[1].bar(x - width/2, min_iters, width, label='Min Iterations')
rects2 = axs[1].bar(x + width/2, max_iters, width, label='Max Iterations')
axs[1].set_xlabel('Bandwidth')
axs[1].set_ylabel('Iterations')
axs[1].set_title('Min/Max Iterations Mean per Bandwidth')
axs[1].set_xticks(x)
axs[1].set_xticklabels([str(bw) for bw in bandwidths])
axs[1].legend()
axs[1].grid(True)

# 3. Grafico tempo di esecuzione e iter/sec per bandwidth (media delle 3 run)
exec_times = [np.mean([float(r['Elapsed Time']) if 'Elapsed Time' in r else 0 for r in bw_dict[bw]]) for bw in bandwidths]
iters_sec = [np.mean([r['Iterations/sec'] for r in bw_dict[bw]]) for bw in bandwidths]
bars = axs[2].bar(x, exec_times, width=0.6, color='skyblue', align='center')
axs[2].set_xlabel('Bandwidth')
axs[2].set_ylabel('Mean Execution Time (s)')
axs[2].set_title('Mean Execution Time per Bandwidth\n(upper value: Iterations/sec)')
axs[2].set_xticks(x)
axs[2].set_xticklabels([str(bw) for bw in bandwidths])
axs[2].set_ylim(bottom=0)
for i, bar in enumerate(bars):
    height = bar.get_height()
    axs[2].annotate(f'{iters_sec[i]:.0f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, color='black')
axs[2].grid(True)

fig.tight_layout()
fig.savefig(output_path)
plt.close(fig)
print(f"Saved all plots to {output_path}")