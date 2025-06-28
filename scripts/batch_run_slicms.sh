#!/bin/bash

# Create results directory and output directory
mkdir -p results_strong_scaling
mkdir -p ./output

# Define thread counts
threads=(1 2 4 8 16 32 64 96)

# Find all original csv files
csv_files=$(find ./data -name "original_*.csv")

mkdir -p "results_strong_scaling/slic_ms"
    
# For each thread count
for t in "${threads[@]}"; do
    echo "Running slic_ms with ${t} threads..."
        
    # Set OpenMP threads
    export OMP_NUM_THREADS=${t}
        
    # Process each CSV file
    for csv_file in $csv_files; do
        # Extract the ID number from filename (e.g., "12003" from "original_12003.csv")
        filename=$(basename "$csv_file")
        id=$(echo "$filename" | sed 's/original_\(.*\)\.csv/\1/')
            
        # Create output directory if it doesn't exist
        mkdir -p "./output/${id}"
            
        # Output filepath
        output_path="./output/${id}/slic_ms_${t}_reconstructed.csv"
            
        echo "  Processing ${filename} -> ${output_path}..."
            
        ./build/slic_ms -i "${csv_file}" -o "${output_path}" >> "results_strong_scaling/slic_ms/slic_ms_${t}_threads.txt"
    done
done
echo "Results for slic_ms saved in results_strong_scaling/slic_ms/"

echo "All SLIC variant tests completed!"