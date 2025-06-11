#!/bin/bash

# setup.sh - Setup script for Mean-Shift Segmentation environment

echo "=== Mean-Shift Segmentation Setup ==="

# 1. Check if Python is available
if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
elif command -v python &>/dev/null; then
    PYTHON_CMD=python
else
    echo "Error: Python not found. Please install Python 3.x"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Using Python: $($PYTHON_CMD --version)"

# 2. Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    $PYTHON_CMD -m venv venv
    VENV_CREATED=1
else
    echo "Virtual environment already exists."
    VENV_CREATED=0
fi

# 3. Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
    source venv/bin/activate
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    source venv/Scripts/activate
else
    echo "Warning: Unsupported OS. Please activate virtual environment manually."
fi

# 4. Install dependencies with version constraints compatible with Python 3.10
echo "Installing required packages..."

# Check Python version and install compatible packages
if [[ $(echo "$PYTHON_VERSION < 3.11" | bc) -eq 1 ]]; then
    echo "Detected Python $PYTHON_VERSION - Installing compatible versions"
    pip install --upgrade pip
    pip install numpy pandas pillow matplotlib==3.7.2 networkx==3.1
else
    echo "Installing packages from requirements.txt"
    pip install -r requirements.txt
fi

# 5. Create directories if they don't exist
echo "Setting up directory structure..."
mkdir -p data
mkdir -p build
mkdir -p results_strong_scaling

# 6. Convert example images
echo "Converting example images to CSV format..."

# Process sample images from examples directory
example_images=$(find ./examples -type f -name "*.jpg")

for img_path in $example_images; do
    echo "Processing: $img_path"
    # Extract filename without extension
    filename=$(basename "$img_path")
    filename_no_ext="${filename%.*}"
    
    # Convert to CSV
    $PYTHON_CMD ./py_utils/img_to_csv.py -i "$img_path" -o "./data/original.csv"
    
    echo "\"$img_path\" converted to ./data/original.csv"
done

echo ""
echo "=== Setup Complete ==="
echo "You can now build and run the Mean-Shift algorithm:"
echo "  cmake -B build"
echo "  cmake --build build"
echo "  ./build/main"
echo ""
echo "After processing, convert back to images with:"
echo "  python ./py_utils/csv_to_img.py"