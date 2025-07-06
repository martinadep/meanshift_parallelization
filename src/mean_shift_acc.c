#include "include/point.h"
#include "include/utils.h"
#include "include/mean_shift.h"
#include <stdio.h>
#include <stdlib.h>
#include <openacc.h>

#ifndef NUM_GANGS
#define NUM_GANGS 256
#endif
#ifndef NUM_WORKERS
#define NUM_WORKERS 32
#endif 

int acc_num_gangs = NUM_GANGS;
int acc_num_workers = NUM_WORKERS;

void print_acc_info() {
    int num_devices = acc_get_num_devices(acc_device_nvidia);
    printf("OpenACC: Found %d NVIDIA device(s)\n", num_devices);

    char* dev_type = getenv("ACC_DEVICE_TYPE");
    printf("OpenACC: Device type: %s\n", dev_type ? dev_type : "default");
}

void mean_shift(unsigned int dataset_size, const Point dataset[],
                Point shifted_dataset[], T bandwidth,
                T (*kernel_func)(T, T), Point cluster_modes[],
                unsigned int *cluster_count)
{
    *cluster_count = 0;
    #ifdef DEBUG
    print_acc_info();
    #endif

    #ifndef DEBUG 
    printf("Debug: Beginning data transfer to device...\n");
    #endif

    #pragma acc data copyin(dataset[0:dataset_size]) copyout(shifted_dataset[0:dataset_size])
    {
        #ifdef DEBUG
        printf("Debug: Data transfer complete, starting computation\n");
        #endif

        #pragma acc parallel loop num_gangs(acc_num_gangs) num_workers(acc_num_workers)
        for (int i = 0; i < dataset_size; i++) {
            shift_point_until_convergence(&dataset[i], &shifted_dataset[i],
                                          dataset, dataset_size, bandwidth, kernel_func);
        }
    }

    for (int i = 0; i < dataset_size; i++) {
        assign_clusters(&shifted_dataset[i], cluster_modes, cluster_count);
    }
}

#pragma acc routine seq
unsigned int shift_point_until_convergence_acc(const Point *input_point, Point *output_point,
                                           const Point dataset[], unsigned int dataset_size,
                                           T bandwidth)
{
    Point prev_point;
    Point next_point;
    unsigned int iter = 0;
    int stop_moving = 0;

    copy_point(input_point, &prev_point);

    while (!stop_moving)
    {
        shift_single_point_acc(&prev_point, &next_point, dataset, dataset_size, bandwidth);

        T shift_distance = euclidean_distance(&prev_point, &next_point);

        if (shift_distance <= EPSILON)
        {
            stop_moving = 1;
        }
        copy_point(&next_point, &prev_point);
        iter++;
    }
    copy_point(&prev_point, output_point);
    #ifdef DEBUG
    printf("Debug: Point converged after %u iterations\n", iter);
    printf("inout_point:");
    print_point(output_point);
    printf("output_point:");
    print_point(input_point);
    #endif
    return iter;
}

#pragma acc routine seq
void shift_single_point_acc(const Point *point, Point *next_point,
                        const Point dataset[], unsigned int dataset_size,
                        T bandwidth)
{
    T total_weight = 0;
    T sum_coords[3] = {0.0, 0.0, 0.0};
    Point point_i;

    for (int i = 0; i < dataset_size; i++)
    {
        copy_point(&dataset[i], &point_i);
        T distance = euclidean_distance(point, &point_i);
        T weight = gaussian_kernel(distance, bandwidth); //kernel_func(distance, bandwidth);

        sum_coords[0] += point_i.coords[0] * weight;
        sum_coords[1] += point_i.coords[1] * weight;
        sum_coords[2] += point_i.coords[2] * weight;

        total_weight += weight;
    }

    if (total_weight > 0)
    {
        next_point->coords[0] = sum_coords[0] / total_weight;
        next_point->coords[1] = sum_coords[1] / total_weight;
        next_point->coords[2] = sum_coords[2] / total_weight;
    }
    else
    {
        next_point->coords[0] = NAN;
        next_point->coords[1] = NAN;
        next_point->coords[2] = NAN;
    }
}


void assign_clusters(Point *shifted_point, Point cluster_modes[],
                     unsigned int *cluster_count)
{
    int c = 0;
    for (; c < *cluster_count; c++)
    {
        T distance_from_cluster = euclidean_distance(shifted_point, &cluster_modes[c]);

        if (distance_from_cluster <= CLUSTER_EPSILON)
        {
            copy_point(&cluster_modes[c], shifted_point);
            break;
        }
    }
    if (c == *cluster_count)
    {
        copy_point(shifted_point, &cluster_modes[c]);
        (*cluster_count)++;
    }
}