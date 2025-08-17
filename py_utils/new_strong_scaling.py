import os
import re
import numpy as np
import matplotlib.pyplot as plt

from config import FONT_AXES, FONT_TICKS, FONT_LEGEND, FONT_TITLE, LANDSCAPE_INCHES, strong_scaling_dir, implementations as all_implementations, threads

# Seleziona solo le tre implementazioni richieste
implementations = [
    next(impl for impl in all_implementations if impl["name"] == "MeanShift (OpenMP)"),
    next(impl for impl in all_implementations if impl["name"] == "MeanShift Matrix (OpenMP)"),
    next(impl for impl in all_implementations if impl["name"] == "MeanShift Matrix (OpenMP + OpenBLAS)")
]

def parse_file(filepath):
    """Estrae (thread, tempo) da un file di output, gestendo diverse varianti di stringa."""
    with open(filepath, "r") as f:
        content = f.read()
    thread_matches = re.findall(r'Running with (\d+) threads', content)
    time_matches = re.findall(r'(?:mean_shift|matrix|openblas)[\s\w]*execution time: ([\d.]+)', content, re.IGNORECASE)
    if not time_matches or len(thread_matches) != len(time_matches):
        time_matches = re.findall(r'execution time: ([\d.]+)', content)
    threads_found = [int(t) for t in thread_matches]
    times_found = [float(t) for t in time_matches]
    if len(threads_found) != len(times_found):
        print(f"Attenzione: mismatch tra thread e tempi in {filepath} ({len(threads_found)} vs {len(times_found)})")
    return list(zip(threads_found, times_found))

# Raccolta dati
all_execution_times = {impl["name"]: {t: [] for t in threads} for impl in implementations}
all_mean_times = {impl["name"]: [] for impl in implementations}

for impl in implementations:
    folder = os.path.join(strong_scaling_dir, impl["folder"])
    for filename in os.listdir(folder):
        if filename.endswith(".txt"):
            filepath = os.path.join(folder, filename)
            pairs = parse_file(filepath)
            for thread, time in pairs:
                if thread in threads:
                    all_execution_times[impl["name"]][thread].append(time)

# Calcola la media per ogni thread
for impl in implementations:
    name = impl["name"]
    for t in threads:
        times = all_execution_times[name][t]
        if times:
            mean_time = np.mean(times)
            all_mean_times[name].append(mean_time)
        else:
            all_mean_times[name].append(np.nan)


plt.rcParams.update({
    "text.usetex": False,  
    "font.family": "serif",
    "font.serif": ["Times New Roman"],
})
plt.rc('axes', titlesize=FONT_AXES)     # fontsize of the axes title
plt.rc('axes', labelsize=FONT_AXES)     # fontsize of the x and y labels
plt.rc('xtick', labelsize=FONT_TICKS)   # fontsize of the tick labels
plt.rc('ytick', labelsize=FONT_TICKS)   # fontsize of the tick labels
plt.rc('legend', fontsize=FONT_LEGEND)  # legend fontsize
plt.rc('figure', titlesize=FONT_TITLE)  # fontsize of the figure title

# Plot tempi di esecuzione
plt.figure(figsize=LANDSCAPE_INCHES)
for impl in implementations:
    name = impl["name"]
    color = impl["color"]
    plt.plot(threads, all_mean_times[name], marker='o', markersize=3, label=name, color=color)
plt.xlabel("OpenMP threads")
plt.ylabel("Average execution time (s)")
plt.yscale('log')
plt.xticks(threads)


plt.grid(True, which="both", ls="--", lw=0.5)
plt.tight_layout()
plt.savefig("ms_strong_scaling.pdf")
plt.show()


# Calcola speedup
speedups = {impl["name"]: [] for impl in implementations}
for impl in implementations:
    name = impl["name"]
    base_time = all_mean_times[name][0]  # tempo con 1 thread
    speedups[name] = [base_time / t if t > 0 else 0 for t in all_mean_times[name]]

# Calcola efficiency
efficiency = {name: [] for name in speedups}
for impl in implementations:
    name = impl["name"]
    efficiency[name] = [speedups[name][i] / threads[i] if threads[i] > 0 else 0 for i in range(len(threads))]

print("Plots generated: strong_scaling_all.png and strong_scaling_speedup_efficiency.png")

print("\nStrong Scaling Results Table:")
header = f"{'Threads':>8} | " + " | ".join([f"{name:^28}" for name in speedups.keys()])
print(header)
print("-" * len(header))

for i, t in enumerate(threads):
    row = f"{t:>8} | "
    for name in speedups.keys():
        sp = speedups[name][i] if i < len(speedups[name]) else float('nan')
        eff = efficiency[name][i] if i < len(efficiency[name]) else float('nan')
        row += f"Speedup: {sp:7.2f} | Eff.: {eff:6.2f}   | "
    print(row)

print("plot saved in ms_strong_scaling.pdf")