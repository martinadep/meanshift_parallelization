#include "include/utils.h"
#include <stdio.h>

T gaussian_kernel(T distance, T bandwidth) {
    T norm_distance = distance / bandwidth;
    return exp(-0.5 * norm_distance * norm_distance);
}
#pragma acc routine seq
T uniform_kernel(T distance, T bandwidth) {
    return (distance <= bandwidth) ? 1.0 : 0.0;
}
#pragma acc routine seq
T epanechnikov_kernel(T distance, T bandwidth) {
    if (distance <= bandwidth) {
        T u = distance / bandwidth;
        return 0.75 * (1.0 - u * u);  // 3/4 = 0.75
    } else {
        return 0.0;
    }
}


// --------- Square distance version of kernel functions -----------
T gaussian_kernel_sqrd(T distance_sqrd, T bandwidth_sqrd) {
    T norm_distance = distance_sqrd / bandwidth_sqrd; 
    return exp(-0.5 * norm_distance);
}

T uniform_kernel_sqrd(T distance_sqrd, T bandwidth_sqrd) {
    return (distance_sqrd <= bandwidth_sqrd) ? 1.0 : 0.0;
}

T epanechnikov_kernel_sqrd(T distance_sqrd, T bandwidth_sqrd) {
    if (distance_sqrd <= bandwidth_sqrd) {
        T u2 = distance_sqrd / bandwidth_sqrd;
        return 0.75 * (1.0 - u2); 
    } else {
        return 0.0;
    }
}