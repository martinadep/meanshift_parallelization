#ifndef __MEAN_SHIFT_H__
#define __MEAN_SHIFT_H__
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
        TIMER_SUM_DEF(distance_iter)
        TIMER_SUM_DEF(distance_cluster)
#endif

#define DEBUG

using namespace std;

class MeanShift {
public:
    const vector<Point> dataset;
    vector<Point> shifted_dataset;
    vector<Point> cluster_modes;

    T bandwidth;
    unsigned int dataset_size;
    T (*kernel_func)(T, unsigned int);

    MeanShift() = default;

    MeanShift(vector<Point> dataset, T _bandwidth) : dataset(dataset) {
        dataset_size = dataset.size();
        bandwidth = _bandwidth;
        shifted_dataset.resize(dataset_size);
    }

    ~MeanShift() = default;

    unsigned int get_clusters_count() const {
        return cluster_modes.size();
    }

    void set_kernel(T (*_kernel_func)(T, unsigned int)) {
        if(!_kernel_func){
            kernel_func = gaussian_kernel;
        } else {
            kernel_func = _kernel_func;
        }
    }

    // Move a single point towards maximum density area
    void shift_single_point(const Point &point, Point &next_pos_point) {
        double total_weight = 0;
        Point point_i;
        init_point(next_pos_point); // set next_pos_point to 0

        for (int i = 0; i < dataset_size; i++) {
            //point_i = dataset[i]; //xi
            copy_point(dataset[i], point_i); // xi = dataset[i]
#ifdef TIMING
            TIMER_START(distance_shift)
#endif
            double distance = euclidean_distance(point, point_i); //x-xi
#ifdef TIMING
            TIMER_SUM(distance_shift)
            TIMER_START(kernel)
#endif
            double weight = kernel_func(distance, bandwidth); // K(x-xi/h)
#ifdef TIMING
            TIMER_SUM(kernel)
            TIMER_START(coords_update)
#endif
            // x' = x + xi * K(x-xi/h)
            for (int j = 0; j < DIM; j++) {
                //next_pos_point.setSingleCoord(j, next_pos_point.getSingleCoord(j) + point_i.getSingleCoord(j) * weight);
                next_pos_point.coords[j] = next_pos_point.coords[j] + point_i.coords[j] * weight;
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
            divide_point(next_pos_point, total_weight); // x' = x' / sum(K(x-xi/h))
        } else {
            cout << "Error: total_weight == 0, couldn't normalize." << endl;
        }
    }

    void mean_shift() {
        vector stop_moving(dataset_size, false);
        Point prev_point;
        Point next_point;
        unsigned int iter;

        // shift each point
        for (int i = 0; i < dataset_size; i++) {
            iter = 0;
#ifdef DEBUG
            if (i % 500 == 0) {
                cout << "points [" << i << "/" << dataset_size << "] ..." << endl;
            }
#endif

            //prev_point = dataset[i];
            copy_point(dataset[i], prev_point);
            
            // shift till convergence
            while (!stop_moving[i] && iter < MAX_ITER) {
                shift_single_point(prev_point, next_point);

#ifdef TIMING
                TIMER_START(distance_iter)
#endif
                double shift_distance = euclidean_distance(prev_point, next_point);
#ifdef TIMING
                TIMER_SUM(distance_iter)
#endif
                if (shift_distance <= EPSILON) {
                    stop_moving[i] = true;
                }
                //prev_point = next_point;
                copy_point(next_point, prev_point); 
                iter++;
            }
            //shifted_dataset[i] = move(next_point);
            copy_point(next_point, shifted_dataset[i]);

            assign_clusters(shifted_dataset[i]);
        }
#ifdef TIMING
        TIMER_SUM_PRINT(coords_update)
        TIMER_SUM_PRINT(kernel)
        TIMER_SUM_PRINT(distance_shift)
        TIMER_SUM_PRINT(distance_iter)
        TIMER_SUM_PRINT(distance_cluster)
#endif
    }

    void assign_clusters(Point &shifted_point) {
        int c = 0;
        for (; c < cluster_modes.size(); c++) {
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
        if (c == cluster_modes.size()) {
            cluster_modes.push_back(move(shifted_point));
#ifdef DEBUG
            cout << "Cluster found! \t\t Number of clusters: " << cluster_modes.size() << endl;
#endif
        }
    }
};

#endif //__MEAN_SHIFT_H__
