#include "include/point.h"
#include "include/utils.h"
#include "include/mean_shift.h"
#include <stdio.h>
#include <stdlib.h>

void mean_shift(unsigned int dataset_size, const Point dataset[],
                Point shifted_dataset[], unsigned int bandwidth,
                T (*kernel_func)(T, unsigned int), Point cluster_modes[],
                unsigned int *cluster_count)
{

    // Phase 1: Independent point shifting - parallelizable
    for (int i = 0; i < dataset_size; i++){
        shift_point_until_convergence(&dataset[i], &shifted_dataset[i],
                                      dataset, dataset_size, bandwidth, kernel_func);
#ifdef DEBUG
        if (i % 500 == 0)
            printf("Shifted %d/%d points... \n", i, dataset_size);
#endif
    }

    // Phase 2: Cluster assignment - requires synchronization when parallelized
    for (int i = 0; i < dataset_size; i++){
        assign_clusters(&shifted_dataset[i], cluster_modes, cluster_count);
    }
}

// Convergence loop for a single point
unsigned int shift_point_until_convergence(const Point *input_point, Point *output_point,
                                   const Point dataset[], unsigned int dataset_size,
                                   unsigned int bandwidth, T (*kernel_func)(T, unsigned int))
{
    Point prev_point;
    Point next_point;
    unsigned int iter = 0;
    int stop_moving = 0;

    copy_point(input_point, &prev_point);

    // Shift until convergence
    while (!stop_moving)
    {
        shift_single_point(&prev_point, &next_point, dataset, dataset_size, bandwidth, kernel_func);

        T shift_distance = euclidean_distance(&prev_point, &next_point);

        if (shift_distance <= EPSILON)
        {
            stop_moving = 1;
        }
        copy_point(&next_point, &prev_point);
        iter++;
    }
    copy_point(&prev_point, output_point);
    return iter;
}

// Move a single point towards the maximum density area
void shift_single_point(const Point *point, Point *next_point,
                        const Point dataset[], unsigned int dataset_size,
                        unsigned int bandwidth, T (*kernel_func)(T, unsigned int))
{
    T total_weight = 0;
    Point point_i;
    init_point(&point_i);   // xi
    init_point(next_point); // x'

    for (int i = 0; i < dataset_size; i++)
    {
        copy_point(&dataset[i], &point_i);                     // xi = dataset[i]
        T distance = euclidean_distance(point, &point_i); // x - xi

        T weight = kernel_func(distance, bandwidth); // K(x - xi / h)

        // x' = x' + xi * K(x - xi / h)
        for (int j = 0; j < DIM; j++)
        {
            (*next_point)[j] += point_i[j] * weight;
        }

        total_weight += weight; // total weight of all points with respect to [point]
    }

    if (total_weight > 0)
    {
        // normalization
        divide_point(next_point, total_weight); // x' = x' / sum(K(x - xi / h))
    }
    else
    {
        fprintf(stderr, "Error: total_weight == 0, couldn't normalize.\n");
    }
}

// Assign clusters to shifted points
void assign_clusters(Point *shifted_point, Point cluster_modes[],
                     unsigned int *cluster_count)
{
    int c = 0;
    for (; c < *cluster_count; c++)
    {

        T distance_from_cluster = euclidean_distance(shifted_point, &cluster_modes[c]);

        if (distance_from_cluster <= CLUSTER_EPSILON)
        {
            copy_point(&cluster_modes[c], shifted_point); // assign cluster mode to shifted point
            break;
        }
    }
    // Whenever [shifted_point] doesn't belong to any cluster:
    // --> create cluster with mode in [shifted_point]
    if (c == *cluster_count)
    {
        copy_point(shifted_point, &cluster_modes[c]); // assign cluster mode to shifted point
        (*cluster_count)++;
    }
}
