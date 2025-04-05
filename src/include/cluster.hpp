//
// Created by marti on 30/03/2025.
//

#ifndef __CLUSTER_H__
#define __CLUSTER_H__
#include <vector>

#include "point.hpp"

using namespace std;

template<typename T>

class Cluster {
public:
    Point<T> mode;

    Cluster() = default;
    Cluster(const Point<T> &_center) : mode(_center){
    }
    Point<T> getCenter() const {
        return mode;
    }

};

#endif //__CLUSTER_H__
