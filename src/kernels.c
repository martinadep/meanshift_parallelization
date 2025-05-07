#include "include/utils.h"

T gaussian_kernel(T distance, unsigned int bandwidth) {
    T norm_distance = distance / bandwidth;
    return exp(-0.5 * norm_distance * norm_distance);
}

T uniform_kernel(T distance, unsigned int bandwidth) {
    T norm_dist = distance / bandwidth;
    return (norm_dist <= 1.0) ? 1.0 : 0.0;
}

T epanechnikov_kernel(T distance, unsigned int bandwidth) {
    T norm_dist = distance / bandwidth;
    return (norm_dist <= 1.0) ? (1.0 - norm_dist * norm_dist) : 0.0;
}