#include "include/utils.h"
#include <stdio.h>

// Kernel functions for Mean Shift algorithm
T gaussian_kernel(T distance, T bandwidth) {
    T norm_distance = distance / bandwidth;
    return exp(-0.5 * norm_distance * norm_distance);
}
T uniform_kernel(T distance, T bandwidth) {
    return (distance <= bandwidth) ? 1.0 : 0.0;
}

T epanechnikov_kernel(T distance, T bandwidth) {
    T norm_dist = distance / bandwidth;
    return (norm_dist <= 1.0) ? (1.0 - norm_dist * norm_dist) : 0.0;
}


// Square distance version of kernel functions
T gaussian_kernel_sqrd(T distance_sqrd, T bandwidth_sqrd) {
    T norm_distance = distance_sqrd / bandwidth_sqrd; 
    return exp(-0.5 * norm_distance);
}

T uniform_kernel_sqrd(T distance_sqrd, T bandwidth_sqrd) {
    return (distance_sqrd <= bandwidth_sqrd) ? 1.0 : 0.0;
}

// (norm_distance)^2 = distance_sqrd / bandwidth_sqrd <= 1.0 
// is equivalent to distance_sqrd <= bandwidth_sqrd
T epanechnikov_kernel_sqrd(T distance_sqrd, T bandwidth_sqrd) {
    if (distance_sqrd <= bandwidth_sqrd) {
        return 1.0 - (distance_sqrd / bandwidth_sqrd);
    } else {
        return 0.0;
    }
}