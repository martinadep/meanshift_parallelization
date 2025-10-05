#!/bin/bash
threads=(1 2 4 8 16 32 64 96)

# python ./plots/img_to_csv.py -i ./dataset/76002.jpg
BREAKDOWN_PATH=./data/breakdown_results_slic.txt
./scripts/compile_variant.sh breakdown_slic_ms

for t in "${threads[@]}"; do
    echo "Running SLIC-MeanShift Breakdown with ${t} threads..."    
    # Set OpenMP threads
    export OMP_NUM_THREADS=${t}
    ./build/breakdown_slic_ms -i ./data/batch/original_76002.csv >> ${BREAKDOWN_PATH}
done
echo "SLIC-MeanShift Breakdown completed!"
echo "Generating SLIC-MeanShift Breakdown plot..."
python ./plots/breakdown_slic.py
