#!/bin/bash

OUTPUT_DIR="./batch_output"
BASE_OUTPUT_DIR="./batch_output"
threads=(1 2 4 8 16 32 64 96)

# Program configurations: name -> [executable, activate_omp_threads, output_suffix]
declare -A PROGRAMS=(
    ["omp"]="slic_ms:true:omp"
    ["acc"]="slic_ms_acc:false:acc" 
    ["matrix_blas"]="slic_ms_matrix_openblas:true:matrix_blas"
    ["matrix_omp"]="slic_ms_matrix:true:matrix_omp"
)

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "  -p PROG1,PROG2,...  Specify programs (omp,acc,matrix_blas,matrix_omp)"
    echo "  -a                  Run all programs"
    echo "  -h                  Show help"
}

run_program() {
    local impl=$1
    local config=(${PROGRAMS[$impl]//:/ })
    local executable=${config[0]}
    local activate_omp_threads=${config[1]}
    local output_suffix=${config[2]}
    
    local output_batch_dir="${BASE_OUTPUT_DIR}/batch_output_${output_suffix}"
    
    echo "=== Running ${impl} version (${executable}) ==="
    ./scripts/compile_variant.sh "$executable"
    rm -rf "${output_batch_dir}"
    mkdir -p "${OUTPUT_DIR}" "${output_batch_dir}"
    
    if [[ "$activate_omp_threads" == "true" ]]; then
        # Multi-threaded version
        for t in "${threads[@]}"; do
            echo "Running ${executable} with ${t} threads..."
            export OMP_NUM_THREADS=${t}
            
            for csv_file in $csv_files; do
                process_file "$csv_file" "$output_batch_dir" "${impl}_${t}" "${executable}" "${impl}_${t}_threads.txt"
            done
        done
    else
        # Single-threaded version
        export OMP_NUM_THREADS=1
        for csv_file in $csv_files; do
            process_file "$csv_file" "$output_batch_dir" "${impl}" "${executable}" "${impl}.txt"
        done
    fi
    
    echo "${impl} version completed! Results saved in ${output_batch_dir}"
}

process_file() {
    local csv_file=$1
    local output_batch_dir=$2
    local suffix=$3
    local executable=$4
    local log_file=$5
    
    local filename=$(basename "$csv_file")
    local id=$(echo "$filename" | sed 's/original_\(.*\)\.csv/\1/')
    
    mkdir -p "${output_batch_dir}/${id}"
    local output_path="${output_batch_dir}/${id}/slic_ms_${suffix}_reconstructed.csv"
    
    echo "  Processing ${filename} -> ${output_path}..."
    ./build/${executable} -i "${csv_file}" -o "${output_path}" >> "${OUTPUT_DIR}/${log_file}"
}

# Parse arguments
PROGRAMS_TO_RUN=()
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--programs) IFS=',' read -ra PROGRAMS_TO_RUN <<< "$2"; shift 2 ;;
        -a|--all) PROGRAMS_TO_RUN=("omp" "acc" "matrix_blas" "matrix_omp"); shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown option: $1"; usage; exit 1 ;;
    esac
done

# Default to all if none specified
if [[ ${#PROGRAMS_TO_RUN[@]} -eq 0 ]]; then
    echo "No programs specified. Use -a for all or -p to specify."
    usage; exit 1
fi

# Find CSV files
csv_files=$(find ./data/batch -name "original_*.csv")
if [[ -z "$csv_files" ]]; then
    echo "No CSV files found in ./data/batch"
    exit 1
fi

mkdir -p "${OUTPUT_DIR}"

# Run selected programs
for program in "${PROGRAMS_TO_RUN[@]}"; do
    if [[ -n "${PROGRAMS[$program]}" ]]; then
        run_program "$program"
    else
        echo "Unknown program: $program"
    fi
done

echo "=== Batch run completed! ==="