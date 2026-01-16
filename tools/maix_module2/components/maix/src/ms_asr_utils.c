#include "ms_asr_utils.h"

#ifdef __cplusplus
extern "C"{
#endif
//note: max 4295s
uint32_t utils_cal_dt_us(struct timespec *t0, struct timespec *t1)
{
    uint32_t dt;
    if(t1->tv_nsec < t0->tv_nsec) {
        long tmp = t1->tv_nsec + 1e9;
        long d_ns = tmp - t0->tv_nsec;
        long d_s  = t1->tv_sec-1-t0->tv_sec;
        dt = (uint32_t)(d_s*1000000+d_ns/1000);
    } else {
        long d_ns = t1->tv_nsec - t0->tv_nsec;
        long d_s  = t1->tv_sec-t0->tv_sec;
        dt = (uint32_t)(d_s*1000000+d_ns/1000);
    }
    return dt;
}

#ifdef __cplusplus
}
#endif
