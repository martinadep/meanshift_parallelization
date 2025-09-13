#!/bin/bash

# Create results directory
mkdir -p results_strong_scaling

# Define implementation types for mean_shift variants
implementations=("mean_shift" "mean_shift_matrix" "mean_shift_matrix_blas")
csv_files=$(find ./data/resized_batch/ -name "resized_*.csv")

# Define thread counts
threads=(1 2 4 8 16 32 64 96)

for csv_file in $csv_files; do
    # Extract the ID number from filename (e.g., "12003" from "original_12003.csv")
    filename=$(basename "$csv_file")
    id=${filename%.csv}                          # rimuove l'estensione -> "resized_385028"
    id=${id#resized_} 
    
    # Run each implementation with different thread counts
    for impl in "${implementations[@]}"; do
        # Create directory for this implementation's results
        mkdir -p "results_strong_scaling/${impl}"
        
        # For each thread count
        for t in "${threads[@]}"; do
            echo "Running ${impl} with ${t} threads on ${id}..."
            # Set OpenMP threads
            export OMP_NUM_THREADS=${t}
            ./build/${impl} -i "${csv_file}" >> "results_strong_scaling/${impl}/${id}.txt"
        done
        echo "Results for ${impl} on ${id} done"
    done
done

echo "All mean_shift variant tests completed!"