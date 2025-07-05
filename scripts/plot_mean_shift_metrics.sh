#!/bin/bash
python ./py_utils/img_to_csv.py

export OMP_NUM_THREADS=1

echo "Running metrics mean-shift..."
echo "Using kernels: gaussian, uniform, epanechnikov"
./build/metrics_mean_shift -b 1
./build/metrics_mean_shift -b 2
./build/metrics_mean_shift -b 4

echo "Metrics mean-shift completed!"

echo "Generating metrics mean-shift plot..."
python ./py_utils/metrics_plot_mean_shift.py
echo "Metrics mean-shift plot generated!"
