#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "include/utils.h" 
#include "include/point.h"

// Initializes a point by setting all dimensions to 0.0
void init_point(Point *p) {
    for (unsigned int i = 0; i < DIM; i++) {
        (*p)[i] = 0.0;
    }
}

// Copies the values from the source point to the destination point
void copy_point(const Point *source, Point *dest) {
    for (unsigned int i = 0; i < DIM; i++) {
        (*dest)[i] = (*source)[i];
    }
}

// Compares two points for equality within a tolerance
int compare_points(const Point *p1, const Point *p2) {
    for (unsigned int i = 0; i < DIM; i++) {
        if (fabs((*p1)[i] - (*p2)[i]) > 0.001) {
            return 0; // Points are not equal
        }
    }
    return 1; // Points are equal
}

// Divides each dimension of a point by a scalar
void divide_point(Point *p, double scalar) {
    if (scalar == 0) {
        fprintf(stderr, "Error: Division by zero\n");
        exit(EXIT_FAILURE);
    }
    for (unsigned int i = 0; i < DIM; i++) {
        (*p)[i] /= scalar;
    }
}

// Prints a point to the standard output
void print_point(const Point *p) {
    for (unsigned int i = 0; i < DIM; i++) {
        printf("%9.5f ", (*p)[i]);
    }
    printf("\n");
}

// Writes a point to a file in a comma-separated format
void write_point_to_file(const Point *p, FILE *file) {
    for (unsigned int i = 0; i < DIM; i++) {
        fprintf(file, "%d", (int)(*p)[i]);
        if (i < DIM - 1) {
            fprintf(file, ",");
        }
    }
    fprintf(file, "\n");
}
