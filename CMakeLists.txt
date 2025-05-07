cmake_minimum_required(VERSION 3.29)
project(mean_shift_segmentation)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_C_STANDARD 11)

add_executable(main 
               src/main.cpp
               src/kernels.c
               src/distances.c
               src/mean_shift.c
               src/point.c)
# Compilation flags
target_compile_definitions(main PRIVATE TOTAL_TIMING)


add_executable(breakdown 
               src/main.cpp
               src/kernels.c
               src/distances.c
               src/timing/mean_shift_breakdown.c
               src/point.c)
# Compilation flags
target_compile_definitions(breakdown PRIVATE TIMING_BREAKDOWN)

add_compile_definitions( 
    BANDWIDTH=10.0
    CSV_IN="./data/original.csv"
    CSV_OUT="./data/modified.csv"
    KERNEL="uniform"
    DIM=3
)