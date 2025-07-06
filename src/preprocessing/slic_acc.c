#include "preprocessing.h"
#include "../include/point.h"
#include "../include/utils.h"
#include <math.h>
#include <float.h>
#include <openacc.h>

#ifdef TOTAL_TIMING
#include "../metrics/timing.h"
#endif

/*
 * SLIC Superpixel segmentation algorithm (OpenACC implementation)
 *
 * dataset[dataset_size] contiene i pixel del dataset
 * dataset_labels[dataset_size] contiene le label assegnate ad ogni pixel
 * superpixel_dataset[num_superpixels] contiene i centri di ogni superpixel
 * superpixel_labels[num_superpixels] contiene le label assegnate ad ogni superpixel
 */

// Calculate combined color and spatial distance in SLIC

unsigned int preprocess_dataset(unsigned int dataset_size,
                                const Point dataset[], int dataset_labels[], Point superpixel_dataset[],
                                unsigned int width, unsigned int height, unsigned int num_superpixels, T m)
{
    // Ideal distance between superpixels
    unsigned int S = sqrt((width * height) / (T)num_superpixels); // area for each superpixel

    unsigned int *center_x = malloc(num_superpixels * sizeof(unsigned int));
    unsigned int *center_y = malloc(num_superpixels * sizeof(unsigned int));
    T *distances = malloc(dataset_size * sizeof(T));

    // Initialize centers
    unsigned int num_centers = 0;
    initialize_centers(dataset, width, height, S, num_superpixels, superpixel_dataset, center_x, center_y, &num_centers);

    // Initialize labels and distances (infinite)
    reset_labels_and_distances(dataset_size, dataset_labels, distances);

    Point *new_centers = malloc(num_superpixels * sizeof(Point));
    unsigned int *counts = malloc(num_superpixels * sizeof(unsigned int));
    unsigned int *sum_x = malloc(num_superpixels * sizeof(unsigned int));
    unsigned int *sum_y = malloc(num_superpixels * sizeof(unsigned int));

    // Create OpenACC data region
    #pragma acc data copyin(dataset[0:dataset_size], superpixel_dataset[0:num_centers], center_x[0:num_centers], center_y[0:num_centers]) \
                  copy(dataset_labels[0:dataset_size], distances[0:dataset_size]) \
                  create(new_centers[0:num_centers], counts[0:num_centers], sum_x[0:num_centers], sum_y[0:num_centers])
    {
        for (int iter = 0; iter < MAX_ITER; iter++)
        {
            // Associate each pixel with nearest cluster center
            assignment_step(dataset, superpixel_dataset, center_x, center_y, num_centers, width, height, S, m, dataset_labels, distances, dataset_size);

            // Zero out temporary arrays
            reset_new_centers(num_centers, new_centers, counts, sum_x, sum_y);

            // Accumulate values for new centers
            accumulate_cluster_sums(dataset, dataset_size, width, dataset_labels, new_centers, counts, sum_x, sum_y);

            // Update centers
            update_centers(num_centers, superpixel_dataset, center_x, center_y, new_centers, counts, sum_x, sum_y);

            // Reset distances
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
        dc_sqrd += (p1->coords[i] - p2->coords[i]) * (p1->coords[i] - p2->coords[i]);
    T ds_sqrd = (x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2);
    return sqrt(dc_sqrd + ds_sqrd / (S * S) * m * m);
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

void reset_new_centers(int num_centers, Point new_centers[], int counts[], int sum_x[], int sum_y[])
{
    #pragma acc parallel loop present(new_centers[0:num_centers], counts[0:num_centers], sum_x[0:num_centers], sum_y[0:num_centers])
    for (int c = 0; c < num_centers; c++)
    {
        init_point(&new_centers[c]);
        counts[c] = 0;
        sum_x[c] = 0;
        sum_y[c] = 0;
    }
}

void assignment_step(const Point dataset[], const Point centers[], const int center_x[], const int center_y[],
                     int num_centers, int width, int height, int S, T m,
                     int labels[], T distances[], int dataset_size)
{
    #pragma acc parallel loop present(dataset[0:dataset_size], centers[0:num_centers], \
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
            T d = 0.0;

            T dc_sqrd = 0.0; // color distance
            for (int j = 0; j < DIM; j++)
                dc_sqrd += (dataset[i].coords[j] - centers[c].coords[j]) * (dataset[i].coords[j] - centers[c].coords[j]);
            T ds_sqrd = (x - center_x[c]) * (x - center_x[c]) + (y - center_y[c]) * (y - center_y[c]);
            d = sqrt(dc_sqrd + ds_sqrd / (S * S) * m * m);

            if (d < min_dist)
            {
                min_dist = d;
                best_label = c;
            }
        }
        labels[i] = best_label;
        distances[i] = min_dist;
    }
}

void accumulate_cluster_sums(const Point dataset[], int dataset_size, int width,
                             int labels[], Point new_centers[], int counts[], int sum_x[], int sum_y[])
{
    #pragma acc parallel loop present(dataset[0:dataset_size], labels[0:dataset_size], \
                                     new_centers[0:MAX_SUPERPIXELS], counts[0:MAX_SUPERPIXELS], \
                                     sum_x[0:MAX_SUPERPIXELS], sum_y[0:MAX_SUPERPIXELS])
    for (int i = 0; i < dataset_size; i++)
    {
        int c = labels[i];
        if (c < 0 || c >= MAX_SUPERPIXELS)
            continue;

        int x = i % width;
        int y = i / width;

        #pragma acc atomic update
        sum_x[c] += x;
        
        #pragma acc atomic update
        sum_y[c] += y;
        
        #pragma acc atomic update
        counts[c]++;

        for (int j = 0; j < DIM; j++)
        {
            #pragma acc atomic update
            new_centers[c].coords[j] += dataset[i].coords[j];
        }
    }
}

void update_centers(int num_centers, Point centers[], int center_x[], int center_y[],
                    const Point new_centers[], const int counts[], const int sum_x[], const int sum_y[])
{
    #pragma acc parallel loop present(centers[0:num_centers], center_x[0:num_centers], center_y[0:num_centers], \
                                     new_centers[0:num_centers], counts[0:num_centers], sum_x[0:num_centers], sum_y[0:num_centers])
    for (int c = 0; c < num_centers; c++)
    {
        if (counts[c] > 0)
        {
            for (int j = 0; j < DIM; j++)
                centers[c].coords[j] = new_centers[c].coords[j] / counts[c];
            center_x[c] = sum_x[c] / counts[c];
            center_y[c] = sum_y[c] / counts[c];
        }
    }
}