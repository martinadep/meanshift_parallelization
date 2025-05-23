cmake_minimum_required(VERSION 3.29)
project(mean_shift_segmentation)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_C_STANDARD 11)

# Common source files
set(COMMON_SOURCES
    src/main.cpp
    src/kernels.c
    src/distances.c
    src/point.c)

# Sequential version
add_executable(main 
               ${COMMON_SOURCES}
               src/mean_shift.c)
target_compile_definitions(main PRIVATE TOTAL_TIMING) #DEBUG)

# Breakdown version
add_executable(breakdown 
               ${COMMON_SOURCES}
               src/metrics/mean_shift_breakdown.c)
target_compile_definitions(breakdown PRIVATE TIMING_BREAKDOWN)

# Metrics version
add_executable(metrics 
               ${COMMON_SOURCES}
               src/metrics/mean_shift_metrics.c)

# SLIC version
add_executable(slic
               ${COMMON_SOURCES}
               src/mean_shift.c
               src/preprocessing/slic.c)
target_compile_definitions(slic PRIVATE 
                PREPROCESSING 
                TOTAL_TIMING
                NUM_SUPERPIXELS=1000)

# SLIC with metrics
add_executable(slic_metrics_double
               ${COMMON_SOURCES}
               src/metrics/mean_shift_metrics.c
               src/preprocessing/slic.c)
target_compile_definitions(slic_metrics_double PRIVATE 
                PREPROCESSING 
                TOTAL_TIMING
                NUM_SUPERPIXELS=1000)

add_compile_definitions( 
    BANDWIDTH=10.0
    CSV_IN="./data/original.csv"
    CSV_OUT="./data/modified.csv"
    CSV_OUT_SLIC="./data/modified_slic.csv"
    KERNEL="uniform"
    DIM=3
    T=double
    TYPENAME="double"
)
