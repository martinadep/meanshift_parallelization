#!/bin/bash

echo "====================================="
echo "Mean Shift Parallelization - Quick Demo"
echo "====================================="
echo

# Parse command line arguments
THREADS=1
if [[ $# -gt 0 ]]; then
    if [[ $1 =~ ^[0-9]+$ ]] && [[ $1 -gt 0 ]]; then
        THREADS=$1
        echo "Using $THREADS threads"
    else
        echo "Usage: $0 [number_of_threads]"
        echo "Example: $0 4"
        echo "number_of_threads must be a positive integer (default: 1)"
        exit 1
    fi
else
    echo "Using default: $THREADS thread"
fi
echo

if [[ ! -f "CMakeLists.txt" ]]; then
    echo "Error: Please run this script from the project root directory"
    echo "Usage: ./mean_shift_demo.sh [number_of_threads]"
    exit 1
fi


echo "Setting up Python environment and dependencies..."
./scripts/setup_python.sh
if [[ $? -ne 0 ]]; then
    echo "Error: Python setup failed"
    exit 1
fi

echo "Setting up directories..."
mkdir -p data
mkdir -p data/plots

echo "Converting sample image to CSV format..."
if [[ -f "dataset/12003.jpg" ]]; then
    python plots/img_to_csv.py -i dataset/12003.jpg -o data/example.csv -r 90 60
    echo "Image converted to CSV: data/example.csv" 
    # you can also use the already provided data/example_90x60.csv or data/example_481x321.csv
else
    echo "Warning: Sample image dataset/12003.jpg not found"
    echo "Please place an image in the dataset folder or use your own image"
    exit 1
fi

echo
echo ">> Building Mean Shift implementation..."
cmake -B build
if [[ $? -ne 0 ]]; then
    echo "Error: CMake configuration failed"
    exit 1
fi

cmake --build build --target mean_shift
if [[ $? -ne 0 ]]; then
    echo "Error: Build failed"
    exit 1
fi
echo ">> Build successful"


echo
echo "Running Mean Shift algorithm with $THREADS threads..."
export OMP_NUM_THREADS=$THREADS
./build/mean_shift -i data/example.csv -o data/demo_result.csv -b 15 -k epanechnikov

if [[ $? -ne 0 ]]; then
    echo "Error: Mean Shift execution failed"
    exit 1
fi
echo "Mean Shift processing completed"

# Convert result back to image
echo
echo "Converting result back to image..."
python plots/csv_to_img.py -i data/demo_result.csv -o data/demo_segmented_result.jpg
if [[ $? -ne 0 ]]; then
    echo "Error: CSV to image conversion failed"
    exit 1
fi
echo "Result image saved: data/demo_segmented_result.jpg"

echo
echo "====================================="
echo "Demo completed successfully!"
echo "====================================="
echo
echo "Files generated:"
echo "  • data/example.csv - Input data"
echo "  • data/demo_result.csv - Processed data"
echo "  • data/demo_segmented_result.jpg - Final segmented image"
echo
echo "You can now:"
echo "  1. View the segmented image: data/demo_segmented_result.jpg"
echo "  2. Try different algorithms: e.g. ./build/mean_shift_matrix, ./build/slic_ms"
echo "  3. Experiment with parameters: -b (bandwidth) -k (kernel)"
echo "  4. Try different thread counts: ./mean_shift_demo.sh 4"
echo "  5. Run performance analysis with scripts in the scripts/ folder"
echo