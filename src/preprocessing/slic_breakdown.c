#include "preprocessing.h"
#include "../include/point.h"
#include "../include/utils.h"
#include <math.h>
#include <float.h>
#include <omp.h>

#ifdef TOTAL_TIMING
#include "../metrics/timing.h"
#endif

#ifdef TIMING_BREAKDOWN
#include "../metrics/timing.h"
// Define timers for different SLIC operations
TIMER_SUM_DEF(slic_distance_calc)
TIMER_SUM_DEF(assignment_op)
TIMER_SUM_DEF(center_init)
TIMER_SUM_DEF(center_update)
TIMER_SUM_DEF(cluster_accumulate)
#endif

/*

dataset[dataset_size] contiene i pixel del dataset
dataset_labels[dataset_size] contiene le label assegnate ad ogni pixel
superpixel_dataset[num_superpixels] contiene i centri di ogni superpixel
superpixel_labels[num_superpixels] contiene le label assegnate ad ogni superpixel (num label = num superpixels)

mean_shift() su superpixels_dataset[] --> ritorna shifted_superpixels[]
Ogni pixel prenderà il valore del superpixel a cui appartiene (check tramite le labels)

-----
se ad esempio il 15esimo pixel con valori [12,5,203] 
viene assegnato al secondo superpixel con label 3 e valore [10,7,203]:
- dataset[15] = [12,5,203]
- dataset_labels[15] = 3
- superpixel_labels[2] = 3


eseguo mean_shift() su superpixel_dataset[], supponendo che 
superpixel_dataset[2] diventerà [15,2,200]:
- dataset[15] = [15,2,200] perchè dataset_labels[15] = 3 e il superpixel
con label 3 è diventato [15,2,200]

*/
unsigned int preprocess_dataset(unsigned int dataset_size,
                        const Point dataset[], int dataset_labels[], Point superpixel_dataset[],
                        unsigned int width, unsigned int height, unsigned int num_superpixels, T m)
{
#ifdef TOTAL_TIMING
    TOTAL_TIMER_START(slic_total);
#endif
    
    // Ideal distance between superpixels 
    unsigned int S = sqrt((width * height) / (T)num_superpixels); //area for each superpixel

    unsigned int *center_x = malloc(num_superpixels * sizeof(unsigned int)); // x-coordinates of superpixel centers
    unsigned int *center_y = malloc(num_superpixels * sizeof(unsigned int)); // y-coordinates of superpixel centers
    T *distances = malloc(dataset_size * sizeof(T)); // distances from each pixel to its assigned superpixel center

    // Initialize centers
    unsigned int num_centers = 0;
#ifdef TIMING_BREAKDOWN
    TIMER_START(center_init);
#endif
    initialize_centers(dataset, width, height, S, num_superpixels, superpixel_dataset, center_x, center_y, &num_centers);
#ifdef TIMING_BREAKDOWN
    TIMER_SUM(center_init);
#endif

    // Initialize labels and distances (infinite)
    reset_labels_and_distances(dataset_size, dataset_labels, distances);

    Point *new_centers = malloc(num_superpixels * sizeof(Point));
    unsigned int *counts = malloc(num_superpixels * sizeof(unsigned int));
    unsigned int *sum_x = malloc(num_superpixels * sizeof(unsigned int));
    unsigned int *sum_y = malloc(num_superpixels * sizeof(unsigned int));


    for (int iter = 0; iter < MAX_ITER; iter++) {
        // Assignment step --- PARALLELIZABLE over pixels
#ifdef TIMING_BREAKDOWN
        TIMER_START(assignment_op);
#endif
        assignment_step(dataset, superpixel_dataset, center_x, center_y, num_centers, width, height, S, m, dataset_labels, distances, dataset_size);
#ifdef TIMING_BREAKDOWN
        TIMER_SUM(assignment_op);
#endif

        // Reset new centers
        reset_new_centers(num_centers, new_centers, counts, sum_x, sum_y);

        // Sum pixels in each cluster -- PARALLELIZABLE (attention to race condition)
#ifdef TIMING_BREAKDOWN
        TIMER_START(cluster_accumulate);
#endif
        accumulate_cluster_sums(dataset, dataset_size, width, dataset_labels, new_centers, counts, sum_x, sum_y);
#ifdef TIMING_BREAKDOWN
        TIMER_SUM(cluster_accumulate);
#endif

        // Update centers -- PARALLELIZABLE over clusters
#ifdef TIMING_BREAKDOWN
        TIMER_START(center_update);
#endif
        update_centers(num_centers, superpixel_dataset, center_x, center_y, new_centers, counts, sum_x, sum_y);
#ifdef TIMING_BREAKDOWN
        TIMER_SUM(center_update);
#endif

        // reset distances
        #pragma omp parallel for
        for (int i = 0; i < dataset_size; i++)
            distances[i] = DBL_MAX;
    }
    
#ifdef TIMING_BREAKDOWN
    TIMER_SUM_PRINT(slic_distance_calc);
    TIMER_SUM_PRINT(assignment_op);
    TIMER_SUM_PRINT(center_init);
    TIMER_SUM_PRINT(center_update);
    TIMER_SUM_PRINT(cluster_accumulate);
#endif

#ifdef TOTAL_TIMING
    TOTAL_TIMER_STOP(slic_total);
#endif

    // Free memory
    free(center_x);
    free(center_y);
    free(distances);
    free(new_centers);
    free(counts);
    free(sum_x);
    free(sum_y);

    return num_centers;
}

