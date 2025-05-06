#ifndef __PROVA_MEAN_SHIFT_H__
#define __PROVA_MEAN_SHIFT_H__
#include "point.hpp"
#include "utils.hpp"
#include <vector>

#define EPSILON 2.0
#define CLUSTER_EPSILON 50 // suggested: bandwidth * 1.5
#define MAX_ITER 50


#ifdef TIMING
        TIMER_SUM_DEF(kernel)
        TIMER_SUM_DEF(distance_shift)
        TIMER_SUM_DEF(coords_update)
        TIMER_SUM_DEF(distance_mode_find)
        TIMER_SUM_DEF(distance_cluster)
#endif

//#define DEBUG
#define MAX_CLUSTERS 1000 // maximum number of clusters

using namespace std;

// Move a single point towards maximum density area
void prova_shift_single_point(const Point &point, Point &next_point,
                        const Point dataset[], unsigned int dataset_size,
                        unsigned int bandwidth, T (*kernel_func)(T, unsigned int)) {
        double total_weight = 0;
        Point point_i;
        init_point(point_i); // xi
        init_point(next_point); // x'

        for (int i = 0; i < dataset_size; i++) {
            //point_i = dataset[i]; //xi
            copy_point(dataset[i], point_i); // xi = dataset[i]
#ifdef TIMING
            TIMER_START(distance_mode_find)
#endif
            double distance = euclidean_distance(point, point_i); //x-xi
#ifdef TIMING
            TIMER_SUM(distance_mode_find)
            TIMER_START(kernel)
#endif
            double weight = kernel_func(distance, bandwidth); // K(x-xi/h)
#ifdef TIMING
            TIMER_SUM(kernel)
            TIMER_START(coords_update)
#endif
            // x' = x + xi * K(x-xi/h)
            for (int j = 0; j < DIM; j++) {
                //next_point.setSingleCoord(j, next_point.getSingleCoord(j) + point_i.getSingleCoord(j) * weight);
                next_point[j] = next_point[j] + point_i[j] * weight;
            }
#ifdef TIMING
            TIMER_SUM(coords_update)
#endif

#ifdef WEIGHT_DEBUG
            cout << "weight " << weight << endl;
#endif
            // total_weight of all points with respect to [point]
            total_weight += weight;
        }
        if (total_weight > 0) {
            // normalization
            divide_point(next_point, total_weight); // x' = x' / sum(K(x-xi/h))
        } else {
            cout << "Error: total_weight == 0, couldn't normalize." << endl;
        }
}




void prova_assign_clusters(Point &shifted_point, Point cluster_modes[], 
                            unsigned int &cluster_count) {
    int c = 0;
    for (; c < cluster_count; c++) {
        #ifdef TIMING
        TIMER_START(distance_cluster)
        #endif
        double distance_from_cluster = euclidean_distance(shifted_point, cluster_modes[c]);
        #ifdef TIMING
        TIMER_SUM(distance_cluster)
        #endif         
        if (distance_from_cluster <= CLUSTER_EPSILON) {
            //shifted_point = cluster_modes[c];
            copy_point(cluster_modes[c], shifted_point); // assign cluster mode to shifted point
            break;
        }
    }
// whenever [shifted_point] doesn't belong to any cluster:
// --> create cluster with mode in [shifted_point]
    if (c == cluster_count) {
        copy_point(shifted_point, cluster_modes[c]); // assign cluster mode to shifted point
        cluster_count++;
        #ifdef DEBUG
        cout << "Cluster found! \t\t Number of clusters: " << cluster_count << endl;
        #endif
    }
}


void prova_mean_shift(unsigned int dataset_size, const Point dataset[], 
                Point shifted_dataset[], unsigned int bandwidth,
                T (*kernel_func)(T, unsigned int), Point cluster_modes[],
                unsigned int &cluster_count) {

        //vector stop_moving(dataset_size, false);
        Point prev_point;
        Point next_point;
        unsigned int iter;
        bool stop_moving; // array to check if each point has converged
        // shift each point
        for (int i = 0; i < dataset_size; i++) {
            stop_moving = false; // reset for each point
            iter = 0;
#ifdef DEBUG
            if (i % 500 == 0) {
                cout << "points [" << i << "/" << dataset_size << "] ..." << endl;
            }
#endif

            //prev_point = dataset[i];
            copy_point(dataset[i], prev_point);
            
            // shift till convergence
            while (!stop_moving && iter < MAX_ITER) {
                prova_shift_single_point(prev_point, next_point, dataset, dataset_size, bandwidth, kernel_func); // x' = x

#ifdef TIMING
                TIMER_START(distance_shift)
#endif
                double shift_distance = euclidean_distance(prev_point, next_point);
#ifdef TIMING
                TIMER_SUM(distance_shift)
#endif
                if (shift_distance <= EPSILON) {
                    stop_moving = true;
                }
                //prev_point = next_point;
                copy_point(next_point, prev_point); 
                iter++;
            }
            //shifted_dataset[i] = move(next_point);
            copy_point(next_point, shifted_dataset[i]);

            prova_assign_clusters(shifted_dataset[i], cluster_modes, cluster_count); // assign clusters to shifted points
        }
#ifdef TIMING
        TIMER_SUM_PRINT(coords_update)
        TIMER_SUM_PRINT(kernel)
        TIMER_SUM_PRINT(distance_shift)
        TIMER_SUM_PRINT(distance_mode_find)
        TIMER_SUM_PRINT(distance_cluster)
#endif
}
#endif //__PROVA_MEAN_SHIFT_H__