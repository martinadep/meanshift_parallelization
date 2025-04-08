#ifndef __TIMING_HPP__
#define __TIMING_HPP__

#define START_TIME(name) \
struct timeval start_##name, end_##name; \
gettimeofday(&start_##name, NULL);

#define END_TIME(name) \
gettimeofday(&end_##name, NULL); \
long seconds_##name = end_##name.tv_sec - start_##name.tv_sec; \
long micros_##name = end_##name.tv_usec - start_##name.tv_usec; \
double elapsed_##name = seconds_##name + micros_##name * 1e-6; \
std::cout << " Elapsed time: " << elapsed_##name << " seconds" << std::endl;

#define SUM_TIME(name) \
gettimeofday(&end_##name, NULL); \
::total_##name##_time += (end_##name.tv_sec - start_##name.tv_sec) + \
                        (end_##name.tv_usec - start_##name.tv_usec) * 1e-6;
extern double total_kernel_time;
extern double total_eucl_dist_time;
extern double total_point_update_time;
#endif
