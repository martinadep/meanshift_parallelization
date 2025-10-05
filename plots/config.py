# Image and data paths
in_img_path = "./dataset/12003.jpg"
original_csv_path = "./data/original.csv"
modified_csv_path = "./data/modified.csv"
out_img_path = "./data/reconstructed.jpg"
metrics_path = "./data/metrics_mean_shift.txt"
breakdown_results_path_mean_shift = "./data/breakdown_results_mean_shift.txt"
breakdown_results_path_slic = "./data/breakdown_results_slic.txt"
strong_scaling_dir = 'results_strong_scaling'
output_plots_dir = "./data/plots"

threads = [1, 2, 4, 8, 16, 32, 64, 96]

implementations = [
    {"name": "MeanShift (OpenMP)", "color": "#f26419", "folder": "mean_shift"},
    {"name": "MeanShift Matrix (OpenMP)", "color": "#4581af", "folder": "mean_shift_matrix"},
    {"name": "MeanShift Matrix (OpenMP + OpenBLAS)", "color": "#2f4858", "folder": "mean_shift_matrix_blas"},
    {"name": "SLIC - MS (OpenMP)", "color": "#f26419", "folder": "slic_ms"},
    {"name": "SLIC - MS Matrix (OpenMP)", "color": "#4581af", "folder": "slic_ms_matrix"},
    {"name": "SLIC - MS Matrix (OpenMP + OpenBLAS)", "color": "#2f4858", "folder": "slic_ms_matrix_blas"}
]

# SLIC to mean_shift implementation mapping for colors
slic_to_ms_map = {
    "slic_ms": "mean_shift",
    "slic_ms_matrix": "mean_shift_matrix",
    "slic_ms_openblas": "mean_shift_openblas"
}

# Color mapping for timing components 
timing_colors = {
    # Mean Shift components
    "coords_update": "#2f4858",  
    "distance_cluster": "#3976A5",     
    "distance_shift": "#86bbd8", 
    "distance_kernel": "#f6ae2d",
    "kernel": "#f26419",
    # SLIC components
    "slic_distance_calc": "#f26419",
    "center_init": "#a7d886",
    "center_update": "#378a33",
    "assignment_op": "#ffbf00",
    "cluster_accumulate": "#2a5507"
}

FONT_TITLE = 16
FONT_AXES = 10
FONT_TICKS = 10
FONT_LEGEND = 9
LANDSCAPE_INCHES = (6.7, 4.1)