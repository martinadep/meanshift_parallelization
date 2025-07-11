#ifndef __MEAN_SHIFT_H__
#define __MEAN_SHIFT_H__

#include "point.h"
#include "utils.h"
#include <stdio.h>
#include <stdlib.h>

#ifdef TIMING_BREAKDOWN
    #include "../metrics/timing.h"
    TIMER_SUM_DEF(kernel)
    TIMER_SUM_DEF(distance_shift)
    TIMER_SUM_DEF(coords_update)
    TIMER_SUM_DEF(distance_mode_find)
    TIMER_SUM_DEF(distance_cluster)
#endif

#ifndef BANDWIDTH
    #define BANDWIDTH 10
#endif
#ifndef EPSILON
#ifdef PREPROCESSING
    #define EPSILON 0.5
#else
    #define EPSILON 2.0
#endif
#endif


#ifndef CLUSTER_EPSILON
#ifdef PREPROCESSING
    #define CLUSTER_EPSILON 4.5
#else
    #define CLUSTER_EPSILON 20 // suggested: bandwidth * 1.5
#endif
#endif
#define MAX_CLUSTERS 1000 // maximum number of clusters

#ifdef __cplusplus
extern "C" {
#endif


// Move a single point towards the maximum density area
#pragma acc routine seq
void shift_single_point_acc(const Point *point, Point *next_point,
                              const Point dataset[], unsigned int dataset_size,
                              T bandwidth);

void shift_single_point(const Point *point, Point *next_point,
                              const Point dataset[], unsigned int dataset_size,
                              T bandwidth, T (*kernel_func)(T, T));
// Assign clusters to shifted points
void assign_clusters(Point *shifted_point, Point cluster_modes[],
                           unsigned int *cluster_count);

// Perform the mean shift clustering
void mean_shift(unsigned int dataset_size, const Point dataset[],
                      Point shifted_dataset[], T bandwidth,
                      T (*kernel_func)(T, T), Point cluster_modes[],
                      unsigned int *cluster_count);

#pragma acc routine seq
unsigned int shift_point_until_convergence_acc(const Point *input_point, Point *output_point,
                      const Point dataset[], unsigned int dataset_size,
                      T bandwidth);

unsigned int shift_point_until_convergence(const Point *input_point, Point *output_point,
                      const Point dataset[], unsigned int dataset_size,
                      T bandwidth, T (*kernel_func)(T, T));


// Move a single point towards the maximum density area
// void shift_single_point_sqrd(const Point *point, Point *next_point,
//                               const Point dataset[], unsigned int dataset_size,
//                               T bandwidth, T (*kernel_func)(T, T));

// Assign clusters to shifted points
// void assign_clusters_sqrd(Point *shifted_point, Point cluster_modes[],
//                            unsigned int *cluster_count);

// unsigned int shift_point_until_convergence_sqrd(const Point *input_point, Point *output_point,
//                     const Point dataset[], unsigned int dataset_size,
//                     T bandwidth_sqrd, T (*kernel_func)(T, T));

void mean_shift_matrix(unsigned int dataset_size, const Point dataset[],
                    Point shifted_dataset[], T bandwidth,
                    T (*kernel_func)(T, T), Point cluster_modes[],
                    unsigned int *cluster_count);


#ifdef __cplusplus
}
#endif
#endif // __MEAN_SHIFT_H__