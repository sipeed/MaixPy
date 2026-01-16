#ifndef _ASR_DECODE_KWS_H
#define _ASR_DECODE_KWS_H

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "ms_asr.h"
#include "ms_asr_cfg.h"

/*****************************************************************************/
// Macro definitions
/*****************************************************************************/
#define KW_LOG_LEN 10  //最多记录的历史拼音格数量

/*****************************************************************************/
// Enums
/*****************************************************************************/


/*****************************************************************************/
// Types
/*****************************************************************************/
typedef void (*decoder_cb_t)(void* data, int cnt);

typedef struct {
	uint16_t pny[ASR_KW_MAX_PNY];	//每个唤醒词最多 KW_MAX_PNY 个字
	uint16_t pny_cnt;			    //该唤醒词的字数
	char*    name;                  //唤醒词的字符表示
	float    gate;					//门限值
}asr_kw_t;


/*****************************************************************************/
// Functions
/*****************************************************************************/

#ifdef __cplusplus
extern "C"{
#endif
int  decoder_kws_init(decoder_cb_t decoder_cb, size_t* decoder_args, int decoder_argc);
void decoder_kws_deinit(void);
void decoder_kws_run(pnyp_t* pnyp_list);
void decoder_kws_clear(void);
int decoder_kws_reg_similar(char* pny, char** similar_pnys, int similar_cnt);

#ifdef __cplusplus
}
#endif

#endif

