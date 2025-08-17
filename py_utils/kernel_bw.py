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
