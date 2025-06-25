#!/bin/bash

set -e

mkdir -p results_weak_scaling

THREADS=(1 2 4 8 16 32 64)
BINARIES=("slic_ms" "slic_ms_sqrd" "slic_ms_matrix"  "slic_ms_matrix_block")

for BIN in "${BINARIES[@]}"; do
    for T in "${THREADS[@]}"; do
        OUT="results_weak_scaling/${BIN}_${T}_threads.txt"
        IMG="./dataset_weak_scaling/374067_${T}t.jpg"
        python ./py_utils/img_to_csv.py -i "$IMG"

        export OMP_NUM_THREADS=$T
        for i in {1..3}; do
                ./build/${BIN} >> "$OUT"
        done
    done
    mkdir -p results_weak_scaling/$BIN
    mv results_weak_scaling/${BIN}_*.txt results_weak_scaling/$BIN/
    echo "Results for $BIN saved in results_weak_scaling/$BIN/"
done