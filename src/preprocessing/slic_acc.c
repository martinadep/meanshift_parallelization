
#include "preprocessing.h"
#include "../include/point.h"
#include "../include/utils.h"
#include <math.h>
#include <float.h>

#ifdef TOTAL_TIMING
#include "../metrics/timing.h"
#endif

// OpenACC implementation of SLIC superpixel algorithm
 
unsigned int preprocess_dataset(unsigned int dataset_size,
                                const Point dataset[], int dataset_labels[], Point superpixel_dataset[],
                                unsigned int width, unsigned int height, unsigned int num_superpixels, T m)
{
    // Ideal distance between superpixels
    unsigned int S = sqrt((width * height) / (T)num_superpixels); // area for each superpixel

    unsigned int *center_x = malloc(num_superpixels * sizeof(unsigned int)); // x-coordinates of superpixel centers
    unsigned int *center_y = malloc(num_superpixels * sizeof(unsigned int)); // y-coordinates of superpixel centers
    T *distances = malloc(dataset_size * sizeof(T));                         // distances from each pixel to its assigned superpixel center

    // Initialize centers
    unsigned int num_centers = 0;
    initialize_centers(dataset, width, height, S, num_superpixels, superpixel_dataset, center_x, center_y, &num_centers);

    // Initialize labels and distances (infinite)
    reset_labels_and_distances(dataset_size, dataset_labels, distances);

    Point *new_centers = malloc(num_superpixels * sizeof(Point));
    unsigned int *counts = malloc(num_superpixels * sizeof(unsigned int));
    unsigned int *sum_x = malloc(num_superpixels * sizeof(unsigned int));
    unsigned int *sum_y = malloc(num_superpixels * sizeof(unsigned int));

    #pragma acc data copyin(dataset[0:dataset_size][0:DIM], superpixel_dataset[0:num_centers][0:DIM], \
                          center_x[0:num_centers], center_y[0:num_centers]) \
                   copy(dataset_labels[0:dataset_size]) \
                   create(distances[0:dataset_size], new_centers[0:num_centers][0:DIM], \
                          counts[0:num_centers], sum_x[0:num_centers], sum_y[0:num_centers])
    {
        for (int iter = 0; iter < MAX_ITER; iter++)
        {
            // Associate each pixel with nearest cluster center based on combined color and spatial distance metric
            assignment_step(dataset, superpixel_dataset, center_x, center_y, num_centers, width, height, S, m, dataset_labels, distances, dataset_size);

            // Zero out temporary arrays for calculating new cluster centers in the update phase
            reset_new_centers(num_centers, new_centers, counts, sum_x, sum_y);

            // For each cluster, sum color values and spatial coordinates of all assigned pixels for centroid calculation
            accumulate_cluster_sums(dataset, dataset_size, width, dataset_labels, new_centers, counts, sum_x, sum_y);

            // Recalculate each cluster's center position and color by averaging the values of all pixels belonging to that cluster
            update_centers(num_centers, superpixel_dataset, center_x, center_y, new_centers, counts, sum_x, sum_y);

            // reset distances
            #pragma acc parallel loop
            for (int i = 0; i < dataset_size; i++)
                distances[i] = DBL_MAX;
        }
    }

    free(center_x);
    free(center_y);
    free(distances);
    free(new_centers);
    free(counts);
    free(sum_x);
    free(sum_y);

    return num_centers;
}

T slic_distance(const Point *p1, const Point *p2, int x1, int y1, int x2, int y2, T S, T m)
{
    T dc_sqrd = 0.0; // color distance
    for (int i = 0; i < DIM; i++)
        dc_sqrd += ((*p1)[i] - (*p2)[i]) * ((*p1)[i] - (*p2)[i]);
    T ds_sqrd = (x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2);
    return sqrt(dc_sqrd + ds_sqrd / (S * S) * m * m);
}

void update_centers(int num_centers, Point centers[], int center_x[], int center_y[],
                    const Point new_centers[], const int counts[], const int sum_x[], const int sum_y[])
{
    #pragma acc parallel loop present(centers[0:num_centers][0:DIM], center_x[0:num_centers], center_y[0:num_centers], \
                                     new_centers[0:num_centers][0:DIM], counts[0:num_centers], \
                                     sum_x[0:num_centers], sum_y[0:num_centers])
    for (int c = 0; c < num_centers; c++)
    {
        if (counts[c] > 0)
        {
            for (int j = 0; j < DIM; j++)
                centers[c][j] = new_centers[c][j] / counts[c];
            center_x[c] = sum_x[c] / counts[c];
            center_y[c] = sum_y[c] / counts[c];
        }
    }
}

