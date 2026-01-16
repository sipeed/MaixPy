#include <float.h>
#include "math.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "string.h"
#include "decoder_kws.h"
#include "ms_asr.h"
#include "ms_asr_cfg.h"
#include "ms_asr_utils.h"

#include <vector> 
#include<algorithm>
using namespace std;

/*****************************************************************************/
// Macro
/*****************************************************************************/
#define DEBUG_LINE()                              \
    do                                             \
    {                                              \
        printf("[decode] L%d\r\n", __LINE__); \
    } while(0)

#define TOK_N       (5)     //toks的剪枝数量
#define BG_P        (1e-6)
#define SIMILAR_CNT (10)

#define TOK_DBG 0

/*****************************************************************************/
// Types
/*****************************************************************************/
typedef struct {
	int   cur_idx;
	float cur_p;
	int   first_t;
    int   blank_flag;
#if TOK_DBG
    vector<const char*> path;
#endif
}kws_tok_t;

/*****************************************************************************/
// Local variable
/*****************************************************************************/
static decoder_cb_t l_decoder_cb=NULL;
static asr_kw_t l_kw_tbl[ASR_KW_MAX];
static int l_kw_cnt = 0;
static int l_init_flag = 0;
static int l_log_len = 0;
static pnyp_t l_log[100][BEAM_CNT];  //记录最近的l_log_len格数据，每格64ms
static int l_log_idx = 0;
static int l_tick = 0;
static int l_kw_res_tick[ASR_KW_MAX];	//记录所有关键词上次识别的tick，防止在滑窗时重复识别

static uint16_t* l_similar_dict = NULL;

extern int ms_asr_dbg_flag;


/*******************Decoder KWS private **********************/
static int pny2idx(char* pny)
{
    int idx = -1;
    for(int i=0; i<asrp.vocab_cnt; i++){
        if(strcmp(pny, am_vocab[i])==0) {
            idx = i; 
        }
    }
    return idx;
}


static int _parse_kw(char* kw_str, float pgate, asr_kw_t* kw)
{
    int len = strlen(kw_str);
    char str_pny[20];
    int pny_i = 0;
    for(char* p = kw_str; p < kw_str+len; )
    {
        char* p_space = strchr(p, ' ');
        if(!p_space) p_space = kw_str+len;
        memcpy(str_pny, p, p_space-p);
        str_pny[p_space-p] = 0;
        
        int idx = pny2idx(str_pny);
        if(idx<0){
            return -1;
        } else {
            kw->pny[pny_i] = idx;
        }

        p = p_space+1;
        pny_i+=1;
    }
    kw->pny_cnt = pny_i;
    kw->name = kw_str;
    kw->gate = pgate;
    return 0;
}

static int is_same_pny(int kw_pny, int rec_pny)
{
    if(rec_pny == kw_pny) return 1;

    int match_flag = 0;
    uint16_t* similar_pnys = l_similar_dict+kw_pny*SIMILAR_CNT;
    for(int i=0; i<SIMILAR_CNT; i++){
        if(similar_pnys[i] == 0xffff){
            break;
        }
        if(rec_pny == similar_pnys[i]) {
            match_flag = 1;
            break;
        }
    }
    return match_flag;
}

static float cal_multip(kws_tok_t* tok, pnyp_t* pnyps, asr_kw_t* kw)
{
    float p = tok->cur_p;
    if (tok->cur_idx > 0){  //至少识别了一个pny才能合并pny
        int last_idx = tok->cur_idx-1;
        int match_flag = 0;
        float psum=0;
        for(int i=0; i<BEAM_CNT; i++){
            pnyp_t* pnyp = &pnyps[i];
            float pp;
            if(is_same_pny(kw->pny[last_idx], pnyp->idx)){
                if(pnyp->p == 0){
                    pp = BG_P;
                } else {
                    pp = pnyp->p;
                }
                psum += pp;
                match_flag = 1;
            }
        }
        if(match_flag==0){
            p *= BG_P;
        } else {
            p *= psum;
        }
    } else {
        p = 0;
    }
    return p;
}

