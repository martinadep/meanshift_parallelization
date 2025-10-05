#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "include/utils.h" 
#include "include/point.h"

// Initializes a point by setting all dimensions to 0.0
#pragma acc routine seq
void init_point(Point *p) {
    for (unsigned int i = 0; i < DIM; i++) {
        p->coords[i] = 0.0;
    }
}

// Copies the values from the source point to the destination point
#pragma acc routine seq
void copy_point(const Point *source, Point *dest) {
    for (unsigned int i = 0; i < DIM; i++) {
        dest->coords[i] = source->coords[i];
    }
}

// Divides each dimension of a point by a scalar
#pragma acc routine seq
void divide_point(Point *p, double scalar) {
    if (scalar == 0) {
        printf("Error: Division by zero\n");
        return;
    }
    for (unsigned int i = 0; i < DIM; i++) {
        p->coords[i] /= scalar;
    }
}

// Prints a point to the standard output
#pragma acc routine seq
void print_point(const Point *p) {
    for (unsigned int i = 0; i < DIM; i++) {
        printf("%9.5f ", p->coords[i]);
    }
    printf("\n");
}

// Writes a point to a file in a comma-separated format
void write_point_to_file(const Point *p, FILE *file) {
    for (unsigned int i = 0; i < DIM; i++) {
        fprintf(file, "%d", (int)p->coords[i]);
        if (i < DIM - 1) {
            fprintf(file, ",");
        }
    }
    fprintf(file, "\n");
}
