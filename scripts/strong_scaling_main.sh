#!/bin/bash

# Create results directory
mkdir -p results_strong_scaling

# Define implementation types for main variants
implementations=("main" "main_matrix" "main_matrix_block" "main_sqrd")

# Define thread counts
threads=(1 2 4 8 16 32 64)

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
done

echo "All main variant tests completed!"