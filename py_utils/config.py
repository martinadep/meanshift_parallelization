# Image and data paths
in_img_path = "./examples/sample_flower.jpg"
original_csv_path = "./data/original.csv"
modified_csv_path = "./data/modified.csv"
out_img_path = "./data/reconstructed.jpg"
metrics_path = "./data/metrics_mean_shift.txt"

# Results directories
strong_scaling_dir = 'results_strong_scaling'
weak_scaling_dir = 'results_weak_scaling'

# Common thread counts for scaling tests
threads = [1, 2, 4, 8, 16, 32, 64, 96]

# Implementations configuration with colors for plotting
implementations = [
    # {"name": "mean_shift", "color": "#BC1957", "folder": "mean_shift"},  
    # {"name": "mean_shift_sqrd", "color": "#D85A1A", "folder": "mean_shift_sqrd"},    
    # {"name": "mean_shift_matrix", "color": "#FFAA00DA", "folder": "mean_shift_matrix"}, 
    # {"name": "mean_shift_matrix_block", "color": "#FFD900", "folder": "mean_shift_matrix_block"}, 
    # {"name": "slic_ms", "color": "#1B529F", "folder": "slic_ms"},               
    # {"name": "slic_ms_sqrd", "color": "#38A5D0", "folder": "slic_ms_sqrd"},
    # {"name": "slic_ms_matrix", "color": "#2A7709", "folder": "slic_ms_matrix"},
    # {"name": "slic_ms_matrix_block", "color": "#1BBA13", "folder": "slic_ms_matrix_block"},
    {"name": "MeanShift (OpenMP)", "color": "#f26419", "folder": "mean_shift"},
    {"name": "MeanShift Matrix (OpenMP)", "color": "#4581af", "folder": "mean_shift_matrix"},
    {"name": "MeanShift Matrix (OpenMP + OpenBLAS)", "color": "#2f4858", "folder": "mean_shift_openblas"},
    {"name": "SLIC + MS (OpenMP)", "color": "#f26419", "folder": "slic_ms"},
    {"name": "SLIC + MS Matrix (OpenMP)", "color": "#4581af", "folder": "slic_ms_matrix"},
    {"name": "SLIC + MS Matrix (OpenMP + OpenBLAS)", "color": "#2f4858", "folder": "slic_ms_openblas"}
]


# Color mapping for timing components - using provided palette
timing_colors = {
    # Mean Shift components - using palette: 2f4858, 33658a, 86bbd8, f6ae2d, f26419
    "coords_update": "#2f4858",  # Dark blue-gray
    "distance_cluster": "#3976A5",         # Medium blue
    "distance_shift": "#86bbd8", # Light blue
    "distance_kernel": "#f6ae2d", # Yellow
    "kernel": "#f26419", # Orange
    # SLIC components
    "slic_distance_calc": "#2f4858",
    "center_init": "#33658a",
    "center_update": "#86bbd8",
    "assignment_op": "#f6ae2d",
    "cluster_accumulate": "#f26419"
}

# SLIC to mean_shift implementation mapping for colors
slic_to_ms_map = {
    "slic_ms": "mean_shift",
    "slic_ms_sqrd": "mean_shift_sqrd",
    "slic_ms_matrix": "mean_shift_matrix",
    "slic_ms_matrix_block": "mean_shift_matrix_block"
}

# plt.rcParams.update({
#     "text.usetex": True,
#     "font.family": "serif",
#     "text.latex.preamble": r"\usepackage{newtxtext}\usepackage{newtxmath}"
# })

FONT_TITLE = 16
FONT_AXES = 10
FONT_TICKS = 10
FONT_LEGEND = 12
LANDSCAPE_INCHES = (6.7, 4.1)


# plt.rc('axes', titlesize=FONT_AXES)     # fontsize of the axes title
# plt.rc('axes', labelsize=FONT_AXES)     # fontsize of the x and y labels
# plt.rc('xtick', labelsize=FONT_TICKS)   # fontsize of the tick labels
# plt.rc('ytick', labelsize=FONT_TICKS)   # fontsize of the tick labels
# plt.rc('legend', fontsize=FONT_LEGEND)  # legend fontsize
# plt.rc('figure', titlesize=FONT_TITLE)  # fontsize of the figure title