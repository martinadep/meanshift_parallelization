#ifndef __UTILS_H__
#define __UTILS_H__

#include <math.h>
#include <stdio.h>
#include <time.h>

#define BANDWIDTH 10.0
#define CSV_IN "./data/original.csv"
#define CSV_OUT "./data/modified.csv"
#define KERNEL "uniform"
#define DIM 3 // RGB

#define T double
typedef T Point[DIM];

// ------- kernel functions ---------
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

// ---------- distances ------------
T euclidean_distance(const Point *point1, const Point *point2) {
    T distance = 0;
    for (unsigned int i = 0; i < DIM; i++) {
        distance += ((*point1)[i] - (*point2)[i]) * ((*point1)[i] - (*point2)[i]);
    }
    return sqrt(distance);
}

T sqrd_euclidean_distance(const Point *point1, const Point *point2) {
    T distance = 0;
    for (unsigned int i = 0; i < DIM; i++) {
        distance += ((*point1)[i] - (*point2)[i]) * ((*point1)[i] - (*point2)[i]);
    }
    return distance;
}

// ---------- timing -----------

#ifdef TIMING_BREAKDOWN
#define TIMER_DEF(label) clock_t start_##label, end_##label;
#define TIMER_START(label) start_##label = clock();
#define TIMER_ELAPSED(label) end_##label = clock();
#define TIMER_PRINT(label) \
    printf(#label " execution time: %f s\n", (double)(end_##label - start_##label) / CLOCKS_PER_SEC);
#else
#define TIMER_DEF(label)
#define TIMER_START(label)
#define TIMER_ELAPSED(label)
#define TIMER_PRINT(label)
#endif

#ifdef TOTAL_TIMING

#define TOTAL_TIMER_START(label) \
    clock_t start_##label, end_##label; \
    double duration_##label = 0.0; \
    start_##label = clock();

#define TOTAL_TIMER_STOP(label) \
    end_##label = clock(); \
    duration_##label = ((double)(end_##label - start_##label)) / CLOCKS_PER_SEC; \
    printf(#label " execution time: %f s\n", duration_##label);

#endif

#endif // __UTILS_H__