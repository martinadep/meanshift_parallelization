cmake_minimum_required(VERSION 3.29)
project(mean_shift_segmentation)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_C_STANDARD 11)

add_executable(main 
               src/main.cpp)

# Compilation flags
target_compile_definitions(main PRIVATE TOTAL_TIMING)