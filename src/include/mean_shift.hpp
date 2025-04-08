#ifndef __MEAN_SHIFT_H__
#define __MEAN_SHIFT_H__
#include "point.hpp"
#include "utils.hpp"
#include "timing.hpp"

using namespace std;

template<typename T>

#define EPSILON 2.0
#define EPSILON_MODE 50.0 // suggested: bandwidth * 1.5
#define MAX_ITER 50

#define DEBUG
//#define WEIGHT_DEBUG

class MeanShift {
public:
    const vector<Point<T> > dataset;
    vector<Point<T> > shifted_dataset;
    unsigned int dim_coords;
    unsigned int dataset_size;

    vector<Point<T> > clusters;
    T bandwidth;

    MeanShift() = default;

    MeanShift(vector<Point<T> > dataset, T _bandwidth, unsigned int _dim_coords) : dataset(dataset) {
        dataset_size = dataset.size();
        bandwidth = _bandwidth;
        dim_coords = _dim_coords;
        shifted_dataset.resize(dataset_size);
    }

    ~MeanShift() = default;

    // Gaussian Kernel
    T kernelFunction(T distance) {
        return exp(-0.5 * (distance * distance) / (bandwidth * bandwidth));
    }

    // Move a single point towards maximum density area
    void shift_single_point(const Point<T> &point, Point<T> &next_pos_point) {
        double total_weight = 0;
        Point<T> point_i;
        next_pos_point = Point<T>(dim_coords); // set next_pos_point to 0

        point_i.resize(dim_coords);
        for (int i = 0; i < dataset_size; i++) {
            point_i = dataset[i]; //xi

            double distance = point.euclidean_distance(point_i); //x-xi

            double weight = kernelFunction(distance); // K(x-xi/h)

            // x' = x + xi * K(x-xi/h)
            for (int j = 0; j < dim_coords; j++) {
                next_pos_point.setSingleCoord(j,
                                              next_pos_point.getSingleCoord(j) + point_i.getSingleCoord(j) * weight);
            }

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

                double shift_distance = prev_point.euclidean_distance(next_point);
                if (shift_distance <= EPSILON) {
                    stop_moving[i] = true;
                }
                prev_point = next_point;
                iter++;
            }
            shifted_dataset[i] = next_point;

            assign_clusters(shifted_dataset[i]);
        }
    }

    void assign_clusters(Point<T> &shifted_point) {
        int c = 0;
        for (; c < clusters.size(); c++) {
            clusters[c].resize(dim_coords);
            if (shifted_point.euclidean_distance(clusters[c]) <= EPSILON_MODE) {
                shifted_point = clusters[c];
                break;
            }
        }
        // whenever [shifted_point] doesn't belong to any cluster:
        // --> create cluster with mode in [shifted_point]
        if (c == clusters.size()) {
            Point<T> new_cluster;
            new_cluster = shifted_point;
            clusters.push_back(new_cluster);
#ifdef DEBUG
            cout << "Cluster found! \t\t Number of clusters: " << clusters.size() << endl;
#endif
        }
    }
};

#endif //__MEAN_SHIFT_H__
