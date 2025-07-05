#!/bin/bash
python ./py_utils/img_to_csv.py

export OMP_NUM_THREADS=1

echo "Running mean-shift breakdown..."
./build/breakdown_mean_shift 
echo "Mean-shift breakdown completed!"

echo "Generating breakdown plot..."
python ./py_utils/breakdown_mean_shift.py
echo "Breakdown plot generated!"
