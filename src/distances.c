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

// // Perceptual distance in CIELAB space
// T lab_distance(const Point *p1, const Point *p2) {
//     // L* has range [0, 100] while a* and b* have range [-128, 127]
//     // Weight L* differently than a* and b* to account for the different scales
//     T deltaL = (*p1)[0] - (*p2)[0];
//     T deltaA = (*p1)[1] - (*p2)[1];
//     T deltaB = (*p1)[2] - (*p2)[2];
    
//     // CIE76 Delta E formula
//     return sqrt(deltaL*deltaL + deltaA*deltaA + deltaB*deltaB);
// }

// Implementazione migliorata della distanza CIELAB (CIE94)
T lab_distance(const Point *p1, const Point *p2) {
    // Estrai componenti LAB
    T L1 = (*p1)[0];
    T a1 = (*p1)[1];
    T b1 = (*p1)[2];
    
    T L2 = (*p2)[0];
    T a2 = (*p2)[1]; 
    T b2 = (*p2)[2];
    
    T deltaL = L1 - L2;
    T deltaA = a1 - a2;
    T deltaB = b1 - b2;
    
    // Calcola coordinate in spazio C*h*
    T C1 = sqrt(a1*a1 + b1*b1);
    T C2 = sqrt(a2*a2 + b2*b2);
    T deltaC = C1 - C2;
    
    // Formula Delta E94
    T deltaH_squared = deltaA*deltaA + deltaB*deltaB - deltaC*deltaC;
    T deltaH = (deltaH_squared > 0) ? sqrt(deltaH_squared) : 0;
    
    // Costanti per immagini (kL=1, k1=0.045, k2=0.015)
    T SL = 1.0;
    T SC = 1.0 + 0.045 * C1;
    T SH = 1.0 + 0.015 * C1;
    
    T term1 = deltaL / SL;
    T term2 = deltaC / SC;
    T term3 = deltaH / SH;
    
    return sqrt(term1*term1 + term2*term2 + term3*term3);
}

T calc_distance(const Point *p1, const Point *p2){
    #ifdef PREPROCESSING
    return lab_distance(p1, p2);
    #else
    return euclidean_distance(p1, p2);
    #endif
}
