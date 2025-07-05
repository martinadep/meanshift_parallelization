#!/bin/bash

output_dir="./output/batch_output_acc"

# Create results directory and output directory
mkdir -p ${output_dir}

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
    mkdir -p "${output_dir}/${id}"
            
    # Output filepath
    output_path="${output_dir}/${id}/mean_shift_acc_reconstructed.csv"
            
    echo "  Processing ${filename} -> ${output_path}..."
            
    ./build/mean_shift_acc -i "${csv_file}" -o "${output_path}" >> "${output_dir}/mean_shift_acc.txt"
done

echo "Batch run completed!"

echo "Batch Results saved in ${output_dir}"