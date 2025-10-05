#!/bin/bash

OUTPUT_DIR="./results_strong_scaling"
mkdir -p "$OUTPUT_DIR"

implementations=("slic_ms" "slic_ms_matrix" "slic_ms_matrix_blas")
csv_files=$(find ./data/batch/ -name "original_*.csv")
threads=(1 2 4 8 16 32 64 96)

for csv_file in $csv_files; do
    # Extract the ID number from filename (e.g., "12003" from "original_12003.csv")
    filename=$(basename "$csv_file")
    id=${filename%.csv}
    id=${id#original_}

    for impl in "${implementations[@]}"; do
        mkdir -p "${OUTPUT_DIR}/${impl}"
        ./scripts/compile_variant.sh "$impl"
        for t in "${threads[@]}"; do
            echo "Running ${impl} with ${t} threads on ${id}..."
            export OMP_NUM_THREADS=${t}
            ./build/${impl} -i "${csv_file}" >> "${OUTPUT_DIR}/${impl}/${impl}_${t}_threads.txt"
        done
        echo "Results for ${impl} on ${id} done"
    done
done

echo "All mean_shift variant tests completed!"