static float cal_blankp(kws_tok_t* tok, pnyp_t* pnyps, asr_kw_t* kw)
{
    int match_flag = 0;
    float p = tok->cur_p;
    for(int i=0; i<BEAM_CNT; i++){
        pnyp_t* pnyp = &pnyps[i];
        float pp;
        if(pnyp->idx == asrp.vocab_cnt-1){
            if(pnyp->p == 0){
                pp = BG_P;
            } else {
                pp = pnyp->p;
            }
            p *= pp;
            match_flag = 1;
        }
    }
    if(match_flag==0){
        p *= BG_P;
    } 
    return p;
}

static float cal_similarp(kws_tok_t* tok, pnyp_t* pnyps, asr_kw_t* kw)
{
    int match_flag = 0;
    int cur_idx = tok->cur_idx;
    float p = tok->cur_p;
    float psum = 0;
    for(int i=0; i<BEAM_CNT; i++){
        pnyp_t* pnyp = &pnyps[i];
        float pp;
        if(is_same_pny(kw->pny[cur_idx], pnyp->idx)){
            if(pnyp->p == 0){
                pp = BG_P;
            } else {
                pp = pnyp->p;
            }
            psum += pp;
            match_flag = 1;
        }
    }
    if(match_flag==0){
        p *= BG_P;
    } else {
        p *= psum;
    }
    return p;
}


static bool tok_sort_func(kws_tok_t &t1, kws_tok_t &t2)
{
	return t1.cur_p > t2.cur_p; 
}

#if TOK_DBG
static void dump_tok(kws_tok_t &tok)
{
    printf("  cur_idx=%d, cur_p=%.3f, blank_flag=%d:  ", tok.cur_idx, tok.cur_p, tok.blank_flag);
    for(int j=0; j<tok.path.size() ; j++){
        printf("%s ", tok.path[j]);
    }
    printf("\n");
    return;
}
#endif


