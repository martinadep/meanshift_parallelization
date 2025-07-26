#!/bin/bash
python ./py_utils/img_to_csv.py

export OMP_NUM_THREADS=1

bandwidths=(0.5 2.0 5.0 7.0)
for bandwidth in "${bandwidths[@]}"; do
    echo "Running mean-shift with bandwidth: $bandwidth"
    ./build/breakdown_mean_shift -k gaussian -b $bandwidth >> ./results.txt
    ./build/breakdown_mean_shift -k uniform -b $bandwidth >> ./results.txt
    ./build/breakdown_mean_shift -k epanechnikov -b $bandwidth >> ./results.txt
done

echo "Mean-shift breakdown completed! results saved to ./results.txt"

echo "Generating breakdown plot..."
python ./py_utils/breakdown_mean_shift.py
echo "Breakdown plot generated!"
