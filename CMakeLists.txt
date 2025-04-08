cmake_minimum_required(VERSION 3.29)
project(mean_shift_segmentation)

set(CMAKE_CXX_STANDARD 20)

add_executable(mean_shift_segmentation src/main.cpp
        src/include/timing.hpp)