static void cal_frame_kw(pnyp_t* pnyp_list, int frame_t, asr_kw_t* kw, float*_p, int* _tick)
{
    float p;
    vector<kws_tok_t>toks;
#if TOK_DBG
    vector<const char*> path;
    kws_tok_t tok0 = {0,1,-1, 1, path};
#else
    kws_tok_t tok0 = {0,1,-1, 1};
#endif
    //printf("kw pny_idx=%d %d %d %d\n", kw->pny[0], kw->pny[1], kw->pny[2], kw->pny[3]);
    toks.push_back(tok0);
    for(int t=0; t < frame_t; t++) {
        vector<kws_tok_t>new_toks;
        for(int i =0; i < toks.size(); i++){
            if(toks[i].cur_idx >= kw->pny_cnt){
                new_toks.push_back(toks[i]);
            } else if(toks[i].cur_p>0){ //未结束的有效tok
                //合并相同拼音
                p = cal_multip(&toks[i], pnyp_list+t*BEAM_CNT, kw);
                if(p>0){
                #if !TOK_DBG
                    kws_tok_t tok = {toks[i].cur_idx, p, toks[i].first_t, 0};
                #else
                    vector<const char*> new_path = toks[i].path;
                    uint16_t pny_idx = kw->pny[toks[i].cur_idx-1];
                    new_path.push_back(am_vocab[pny_idx]);
                    kws_tok_t tok = {toks[i].cur_idx, p, toks[i].first_t, 0, new_path};
                #endif
                    new_toks.push_back(tok);
                }
                //合并blank
                p = cal_blankp(&toks[i], pnyp_list+t*BEAM_CNT, kw);
                if(p>0){
                    int blank_flag = 0;
                    if(toks[i].cur_idx == 0){
                        p = toks[i].cur_p;
                        blank_flag = 1;
                    }
                #if !TOK_DBG
                    kws_tok_t tok = {toks[i].cur_idx, p, toks[i].first_t, blank_flag};
                #else
                    vector<const char*> new_path = toks[i].path;
                    new_path.push_back(am_vocab[asrp.vocab_cnt-1]);
                    kws_tok_t tok = {toks[i].cur_idx, p, toks[i].first_t, blank_flag, new_path};
                #endif
                    new_toks.push_back(tok);
                }
                //合并近音词
                p = cal_similarp(&toks[i], pnyp_list+t*BEAM_CNT, kw);
                if(p>0){
                    int first_t;
                    if(toks[i].cur_idx == 0){
                        first_t = t;
                    } else {
                        first_t = toks[i].first_t;
                    }
                #if !TOK_DBG
                    kws_tok_t tok = {toks[i].cur_idx+1, p, first_t, 0};
                #else
                    vector<const char*> new_path = toks[i].path;
                    uint16_t pny_idx = kw->pny[toks[i].cur_idx];
                    new_path.push_back(am_vocab[pny_idx]);
                    kws_tok_t tok = {toks[i].cur_idx+1, p, first_t, 0, new_path};
                    //dump_tok(tok);
                #endif
                    new_toks.push_back(tok);
                }
            }
        }
        //printf("Total %d new toks\n", new_toks.size());
        //去除所有全部都blank的tok
        for(int i =0; i < new_toks.size(); ){
            if(new_toks[i].blank_flag == 1){
                new_toks.erase(std::begin(new_toks)+i);
                //删除后下一个元素到了i处，所以无需自增i
            } else {
                i++;
            }
        }
        //对所有有效tok进行剪枝，从最多3*TOK_N+2 剪刀TOK_N个
        sort(new_toks.begin(), new_toks.end(), tok_sort_func);
        int topn = new_toks.size()>TOK_N ? TOK_N : new_toks.size();
        int end_cnt = 0;
        toks.clear();
        #if TOK_DBG
            printf("DBG T=%d:\n", t);
        #endif
        for(int i = 0; i < topn; i++){
            toks.push_back(new_toks[i]);
            if(new_toks[i].cur_idx == kw->pny_cnt){
                end_cnt += 1;
            }
        #if TOK_DBG
            printf("tok%d:", i);
            dump_tok(new_toks[i]);
        #endif
        }
        if(end_cnt >= TOK_N){
            //printf("All toks reach end! exit!\n");
            break;  
        }
        //重新加回一个全blank的tok
    #if TOK_DBG
        vector<const char*> new_path;
        for(int i=0; i<t+1; i++){
            new_path.push_back((char*)"^");
        }
        kws_tok_t blank_tok = {0,1,-1, 1, new_path};
    #else
        kws_tok_t blank_tok = {0,1,-1, 1};
    #endif
        toks.push_back(blank_tok);
    }
    //分别统计各个起始位置处的对应关键词的概率之和
    vector<float> sump;
    vector<int> first_t;
    for(int i =0; i < toks.size(); i++){
        if(toks[i].cur_idx >= kw->pny_cnt){
            int _first_t = toks[i].first_t;
            int first_t_idx = -1;
            for(int j=0; j < first_t.size(); j++){
                if(_first_t == first_t[j]){
                    first_t_idx = j;
                    break;
                }
            }
            if(first_t_idx >= 0){
                sump[first_t_idx] += toks[i].cur_p;
            } else {
                first_t.push_back(toks[i].first_t);
                sump.push_back(toks[i].cur_p);
            }
        }
    }
    //返回概率最大位置
    if(sump.size()>0){
        int max_i = -1;
        float max_p = -1;
        for(int i=0; i < sump.size(); i++){
            if(sump[i]>max_p){
                max_i = i;
                max_p = sump[i];
            }
        }
        *_p = max_p;
        *_tick = first_t[max_i];
    }else{
        *_p = 0;
        *_tick = -1;
    }

    return;
}

