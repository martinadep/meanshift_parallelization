#ifndef __UTILS_HPP__
#define __UTILS_HPP__

#define BANDWIDTH 10.0
#define CSV_IN "./data/original.csv";
#define CSV_OUT "./data/modified.csv";
#define KERNEL "uniform"

#define DEBUG
#define MS_TIMING
//#define WEIGHT_DEBUG
//#define TIMING

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

// ---------- distances ------------
template<typename T>
T euclidean_distance(const Point<T> &point1, const Point<T> &point2) {
    if (point1.coords.size() != point2.coords.size()) {
        cout << "Error: points have different dimensions." << endl;
        return -1;
    }
    T distance = 0;
    for (unsigned int i = 0; i < point1.coords.size(); i++) {
        distance += (point1.coords[i] - point2.coords[i]) *
                    (point1.coords[i] - point2.coords[i]);
    }
    return sqrt(distance);
}
template<typename T>
T sqrd_euclidean_distance(const Point<T> &point1, const Point<T> &point2) {
    if (point1.coords.size() != point2.coords.size()) {
        cout << "Error: points have different dimensions." << endl;
        return -1;
    }
    T distance = 0;
    for (unsigned int i = 0; i < point1.coords.size(); i++) {
        distance += (point1.coords[i] - point2.coords[i]) *
                    (point1.coords[i] - point2.coords[i]);
    }
    return distance;
}

// ---------- timing -----------

#ifdef TIMING

#include <chrono>
#define TIMER_DEF(label) \
    std::chrono::high_resolution_clock::time_point start_##label, end_##label; \
    double duration_##label = 0.0;
#define TIMER_START(label) start_##label = std::chrono::high_resolution_clock::now();   
#define TIMER_ELAPSED(label)                  \
    end_##label = std::chrono::high_resolution_clock::now(); \
    duration_##label = std::chrono::duration<double>(end_##label - start_##label).count();
#define TIMER_PRINT(label)                    \
    std::cout << #label << " execution time: " << duration_##label << " s" << std::endl;

#define TIMER_SUM_DEF(label)                  \
    TIMER_DEF(label)                          \
    double total_##label##_time = 0.0;
#define TIMER_SUM(label)                      \
    TIMER_ELAPSED(label)                      \
    total_##label##_time += duration_##label; 
#define TIMER_SUM_PRINT(label)                \
    std::cout << #label << " total execution time: " << total_##label##_time << " s" << std::endl;

#else
#define TIMER_DEF(label)
#define TIMER_START(label)
#endif

#ifdef MS_TIMING
#define TIMER_START(label) \
    std::chrono::high_resolution_clock::time_point start_##label, end_##label; \
    double duration_##label = 0.0; \
    start_##label = std::chrono::high_resolution_clock::now();  
    
#define TIMER_STOP(label)                  \
    end_##label = std::chrono::high_resolution_clock::now(); \
    duration_##label = std::chrono::duration<double>(end_##label - start_##label).count(); \
    std::cout << #label << " execution time: " << duration_##label << " s" << std::endl;
#endif

#endif //__UTILS_HPP__
