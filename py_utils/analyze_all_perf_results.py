import os
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from py_utils.plot_metrics import parse_perf_file

# Modifica qui il path al perf_results.txt che vuoi analizzare
perf_path = "./test/epanechnikov/8049/perf_results.txt"

# Carica tutte le run
all_data = parse_perf_file(perf_path)

# Raggruppa per bandwidth
bw_dict = defaultdict(list)
for d in all_data:
    bw_dict[d['Bandwidth']].append(d)

# Prepara la directory di output e il path del file
output_dir = os.path.dirname(os.path.abspath(perf_path))
output_path = os.path.join(output_dir, "perf_analysis_plots.png")

# Crea una figura con 3 subplot
fig, axs = plt.subplots(3, 1, figsize=(10, 18))

# 1. Istogramma iterazioni per punto (media delle 3 run per bandwidth)
for bw, runs in sorted(bw_dict.items()):
    all_iters = np.stack([r['Iterations per point'] for r in runs])
    mean_iters = np.mean(all_iters, axis=0)
    hist_vals, bins = np.histogram(np.round(mean_iters), bins=np.arange(0, np.max(mean_iters)+2)-0.5)
    axs[0].plot(bins[:-1], hist_vals, marker='o', label=f'Bandwidth {bw}')
axs[0].set_xlabel('Iterazioni per punto')
axs[0].set_ylabel('Numero di punti')
axs[0].set_title('Istogramma iterazioni per punto (media su 3 run)')
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
axs[1].set_ylabel('Numero Iterazioni')
axs[1].set_title('Media Min/Max Iterazioni per Bandwidth')
axs[1].set_xticks(x)
axs[1].set_xticklabels([str(bw) for bw in bandwidths])
axs[1].legend()
axs[1].grid(True)

# 3. Grafico tempo di esecuzione e iter/sec per bandwidth (media delle 3 run)
exec_times = [np.mean([float(r['Elapsed Time']) if 'Elapsed Time' in r else 0 for r in bw_dict[bw]]) for bw in bandwidths]
iters_sec = [np.mean([r['Iterations/sec'] for r in bw_dict[bw]]) for bw in bandwidths]
bars = axs[2].bar(x, exec_times, width=0.6, color='skyblue', align='center')
axs[2].set_xlabel('Bandwidth')
axs[2].set_ylabel('Tempo di esecuzione medio (s)')
axs[2].set_title('Tempo di esecuzione medio per Bandwidth\n(valore sopra: Iterazioni/sec medie)')
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