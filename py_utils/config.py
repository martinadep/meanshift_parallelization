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
threads = [1, 2, 4, 8, 16, 32, 64]

# Implementations configuration with colors for plotting
implementations = [
    {"name": "mean_shift", "color": "#BC1957", "folder": "mean_shift"},  
    {"name": "mean_shift_sqrd", "color": "#D85A1A", "folder": "mean_shift_sqrd"},    
    {"name": "mean_shift_matrix", "color": "#FFAA00DA", "folder": "mean_shift_matrix"}, 
    {"name": "mean_shift_matrix_block", "color": "#FFD900", "folder": "mean_shift_matrix_block"}, 
    {"name": "slic_ms", "color": "#1B529F", "folder": "slic_ms"},               
    {"name": "slic_ms_sqrd", "color": "#38A5D0", "folder": "slic_ms_sqrd"},
    {"name": "slic_ms_matrix", "color": "#2A7709", "folder": "slic_ms_matrix"},
    {"name": "slic_ms_matrix_block", "color": "#1BBA13", "folder": "slic_ms_matrix_block"} 
]

# Color mapping for timing components
timing_colors = {
    # Mean Shift components
    "coords_update": "blue", 
    "kernel": "orange",
    "distance_shift": "red",
    "distance_kernel": "green",
    "distance_cluster": "purple", 
    # SLIC components
    "slic_distance_calc": "blue",
    "assignment_op": "orange",
    "center_init": "green",
    "center_update": "red",
    "cluster_accumulate": "purple"
}

# SLIC to mean_shift implementation mapping for colors
slic_to_ms_map = {
    "slic_ms": "mean_shift",
    "slic_ms_sqrd": "mean_shift_sqrd",
    "slic_ms_matrix": "mean_shift_matrix",
    "slic_ms_matrix_block": "mean_shift_matrix_block"
}