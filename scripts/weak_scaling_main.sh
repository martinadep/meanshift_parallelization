#!/bin/bash

set -e

mkdir -p results_weak_scaling

THREADS=(1 2 4 8 16 32 64)
BINARIES=("main" "main_matrix" "main_sqrd" "main_matrix_block")

for BIN in "${BINARIES[@]}"; do
    for T in "${THREADS[@]}"; do
        IMG="./dataset_weak_scaling/374067_${T}t.jpg"
        python ./py_utils/img_to_csv.py -i "$IMG"
        export OMP_NUM_THREADS=$T
        OUT="results_weak_scaling/${BIN}_${T}_threads.txt"
        # 5 runs for 1,2,4,8 threads 
        # Only 1 run for 16,32,64 threads
        if [[ "$T" -le 4 ]]; then
            for i in {1..3}; do
                ./build/${BIN} >> "$OUT"
            done
        else
            ./build/${BIN} >> "$OUT"
        fi
    done
    mkdir -p results_weak_scaling/$BIN
    mv results_weak_scaling/${BIN}_*.txt results_weak_scaling/$BIN/
done