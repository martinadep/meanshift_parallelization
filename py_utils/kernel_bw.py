import numpy as np
import matplotlib.pyplot as plt

# --------------------------
# Config
# --------------------------
FONT_TITLE = 16
FONT_AXES = 10
FONT_TICKS = 10
FONT_LEGEND = 12
LANDSCAPE_INCHES = (6.7, 4.1)

# --------------------------
# Kernel Definitions with Bandwidth
# --------------------------
def gaussian_kernel(x, h=1):
    return np.exp(-0.5 * (x / h)**2)

def uniform_kernel(x, h=1):
    return np.where(np.abs(x / h) <= 1, 1, 0)

def epanechnikov_kernel(x, h=1):
    return np.where(np.abs(x / h) <= 1, 0.75 * (1 - (x / h)**2), 0)

plt.rcParams.update({
    "text.usetex": False,  
    "font.family": "serif",
    "font.serif": ["Times New Roman"],
})
# --------------------------
# Plot Kernels with Different Bandwidths
# --------------------------
x = np.linspace(-5, 5, 500)
bandwidths = [0.5, 1, 2]
colors = {"Gaussian": "blue", "Uniform": "green", "Epanechnikov": "red"}

fig, axes = plt.subplots(1, 3, figsize=(10, 3), sharey=True)

for ax, h in zip(axes, bandwidths):
    ax.plot(x, gaussian_kernel(x, h), label="Gaussian", color=colors["Gaussian"], linewidth=2)
    ax.plot(x, uniform_kernel(x, h), label="Uniform", color=colors["Uniform"], linewidth=2)
    ax.plot(x, epanechnikov_kernel(x, h), label="Epanechnikov", color=colors["Epanechnikov"], linewidth=2)

    ax.set_title(f"h = {h}", fontsize=FONT_AXES)
    ax.set_xlabel("x", fontsize=FONT_AXES)
    ax.tick_params(axis='both', which='major', labelsize=FONT_TICKS)
    ax.grid(alpha=0.3)

# Label y solo sul primo subplot
axes[0].set_ylabel("K(x)", fontsize=FONT_AXES)

# Titolo globale
# plt.suptitle("Effect of Bandwidth on Kernel Functions", fontsize=FONT_TITLE)

# Legenda comune
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center", ncol=3, fontsize=FONT_LEGEND, frameon=False)

plt.tight_layout(rect=[0, 0, 1, 0.9])  # lascia spazio al titolo e legenda
plt.savefig("kernel_bandwidths.pdf", dpi=300)
plt.show()

# ...existing code...

# --------------------------
# Plot: Somma dei Kernel centrati sui sample
# --------------------------
sample_points = np.array([-3, 0, 1, 2])  # punti sample
x = np.linspace(-5, 5, 500)
bandwidths = [0.5, 1, 2]

fig2, axes2 = plt.subplots(1, 3, figsize=(10, 3), sharey=True)

for ax, h in zip(axes2, bandwidths):
    kernels = []
    for pt in sample_points:
        k = gaussian_kernel(x - pt, h)
        kernels.append(k)
        ax.plot(x, k, '--', linewidth=1, color='black')
        ax.scatter(pt, gaussian_kernel(0, h), color='black', zorder=5)
    sum_kernels = np.sum(kernels, axis=0)
    ax.plot(x, sum_kernels, color='darkblue', linewidth=1.5)
    ax.set_title(f"h = {h}", fontsize=12)
    ax.set_xlabel("x", fontsize=12)
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.grid(alpha=0.3)

axes2[0].set_ylabel("K(x)", fontsize=12)
handles2, labels2 = axes2[0].get_legend_handles_labels()
fig2.legend(handles2, labels2, loc="upper center", ncol=4, fontsize=FONT_LEGEND, frameon=False)
plt.tight_layout()
plt.savefig("kernel_sum_samples.pdf", dpi=600)
plt.show()