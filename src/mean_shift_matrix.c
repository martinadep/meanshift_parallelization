#include "include/point.h"
#include "include/utils.h"
#include "include/mean_shift.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <omp.h>

// 8GB RAM using 4 bytes per float (T)
#define MAX_DATASET_SIZE 100000 // Define a maximum dataset size for safety

// Matrix-based implementation of Mean Shift algorithm
void mean_shift(unsigned int dataset_size, const Point dataset[],
                Point shifted_dataset[], T bandwidth,
                T (*kernel_func)(T, T), Point cluster_modes[],
                unsigned int *cluster_count)
{
    if (dataset_size > MAX_DATASET_SIZE) {
        fprintf(stderr, "Error: dataset_size exceeds MAX_DATASET_SIZE (%d)\n", MAX_DATASET_SIZE);
        return;
    }
    T* distances = (T*)malloc(dataset_size * dataset_size * sizeof(T));
    T* weights = (T*)malloc(dataset_size * dataset_size * sizeof(T));
    T* weight_sums = (T*)malloc(dataset_size * sizeof(T));
    
    Point* next_points = (Point*)malloc(dataset_size * sizeof(Point)); // Matrix of next points
    
    if (!distances || !weights || !weight_sums || !next_points) {
        fprintf(stderr, "Error: Memory allocation failed in mean_shift_matrix\n");
        goto cleanup;
    }
    
    #pragma omp parallel
    {
        #pragma omp master
        {
            printf("Running matrix implementation with %d threads\n", omp_get_num_threads());
        }
    }

    #pragma omp parallel for
    for (unsigned int i = 0; i < dataset_size; i++) {
        // copy_point(&dataset[i], &current_points[i]); // Initialize current points with the dataset
        copy_point(&dataset[i], &shifted_dataset[i]);
    }
    
    *cluster_count = 0;
    
    // Iterate until convergence or max iterations
    unsigned int iter = 0;
    T shift_norm = INFINITY;
    const unsigned int MAX_ITER = 50;
    const T TOLERANCE = EPSILON;
    
    while (iter < MAX_ITER && shift_norm > TOLERANCE) {
        shift_norm = 0.0;
        
        // Compute all pairwise distances 
        #pragma omp parallel for // schedule(dynamic, 64)
        for (unsigned int i = 0; i < dataset_size; i++) {
            for (unsigned int j = 0; j < dataset_size; j++) {
                // distances[i * dataset_size + j] = euclidean_distance(&current_points[i], &current_points[j]);
                distances[i * dataset_size + j] = euclidean_distance(&shifted_dataset[i], &shifted_dataset[j]);
            }
        }
        
        // Apply kernel function to distances
        #pragma omp parallel for // schedule(dynamic, 64)
        for (unsigned int i = 0; i < dataset_size; i++) {
            for (unsigned int j = 0; j < dataset_size; j++) {
                weights[i * dataset_size + j] = kernel_func(distances[i * dataset_size + j], bandwidth);
            }
        }
        
        // Calculate sum of weights (kernels)
        #pragma omp parallel for
        for (unsigned int i = 0; i < dataset_size; i++) {
            weight_sums[i] = 0.0;
            for (unsigned int j = 0; j < dataset_size; j++) {
                weight_sums[i] += weights[i * dataset_size + j];
            }
        }
        
        // Compute new points
        #pragma omp parallel for
        for (unsigned int i = 0; i < dataset_size; i++) {
            init_point(&next_points[i]);
            
            // Matrix multiplication: weights * points
            for (unsigned int j = 0; j < dataset_size; j++) {
                for (unsigned int d = 0; d < DIM; d++) {
                    // next_points[i][d] += weights[i * dataset_size + j] * current_points[j][d];
                    next_points[i][d] += weights[i * dataset_size + j] * shifted_dataset[j][d];
                }
            }
            
            // Normalize by weight sum
            if (weight_sums[i] > 0) {
                for (unsigned int d = 0; d < DIM; d++) {
                    next_points[i][d] /= weight_sums[i];
                }
            } else {
                #pragma omp critical
                {
                    fprintf(stderr, "Error: total_weight == 0, couldn't normalize.\n");
                }
            }
        }
        
        // Calculate convergence metric
        T total_shift = 0.0;
        #pragma omp parallel for reduction(+:total_shift)
        for (unsigned int i = 0; i < dataset_size; i++) {
            // T point_shift = euclidean_distance(&current_points[i], &next_points[i]);
            T point_shift = euclidean_distance(&shifted_dataset[i], &next_points[i]);
            total_shift += point_shift;
        }
        shift_norm = total_shift / dataset_size;
        
        // Update current points
        #pragma omp parallel for
        for (unsigned int i = 0; i < dataset_size; i++) {
            // copy_point(&next_points[i], &current_points[i]);
            copy_point(&next_points[i], &shifted_dataset[i]);
        }
        
        iter++;
#ifdef DEBUG
        if (iter % 10 == 0)
            printf("Iteration %d, shift_norm: %f\n", iter, shift_norm);
#endif
    }
    
    // Copy the final shifted points to the output
    // for (unsigned int i = 0; i < dataset_size; i++) {
    //     copy_point(&current_points[i], &shifted_dataset[i]);
    // }
    
    // Cluster assignment (same as in original mean_shift)
    #pragma omp parallel for
    for (int i = 0; i < dataset_size; i++) {
        assign_clusters(&shifted_dataset[i], cluster_modes, cluster_count);
    }
    
cleanup:
    // Free allocated memory
    free(distances);
    free(weights);
    free(weight_sums);
    // free(current_points);
    free(next_points);
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
