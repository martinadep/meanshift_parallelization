#include "include/utils.h"
#pragma acc routine seq
T euclidean_distance(const Point *point1, const Point *point2) {
    T distance = 0;
    for (unsigned int i = 0; i < DIM; i++) {
        distance += ((*point1)[i] - (*point2)[i]) * ((*point1)[i] - (*point2)[i]);
    }
    return sqrt(distance);
}

T sqrd_euclidean_distance(const Point *point1, const Point *point2) {
    T distance = 0;
    for (unsigned int i = 0; i < DIM; i++) {
        distance += ((*point1)[i] - (*point2)[i]) * ((*point1)[i] - (*point2)[i]);
    }
    return distance;
}
