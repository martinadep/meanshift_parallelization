#ifndef __TIMING_H__
#define __TIMING_H__
#include <stdio.h>
#include <time.h>

#ifdef TIMING_BREAKDOWN
// Timer definition
#define TIMER_DEF(label) \
    static clock_t start_##label, end_##label; \
    static double duration_##label = 0.0;

// Timer start
#define TIMER_START(label) \
    start_##label = clock();

// Duration calculation
#define TIMER_ELAPSED(label) \
    end_##label = clock(); \
    duration_##label = ((double)(end_##label - start_##label)) / CLOCKS_PER_SEC;

// Print elapsed time
#define TIMER_PRINT(label) \
    printf(#label " execution time: %f s\n", duration_##label);

// Define the total time spent in the function
#define TIMER_SUM_DEF(label) \
    TIMER_DEF(label) \
    static double total_##label##_time = 0.0;

// Accumulates the total time spent in the function
#define TIMER_SUM(label) \
    TIMER_ELAPSED(label) \
    total_##label##_time += duration_##label;

// Print the total time spent in the function
#define TIMER_SUM_PRINT(label) \
    printf(#label " total execution time: %f s\n", total_##label##_time);

#else
#define TIMER_DEF(label)
#define TIMER_START(label)
#define TIMER_ELAPSED(label)
#define TIMER_PRINT(label)
#define TIMER_SUM_DEF(label)
#define TIMER_SUM(label)
#define TIMER_SUM_PRINT(label)
#endif

#ifdef TOTAL_TIMING

#define TOTAL_TIMER_START(label) \
    clock_t start_##label, end_##label; \
    double duration_##label = 0.0; \
    start_##label = clock();

#define TOTAL_TIMER_STOP(label) \
    end_##label = clock(); \
    duration_##label = ((double)(end_##label - start_##label)) / CLOCKS_PER_SEC; \
    printf(#label " execution time: %f s\n", duration_##label);

#endif
#endif // __TIMING_H__