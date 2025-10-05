#ifndef __UTILS_H__
#define __UTILS_H__

#include <math.h>
#ifndef T
#define T float
#define TYPENAME "float"
#endif
typedef struct {
    T coords[DIM];
} Point;

#ifdef __cplusplus
extern "C" {
#endif

// ------------ src/kernels.c ------------
#pragma acc routine seq
T gaussian_kernel(T distance, T bandwidth);
#pragma acc routine seq
T uniform_kernel(T distance, T bandwidth);
#pragma acc routine seq
T epanechnikov_kernel(T distance, T bandwidth);

T gaussian_kernel_sqrd(T distance_sqrd, T bandwidth_sqrd);
T uniform_kernel_sqrd(T distance_sqrd, T bandwidth_sqrd);
T epanechnikov_kernel_sqrd(T distance_sqrd, T bandwidth_sqrd);

// ---------- src/distances.c ------------
#pragma acc routine seq
T euclidean_distance(const Point *point1, const Point *point2);
T sqrd_euclidean_distance(const Point *point1, const Point *point2);

void parse_args(int argc, char *argv[]);

#ifdef __cplusplus
}
#endif



#endif // __UTILS_H__