# Mean-Shift Parallelization
A parallel implementation of the Mean-Shift algorithm applied 
to image segmentation. This project optimizes the performance 
of the Mean-Shift algorithm through parallelization techniques, 
enabling more efficient and scalable image segmentation.

## Technical Background
Mean-Shift is a non-parametric density-based clustering algorithm 
used in computer vision and machine learning. In this project, the 
algorithm is applied to image segmentation, a process that divides 
an image into multiple uniform regions, making the image easier to analyze.

The parallel version implemented in this project leverages 
modern multi-core architectures to significantly accelerate 
processing while maintaining the quality of segmentation results.

## Examples
![asto](examples/sample_astro.jpg)
![astoB10](docs/astro_B10.jpg)
![astoB30](docs/astro_B30.jpg)
![flower](examples/sample_flower.jpg)
![flowerB10](docs/flower_B10.jpg)
![flowerB40](docs/flower_B40.jpg)


## Prerequisites
- [CMake](https://cmake.org/download/) (version 3.10 or higher)
- A C++ compiler compatible with C++11 or higher (GCC, Clang, or MSVC)
- Python 3.12 with required packages (NumPy, pandas)

## Complete Workflow
1. Clone the repository:
   ```bash
   git clone https://github.com/martinadep/meanshift_parallelization
   cd mean-shift-parallel
   ```

2. Convert input image to CSV format using the first Python script:
   ```bash
   python .\py_utils\img_to_csv.py (input_image.jpg)
   ```
   This will generate a CSV file that will be processed by the C++ program.

3. Run the C++ program to apply the Mean-Shift algorithm:
   - **Using command line**:
     ```bash
     mkdir build && cd build
     cmake ..
     cmake --build .
     ./mean_shift_segmentation.exe
     ```
   This will process the CSV file and generate a new output CSV file.

4. Convert the output CSV back to an image using the second Python script:
   ```bash
   python .\py_utils\csv_to_img.py (output_csv_file.csv output_image.jpg)
   ```
   This will transform the processed data back into a **segmented image**.

## Project Structure

```
.
├── CMakeLists.txt
├── src/
│   ├── include/
│   │    ├── point.hpp
│   │    ├── cluster.hpp
│   │    └── mean_shift.hpp
│   └── main.cpp
├── examples/
│   ├── sample_flower.jpg
│   └── sample_astro.jpg
├── py_utils/
│   ├── config.py
│   ├── csv_to_img.py
│   └── img_to_csv.py
├── data/
├── docs/ 
└── README.md
```

## Performance

The parallel version of the algorithm offers significant performance improvements over the sequential version, especially for large images:

| Image Size | Sequential Version | Parallel Version | Speedup |
|------------|-------------------|-----------------|---------|
| ...        | x.xx seconds      | x.xx seconds    | x.xx    |
| ...        | x.xx seconds      | x.xx seconds    | x.xx    |
| ...        | x.xx seconds      | x.xx seconds    | x.xx    |
