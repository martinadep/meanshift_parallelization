#!/bin/bash

OUTPUT_DIR="./output"
OUTPUT_BATCH_DIR="./output/batch_output_blas"

# Create results directory and output directory
rm -rf "${OUTPUT_BATCH_DIR}"
mkdir -p "${OUTPUT_BATCH_DIR}" 

# Find all original csv files
csv_files=$(find ./data/batch -name "original_*.csv")
     
# Set OpenMP threads to 1
export OMP_NUM_THREADS=1
        
# Process each CSV file
for csv_file in $csv_files; do
    # Extract the ID number from filename (e.g., "12003" from "original_12003.csv")
    filename=$(basename "$csv_file")
    id=$(echo "$filename" | sed 's/original_\(.*\)\.csv/\1/')
            
    # Create output directory if it doesn't exist
    mkdir -p "${OUTPUT_BATCH_DIR}/${id}"
            
    # Output filepath
    output_path="${OUTPUT_BATCH_DIR}/${id}/slic_ms_blas_reconstructed.csv"
            
    echo "  Processing ${filename} -> ${output_path}..."
            
    ./build/slic_ms_blas -i "${csv_file}" -o "${output_path}" >> "${OUTPUT_DIR}/slic_ms_blas.txt"
done

echo "Batch run completed!"
echo "Batch Results saved in ${OUTPUT_BATCH_DIR}"
echo "Execution outputs for slic_ms_acc saved in ${OUTPUT_DIR}"