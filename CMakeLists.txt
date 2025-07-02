cmake_minimum_required(VERSION 3.13)
project(mean_shift_segmentation LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_C_STANDARD 11)

# Find OpenMP
find_package(OpenMP REQUIRED)
if(OpenMP_FOUND)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${OpenMP_EXE_LINKER_FLAGS}")
endif()

# Common source files (excluding the mean-shift implementations)
set(COMMON_SOURCES
    src/main.cpp
    src/kernels.c
    src/distances.c
    src/point.c)

# Define global compilation options
option(ENABLE_DEBUG "Enable debug output" OFF)
option(ENABLE_TIMING "Enable total timing measurements" ON)

# Create mean-shift targets with consistent settings
function(add_mean_shift_target TARGET_NAME MS_TYPE)
    cmake_parse_arguments(ARG "PREPROCESSING;METRICS;BREAKDOWN" "" "" ${ARGN})
    
    set(TARGET_SOURCES ${COMMON_SOURCES})
    set(TARGET_DEFINITIONS "")
    
    # Add mean-shift implementation based on type and breakdown/metrics options
    if(ARG_BREAKDOWN)
        if(MS_TYPE STREQUAL "SQRD")
            list(APPEND TARGET_SOURCES src/metrics/mean_shift_sqrd_breakdown.c)
            list(APPEND TARGET_DEFINITIONS MEAN_SHIFT_SQRD TIMING_BREAKDOWN)
        else()
            list(APPEND TARGET_SOURCES src/metrics/mean_shift_breakdown.c)
            list(APPEND TARGET_DEFINITIONS TIMING_BREAKDOWN)
        endif()
    elseif(ARG_METRICS)
        list(APPEND TARGET_SOURCES src/metrics/mean_shift_metrics.c)
    else()
        # Only add the base implementation if we're not using a special one
        if(MS_TYPE STREQUAL "BASIC")
            list(APPEND TARGET_SOURCES src/mean_shift.c)
        elseif(MS_TYPE STREQUAL "SQRD")
            list(APPEND TARGET_SOURCES src/mean_shift_sqrd.c)
            list(APPEND TARGET_DEFINITIONS MEAN_SHIFT_SQRD)
        elseif(MS_TYPE STREQUAL "MATRIX")
            list(APPEND TARGET_SOURCES src/mean_shift_matrix.c)
            list(APPEND TARGET_DEFINITIONS MATRIX)
        elseif(MS_TYPE STREQUAL "OPENBLAS")
            list(APPEND TARGET_SOURCES src/mean_shift_openblas.c)
            list(APPEND TARGET_DEFINITIONS MATRIX)
        elseif(MS_TYPE STREQUAL "MATRIX_BLOCK")
            list(APPEND TARGET_SOURCES src/mean_shift_matrix_block.c)
        endif()
    endif()
    
    # Add preprocessing if requested
    if(ARG_PREPROCESSING)
        list(APPEND TARGET_SOURCES src/preprocessing/slic.c)
        list(APPEND TARGET_DEFINITIONS PREPROCESSING)
    endif()
    
    # Add timing if enabled globally and not using breakdown
    if(ENABLE_TIMING AND NOT ARG_BREAKDOWN)
        list(APPEND TARGET_DEFINITIONS TOTAL_TIMING)
    endif()
    
    # Add debug if enabled globally
    if(ENABLE_DEBUG)
        list(APPEND TARGET_DEFINITIONS DEBUG)
    endif()
    
    # Create the executable
    add_executable(${TARGET_NAME} ${TARGET_SOURCES})
    target_compile_definitions(${TARGET_NAME} PRIVATE ${TARGET_DEFINITIONS})

    if(MS_TYPE STREQUAL "OPENBLAS")
        find_package(BLAS REQUIRED)
        message(${BLAS_LIBRARIES})
        target_link_libraries(${TARGET_NAME} PRIVATE ${BLAS_LIBRARIES})
    endif()
endfunction()


# Create all the executables using the function
# --- Basic MeanShift targets ---
add_mean_shift_target(mean_shift BASIC)
add_mean_shift_target(mean_shift_sqrd SQRD)
add_mean_shift_target(mean_shift_matrix MATRIX)
add_mean_shift_target(mean_shift_matrix_block MATRIX_BLOCK)

# --- SLIC-MeanShift targets ---
add_mean_shift_target(slic_ms BASIC PREPROCESSING)
add_mean_shift_target(slic_ms_sqrd SQRD PREPROCESSING)
add_mean_shift_target(slic_ms_matrix MATRIX PREPROCESSING)
add_mean_shift_target(slic_ms_matrix_block MATRIX_BLOCK PREPROCESSING)
add_mean_shift_target(slic_ms_openblas OPENBLAS PREPROCESSING)

add_mean_shift_target(breakdown_mean_shift BASIC BREAKDOWN)
add_mean_shift_target(metrics_mean_shift BASIC METRICS)

add_executable(breakdown_slic_ms 
               src/main.cpp
               src/kernels.c
               src/distances.c
               src/point.c
               src/mean_shift.c
               src/preprocessing/slic_breakdown.c)
target_compile_definitions(breakdown_slic_ms PRIVATE 
                TIMING_BREAKDOWN
                PREPROCESSING)

# Common definitions for all targets
add_compile_definitions( 
    BANDWIDTH=3.0
    CSV_IN="./data/original.csv"
    CSV_OUT="./data/modified.csv"
    CSV_OUT_SLIC="./data/modified_slic.csv"
    KERNEL="gaussian"
    DIM=3
    T=float
    TYPENAME="float"
)  