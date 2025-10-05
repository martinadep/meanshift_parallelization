#!/bin/bash
python ./plots/img_to_csv.py

BREAKDOWN_PATH="./data/breakdown_results_mean_shift.txt"

export OMP_NUM_THREADS=1
./scripts/compile_variant.sh "breakdown_mean_shift"

bandwidths=(0.5 2.0 5.0 7.0)
for bandwidth in "${bandwidths[@]}"; do
    echo "Running mean-shift with bandwidth: $bandwidth"
    ./build/breakdown_mean_shift -k gaussian -b $bandwidth >> ${BREAKDOWN_PATH}
    ./build/breakdown_mean_shift -k uniform -b $bandwidth >> ${BREAKDOWN_PATH}
    ./build/breakdown_mean_shift -k epanechnikov -b $bandwidth >> ${BREAKDOWN_PATH}
done

echo "Mean-shift breakdown completed! results saved to ${BREAKDOWN_PATH}"

echo "Generating breakdown plot..."
python ./plots/breakdown_mean_shift.py
echo "Breakdown plot generated!"

# change py_utils to plots and combine plots