T slic_distance(const Point *p1, const Point *p2, int x1, int y1, int x2, int y2, T S, T m) {
#ifdef TIMING_BREAKDOWN
    TIMER_START(slic_distance_calc);
#endif
    T dc_sqrd = 0.0; // color distance
    for (int i = 0; i < DIM; i++)
        dc_sqrd += ((*p1)[i] - (*p2)[i]) * ((*p1)[i] - (*p2)[i]);
    T ds_sqrd = (x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2);
    T result = sqrt(dc_sqrd + ds_sqrd / (S*S) * m*m);
#ifdef TIMING_BREAKDOWN
    TIMER_SUM(slic_distance_calc);
#endif
    return result;
}

void update_centers(int num_centers, Point centers[], int center_x[], int center_y[],
                           const Point new_centers[], const int counts[], const int sum_x[], const int sum_y[])
{
     #pragma omp parallel for
    for (int c = 0; c < num_centers; c++) {
        if (counts[c] > 0) {
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
    // Using OpenMP with private arrays for reduction
    int local_counts[MAX_SUPERPIXELS] = {0};
    int local_sum_x[MAX_SUPERPIXELS] = {0};
    int local_sum_y[MAX_SUPERPIXELS] = {0};
    Point local_centers[MAX_SUPERPIXELS];
    
    // Initialize local centers
    for (int c = 0; c < MAX_SUPERPIXELS; c++) {
        init_point(&local_centers[c]);
    }
    
    #pragma omp parallel
    {
        // Thread-private arrays
        int private_counts[MAX_SUPERPIXELS] = {0};
        int private_sum_x[MAX_SUPERPIXELS] = {0};
        int private_sum_y[MAX_SUPERPIXELS] = {0};
        Point private_centers[MAX_SUPERPIXELS];
        
        for (int c = 0; c < MAX_SUPERPIXELS; c++) {
            init_point(&private_centers[c]);
        }
        
        #pragma omp for nowait
        for (int i = 0; i < dataset_size; i++) {
            int c = labels[i];
            if (c < 0) continue;
            
            for (int j = 0; j < DIM; j++)
                private_centers[c][j] += dataset[i][j];
            
            private_sum_x[c] += i % width;
            private_sum_y[c] += i / width;
            private_counts[c]++;
        }
        
        // Combine results from all threads
        #pragma omp critical
        {
            for (int c = 0; c < MAX_SUPERPIXELS; c++) {
                if (private_counts[c] > 0) {
                    for (int j = 0; j < DIM; j++)
                        local_centers[c][j] += private_centers[c][j];
                    local_sum_x[c] += private_sum_x[c];
                    local_sum_y[c] += private_sum_y[c];
                    local_counts[c] += private_counts[c];
                }
            }
        }
    }
    
    // Copy local results to output arrays
    for (int c = 0; c < MAX_SUPERPIXELS; c++) {
        if (local_counts[c] > 0) {
            for (int j = 0; j < DIM; j++)
                new_centers[c][j] = local_centers[c][j];
            sum_x[c] = local_sum_x[c];
            sum_y[c] = local_sum_y[c];
            counts[c] = local_counts[c];
        }
    }
}

void reset_new_centers(int num_centers, Point new_centers[], int counts[], int sum_x[], int sum_y[])
{
    #pragma omp parallel for
    for (int c = 0; c < num_centers; c++) {
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
    int n_threads;
#pragma omp parallel
    {
#pragma omp single
        n_threads = omp_get_num_threads();
    }

    if (n_threads > 4)
    {
        // Parallelize over pixels
#pragma omp parallel for
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
    }
    else
    {
#pragma omp parallel for
        for (int c = 0; c < num_centers; c++)
        {
            int cx = center_x[c];
            int cy = center_y[c];
            for (int dy = -S; dy <= S; dy++)
            {
                for (int dx = -S; dx <= S; dx++)
                {
                    int x = cx + dx;
                    int y = cy + dy;
                    if (x < 0 || x >= width || y < 0 || y >= height)
                        continue;
                    int idx = y * width + x;

                    T d = slic_distance(&dataset[idx], &centers[c], x, y, cx, cy, S, m);

                    int updated = 0;
#pragma omp critical(dist_update)
                    {
                        if (d < distances[idx])
                        {
                            distances[idx] = d;
                            labels[idx] = c;
                            updated = 1;
                        }
                    }
                }
            }
        }

// Assegna i pixel rimasti senza cluster al più vicino centro
#pragma omp parallel for
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
}



void initialize_centers(const Point dataset[], unsigned int width, unsigned int height, int S, unsigned int num_superpixels,
                               Point centers[], unsigned int center_x[], unsigned int center_y[], unsigned int *num_centers)
{
    int count = 0;
    for (int y = S / 2; y < height; y += S) {
        for (int x = S / 2; x < width; x += S) {
            copy_point(&dataset[y * width + x], &centers[count]); // Copy each center from the dataset
            center_x[count] = x;
            center_y[count] = y;
            count++;
            if (count >= num_superpixels) break;
        }
        if (count >= num_superpixels) break;
    }
    *num_centers = count;
}

void reset_labels_and_distances(int dataset_size, int labels[], T distances[])
{
    #pragma omp parallel for
    for (int i = 0; i < dataset_size; i++) {
        labels[i] = -1;
        distances[i] = DBL_MAX;
    }
}