static void push_pny(pnyp_t* pnyp_list, int cnt)
{
	memmove(l_log, &l_log[cnt], (l_log_len-cnt)*BEAM_CNT*sizeof(pnyp_t));
	memcpy(&l_log[l_log_len-cnt], pnyp_list, cnt*BEAM_CNT*sizeof(pnyp_t));
	return;
}

static void do_auto_similar(void)
{
    for(int i=0; i<asrp.vocab_cnt; i++){
        const char* pny = am_vocab[i];
        int len = strlen(pny);
        char pny_strip[16];
        strcpy(pny_strip, pny);
        if(pny[len-1]>='0' && pny[len-1]<='9'){
            pny_strip[len-1] = 0; //去掉最后的音调
        }
        len = strlen(pny_strip);
        int s_idx = 0;
        int idx;
        idx = pny2idx(pny_strip);   //轻声
        if(idx>=0) {l_similar_dict[i*SIMILAR_CNT+s_idx] = idx; s_idx++;}
        pny_strip[len] = '1';  pny_strip[len+1] = 0;  
        idx = pny2idx(pny_strip);   //一声
        if(idx>=0) {l_similar_dict[i*SIMILAR_CNT+s_idx] = idx; s_idx++;}
        pny_strip[len] = '2';  pny_strip[len+1] = 0;  
        idx = pny2idx(pny_strip);   //二声
        if(idx>=0) {l_similar_dict[i*SIMILAR_CNT+s_idx] = idx; s_idx++;}
        pny_strip[len] = '3';  pny_strip[len+1] = 0;  
        idx = pny2idx(pny_strip);   //三声
        if(idx>=0) {l_similar_dict[i*SIMILAR_CNT+s_idx] = idx; s_idx++;}
        pny_strip[len] = '4';  pny_strip[len+1] = 0;  
        idx = pny2idx(pny_strip);   //四声
        if(idx>=0) {l_similar_dict[i*SIMILAR_CNT+s_idx] = idx; s_idx++;}
    }
    /*for(int i=0; i<asrp.vocab_cnt; i++){
        printf("%04d %7s: ", i, am_vocab[i]);
        for(int j=0; j<SIMILAR_CNT; j++){
            if(l_similar_dict[i*SIMILAR_CNT+j] != 0xffff) {
                printf("%7s,", am_vocab[l_similar_dict[i*SIMILAR_CNT+j]]);
            } else {
                break;
            }
        }
        printf("\n");
    }*/
    return;
}


/*****************************Decoder KWS public**********************************/
/**********************extern for C*********************************/

