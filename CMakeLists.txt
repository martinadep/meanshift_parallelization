cmake_minimum_required(VERSION 3.13)
project(mean_shift_segmentation)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_C_STANDARD 11)

find_package(OpenMP REQUIRED)
if(OpenMP_FOUND)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${OpenMP_EXE_LINKER_FLAGS}")
endif()

# option(ENABLE_PROFILING "Enable gprof profiling instrumentation" ON)
# set(PROFILING_FLAGS -pg)

# Common source files
set(COMMON_SOURCES
    src/main.cpp
    src/kernels.c
    src/distances.c
    src/point.c)

# Create all your executables
add_executable(main 
               ${COMMON_SOURCES}
               src/mean_shift.c)
target_compile_definitions(main PRIVATE 
                TOTAL_TIMING 
                # DEBUG
                )
add_executable(main_sqrd
               ${COMMON_SOURCES}
               src/mean_shift_sqrd.c)
target_compile_definitions(main_sqrd PRIVATE 
                TOTAL_TIMING 
                # DEBUG
                )
add_executable(main_matrix
               ${COMMON_SOURCES}
               src/mean_shift_matrix.c)
target_compile_definitions(main_matrix PRIVATE 
                TOTAL_TIMING 
                # DEBUG
                )
add_executable(main_matrix_block
               ${COMMON_SOURCES}
               src/mean_shift_matrix_block.c)
target_compile_definitions(main_matrix_block PRIVATE 
                TOTAL_TIMING 
                # DEBUG
                )

add_executable(breakdown 
               ${COMMON_SOURCES}
               src/metrics/mean_shift_breakdown.c)
target_compile_definitions(breakdown PRIVATE 
                TIMING_BREAKDOWN)

add_executable(metrics 
               ${COMMON_SOURCES}
               src/metrics/mean_shift_metrics.c)

add_executable(slic
               ${COMMON_SOURCES}
               src/mean_shift.c
               src/preprocessing/slic.c)
target_compile_definitions(slic PRIVATE 
                PREPROCESSING 
                TOTAL_TIMING)

add_executable(slic_matrix
               ${COMMON_SOURCES}
               src/mean_shift_matrix.c
               src/preprocessing/slic.c)
target_compile_definitions(slic_matrix PRIVATE 
                PREPROCESSING 
                MATRIX
                TOTAL_TIMING)

add_executable(slic_sqrd
               ${COMMON_SOURCES}
               src/mean_shift_sqrd.c
               src/preprocessing/slic.c)
target_compile_definitions(slic_sqrd PRIVATE
                MEAN_SHIFT_SQRD
                PREPROCESSING
                TOTAL_TIMING)

add_executable(slic_breakdown
               ${COMMON_SOURCES}
               src/preprocessing/slic.c
               src/metrics/mean_shift_breakdown.c)
target_compile_definitions(slic_breakdown PRIVATE 
                TIMING_BREAKDOWN
                PREPROCESSING)

add_executable(slic_breakdown_sqrd
               ${COMMON_SOURCES}
               src/preprocessing/slic.c
               src/metrics/mean_shift_sqrd_breakdown.c)
target_compile_definitions(slic_breakdown_sqrd PRIVATE 
                TIMING_BREAKDOWN
                MEAN_SHIFT_SQRD
                PREPROCESSING)

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

# Lista dei target da modificare per profiling
# set(TARGETS
#     main
#     breakdown
#     metrics
#     slic
#     slic_matrix
#     slic_sqrd
#     slic_breakdown
#     slic_breakdown_sqrd
#     slic_metrics
# )

# if(ENABLE_PROFILING)
#     foreach(target ${TARGETS})
#         target_compile_options(${target} PRIVATE ${PROFILING_FLAGS})
#         target_link_options(${target} PRIVATE ${PROFILING_FLAGS})
#     endforeach()
# endif()
