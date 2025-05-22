#include "include/utils.h"
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

// Perceptual distance in CIELAB space
T lab_distance(const Point *p1, const Point *p2) {
    // L* has range [0, 100] while a* and b* have range [-128, 127]
    // Weight L* differently than a* and b* to account for the different scales
    T deltaL = (*p1)[0] - (*p2)[0];
    T deltaA = (*p1)[1] - (*p2)[1];
    T deltaB = (*p1)[2] - (*p2)[2];
    
    // CIE76 Delta E formula
    return sqrt(deltaL*deltaL + deltaA*deltaA + deltaB*deltaB);
}

T calc_distance(const Point *p1, const Point *p2){
    #ifdef PREPROCESSING
    return lab_distance(p1, p2);
    #else
    return euclidean_distance(p1, p2);
    #endif
}
