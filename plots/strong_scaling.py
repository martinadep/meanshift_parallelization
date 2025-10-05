import matplotlib.pyplot as plt
import numpy as np
import os
import argparse
from utils import try_read_file, extract_times, extract_separate_times
from config import (
    threads, implementations, strong_scaling_dir, output_plots_dir,
    slic_to_ms_map, FONT_AXES, FONT_TICKS, 
    FONT_LEGEND, LANDSCAPE_INCHES
)

def get_color(impl_folder, lighter=False):
    """Get color for implementation."""
    for impl in implementations:
        if impl["folder"] == impl_folder or impl["folder"] == slic_to_ms_map.get(impl_folder):
            color = impl["color"]
            if lighter:
                color = color.lstrip('#')
                rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
                rgb = tuple(int(c + (255 - c) * 0.5) for c in rgb)
                return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
            return impl["color"]
    return "#666666"

def get_timing_data(impl_folder, combined=False):
    """Get timing data for all thread counts."""
    data = {}
    for t in threads:
        filepath = os.path.join(strong_scaling_dir, impl_folder, f"{impl_folder}_{t}_threads.txt")
        if os.path.exists(filepath):
            content = try_read_file(filepath)
            if combined:
                data[t] = extract_separate_times(content)
            else:
                data[t] = extract_times(content, include_slic=True)
        else:
            data[t] = ([], []) if combined else []
    return data

def plot_bars(impl_folders, combined=False, separate=False, save_path=None):
    """Generic bar plotting function."""
    fig, ax = plt.subplots(figsize=LANDSCAPE_INCHES)
    x = np.arange(len(threads))
    width = 0.25
    
    for i, impl in enumerate(impl_folders):
        data = get_timing_data(impl, combined)
        impl_entry = next((imp for imp in implementations if imp["folder"] == impl), None)
        impl_name = impl_entry["name"] if impl_entry else impl

        if combined and separate:
            # Combined bars for SLIC + Mean Shift
            slic_means = [np.mean(data[t][0]) if data[t][0] else 0 for t in threads]
            ms_means = [np.mean(data[t][1]) if data[t][1] else 0 for t in threads]
            
            ax.bar(x + i * width, slic_means, width, 
                   color=get_color(impl, lighter=True))
            ax.bar(x + i * width, ms_means, width, bottom=slic_means,
                   label=f'{impl_name}',color=get_color(impl))
        else:
            if combined:
                # Use combined times (SLIC + Mean Shift)
                means = []
                stds = []
                for t in threads:
                    slic_times, ms_times = data[t]
                    if slic_times and ms_times:
                        combined_times = [slic_times[j] + ms_times[j] for j in range(min(len(slic_times), len(ms_times)))]
                        means.append(np.mean(combined_times))
                        stds.append(np.std(combined_times))
                    else:
                        means.append(0)
                        stds.append(0)
            else:
                # Mean Shift only
                means = [np.mean(data[t]) if data[t] else 0 for t in threads]
                stds = [np.std(data[t]) if data[t] else 0 for t in threads]
            
            ax.bar(x + i * width, means, width, 
                  label=impl_name, color=get_color(impl))
    
    # title = "SLIC + Mean Shift" if "slic" in impl_folders[0] else "Mean Shift"
    # if combined and separate:
    #     title += " (separate)"
    # elif combined:
    #     title += " (Total)"
    
    ax.set_xlabel('Number of Threads', fontsize=FONT_AXES)
    ax.set_ylabel('Execution Time (seconds)', fontsize=FONT_AXES)
    # ax.set_title(f'{title} Strong Scaling Performance', fontsize=FONT_TITLE)
    ax.set_xticks(x + width * (len(impl_folders) - 1) / 2)
    ax.set_xticklabels(threads, fontsize=FONT_TICKS)
    ax.tick_params(axis='y', labelsize=FONT_TICKS)
    ax.legend(fontsize=FONT_LEGEND)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    if save_path:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    plt.close()

def create_plots(impl_type="mean_shift"):
    """Create strong scaling plots."""
    # Ensure output directory exists
    os.makedirs(output_plots_dir, exist_ok=True)
    
    if impl_type == "mean_shift":
        impls = ["mean_shift", "mean_shift_matrix", "mean_shift_matrix_blas"]
        save_path = os.path.join(output_plots_dir, "strong_scaling_mean_shift.png")
        plot_bars(impls, save_path=save_path)
    
    elif impl_type == "slic_ms":
        impls = ["slic_ms", "slic_ms_matrix", "slic_ms_matrix_blas"]
        # Total time plot
        save_path_total = os.path.join(output_plots_dir, "strong_scaling_slic_total.png")
        plot_bars(impls, combined=True, save_path=save_path_total)
        # Separate plot
        save_path_separate = os.path.join(output_plots_dir, "strong_scaling_slic_separate.png")
        plot_bars(impls, combined=True, separate=True, save_path=save_path_separate)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot strong scaling results.")
    parser.add_argument('--type', choices=['mean_shift', 'slic_ms'], default='mean_shift',
                        help='Type of plot to generate: mean_shift or slic_ms')
    args = parser.parse_args()

    create_plots(args.type)