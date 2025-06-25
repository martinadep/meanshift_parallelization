#!/bin/bash
python ./py_utils/img_to_csv.py

export OMP_NUM_THREADS=1

echo "Running mean-shift breakdown..."
./build/breakdown_mean_shift 

python ./py_utils/breakdown_plot_mean_shift.py
echo "Mean-shift Breakdown completed!"
