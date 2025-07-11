#!/bin/bash

set -e

mkdir -p results_weak_scaling

THREADS=(1 2 4 8 16 32 64)
BINARIES=("mean_shift" "mean_shift_sqrd" "mean_shift_matrix" "mean_shift_matrix_block")

for BIN in "${BINARIES[@]}"; do
    for T in "${THREADS[@]}"; do
        IMG="./dataset_weak_scaling/374067_${T}t.jpg"
        python ./py_utils/img_to_csv.py -i "$IMG"
        export OMP_NUM_THREADS=$T
        OUT="results_weak_scaling/${BIN}_${T}_threads.txt"

        if [[ "$T" -le 4 ]]; then
            for i in {1..3}; do
                ./build/${BIN} >> "$OUT"
            done
        elif [[ "$T" -le 16 ]]; then
            ./build/${BIN} >> "$OUT"
        else
            if [[ "$BIN" == "mean_shift_matrix" || "$BIN" == "mean_shift_matrix_block" ]]; then
                echo "not running ${BIN} with ${T} threads to avoid segmentation fault"
            else
                ./build/${BIN} >> "$OUT"
            fi
        fi
    done

    mkdir -p results_weak_scaling/$BIN
    mv results_weak_scaling/${BIN}_*.txt results_weak_scaling/$BIN/
    echo "Results for $BIN saved in results_weak_scaling/$BIN/"
done
