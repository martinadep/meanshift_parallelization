import matplotlib.pyplot as plt
import numpy as np
from config import timing_colors, slic_to_ms_map

def setup_plot_style():
    """Set common plot styling."""
    plt.rcParams.update({'font.size': 14})

def create_bar_chart(data, x_labels, title, xlabel, ylabel, 
                    legend_title=None, log_scale=False, 
                    filename=None, show_values=True):
    """Create a general bar chart with the given data."""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot bars
    bars = ax.bar(x_labels, data, color='skyblue', edgecolor='navy')
    
    # Add values on top of bars if requested
    if show_values:
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01*max(data),
                    f'{data[i]:.3f}', ha='center', va='bottom')
    
    # Configure axes
    ax.set_xlabel(xlabel, fontsize=16)
    ax.set_ylabel(ylabel, fontsize=16)
    ax.set_title(title, fontsize=18)
    if log_scale:
        ax.set_yscale('log')
    
    # Add grid and legend if needed
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    if legend_title:
        ax.legend(title=legend_title)
    
    # Save figure if filename is provided
    if filename:
        plt.tight_layout()
        plt.savefig(filename)
        print(f"Plot saved as '{filename}'")
    
    return fig, ax

def create_scaling_bar_chart(implementations, threads, times_dict, 
                           title, ylabel, filename, log_scale=False):
    """Create bar chart for scaling data with multiple implementations."""
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Setup
    bar_width = 0.11
    index = np.arange(len(threads))
    
    # Plot each implementation as a set of bars
    for i, impl in enumerate(implementations):
        impl_name = impl["name"]
        color = impl["color"]
        times = times_dict[impl_name]
        
        # Position the bars
        position = index + (i - len(implementations)/2 + 0.5) * bar_width
        ax.bar(position, times, bar_width, color=color, label=impl_name)
    
    # Configure the chart
    ax.set_xlabel('Number of Threads', fontsize=16)
    ax.set_ylabel(ylabel, fontsize=16)
    ax.set_title(title, fontsize=18)
    ax.set_xticks(index)
    ax.set_xticklabels([str(t) for t in threads], fontsize=14)
    if log_scale:
        ax.set_yscale('log')
    
    # Add grid and legend
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.legend(fontsize=12)
    
    plt.tight_layout()
    plt.savefig(filename)
    print(f"Plot saved as '{filename}'")
    
    return fig, ax

def create_stacked_scaling_chart(implementations, threads, times_dict, 
                               title, ylabel, filename, log_scale=False):
    """Create stacked bar chart for SLIC + MeanShift implementations."""
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Setup
    bar_width = 0.11
    index = np.arange(len(threads))
    
    # Create color map from implementations
    color_map = {impl["name"]: impl["color"] for impl in implementations}
    
    # Plot each implementation
    for i, impl in enumerate(implementations):
        impl_name = impl["name"]
        color = impl["color"]
        
        # Position the bars
        position = index + (i - len(implementations)/2 + 0.5) * bar_width
        
        if "slic" in impl_name:
            # For SLIC implementations, show stacked bars
            slic_times = times_dict[impl_name]["slic"]
            ms_times = times_dict[impl_name]["mean_shift"]
            
            # Get corresponding mean_shift implementation color
            ms_impl = slic_to_ms_map.get(impl_name)
            ms_color = color_map.get(ms_impl, color)
            
            # Draw SLIC part (bottom)
            ax.bar(position, slic_times, bar_width, 
                  color='#38A5D0', label=f"{impl_name} (SLIC)" if i == 4 else "")
            
            # Draw mean_shift part (top)
            ax.bar(position, ms_times, bar_width, bottom=slic_times, 
                  color=ms_color, label=f"{impl_name} (mean-shift)" if i == 4 else "")
        else:
            # For regular mean_shift implementations, show simple bars
            times = times_dict[impl_name]["mean_shift"]
            ax.bar(position, times, bar_width, color=color, label=impl_name)
    
    # Fix legend to avoid duplicates
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), fontsize=12)
    
    # Configure the chart
    ax.set_xlabel('Number of Threads', fontsize=16)
    ax.set_ylabel(ylabel, fontsize=16)
    ax.set_title(title, fontsize=18)
    ax.set_xticks(index)
    ax.set_xticklabels([str(t) for t in threads], fontsize=14)
    if log_scale:
        ax.set_yscale('log')
    
    # Add grid
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(filename)
    print(f"Plot saved as '{filename}'")
    
    return fig, ax