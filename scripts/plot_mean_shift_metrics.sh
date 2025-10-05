#!/bin/bash
python ./plots/img_to_csv.py

export OMP_NUM_THREADS=1
./scripts/compile_variant.sh "metrics_mean_shift"

bandwidths=(2.0 5.0 7.0)
for bandwidth in "${bandwidths[@]}"; do
    echo "Running mean-shift with bandwidth: $bandwidth"
    ./build/metrics_mean_shift -b $bandwidth 
done

echo "Metrics mean-shift completed!"

echo "Generating metrics mean-shift plot..."
python ./plots/metrics_plot_mean_shift.py
echo "Metrics mean-shift plot generated!"
