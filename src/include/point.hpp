//
// Created by marti on 28/03/2025.
//

#ifndef __POINT_H__
#define __POINT_H__

#include <cmath>
#include <iomanip>
#include <iostream>
#include "utils.hpp"

using namespace std;


void init_point(Point &p) {
    for(unsigned int i = 0; i < DIM; i++) {
        p.coords[i] = 0.0;
    }
}

void copy_point(const Point &source, Point &dest) {
    for(unsigned int i = 0; i < DIM; i++) {
        dest.coords[i] = source.coords[i];
    }
}

bool compare_points(const Point &p1, const Point &p2) {
    for (unsigned int i = 0; i < DIM; i++) {
        if (fabs(p1.coords[i] - p2.coords[i]) > 0.001) {
            return false;
        }
    }
    return true;
}

void divide_point(Point &p1, T scalar) {
    if (scalar == 0) {
        throw std::invalid_argument("Division by zero");
    }
    for (unsigned int i = 0; i < DIM; i++) {
        p1.coords[i] /= scalar;
    }
}

void print_point(const Point &p) {
    for (unsigned int i = 0; i < DIM; i++) {
        cout << setw(9) << setprecision(5) << p.coords[i];
    }
}
    
void write_point_to_file(const Point &p, FILE *file) {
    for (unsigned int i = 0; i < DIM; i++) {
        fprintf(file, "%d", (int)p.coords[i]);
        if (i < DIM - 1) {
            fprintf(file, ",");
        }
    }
    fprintf(file, "\n");
}

#endif //__POINT_H__
