//
// Created by marti on 30/03/2025.
//

#ifndef __MEAN_SHIFT_H__
#define __MEAN_SHIFT_H__
#include "point.h"
#include "cluster.h"

using namespace std;

template<typename T>

#define EPSILON 2.0
#define EPSILON_MODE 50.0 // suggested bandwidth * 1.5
#define MAX_ITER 50

class MeanShift {
public:
    const vector<Point<T> > dataset;
    vector<Point<T>> shifted_dataset;
    unsigned int dim_coords;
    unsigned int dataset_size;

    vector<Cluster<T> > clusters;
    T bandwidth;

    MeanShift() = default;

    MeanShift(vector<Point<T>> dataset, T _bandwidth, unsigned int _dim_coords) : dataset(dataset) {
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

    // Sposta un punto verso il massimo della densità
    void shift_single_point(const Point<T> &point, Point<T> &next_pos_point) {

        // compute weight of the shift
        double total_weight = 0;
        Point<T> point_i;
        next_pos_point.coords.resize(dim_coords);
        for (int i = 0; i < dim_coords; i++) {
            next_pos_point.coords[i] = 0;
        }
        point_i.coords.resize(dim_coords);
        int iter = 0;
        for (int i = 0; i < dataset.size(); i++) {
            // xi
            point_i = dataset[i];
            // x - xi
            double distance = point.euclidean_distance(point_i);

            // K(x-xi/h)
            //cout << "distance" << distance << endl;
            double weight = kernelFunction(distance);
            //cout << "weight" << weight << endl;
            // x' = x + xi * K(x-xi/h)
            for (int j = 0; j < dim_coords; j++) {
                next_pos_point.coords[j] += point_i.coords[j] * weight;
            }
            // total_weight of all points with respect to [point]
            // E K(x-xi/h)
            total_weight += weight;
        }
        //cout<<"total_weight: "<<total_weight<<endl;
        if (total_weight > 0) {
            // normalization
            const double total_weight_inv = 1.0 / total_weight;
            for (int i = 0; i < dim_coords; i++) {
                // x' = (x + xi * K(x-xi/h)) /E K(x-xi/h)
                next_pos_point.coords[i] *= total_weight_inv;
            }
        } else {
            cout << "Error: total_weight == 0, couldn't normalize." << endl;
        }
    }

    void mean_shift() {
        vector<bool> stop_moving(dataset.size(), false);
        double max_shift_distance;

        cout << "--- shifting points ---" << endl;
        Point<T> prev_point;
        Point<T> next_point;

        unsigned int iter;
        for (int i = 0; i < dataset.size(); i++) {
            iter = 0;
            if(i % 500 == 0) {
                cout << "point[" << i << "] ..." << endl;
            }
            prev_point = dataset[i];
            next_point.coords.resize(dim_coords);

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
            clusters[c].mode.coords.resize(dim_coords);
            if (shifted_point.euclidean_distance(clusters[c].mode) <= EPSILON_MODE) {
                shifted_point = clusters[c].mode;
                break;
            }
        }
        // create cluster with [mode] in [shifted_point]
        // whenever [shifted_point] doesn't belong to any cluster
        if (c == clusters.size()) {
            Cluster<T> new_cluster;
            new_cluster.mode.coords = shifted_point.coords;
            clusters.push_back(new_cluster);
            cout << "--- cluster found! --- NUM of clusters: " << clusters.size() << endl;
        }
    }
};

#endif //__MEAN_SHIFT_H__
