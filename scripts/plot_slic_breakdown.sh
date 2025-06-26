#!/bin/bash
threads=(1 2 4 8 16 32 64 96)

python ./py_utils/img_to_csv.py -i ./dataset/76002.jpg

for t in "${threads[@]}"; do
    echo "Running SLIC-MeanShift Breakdown with ${t} threads..."    
    # Set OpenMP threads
    export OMP_NUM_THREADS=${t}
    ./build/breakdown_slic_ms >> ./data/slic_ms_breakdown.txt   
done

python ./py_utils/breakdown_plot_slic.py
echo "SLIC-MeanShift Breakdown completed!"