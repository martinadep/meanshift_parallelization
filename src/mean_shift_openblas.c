#include "include/point.h"
#include "include/utils.h"
#include "include/mean_shift.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <omp.h>
#include <cblas.h>

// Matrix-based implementation of Mean Shift algorithm (using OpenBLAS)
void mean_shift(unsigned int dataset_size, const Point dataset[],
                     Point shifted_dataset[], T bandwidth,
                     T (*kernel_func)(T, T), Point cluster_modes[],
                     unsigned int* cluster_count)
{
    printf("OpenBLAS Mean shift\n");
    exit(0);
    const unsigned int N = dataset_size;
    const unsigned int D = DIM;

    T* distances = (T*)malloc(N * N * sizeof(T));
    T* weights = (T*)malloc(N * N * sizeof(T));
    T* weight_sums = (T*)malloc(N * sizeof(T));
    T* flat_points = (T*)malloc(N * D * sizeof(T));
    T* flat_new_points = (T*)malloc(N * D * sizeof(T));
    
    if (!distances || !weights || !weight_sums || !flat_points || !flat_new_points) {
        fprintf(stderr, "Error: Memory allocation failed in mean_shift_blas\n");
        goto cleanup;
    }

    // Flatten dataset into row-major matrix [N x D]
    #pragma omp parallel for
    for (unsigned int i = 0; i < N; i++)
        for (unsigned int d = 0; d < D; d++)
            flat_points[i * D + d] = dataset[i][d];

    memcpy(shifted_dataset, dataset, N * sizeof(Point)); // Initial copy

    const unsigned int MAX_ITER = 50;
    const T TOLERANCE = 1e-3;
    T shift_norm = INFINITY;
    unsigned int iter = 0;

    while (iter < MAX_ITER && shift_norm > TOLERANCE) {
        // 1. Compute pairwise distances
        #pragma omp parallel for collapse(2)
        for (unsigned int i = 0; i < N; i++) {
            for (unsigned int j = 0; j < N; j++) {
                T dist = 0.0;
                for (unsigned int d = 0; d < D; d++) {
                    T diff = shifted_dataset[i][d] - shifted_dataset[j][d];
                    dist += diff * diff;
                }
                distances[i * N + j] = sqrt(dist);
            }
        }

        // 2. Apply kernel
        #pragma omp parallel for
        for (unsigned int i = 0; i < N * N; i++)
            weights[i] = kernel_func(distances[i], bandwidth);

        // 3. Compute row-wise sum of weights (W1)
        #pragma omp parallel for
        for (unsigned int i = 0; i < N; i++) {
            weight_sums[i] = cblas_dasum(N, &weights[i * N], 1); // sum of row i
        }

        // 4. Matrix multiplication: new_points = weights @ flat_points
        // weights: [N x N], flat_points: [N x D], result: flat_new_points [N x D]
        cblas_dgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
                    N, D, N,
                    1.0, weights, N, flat_points, D,
                    0.0, flat_new_points, D);

        // 5. Normalize rows by weight_sums
        #pragma omp parallel for
        for (unsigned int i = 0; i < N; i++) {
            T norm = weight_sums[i];
            if (norm > 0) {
                for (unsigned int d = 0; d < D; d++)
                    flat_new_points[i * D + d] /= norm;
            } else {
                fprintf(stderr, "Warning: weight_sums[%u] == 0\n", i);
            }
        }

        // 6. Convergence check: compute L2 norm of difference
        T diff_norm = 0.0;
        #pragma omp parallel for reduction(+:diff_norm)
        for (unsigned int i = 0; i < N * D; i++) {
            T diff = flat_new_points[i] - flat_points[i];
            diff_norm += diff * diff;
        }
        shift_norm = sqrt(diff_norm);

        // 7. Update current points
        memcpy(flat_points, flat_new_points, N * D * sizeof(T));

        // Sync back to shifted_dataset
        #pragma omp parallel for
        for (unsigned int i = 0; i < N; i++)
            for (unsigned int d = 0; d < D; d++)
                shifted_dataset[i][d] = flat_points[i * D + d];

        iter++;
#ifdef DEBUG
        if (iter % 10 == 0)
            printf("Iteration %d, shift_norm: %f\n", iter, shift_norm);
#endif
    }

    // Cluster assignment
    #pragma omp parallel for
    for (int i = 0; i < N; i++) {
        assign_clusters(&shifted_dataset[i], cluster_modes, cluster_count);
    }

cleanup:
    free(distances);
    free(weights);
    free(weight_sums);
    free(flat_points);
    free(flat_new_points);
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
