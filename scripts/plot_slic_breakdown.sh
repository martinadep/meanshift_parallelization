#!/bin/bash
python ./py_utils/img_to_csv.py -i ./dataset/76002.jpg

export OMP_NUM_THREADS=1

echo "Running SLIC-MeanShift breakdown..."
./build/breakdown_slic_ms >> ./data/slic_ms_breakdown.txt

python ./py_utils/breakdown_plot_slic.py
echo "SLIC-MeanShift Breakdown completed!"
