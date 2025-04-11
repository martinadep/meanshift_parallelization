#ifndef __UTILS_HPP__
#define __UTILS_HPP__

#define BANDWIDTH 10.0
#define CSV_IN "./data/original.csv";
#define CSV_OUT "./data/modified.csv";
#define KERNEL "uniform"

//#define DEBUG
//#define WEIGHT_DEBUG
#define TIMING

using namespace std;

template<typename T>

// ------- kernel functions ---------
T gaussian_kernel(T distance, unsigned int bandwidth) {
    T norm_distance = distance / bandwidth;
    return exp(-0.5 * norm_distance * norm_distance);
}

template<typename T>
T uniform_kernel(T distance, unsigned int bandwidth) {
    T norm_dist = distance / bandwidth;
    return (norm_dist <= 1.0) ? 1.0 : 0.0;
}

template<typename T>
T epanechnikov_kernel(T distance, unsigned int bandwidth) {
    T norm_dist = distance / bandwidth;
    return (norm_dist <= 1.0) ? (1.0 - norm_dist * norm_dist) : 0.0;
}

// ---------- timing -----------

#ifdef TIMING

#include <chrono>
#define START_TIME(label) auto start_##label = std::chrono::high_resolution_clock::now();

#define END_TIME(label)                                                                 \
    auto end_##label = std::chrono::high_resolution_clock::now();                      \
    auto duration_##label = std::chrono::duration<double>(end_##label - start_##label).count(); \
    std::cout << #label << " execution time: " << duration_##label << " s" << std::endl;

#define SUM_TIME(label)                                                                 \
    auto end_##label = std::chrono::high_resolution_clock::now();                      \
    auto duration_##label = std::chrono::duration<double>(end_##label - start_##label).count(); \
    total_##label##_time += duration_##label; \

#else
#define START_TIME(label)
#define END_TIME(label)
#endif

#endif //__UTILS_HPP__
