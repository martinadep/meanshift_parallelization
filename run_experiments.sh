#!/bin/bash
set -x
cd "$(dirname "$0")"
# File di output per salvare i risultati
OUTPUT_FILE="./test/results.txt"
EXECUTABLE="./build/main.exe"

mkdir -p ./test
mkdir -p ./data

cmake -B build
cmake --build build


# Configurazioni di kernel e bandwidth
KERNELS=("gaussian" "uniform" "epanechnikov")
BANDWIDTHS=(10 20 30 40 50)

# Esegui il programma per ogni combinazione di kernel e bandwidth
for kernel in "${KERNELS[@]}"; do
    for bandwidth in "${BANDWIDTHS[@]}"; do
        echo "Running with kernel=$kernel and bandwidth=$bandwidth..." >> $OUTPUT_FILE
        $EXECUTABLE -k $kernel -b $bandwidth -o ./data/modified_${kernel}_${bandwidth}.csv 2>> ./test/errors.log
        if [ $? -ne 0 ]; then
            echo "Error: Execution failed for kernel=$kernel and bandwidth=$bandwidth" >&2
        fi
    done
done

echo "Experiments completed. Results saved in $OUTPUT_FILE."