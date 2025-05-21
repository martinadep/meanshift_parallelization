#include "../include/point.h"
#include "../include/utils.h"
#include "../include/mean_shift.h"
#include "timing.h"
#include <stdio.h>
#include <stdlib.h>

// Move a single point towards the maximum density area
void shift_single_point(const Point *point, Point *next_point,
                              const Point dataset[], unsigned int dataset_size,
                              unsigned int bandwidth, T (*kernel_func)(T, unsigned int)) {
    T total_weight = 0;
    Point point_i;
    init_point(&point_i); // xi
    init_point(next_point); // x'

    for (int i = 0; i < dataset_size; i++) {
        copy_point(&dataset[i], &point_i); // xi = dataset[i]
#ifdef TIMING_BREAKDOWN
        TIMER_START(distance_mode_find)
#endif
        T distance = euclidean_distance(point, &point_i); // x - xi
#ifdef TIMING_BREAKDOWN
        TIMER_SUM(distance_mode_find)
        TIMER_START(kernel)
#endif
        T weight = kernel_func(distance, bandwidth); // K(x - xi / h)
#ifdef TIMING_BREAKDOWN
        TIMER_SUM(kernel)
        TIMER_START(coords_update)
#endif
        // x' = x' + xi * K(x - xi / h)
        for (int j = 0; j < DIM; j++) {
            (*next_point)[j] += point_i[j] * weight;
        }
#ifdef TIMING_BREAKDOWN
        TIMER_SUM(coords_update)
#endif
        total_weight += weight; // total weight of all points with respect to [point]
    }

    if (total_weight > 0) {
        // normalization
        divide_point(next_point, total_weight); // x' = x' / sum(K(x - xi / h))
    } else {
        fprintf(stderr, "Error: total_weight == 0, couldn't normalize.\n");
    }
}

// Assign clusters to shifted points
void assign_clusters(Point *shifted_point, Point cluster_modes[],
                           unsigned int *cluster_count) {
    int c = 0;
    for (; c < *cluster_count; c++) {
#ifdef TIMING_BREAKDOWN
        TIMER_START(distance_cluster)
#endif
        T distance_from_cluster = euclidean_distance(shifted_point, &cluster_modes[c]);
#ifdef TIMING_BREAKDOWN
        TIMER_SUM(distance_cluster)
#endif
        if (distance_from_cluster <= CLUSTER_EPSILON) {
            copy_point(&cluster_modes[c], shifted_point); // assign cluster mode to shifted point
            break;
        }
    }
    // Whenever [shifted_point] doesn't belong to any cluster:
    // --> create cluster with mode in [shifted_point]
    if (c == *cluster_count) {
        copy_point(shifted_point, &cluster_modes[c]); // assign cluster mode to shifted point
        (*cluster_count)++;
#ifdef DEBUG
        printf("Cluster found! \t\t Number of clusters: %u\n", *cluster_count);
#endif
    }
}

// Perform the mean shift clustering
void mean_shift(unsigned int dataset_size, const Point dataset[],
                      Point shifted_dataset[], unsigned int bandwidth,
                      T (*kernel_func)(T, unsigned int), Point cluster_modes[],
                      unsigned int *cluster_count) {
    Point prev_point;
    Point next_point;
    unsigned int iter;
    int stop_moving; // flag to check if each point has converged

    // Shift each point
    for (int i = 0; i < dataset_size; i++) {
        stop_moving = 0; // reset for each point
        iter = 0;
#ifdef DEBUG
        if (i % 500 == 0) {
            printf("points [%d/%u] ...\n", i, dataset_size);
        }
#endif
        copy_point(&dataset[i], &prev_point);

        // Shift until convergence
        while (!stop_moving) {
            shift_single_point(&prev_point, &next_point, dataset, dataset_size, bandwidth, kernel_func);

#ifdef TIMING_BREAKDOWN
            TIMER_START(distance_shift)
#endif
            T shift_distance = euclidean_distance(&prev_point, &next_point);
#ifdef TIMING_BREAKDOWN
            TIMER_SUM(distance_shift)
#endif
            if (shift_distance <= EPSILON) {
                stop_moving = 1;
            }
            copy_point(&next_point, &prev_point);
            iter++;
        }
        copy_point(&next_point, &shifted_dataset[i]);

        assign_clusters(&shifted_dataset[i], cluster_modes, cluster_count); // assign clusters to shifted points
    }

#ifdef TIMING_BREAKDOWN
    TIMER_SUM_PRINT(coords_update)
    TIMER_SUM_PRINT(kernel)
    TIMER_SUM_PRINT(distance_shift)
    TIMER_SUM_PRINT(distance_mode_find)
    TIMER_SUM_PRINT(distance_cluster)
#endif
}