extern "C"{
int  decoder_kws_init(decoder_cb_t decoder_cb, size_t* decoder_args, int decoder_argc)
{
    int res;
    l_log_len = ((1024-1)/8/8/asrp.model_core_len+1)*asrp.model_core_len;
    printf("kws log 2.048s, len %d\n", l_log_len);

    l_decoder_cb = decoder_cb;
    char** kw_strs = (char**)decoder_args[0];
    float* p_gate = (float*)decoder_args[1];
    l_kw_cnt = (size_t)decoder_args[2];
    size_t auto_similar = (size_t)decoder_args[3];
    if(l_kw_cnt>ASR_KW_MAX) {
        printf("cnt exceed ASR_KW_MAX!\n");
        return -1;
    }
    printf("decoder_kws_init get %d kws\n", l_kw_cnt);
    for(int i=0; i <l_kw_cnt; i++){
        asr_kw_t* kw = &l_kw_tbl[i];
        res = _parse_kw(kw_strs[i], p_gate[i], kw);
        if(res != 0){
            printf("parse kws %s error!\n", kw_strs[i]);
            l_decoder_cb = NULL;
            l_kw_cnt = 0;
            return -1;
        }
        printf("  %02d, %s\n", i, kw->name);
    }
    l_similar_dict = (uint16_t*)malloc(sizeof(uint16_t)*asrp.vocab_cnt*SIMILAR_CNT);
    if(l_similar_dict == NULL) {
        printf("alloc l_similar_dict failed!\n");
        return -1;
    }
    memset(l_similar_dict, 0xff, sizeof(uint16_t)*asrp.vocab_cnt*SIMILAR_CNT);
    if(auto_similar) do_auto_similar();
    l_init_flag = 1;
    decoder_kws_clear();
    return 0;
}

void decoder_kws_deinit(void)
{
    if(l_init_flag == 1){
        decoder_kws_clear();
        free(l_similar_dict);
        l_similar_dict = NULL;
        l_decoder_cb = NULL;
        l_init_flag = 0;
    }
	return;
}

void decoder_kws_run(pnyp_t* pnyp_list)
{
	float kw_res[ASR_KW_MAX];
	int kw_res_cnt;
    
    if(l_decoder_cb) {
        DBG_TIME_INIT();DBG_TIME_START();
        push_pny(pnyp_list, asrp.model_core_len);	//推入历史拼音列表
        //printf("###l_kw_cnt=%d, l_log_len=%d\n", l_kw_cnt, l_log_len);
		for(int i=0; i < l_kw_cnt; i++) {
			float p; int tick;
			cal_frame_kw((pnyp_t*)l_log, l_log_len, &l_kw_tbl[i], &p, &tick);
            //cal_frame_kw(pnyp_t* pnyp_list, int frame_t, asr_kw_t* kw, float*_p, int* _tick)
			// 检查重复性，这里的4是随便写的一个数，预留余量
			if((l_kw_res_tick[i] >= 0) && ((l_tick + tick) < l_kw_res_tick[i]+4)){
				kw_res[i] = -1.0*p; //标记是重复的
			} else {
				kw_res[i] = p;
                if(p >= l_kw_tbl[i].gate) {
				    l_kw_res_tick[i] = l_tick + tick;
                } else {
                    l_kw_res_tick[i] = 0;   //非有效概率，则清零，方便下次更大值唤醒
                }
			}
		}
        if(ms_asr_dbg_flag&DBGT_KWS)DBG_TIME("KWS");
        l_decoder_cb(kw_res, l_kw_cnt);//关键词回调	
    }
    l_tick += asrp.model_core_len;
    return;
}

void decoder_kws_clear(void)
{
    if(l_init_flag){
        l_log_idx = 0;
        for(int t=0; t<KW_LOG_LEN; t++){    //重置全部为blank
            pnyp_t* pnyp = &l_log[t][0];
            pnyp->idx = asrp.vocab_cnt-1;
            pnyp->p   = 1.0;
            for(int i=1; i<BEAM_CNT;i++) {
                pnyp_t* pnyp = &l_log[t][i];
                pnyp->idx = i;
                pnyp->p   = 0.0;
            }
        }
        memset(l_log, 0, sizeof(pnyp_t)*BEAM_CNT*KW_LOG_LEN);
		l_tick = 0;
		for(int i=0; i<ASR_KW_MAX; i++){
			l_kw_res_tick[i] = -1;
		}
    }
    return;
}

int decoder_kws_reg_similar(char* pny, char** similar_pnys, int similar_cnt)
{
    uint16_t similar_idxs[SIMILAR_CNT];
    int pny_idx = pny2idx(pny);
    if(pny_idx < 0) return -1;
    if(similar_cnt > SIMILAR_CNT) return -1;
    for(int i=0; i < similar_cnt; i++){
        int idx = pny2idx(similar_pnys[i]);
        if(idx < 0) { //出现非法pny，则清空之前的设置
            memset(l_similar_dict+pny_idx*SIMILAR_CNT, 0xff, sizeof(uint16_t)*SIMILAR_CNT);
            return -1;
        }
        l_similar_dict[pny_idx*SIMILAR_CNT+i] = idx;
    }
    return 0;
}


}

