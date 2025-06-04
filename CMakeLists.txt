cmake_minimum_required(VERSION 3.12)
project(mean_shift_segmentation)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_C_STANDARD 11)

# Common source files
set(COMMON_SOURCES
    src/main.cpp
    src/kernels.c
    src/distances.c
    src/point.c)

# Mean-Shift base version
add_executable(main 
               ${COMMON_SOURCES}
               src/mean_shift.c)
target_compile_definitions(main PRIVATE 
                TOTAL_TIMING 
                DEBUG)

# Mean-Shift Breakdown version
add_executable(breakdown 
               ${COMMON_SOURCES}
               src/metrics/mean_shift_breakdown.c)
target_compile_definitions(breakdown PRIVATE 
                TIMING_BREAKDOWN)

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
                TOTAL_TIMING)

# SLIC with matrix
add_executable(slic_matrix
               ${COMMON_SOURCES}
               src/mean_shift_matrix.c
               src/preprocessing/slic.c)

target_compile_definitions(slic_matrix PRIVATE 
                PREPROCESSING 
                MATRIX
                TOTAL_TIMING)

# SLIC with Mean-Shift squared distance
add_executable(slic_sqrd
               ${COMMON_SOURCES}
               src/mean_shift_sqrd.c
               src/preprocessing/slic.c)

target_compile_definitions(slic_sqrd PRIVATE
                MEAN_SHIFT_SQRD
                PREPROCESSING
                TOTAL_TIMING)

# Mean-Shift Breakdown version
add_executable(slic_breakdown
               ${COMMON_SOURCES}
               src/preprocessing/slic.c
               src/metrics/mean_shift_breakdown.c)
target_compile_definitions(slic_breakdown PRIVATE 
                TIMING_BREAKDOWN
                PREPROCESSING)
# SLIC with Mean-Shift squared distance Breakdown version
add_executable(slic_breakdown_sqrd
               ${COMMON_SOURCES}
               src/preprocessing/slic.c
               src/metrics/mean_shift_sqrd_breakdown.c)
target_compile_definitions(slic_breakdown_sqrd PRIVATE 
                TIMING_BREAKDOWN
                MEAN_SHIFT_SQRD
                PREPROCESSING)

# SLIC with metrics
add_executable(slic_metrics
               ${COMMON_SOURCES}
               src/metrics/mean_shift_metrics.c
               src/preprocessing/slic.c)
target_compile_definitions(slic_metrics PRIVATE 
                PREPROCESSING 
                TOTAL_TIMING)

add_compile_definitions( 
    BANDWIDTH=3.0
    CSV_IN="./data/original.csv"
    CSV_OUT="./data/modified.csv"
    CSV_OUT_SLIC="./data/modified_slic.csv"
    KERNEL="gaussian"
    DIM=3
    T=double
    TYPENAME="double"
)
