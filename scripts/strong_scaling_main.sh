#!/bin/bash

# Create results directory
mkdir -p results_strong_scaling

# Define implementation types for mean_shift variants
implementations=("mean_shift" "mean_shift_sqrd" "mean_shift_matrix" "mean_shift_matrix_block" )

# Define thread counts
threads=(1 2 4 8 16 32 64 96)

# Number of runs per configuration
num_runs=5

# Run each implementation with different thread counts
for impl in "${implementations[@]}"; do
    # Create directory for this implementation's results
    mkdir -p "results_strong_scaling/${impl}"
    
    # For each thread count
    for t in "${threads[@]}"; do
        echo "Running ${impl} with ${t} threads..."
        
        # Set OpenMP threads
        export OMP_NUM_THREADS=${t}
        
        # Run multiple times for statistical significance
        for ((run=1; run<=${num_runs}; run++)); do
            echo "  Run ${run}/${num_runs}..."
            ./build/${impl} >> "results_strong_scaling/${impl}/${impl}_${t}_threads.txt"
        done
    done
    echo "Results for ${impl} saved in results_strong_scaling/${impl}/"
done

echo "All mean_shift variant tests completed!"