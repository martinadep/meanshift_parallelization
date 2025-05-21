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
target_compile_definitions(main PRIVATE TOTAL_TIMING DEBUG)

# Breakdown version
add_executable(breakdown 
               ${COMMON_SOURCES}
               src/metrics/mean_shift_breakdown.c)
target_compile_definitions(breakdown PRIVATE TIMING_BREAKDOWN)

add_executable(metrics 
               ${COMMON_SOURCES}
               src/metrics/mean_shift_metrics.c)

# Prepare for future parallel version
# (Uncomment when ready to parallelize)
#add_executable(parallel_main
#               ${COMMON_SOURCES}
#               src/parallel/mean_shift_parallel.c)
#target_compile_definitions(parallel_main PRIVATE TOTAL_TIMING PARALLEL)

add_compile_definitions( 
    BANDWIDTH=10.0
    CSV_IN="./data/original.csv"
    CSV_OUT="./data/modified.csv"
    KERNEL="uniform"
    DIM=3
    T=float
    TYPENAME="float"
)