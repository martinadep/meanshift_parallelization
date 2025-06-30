#include "include/point.h"
#include "include/utils.h"
#include "include/mean_shift.h"
#include <stdio.h>
#include <stdlib.h>

#ifndef NUM_GANGS
#define NUM_GANGS 256
#endif
#ifndef NUM_WORKERS
#define NUM_WORKERS 32
#endif 

int acc_num_gangs = NUM_GANGS;
int acc_num_workers = NUM_WORKERS;

void print_acc_info() {
    int num_devices = 0;
    #pragma acc parallel
    {
        #pragma acc loop seq
        for (int i = 0; i < 1; i++) {
            if (i == 0) {
                #pragma acc atomic update
                num_devices++;
            }
        }
    }
    printf("OpenACC: Found %d device(s)\n", num_devices);

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

unsigned int shift_point_until_convergence(const Point *input_point, Point *output_point,
                                           const Point dataset[], unsigned int dataset_size,
                                           T bandwidth, T (*kernel_func)(T, T))
{
    Point prev_point;
    Point next_point;
    unsigned int iter = 0;
    int stop_moving = 0;

    copy_point(input_point, &prev_point);

    while (!stop_moving)
    {
        shift_single_point(&prev_point, &next_point, dataset, dataset_size, bandwidth, kernel_func);

        T shift_distance = euclidean_distance(&prev_point, &next_point);

        if (shift_distance <= EPSILON)
        {
            stop_moving = 1;
        }
        copy_point(&next_point, &prev_point);
        iter++;
    }
    copy_point(&prev_point, output_point);
    return iter;
}

void shift_single_point(const Point *point, Point *next_point,
                        const Point dataset[], unsigned int dataset_size,
                        T bandwidth, T (*kernel_func)(T, T))
{
    T total_weight = 0;
    Point point_i;
    init_point(&point_i);
    init_point(next_point);

    #pragma acc parallel loop reduction(+:total_weight) private(point_i)
    for (int i = 0; i < dataset_size; i++)
    {
        copy_point(&dataset[i], &point_i);
        T distance = euclidean_distance(point, &point_i);
        T weight = kernel_func(distance, bandwidth);

        #pragma acc atomic
        (*next_point)[0] += point_i[0] * weight;
        #pragma acc atomic
        (*next_point)[1] += point_i[1] * weight;
        #pragma acc atomic
        (*next_point)[2] += point_i[2] * weight;

        total_weight += weight;
    }

    if (total_weight > 0)
    {
        divide_point(next_point, total_weight);
    } else {
        fprintf(stderr, "Error: total_weight == 0, couldn't normalize.\n");
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
