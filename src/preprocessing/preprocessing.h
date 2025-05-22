#ifndef __PREPROCESSING_H__
#define __PREPROCESSING_H__
#include "../include/point.h"

#ifdef __cplusplus
extern "C" {
#endif


unsigned int preprocess_dataset(unsigned int dataset_size,
                        const Point dataset[], Point processed_dataset[],
                        int width, int height, int num_superpixels, double m);
                        
double slic_distance(const Point *p1, const Point *p2, 
    int x1, int y1, int x2, int y2, double S, double m);


#ifdef __cplusplus
}
#endif
#endif // __PREPROCESSING_H__