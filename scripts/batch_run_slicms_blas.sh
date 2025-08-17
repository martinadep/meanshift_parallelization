#!/bin/bash
OUTPUT_DIR="./output"
OUTPUT_BATCH_DIR="./output/batch_output_blas"

# Create results directory and output directory
rm -rf "${OUTPUT_BATCH_DIR}"
mkdir -p "${OUTPUT_DIR}"
mkdir -p "${OUTPUT_BATCH_DIR}" 

# Define thread counts
threads=(1 2 4 8 16 32) # 64 96)

# Find all original csv files
csv_files=$(find ./data/batch -name "original_*.csv")

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
        mkdir -p "${OUTPUT_BATCH_DIR}/${id}"
            
        # Output filepath
        output_path="${OUTPUT_BATCH_DIR}/${id}/slic_ms_blas_${t}_reconstructed.csv"
            
        echo "  Processing ${filename} -> ${output_path}..."
            
        ./build/slic_ms_openblas -i "${csv_file}" -o "${output_path}" >> "${OUTPUT_DIR}/slic_ms_blas_${t}_threads.txt"
    done
done

echo "Batch run completed!"
echo "Batch Results saved in ${OUTPUT_BATCH_DIR}"
echo "Execution outputs for slic_ms_blas saved in ${OUTPUT_DIR}"