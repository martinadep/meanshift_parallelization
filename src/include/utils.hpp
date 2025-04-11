#ifndef __UTILS_HPP__
#define __UTILS_HPP__

#define BANDWIDTH 10.0
#define CSV_IN "./data/original.csv";
#define CSV_OUT "./data/modified.csv";
#define KERNEL "uniform"

#define TIMING

using namespace std;

template<typename T>

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
#endif //__UTILS_HPP__
