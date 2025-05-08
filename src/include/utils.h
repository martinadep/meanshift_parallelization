#ifndef __UTILS_H__
#define __UTILS_H__

#include <math.h>
#define T double
typedef T Point[DIM];


#ifdef __cplusplus
extern "C" {
#endif

// ------------ src/kernels.c ------------
T gaussian_kernel(T distance, unsigned int bandwidth);
T uniform_kernel(T distance, unsigned int bandwidth);
T epanechnikov_kernel(T distance, unsigned int bandwidth);

// ---------- src/distances.c ------------
T euclidean_distance(const Point *point1, const Point *point2);
T sqrd_euclidean_distance(const Point *point1, const Point *point2);

#ifdef __cplusplus
}
#endif



#endif // __UTILS_H__