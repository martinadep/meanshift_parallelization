#ifndef __PREPROCESSING_H__
#define __PREPROCESSING_H__
#include "../include/point.h"
#include "../include/utils.h"

#ifndef NUM_SUPERPIXELS
#define NUM_SUPERPIXELS 1000
#endif
#define MAX_SUPERPIXELS 6000
#define MAX_ITER 10

#ifdef __cplusplus
extern "C" {
#endif

unsigned int preprocess_dataset(unsigned int dataset_size,
                        const Point dataset[], unsigned int dataset_labels[], Point superpixel_dataset[],
                        unsigned int width, unsigned int height, unsigned int num_superpixels, T m);

// ---------------- slic.c -----------------
T slic_distance(const Point *p1, const Point *p2, 
    int x1, int y1, int x2, int y2, T S, T m);

void initialize_centers(const Point dataset[], int width, int height, int S, int num_superpixels,
                               Point centers[], int center_x[], int center_y[], int *num_centers);

void reset_labels_and_distances(int dataset_size, int labels[], T distances[]);

void assignment_step(const Point dataset[], const Point centers[], const int center_x[], const int center_y[],
                            int num_centers, int width, int height, int S, T m,
                            int labels[], T distances[], int dataset_size);

void reset_new_centers(int num_centers, Point new_centers[], int counts[], int sum_x[], int sum_y[]);

void accumulate_cluster_sums(const Point dataset[], int dataset_size, int width,
                                    const int labels[], Point new_centers[], int counts[], int sum_x[], int sum_y[]);

void update_centers(int num_centers, Point centers[], int center_x[], int center_y[],
                           const Point new_centers[], const int counts[], const int sum_x[], const int sum_y[]);

#ifdef __cplusplus
}
#endif
#endif // __PREPROCESSING_H__