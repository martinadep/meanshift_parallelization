#include "preprocessing.h"
#include "../include/point.h"
#include "../include/utils.h"
#include <math.h>
#include <float.h>


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
                        int width, int height, int num_superpixels, T m)
{
    // Ideal distance between superpixels 
    int S = sqrt((width * height) / (T)num_superpixels);
;
    int center_x[NUM_SUPERPIXELS];
    int center_y[NUM_SUPERPIXELS];
    T distances[dataset_size];

    // Initialize centers
    int num_centers = 0;
    initialize_centers(dataset, width, height, S, num_superpixels, superpixel_dataset, center_x, center_y, &num_centers);

    // Initialize labels and distances (inifinite)
    reset_labels_and_distances(dataset_size, dataset_labels, distances);

    Point new_centers[NUM_SUPERPIXELS];
    int counts[NUM_SUPERPIXELS];
    int sum_x[NUM_SUPERPIXELS];
    int sum_y[NUM_SUPERPIXELS];


    for (int iter = 0; iter < MAX_ITER; iter++) {
        // Assignment step --- PARALLELIZABLE over pixels
        assignment_step(dataset, superpixel_dataset, center_x, center_y, num_centers, width, height, S, m, dataset_labels, distances, dataset_size);

        // Reset new centers
        reset_new_centers(num_centers, new_centers, counts, sum_x, sum_y);

        // Sum pixels in each cluster -- PARALLELIZABLE (attention to race condition)
        accumulate_cluster_sums(dataset, dataset_size, width, dataset_labels, new_centers, counts, sum_x, sum_y);

        // Update centers -- PARALLELIZABLE over clusters
        update_centers(num_centers, superpixel_dataset, center_x, center_y, new_centers, counts, sum_x, sum_y);

        // reset distances
        for (int i = 0; i < dataset_size; i++)
            distances[i] = DBL_MAX;
    }

    return num_centers;
}

T slic_distance(const Point *p1, const Point *p2, int x1, int y1, int x2, int y2, T S, T m) {
    T dc_sqrd = 0.0; // color distance
    for (int i = 0; i < DIM; i++)
        dc_sqrd += ((*p1)[i] - (*p2)[i]) * ((*p1)[i] - (*p2)[i]);
    T ds_sqrd = (x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2);
    return sqrt(dc_sqrd + ds_sqrd / (S*S) * m*m);
}

void update_centers(int num_centers, Point centers[], int center_x[], int center_y[],
                           const Point new_centers[], const int counts[], const int sum_x[], const int sum_y[])
{
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
                                    const int labels[], Point new_centers[], int counts[], int sum_x[], int sum_y[])
{
    for (int i = 0; i < dataset_size; i++) {
        int c = labels[i];
        if (c < 0) continue;
        for (int j = 0; j < DIM; j++)
            new_centers[c][j] += dataset[i][j];
        sum_x[c] += i % width;
        sum_y[c] += i / width;
        counts[c]++;
    }
}

void reset_new_centers(int num_centers, Point new_centers[], int counts[], int sum_x[], int sum_y[])
{
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
    for (int c = 0; c < num_centers; c++) {
        int cx = center_x[c];
        int cy = center_y[c];
        for (int dy = -S; dy <= S; dy++) {
            for (int dx = -S; dx <= S; dx++) {
                int x = cx + dx;
                int y = cy + dy;
                if (x < 0 || x >= width || y < 0 || y >= height)
                    continue;
                int idx = y * width + x;
                T d = slic_distance(&dataset[idx], &centers[c], x, y, cx, cy, S, m);
                if (d < distances[idx]) {
                    distances[idx] = d;
                    labels[idx] = c;
                }
            }
        }
    }

    // Assign pixels which are not assigned to any center to the closest center
    for (int i = 0; i < dataset_size; i++) {
    if (labels[i] == -1) {
        T min_dist = DBL_MAX;
        int best = 0;
        int x = i % width;
        int y = i / width;
        for (int c = 0; c < num_centers; c++) {
            T d = slic_distance(&dataset[i], &centers[c], x, y, center_x[c], center_y[c], S, m);
            if (d < min_dist) {
                min_dist = d;
                best = c;
            }
        }
        labels[i] = best;
    }
}

}

void initialize_centers(const Point dataset[], int width, int height, int S, int num_superpixels,
                               Point centers[], int center_x[], int center_y[], int *num_centers)
{
    int count = 0;
    for (int y = S / 2; y < height; y += S) {
        for (int x = S / 2; x < width; x += S) {
            copy_point(&dataset[y * width + x], &centers[count]);
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
    for (int i = 0; i < dataset_size; i++) {
        labels[i] = -1;
        distances[i] = DBL_MAX;
    }
}