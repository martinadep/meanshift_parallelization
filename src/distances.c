#include "include/utils.h"
T euclidean_distance(const Point *point1, const Point *point2) {
    T distance = 0;
    for (unsigned int i = 0; i < DIM; i++) {
        distance += (point1->coords[i] - point2->coords[i]) * (point1->coords[i] - point2->coords[i]);
    }
    return sqrt(distance);
}

T sqrd_euclidean_distance(const Point *point1, const Point *point2) {
    T distance = 0;
    for (unsigned int i = 0; i < DIM; i++) {
        distance += (point1->coords[i] - point2->coords[i])  * (point1->coords[i] - point2->coords[i]);
    }
    return distance;
}
