import os
import re
import numpy as np
import matplotlib.pyplot as plt

from config import FONT_AXES, FONT_TICKS, FONT_LEGEND, FONT_TITLE, LANDSCAPE_INCHES, strong_scaling_dir, implementations as all_implementations, threads

# Seleziona solo le tre implementazioni richieste
implementations = [
    next(impl for impl in all_implementations if impl["name"] == "SLIC + MS (OpenMP)"),
    next(impl for impl in all_implementations if impl["name"] == "SLIC + MS Matrix (OpenMP)"),
    next(impl for impl in all_implementations if impl["name"] == "SLIC + MS Matrix (OpenMP + OpenBLAS)")
]

def parse_file(filepath):
    """Estrae (thread, tempo_slic, tempo_mean_shift) da un file di output."""
    with open(filepath, "r") as f:
        content = f.read()
    
    # Thread per Mean-Shift
    thread_matches = re.findall(r'Running with (\d+) threads', content)
    threads_found = [int(t) for t in thread_matches]

    # Tempi SLIC
    slic_times = [float(t) for t in re.findall(r'slic execution time: ([\d.]+)', content, re.IGNORECASE)]

    # Tempi Mean-Shift
    ms_times = [float(t) for t in re.findall(r'mean_shift execution time: ([\d.]+)', content, re.IGNORECASE)]

    if len(threads_found) != len(ms_times) or len(ms_times) != len(slic_times):
        print(f"Attenzione: mismatch in {filepath} (threads: {len(threads_found)}, SLIC: {len(slic_times)}, MS: {len(ms_times)})")

    return list(zip(threads_found, slic_times, ms_times))


# Raccolta dati
all_times = {impl["name"]: {t: {"slic": [], "ms": []} for t in threads} for impl in implementations}

for impl in implementations:
    folder = os.path.join(strong_scaling_dir, impl["folder"])
    for filename in os.listdir(folder):
        if filename.endswith(".txt"):
            filepath = os.path.join(folder, filename)
            entries = parse_file(filepath)
            for thread, slic_time, ms_time in entries:
                if thread in threads:
                    all_times[impl["name"]][thread]["slic"].append(slic_time)
                    all_times[impl["name"]][thread]["ms"].append(ms_time)

# Calcola media dei tempi
mean_times = {impl["name"]: {"slic": [], "ms": []} for impl in implementations}
for impl in implementations:
    name = impl["name"]
    for t in threads:
        slic_list = all_times[name][t]["slic"]
        ms_list = all_times[name][t]["ms"]
        mean_times[name]["slic"].append(np.mean(slic_list) if slic_list else np.nan)
        mean_times[name]["ms"].append(np.mean(ms_list) if ms_list else np.nan)


# Impostazioni grafico
plt.rcParams.update({
    "text.usetex": False,
    "font.family": "serif",
    "font.serif": ["Times New Roman"],
})
plt.rc('axes', titlesize=FONT_LEGEND)
plt.rc('axes', labelsize=FONT_LEGEND)
plt.rc('xtick', labelsize=FONT_TICKS)
plt.rc('ytick', labelsize=FONT_TICKS)
plt.rc('legend', fontsize=FONT_LEGEND)
plt.rc('figure', titlesize=FONT_TITLE)

# Bar chart impilato con due tonalità dello stesso colore (arancio)
plt.figure(figsize=LANDSCAPE_INCHES)
bar_width = 0.2
x = np.arange(len(threads))

for i, impl in enumerate(implementations):
    name = impl["name"]
    base_color = np.array([int(impl["color"][1:3],16)/255,
                           int(impl["color"][3:5],16)/255,
                           int(impl["color"][5:7],16)/255])  # colore da hex a RGB
    slic_color = base_color + (1 - base_color) * 0.5  # schiarisce il colore
    slic_color = np.clip(slic_color, 0, 1)
    ms_color = base_color  # colore pieno per Mean-Shift

    # barra SLIC (chiaro)
    plt.bar(x + i*bar_width, mean_times[name]["slic"], width=bar_width, color=slic_color)
    # barra MS (pieno) impilata sopra
    plt.bar(x + i*bar_width, mean_times[name]["ms"], width=bar_width, bottom=mean_times[name]["slic"], color=ms_color, label=name)

plt.xlabel("OpenMP threads")
plt.ylabel("Average execution time (s)")
plt.xticks(x + bar_width, threads)
# plt.yscale('log')
plt.legend()
plt.grid(True, which="both", ls="--", lw=0.5)
plt.tight_layout()
plt.savefig("slic_ms_separate.pdf")
plt.show()


print("Stacked bar chart generated: slic_ms_stacked_bar_orange.png")
