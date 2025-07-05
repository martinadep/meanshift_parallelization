#ifndef __POINT_H__
#define __POINT_H__

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "utils.h" // Contains the definition of Point and DIM

#ifdef __cplusplus
extern "C" {
#endif

// Initializes a point by setting all dimensions to 0.0
void init_point(Point *p);

// Copies the values from the source point to the destination point
#pragma acc routine seq
void copy_point(const Point *source, Point *dest);

// Compares two points for equality within a tolerance
int compare_points(const Point *p1, const Point *p2);

// Divides each dimension of a point by a scalar
void divide_point(Point *p, double scalar);

// Prints a point to the standard output
void print_point(const Point *p);

// Writes a point to a file in a comma-separated format
void write_point_to_file(const Point *p, FILE *file);

#ifdef __cplusplus
}
#endif

#endif // __POINT_H__
