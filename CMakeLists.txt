cmake_minimum_required(VERSION 3.13)
project(mean_shift_segmentation)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_C_STANDARD 11)

# ===================================================
# Globali options
# ===================================================
option(ENABLE_DEBUG "Enable debug output" OFF)
option(ENABLE_TIMING "Enable total timing measurements" ON)
option(ENABLE_OPENACC "Enable OpenACC support" OFF)

# ===================================================
# OpenMP
# ===================================================
find_package(OpenMP REQUIRED)
if(OpenMP_FOUND)
    message(STATUS "OpenMP found")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${OpenMP_EXE_LINKER_FLAGS}")
endif()

# ===================================================
# OpenACC
# ===================================================
if(ENABLE_OPENACC)
    message(STATUS "OpenACC enabled — using NVIDIA HPC compiler")
    set(CMAKE_C_COMPILER nvc)
    set(CMAKE_CXX_COMPILER nvc++)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -acc -Minfo=accel")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -acc -Minfo=accel")
endif()

# ===================================================
# Common sources
# ===================================================
set(COMMON_SOURCES
    src/main.cpp
    src/kernels.c
    src/distances.c
    src/point.c)

# ===================================================
# Function to add targets
# ===================================================
function(add_mean_shift_target TARGET_NAME MS_TYPE)
    cmake_parse_arguments(ARG "PREPROCESSING;METRICS;BREAKDOWN" "" "" ${ARGN})

    set(TARGET_SOURCES ${COMMON_SOURCES})
    set(TARGET_DEFINITIONS "")

    # Implementazione specifica
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
        if(MS_TYPE STREQUAL "BASIC")
            list(APPEND TARGET_SOURCES src/mean_shift.c)
        elseif(MS_TYPE STREQUAL "SQRD")
            list(APPEND TARGET_SOURCES src/mean_shift_variants/mean_shift_sqrd.c)
            list(APPEND TARGET_DEFINITIONS MEAN_SHIFT_SQRD)
        elseif(MS_TYPE STREQUAL "MATRIX")
            list(APPEND TARGET_SOURCES src/mean_shift_variants/mean_shift_matrix.c)
            list(APPEND TARGET_DEFINITIONS MATRIX)
        elseif(MS_TYPE STREQUAL "MATRIX_BLOCK")
            list(APPEND TARGET_SOURCES src/mean_shift_variants/mean_shift_matrix_block.c)
        elseif(MS_TYPE STREQUAL "OPENBLAS")
            list(APPEND TARGET_SOURCES src/mean_shift_variants/mean_shift_openblas.c)
            list(APPEND TARGET_DEFINITIONS MATRIX)
        endif()
    endif()

    if(ARG_PREPROCESSING)
        list(APPEND TARGET_SOURCES src/preprocessing/slic.c)
        list(APPEND TARGET_DEFINITIONS PREPROCESSING)
    endif()

    if(ENABLE_TIMING AND NOT ARG_BREAKDOWN)
        list(APPEND TARGET_DEFINITIONS TOTAL_TIMING)
    endif()

    if(ENABLE_DEBUG)
        list(APPEND TARGET_DEFINITIONS DEBUG)
    endif()

    add_executable(${TARGET_NAME} ${TARGET_SOURCES})
    target_compile_definitions(${TARGET_NAME} PRIVATE ${TARGET_DEFINITIONS})

    if(MS_TYPE STREQUAL "OPENBLAS")
        find_package(BLAS REQUIRED)
        message(${BLAS_LIBRARIES})
        target_link_libraries(${TARGET_NAME} PRIVATE ${BLAS_LIBRARIES})
    endif()

endfunction()

# ===================================================
# OpenMP targets
# ===================================================
add_mean_shift_target(mean_shift BASIC)
add_mean_shift_target(mean_shift_sqrd SQRD)
add_mean_shift_target(mean_shift_matrix MATRIX)
add_mean_shift_target(mean_shift_matrix_block MATRIX_BLOCK)

add_mean_shift_target(slic_ms BASIC PREPROCESSING)
add_mean_shift_target(slic_ms_sqrd SQRD PREPROCESSING)
add_mean_shift_target(slic_ms_matrix MATRIX PREPROCESSING)
add_mean_shift_target(slic_ms_matrix_block MATRIX_BLOCK PREPROCESSING)

find_package(BLAS QUIET)
# Only add OpenBLAS targets if BLAS is found
if(BLAS_FOUND)
    message(STATUS "BLAS found, building OpenBLAS targets")
    add_mean_shift_target(mean_shift_openblas OPENBLAS)
    add_mean_shift_target(slic_ms_openblas OPENBLAS PREPROCESSING)
else()
    message(STATUS "BLAS not found, skipping OpenBLAS targets")
endif()

add_mean_shift_target(breakdown_mean_shift BASIC BREAKDOWN)
add_mean_shift_target(metrics_mean_shift BASIC METRICS)

add_executable(breakdown_slic_ms
    src/main.cpp
    src/kernels.c
    src/distances.c
    src/point.c
    src/mean_shift.c
    src/preprocessing/slic_breakdown.c)
target_compile_definitions(breakdown_slic_ms PRIVATE TIMING_BREAKDOWN PREPROCESSING)

# ===================================================
# OpenACC targets
# ===================================================
if(ENABLE_OPENACC)
    function(add_mean_shift_acc_target TARGET_NAME)
        set(TARGET_SOURCES
            ${COMMON_SOURCES}
            src/mean_shift_acc.c)

        add_executable(${TARGET_NAME} ${TARGET_SOURCES})
        target_compile_options(${TARGET_NAME} PRIVATE -acc -Minfo=accel)
        target_compile_definitions(${TARGET_NAME} PRIVATE TOTAL_TIMING)

        if(ENABLE_DEBUG)
            target_compile_definitions(${TARGET_NAME} PRIVATE DEBUG)
        endif()
    endfunction()

    add_mean_shift_acc_target(mean_shift_acc)

    add_executable(slic_ms_acc
        ${COMMON_SOURCES}
        src/mean_shift_acc.c
        src/preprocessing/slic_acc.c)
    target_compile_options(slic_ms_acc PRIVATE -acc -Minfo=accel)
    target_compile_definitions(slic_ms_acc PRIVATE TOTAL_TIMING PREPROCESSING)

    if(ENABLE_DEBUG)
        target_compile_definitions(slic_ms_acc PRIVATE DEBUG)
    endif()
endif()

# ===================================================
# Common definitions
# ===================================================
add_compile_definitions(
    BANDWIDTH=3.0
    CSV_IN="./data/original.csv"
    CSV_OUT="./data/modified.csv"
    CSV_OUT_SLIC="./data/modified_slic.csv"
    KERNEL="epanechnikov"
    DIM=3
    T=float
    TYPENAME="float"
)
