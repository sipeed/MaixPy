#ifndef _MS_ASR_TBL_H
#define _MS_ASR_TBL_H

#include <stdint.h>
#include <stddef.h>

#define MAX_VOCAB_CNT   1250

extern uint32_t lm_tbl_cnt;
extern char** am_vocab;
extern char* lm_tbl[MAX_VOCAB_CNT];
extern uint16_t am2lm[MAX_VOCAB_CNT];

extern const char digit_char[16];
extern const char* am_pny_vocab[408];
extern const char* am_pnytone_vocab[1250];

#endif
