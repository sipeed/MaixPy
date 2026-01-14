#ifndef __SP_ASR_UTILS_H
#define __SP_ASR_UTILS_H

#include <sys/time.h>
#include <time.h>
#include "stdint.h"

//CLOCK_MONOTONIC_COARSE  CLOCK_MONOTONIC
#define DBG_TIME_INIT()     struct timespec start,finish;clock_gettime(CLOCK_MONOTONIC,&start);
#define DBG_TIME_START()    clock_gettime(CLOCK_MONOTONIC,&start);
#define DBG_TIME(x)   {clock_gettime(CLOCK_MONOTONIC,&finish);printf("%s use %.3f ms\n", (x), (double)(utils_cal_dt_us(&start, &finish))/1000.0);clock_gettime(CLOCK_MONOTONIC,&start);}

#ifdef __cplusplus
extern "C"{
#endif

uint32_t utils_cal_dt_us(struct timespec *t0, struct timespec *t1);

#ifdef __cplusplus
}
#endif

#endif

