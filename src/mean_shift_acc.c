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
    print_acc_info();
    printf("Debug: Beginning data transfer to device...\n");

    #pragma acc data copyin(dataset[0:dataset_size]) copyout(shifted_dataset[0:dataset_size])
    {
        printf("Debug: Data transfer complete, starting computation\n");
        #pragma acc parallel loop num_gangs(acc_num_gangs) num_workers(acc_num_workers)
        for (int i = 0; i < dataset_size; i++) {
            shift_point_until_convergence_acc(&dataset[i], &shifted_dataset[i],
                                        dataset, dataset_size, bandwidth);
        }
        #pragma acc update self(shifted_dataset[0:dataset_size])
	}
    
    printf("Debug: Dataset point [0] outside loop");
    print_point(&dataset[0]);
    printf("Debug: Shifted Dataset point [0] outside loop");
    print_point(&shifted_dataset[0]);;

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
    return iter;
}
#pragma acc routine seq
void shift_single_point_acc(const Point *point, Point *next_point,
                        const Point dataset[], unsigned int dataset_size,
                        T bandwidth)
{
    T total_weight = 0;
    Point point_i;
    init_point(&point_i);
    init_point(next_point);

    for (int i = 0; i < dataset_size; i++)
    {
        copy_point(&dataset[i], &point_i);
        T distance = euclidean_distance(point, &point_i);
        T weight = gaussian_kernel(distance, bandwidth);
        
        (*next_point)[0] += point_i[0] * weight;
        (*next_point)[1] += point_i[1] * weight;
        (*next_point)[2] += point_i[2] * weight;

        total_weight += weight;
    }

    if (total_weight > 0)
    {
        divide_point(next_point, total_weight);
    } else {
        printf("Error: total_weight == 0, couldn't normalize.\n");
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