void accumulate_cluster_sums(const Point dataset[], int dataset_size, int width,
                             int labels[], Point new_centers[], int counts[], int sum_x[], int sum_y[])
{
    #pragma acc parallel loop present(dataset[0:dataset_size][0:DIM], labels[0:dataset_size], \
                                     new_centers[0:MAX_SUPERPIXELS][0:DIM], counts[0:MAX_SUPERPIXELS], \
                                     sum_x[0:MAX_SUPERPIXELS], sum_y[0:MAX_SUPERPIXELS])
    for (int i = 0; i < dataset_size; i++)
    {
        int c = labels[i];
        if (c < 0)
            continue;

        int x = i % width;
        int y = i / width;

        #pragma acc atomic
        sum_x[c] += x;

        #pragma acc atomic
        sum_y[c] += y;

        #pragma acc atomic
        counts[c]++;

        for (int j = 0; j < DIM; j++) {
            #pragma acc atomic
            new_centers[c][j] += dataset[i][j];
        }
    }
}

void reset_new_centers(int num_centers, Point new_centers[], int counts[], int sum_x[], int sum_y[])
{
    #pragma acc parallel loop present(new_centers[0:num_centers][0:DIM], counts[0:num_centers], \
                                     sum_x[0:num_centers], sum_y[0:num_centers])
    for (int c = 0; c < num_centers; c++)
    {
        for (int j = 0; j < DIM; j++)
            new_centers[c][j] = 0;
        counts[c] = 0;
        sum_x[c] = 0;
        sum_y[c] = 0;
    }
}

void initialize_centers(const Point dataset[], unsigned int width, unsigned int height, int S, unsigned int num_superpixels,
                        Point centers[], unsigned int center_x[], unsigned int center_y[], unsigned int *num_centers)
{
    int count = 0;
    for (int y = S / 2; y < height; y += S)
    {
        for (int x = S / 2; x < width; x += S)
        {
            copy_point(&dataset[y * width + x], &centers[count]); // Copy each center from the dataset
            center_x[count] = x;
            center_y[count] = y;
            count++;
            if (count >= num_superpixels)
                break;
        }
        if (count >= num_superpixels)
            break;
    }
    *num_centers = count;
}

void reset_labels_and_distances(int dataset_size, int labels[], T distances[])
{
    #pragma acc parallel loop present(labels[0:dataset_size], distances[0:dataset_size])
    for (int i = 0; i < dataset_size; i++)
    {
        labels[i] = -1;
        distances[i] = DBL_MAX;
    }
}

void assignment_step(const Point dataset[], const Point centers[], const int center_x[], const int center_y[],
                     int num_centers, int width, int height, int S, T m,
                     int labels[], T distances[], int dataset_size)
{
    // Parallelize over pixels
    #pragma acc parallel loop present(dataset[0:dataset_size][0:DIM], centers[0:num_centers][0:DIM], \
                                     center_x[0:num_centers], center_y[0:num_centers], \
                                     labels[0:dataset_size], distances[0:dataset_size])
    for (int i = 0; i < dataset_size; i++)
    {
        int x = i % width;
        int y = i / width;
        T min_dist = DBL_MAX;
        int best_label = -1;

        for (int c = 0; c < num_centers; c++)
        {
            if (abs(x - center_x[c]) > S || abs(y - center_y[c]) > S)
                continue;
            T d = slic_distance(&dataset[i], &centers[c], x, y, center_x[c], center_y[c], S, m);
            if (d < min_dist)
            {
                min_dist = d;
                best_label = c;
            }
        }
        labels[i] = best_label;
        distances[i] = min_dist;
    }

    // Second pass for remaining pixels
    #pragma acc parallel loop present(dataset[0:dataset_size][0:DIM], centers[0:num_centers][0:DIM], \
                                     center_x[0:num_centers], center_y[0:num_centers], \
                                     labels[0:dataset_size])
    for (int i = 0; i < dataset_size; i++)
    {
        if (labels[i] == -1)
        {
            T min_dist = DBL_MAX;
            int best = 0;
            int x = i % width;
            int y = i / width;
            
            for (int c = 0; c < num_centers; c++)
            {
                T d = slic_distance(&dataset[i], &centers[c], x, y, center_x[c], center_y[c], S, m);
                if (d < min_dist)
                {
                    min_dist = d;
                    best = c;
                }
            }
            labels[i] = best;
        }
    }
}