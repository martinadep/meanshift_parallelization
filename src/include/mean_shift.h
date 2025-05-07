#ifndef __MEAN_SHIFT_H__
#define __MEAN_SHIFT_H__

#include "point.h"
#include "utils.h"
#include <stdio.h>
#include <stdlib.h>

#ifdef TIMING_BREAKDOWN
    #include "../timing/timing.h"
    TIMER_SUM_DEF(kernel)
    TIMER_SUM_DEF(distance_shift)
    TIMER_SUM_DEF(coords_update)
    TIMER_SUM_DEF(distance_mode_find)
    TIMER_SUM_DEF(distance_cluster)
#endif

#define EPSILON 2.0
#define CLUSTER_EPSILON 50 // suggested: bandwidth * 1.5
#define MAX_ITER 50
#define MAX_CLUSTERS 1000 // maximum number of clusters

#ifdef __cplusplus
extern "C" {
#endif


// Move a single point towards the maximum density area
void shift_single_point(const Point *point, Point *next_point,
                              const Point dataset[], unsigned int dataset_size,
                              unsigned int bandwidth, double (*kernel_func)(double, unsigned int));

// Assign clusters to shifted points
void assign_clusters(Point *shifted_point, Point cluster_modes[],
                           unsigned int *cluster_count);

// Perform the mean shift clustering
void mean_shift(unsigned int dataset_size, const Point dataset[],
                      Point shifted_dataset[], unsigned int bandwidth,
                      double (*kernel_func)(double, unsigned int), Point cluster_modes[],
                      unsigned int *cluster_count);



#ifdef __cplusplus
}
#endif
#endif // __MEAN_SHIFT_H__