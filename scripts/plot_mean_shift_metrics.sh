#!/bin/bash
python ./py_utils/img_to_csv.py

export OMP_NUM_THREADS=1

echo "Running metrics mean-shift..."
./build/metrics_mean_shift 

python ./py_utils/metrics_plot_mean_shift.py
echo "Metrics mean-shift completed!"
