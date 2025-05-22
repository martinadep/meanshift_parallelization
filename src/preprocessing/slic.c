#include "preprocessing.h"
#include "../include/point.h"
#include "../include/utils.h"
#include <math.h>
#include <float.h>

#define MAX_SUPERPIXELS 1000
#define MAX_PIXELS 4096*4096 
#define MAX_ITER 10

/*

Processed_dataset[] contiene tutti i pixel assegnati a un superpixel con flag (4D)
Ritorna superpixel_dataset[] con i pixel di ogni superpixel con relativa flag (4D)
mean_shift() su superpixels[] --> ritorna shifted_superpixels[] con flag immutata
mappatura dei cluster di processed_dataset[] tramite flag

*/
unsigned int preprocess_dataset(unsigned int dataset_size,
                        const Point dataset[], Point processed_dataset[],
                        int width, int height, int num_superpixels, double m)
{
    int S = sqrt((width * height) / (double)num_superpixels);

    static Point centers[MAX_SUPERPIXELS];
    static int center_x[MAX_SUPERPIXELS];
    static int center_y[MAX_SUPERPIXELS];
    static int labels[MAX_PIXELS];
    static double distances[MAX_PIXELS];

    int num_centers = 0;
    for (int y = S / 2; y < height; y += S) {
        for (int x = S / 2; x < width; x += S) {
            int idx = y * width + x;
            copy_point(&dataset[idx], &centers[num_centers]);
            center_x[num_centers] = x;
            center_y[num_centers] = y;
            num_centers++;
            if (num_centers >= MAX_SUPERPIXELS) break;
        }
        if (num_centers >= MAX_SUPERPIXELS) break;
    }

    for (int i = 0; i < dataset_size; i++) {
        labels[i] = -1;
        distances[i] = DBL_MAX;
    }

    for (int iter = 0; iter < MAX_ITER; iter++) {
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
                    double d = slic_distance(&dataset[idx], &centers[c], x, y, cx, cy, S, m);
                    if (d < distances[idx]) {
                        distances[idx] = d;
                        labels[idx] = c;
                    }
                }
            }
        }
        // Update step
        static Point new_centers[MAX_SUPERPIXELS];
        static int counts[MAX_SUPERPIXELS];
        static int sum_x[MAX_SUPERPIXELS];
        static int sum_y[MAX_SUPERPIXELS];
        for (int c = 0; c < num_centers; c++) {
            init_point(&new_centers[c]);
            counts[c] = 0;
            sum_x[c] = 0;
            sum_y[c] = 0;
        }
        for (int i = 0; i < dataset_size; i++) {
            int c = labels[i];
            if (c < 0) continue;
            for (int j = 0; j < 3; j++)
                new_centers[c][j] += dataset[i][j];
            sum_x[c] += i % width;
            sum_y[c] += i / width;
            counts[c]++;
        }
        for (int c = 0; c < num_centers; c++) {
            if (counts[c] > 0) {
                for (int j = 0; j < 3; j++)
                    centers[c][j] = new_centers[c][j] / counts[c];
                center_x[c] = sum_x[c] / counts[c];
                center_y[c] = sum_y[c] / counts[c];
            }
        }
        for (int i = 0; i < dataset_size; i++)
            distances[i] = DBL_MAX;
    }

    for (int i = 0; i < dataset_size; i++) {
        int c = labels[i];
        copy_point(&centers[c], &processed_dataset[i]);
    }
    return num_centers;
}

double slic_distance(const Point *p1, const Point *p2, int x1, int y1, int x2, int y2, double S, double m) {
    double dc_sqrd = 0.0; // color distance
    for (int i = 0; i < 3; i++)
        dc_sqrd += ((*p1)[i] - (*p2)[i]) * ((*p1)[i] - (*p2)[i]);
    double ds_sqrd = (x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2);
    return sqrt(dc_sqrd + ds_sqrd / (S*S) * m*m);
}