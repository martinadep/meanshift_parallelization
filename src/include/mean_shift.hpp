#ifndef __MEAN_SHIFT_H__
#define __MEAN_SHIFT_H__
#include "point.hpp"
#include "utils.hpp"

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

using namespace std;
template<typename T>
class MeanShift {
public:
    const vector<Point<T>> dataset;
    vector<Point<T>> shifted_dataset;
    vector<Point<T>> cluster_modes;

    T bandwidth;
    unsigned int dim_coords;
    unsigned int dataset_size;
    T (*kernel_func)(T, unsigned int);

    MeanShift() = default;

    MeanShift(vector<Point<T>> dataset, T _bandwidth) : dataset(dataset) {
        dataset_size = dataset.size();
        bandwidth = _bandwidth;
        dim_coords = dataset[0].size();
        shifted_dataset.resize(dataset_size);
    }

    ~MeanShift() = default;

    unsigned int get_clusters_count() const {
        return cluster_modes.size();
    }

    T euclidean_distance(const Point<T> &point1, const Point<T> &point2) {
        if (point1.size() != point2.size()) {
            cout << "Error: points have different dimensions." << endl;
            return -1;
        }
        T distance = 0;
        for (unsigned int i = 0; i < dim_coords; i++) {
            distance += (point1.getSingleCoord(i) - point2.getSingleCoord(i)) *
                        (point1.getSingleCoord(i) - point2.getSingleCoord(i));
        }
        return sqrt(distance);
    }

    void set_kernel(T (*_kernel_func)(T, unsigned int)) {
        if(!_kernel_func){
            kernel_func = gaussian_kernel;
        } else {
            kernel_func = _kernel_func;
        }
    }

    // Move a single point towards maximum density area
    void shift_single_point(const Point<T> &point, Point<T> &next_pos_point) {
        double total_weight = 0;
        Point<T> point_i;
        next_pos_point = Point<T>(dim_coords); // set next_pos_point to 0

        for (int i = 0; i < dataset_size; i++) {
            point_i = dataset[i]; //xi
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
            for (int j = 0; j < dim_coords; j++) {
                next_pos_point.setSingleCoord(j, next_pos_point.getSingleCoord(j) + point_i.getSingleCoord(j) * weight);
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
            next_pos_point /= total_weight;
        } else {
            cout << "Error: total_weight == 0, couldn't normalize." << endl;
        }
    }

    void mean_shift() {
        vector stop_moving(dataset_size, false);
        Point<T> prev_point;
        Point<T> next_point;
        unsigned int iter;

        // shift each point
        for (int i = 0; i < dataset_size; i++) {
            iter = 0;
#ifdef DEBUG
            if (i % 500 == 0) {
                cout << "points [" << i << "/" << dataset_size << "] ..." << endl;
            }
#endif

            prev_point = dataset[i];
            next_point.resize(dim_coords);

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
                prev_point = next_point;
                iter++;
            }
            shifted_dataset[i] = move(next_point);

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

    void assign_clusters(Point<T> &shifted_point) {
        int c = 0;
        for (; c < cluster_modes.size(); c++) {
            cluster_modes[c].resize(dim_coords);
#ifdef TIMING
            TIMER_START(distance_cluster)
#endif
            double distance_from_cluster = euclidean_distance(shifted_point, cluster_modes[c]);
#ifdef TIMING
            TIMER_SUM(distance_cluster)
#endif         
            if (distance_from_cluster <= CLUSTER_EPSILON) {
                shifted_point = cluster_modes[c];
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
