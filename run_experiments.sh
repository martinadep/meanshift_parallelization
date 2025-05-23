#!/bin/bash

KERNELS=("uniform" "gaussian" "epanechnikov")
IMAGES=("8049.jpg" "12003.jpg" "35010.jpg")
BANDWIDTHS=(5 10 20)
RUNS=3

DATASET_DIR="./dataset"
DATA_DIR="./data"
TESTS_DIR="./test"
PY_IMG2CSV="python ./py_utils/img_to_csv.py -i"

# Ensure output directories exist
mkdir -p "$DATA_DIR"
mkdir -p "$TESTS_DIR"

echo "Starting experiments..."
for kernel in "${KERNELS[@]}"; do
    # Create a directory for each kernel
    echo "Processing kernel: $kernel"
    mkdir -p "$TESTS_DIR/$kernel"
    for img in "${IMAGES[@]}"; do
        img_base="${img%.*}"
        img_path="$DATASET_DIR/$img"
        csv_path="$DATA_DIR/${img_base}.csv"

        # Convert image to CSV
         echo "  Converting $img to CSV..."
        $PY_IMG2CSV "$img_path" -o "$csv_path"

        for bandwidth in "${BANDWIDTHS[@]}"; do
            for run in $(seq 1 $RUNS); do
                out_csv="$DATA_DIR/modifiedB${bandwidth}_${run}.csv"
                slic_csv="$DATA_DIR/slic_outputB${bandwidth}_${run}.csv"
                
                echo "    Running mean-shift: img=$img_base, K=$kernel, B=$bandwidth, run=$run"
                ./build/slic_metrics_double.exe --kernel "$kernel" --bandwidth "$bandwidth" --input "$csv_path" --output "$out_csv" --slic_out "$slic_csv"
                if [ $? -ne 0 ]; then
                    echo "Errore nell'esecuzione di slic_metrics_float.exe per $img_base, kernel $kernel, bandwidth $bandwidth, run $run"
                fi
                # Controllo se i file sono stati creati
                [ -f "$out_csv" ] || echo "File $out_csv NON creato"
                [ -f "$slic_csv" ] || echo "File $slic_csv NON creato"
            done
        done

        # Prepare test directory
        test_dir="$TESTS_DIR/$kernel/$img_base"
        mkdir -p "$test_dir"

        # Move all generated files for this image and kernel
        echo "  Moving results to $test_dir"
        mv "$DATA_DIR"/modifiedB* "$test_dir"/ 2>/dev/null
        mv "$DATA_DIR"/slic_outputB* "$test_dir"/ 2>/dev/null
        [ -f "$DATA_DIR/perf_results.txt" ] && mv "$DATA_DIR/perf_results.txt" "$test_dir"/
        [ -f "$csv_path" ] && mv "$csv_path" "$test_dir"/
    done
done
echo "All experiments completed."
read -p "Press ENTER to exit..."