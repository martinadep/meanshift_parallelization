#!/bin/bash

set -e

mkdir -p results_weak_scaling

THREADS=(1 2 4 8 16 32 64 96)
BINARIES=("slic" "slic_matrix" "slic_sqrd" "slic_matrix_block")

for BIN in "${BINARIES[@]}"; do
    for T in "${THREADS[@]}"; do
        OUT="results_weak_scaling/${BIN}_${T}_threads.txt"
        IMG="./dataset_weak_scaling/374067_${T}t.jpg"
        python ./py_utils/img_to_csv.py -i "$IMG"

        export OMP_NUM_THREADS=$T
        for i in {1..5}; do
                ./build/${BIN}.exe >> "$OUT"
        done
    done
    mkdir -p results_weak_scaling/$BIN
    mv results_weak_scaling/${BIN}_*.txt results_weak_scaling/$BIN/
done