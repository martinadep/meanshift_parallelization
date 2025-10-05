#!/bin/bash

OUTPUT_DIR="./results_strong_scaling"
threads=(1 2 4 8 16 32 64 96)

usage() {
    echo "Usage: $0 [OPTION]"
    echo "  meanshift    Run mean shift strong scaling tests"
    echo "  slicms       Run SLIC-MS strong scaling tests"
    echo "  all          Run both (default)"
    echo "  -h           Show help"
    echo ""
    echo "Examples:"
    echo "  $0           # Run everything"
    echo "  $0 all       # Run everything"
    echo "  $0 meanshift # Run only mean shift tests"
    echo "  $0 slicms    # Run only SLIC-MS tests"
}

run_tests() {
    local algorithm=$1
    local implementations
    local csv_files
    local file_prefix
    
    case $algorithm in
        meanshift)
            echo "=== Running Mean Shift Strong Scaling Tests ==="
            implementations=("mean_shift" "mean_shift_matrix" "mean_shift_matrix_blas")
            csv_files=$(find ./data/resized_batch/ -name "resized_*.csv")
            file_prefix="resized_"
            ;;
        slicms)
            echo "=== Running SLIC-MS Strong Scaling Tests ==="
            implementations=("slic_ms" "slic_ms_matrix" "slic_ms_matrix_blas")
            csv_files=$(find ./data/batch/ -name "original_*.csv")
            file_prefix="original_"
            ;;
    esac
    
    if [[ -z "$csv_files" ]]; then
        echo "No CSV files found for $algorithm"
        return 1
    fi
    
    for csv_file in $csv_files; do
        filename=$(basename "$csv_file")
        id=${filename%.csv}
        id=${id#${file_prefix}}
        
        echo "Processing: $filename (ID: $id)"
        
        for impl in "${implementations[@]}"; do
            echo "  Running: $impl"
            mkdir -p "${OUTPUT_DIR}/${impl}"
            ./scripts/compile_variant.sh "$impl"
            
            for t in "${threads[@]}"; do
                echo "Running ${impl} with ${t} threads..."
                export OMP_NUM_THREADS=${t}
                ./build/${impl} -i "${csv_file}" >> "${OUTPUT_DIR}/${impl}/${impl}_${t}_threads.txt"
            done
        done
    done
    
    echo "$algorithm tests completed!"
}

# Main execution
mkdir -p "${OUTPUT_DIR}"

case "${1:-all}" in
    meanshift)
        run_tests meanshift
        python plots/strong_scaling.py --type mean_shift
        ;;
    slicms)
        run_tests slicms
        python plots/strong_scaling.py --type slic_ms
        ;;
    all|"")
        run_tests meanshift
        run_tests slicms
        python plots/strong_scaling.py --type mean_shift
        python plots/strong_scaling.py --type slic_ms
        ;;
    -h|--help)
        usage
        exit 0
        ;;
    *)
        echo "Unknown option: $1"
        usage
        exit 1
        ;;
esac

echo ""
echo "=== All tests completed! ==="
echo "Results saved in: ${OUTPUT_DIR}"