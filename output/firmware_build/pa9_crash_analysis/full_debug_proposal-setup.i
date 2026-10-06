# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\cpu\\br23\\setup.c"
# 1 "<built-in>" 1
# 1 "<built-in>" 3
# 290 "<built-in>" 3
# 1 "<command line>" 1
# 1 "<built-in>" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\cpu\\br23\\setup.c" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/includes.h" 1



# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/cpu.h" 1





# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/br23.h" 1
# 36 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/br23.h"
typedef struct {
    volatile unsigned int CON;
    volatile unsigned int BAUD;
    volatile unsigned int CODE;
    volatile unsigned int BASE_ADR;
    volatile unsigned int QUCNT;
} JL_SFC_TypeDef;





typedef struct {
    volatile unsigned int CON;
    volatile unsigned int KEY;
    volatile unsigned int UNENC_ADRH;
    volatile unsigned int UNENC_ADRL;
    volatile unsigned int LENC_ADRH;
    volatile unsigned int LENC_ADRL;
} JL_SFCENC_TypeDef;





typedef struct {
    volatile unsigned int CON;
    volatile unsigned int BAUD;
    volatile unsigned int QUCNT;
} JL_PSRAM_TypeDef;





typedef struct {
    volatile unsigned int CON;
    volatile unsigned int ADR;
} JL_DCP_TypeDef;






typedef struct {
    volatile unsigned int CON0;
    volatile unsigned int CON1;
    volatile unsigned int DATAI_ADR;
    volatile unsigned int DATAO_ADR;
    volatile unsigned int DATA_LEN;
    volatile unsigned int FLT_ADR;

} JL_EQ_TypeDef;





typedef struct {
    volatile unsigned int CON0;
    volatile unsigned int CON1;
    volatile unsigned int CON2;
    volatile unsigned int CON3;
    volatile unsigned int IDAT_ADR;
    volatile unsigned int IDAT_LEN;
    volatile unsigned int ODAT_ADR;
    volatile unsigned int ODAT_LEN;
    volatile unsigned int FLTB_ADR;
} JL_SRC_TypeDef;





typedef struct {
    volatile unsigned int CON;
    volatile unsigned int BASE;
    volatile unsigned int ADC_CON;
    volatile unsigned int ADC_CON1;
    volatile unsigned int HF_CON0;
    volatile unsigned int HF_CON1;
    volatile unsigned int HF_CRAM;
    volatile unsigned int HF_CRAM2;
    volatile unsigned int HF_DRAM;
    volatile unsigned int LF_CON;
    volatile unsigned int LF_RES;
    volatile unsigned int FMRX_CON4;
    volatile unsigned int FMRX_CON5;


    volatile unsigned int TX_CON0;
    volatile unsigned int TX_CON1;
    volatile unsigned int TX_PILOT;
    volatile unsigned int TX_SYN_GAIN;
    volatile unsigned int TX_MUL;
    volatile unsigned int TX_ADR;
    volatile unsigned int TX_LEN;
    volatile unsigned int TX_FREQ;
    volatile unsigned int TX_BASE_ADR;
} JL_FM_TypeDef;






typedef struct {
    volatile unsigned int CON0;
    volatile unsigned int CON3;
    volatile unsigned int LOFC_CON;
    volatile unsigned int LOFC_RES;
} JL_WL_TypeDef;
# 160 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/br23.h"
typedef struct {
    volatile unsigned int PWR_CON;
    volatile unsigned int HTC_CON;
    volatile unsigned int SYS_DIV;
    volatile unsigned int CLK_CON0;
    volatile unsigned int CLK_CON1;
    volatile unsigned int CLK_CON2;
    volatile unsigned int CLK_CON3;
    volatile unsigned int RESERVED0[0x10 - 0x6 - 1];
    volatile unsigned int PLL_CON;
    volatile unsigned int PLL_CON1;
    volatile unsigned int PLL_INTF;
    volatile unsigned int PLL_DMAX;
    volatile unsigned int PLL_DMIN;
    volatile unsigned int PLL_DSTP;
} JL_CLOCK_TypeDef;




typedef struct {
    volatile unsigned int SRC;
} JL_RST_TypeDef;





typedef struct {
    volatile unsigned int MODE_CON;
} JL_MODE_TypeDef;





typedef struct {
    volatile unsigned int CHIP_ID;
    volatile unsigned int MBIST_CON;
} JL_SYSTEM_TypeDef;





typedef struct {
    volatile unsigned int CON;
    volatile unsigned int CNT;
    volatile unsigned int PRD;
    volatile unsigned int PWM;
} JL_TIMER_TypeDef;
# 226 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/br23.h"
typedef struct {
    volatile unsigned int CON;
    volatile unsigned int VAL;
} JL_PCNT_TypeDef;





typedef struct {
    volatile unsigned int CON;
    volatile const unsigned int NUM;
} JL_GPCNT_TypeDef;






typedef struct {
    volatile unsigned int CON0;
    volatile unsigned int CON1;
    volatile unsigned int CON2;
    volatile unsigned int CPTR;
    volatile unsigned int DPTR;
    volatile unsigned int CTU_CON;
    volatile unsigned int CTU_CNT;
} JL_SD_TypeDef;
# 262 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/br23.h"
typedef struct {
    volatile unsigned int CON0;
    volatile unsigned int CON1;
    volatile unsigned int EP0_CNT;
    volatile unsigned int EP1_CNT;
    volatile unsigned int EP2_CNT;
    volatile unsigned int EP3_CNT;
    volatile unsigned int EP4_CNT;
    volatile unsigned int EP0_ADR;
    volatile unsigned int EP1_TADR;
    volatile unsigned int EP1_RADR;
    volatile unsigned int EP2_TADR;
    volatile unsigned int EP2_RADR;
    volatile unsigned int EP3_TADR;
    volatile unsigned int EP3_RADR;
    volatile unsigned int EP4_TADR;
    volatile unsigned int EP4_RADR;
} JL_USB_TypeDef;





typedef struct {
    volatile unsigned int WLA_CON0 ;
    volatile unsigned int WLA_CON1 ;
    volatile unsigned int WLA_CON2 ;
    volatile unsigned int WLA_CON3 ;
    volatile unsigned int WLA_CON4 ;
    volatile unsigned int WLA_CON5 ;
    volatile unsigned int WLA_CON6 ;
    volatile unsigned int WLA_CON7 ;
    volatile unsigned int WLA_CON8 ;
    volatile unsigned int WLA_CON9 ;
    volatile unsigned int WLA_CON10;
    volatile unsigned int WLA_CON11;
    volatile unsigned int WLA_CON12;
    volatile unsigned int WLA_CON13;
    volatile unsigned int WLA_CON14;
    volatile unsigned int WLA_CON15;
    volatile unsigned int WLA_CON16;
    volatile unsigned int WLA_CON17;
    volatile unsigned int WLA_CON18;
    volatile unsigned int WLA_CON19;
    volatile unsigned int WLA_CON20;
    volatile unsigned int WLA_CON21;
    volatile unsigned int WLA_CON22;
    volatile unsigned int WLA_CON23;
    volatile unsigned int WLA_CON24;
    volatile unsigned int WLA_CON25;
    volatile unsigned int WLA_CON26;
    volatile unsigned int WLA_CON27;
    volatile unsigned int WLA_CON28;
    volatile unsigned int WLA_CON29;
    volatile const unsigned int WLA_CON30;
    volatile const unsigned int WLA_CON31;
    volatile const unsigned int WLA_CON32;
    volatile const unsigned int WLA_CON33;
    volatile const unsigned int WLA_CON34;
    volatile const unsigned int WLA_CON35;
    volatile const unsigned int WLA_CON36;
    volatile const unsigned int WLA_CON37;
    volatile const unsigned int WLA_CON38;
    volatile const unsigned int WLA_CON39;
    volatile const unsigned int RESERVED0[0x30 - 0x27 - 1];
    volatile unsigned int DAA_CON0;
    volatile unsigned int DAA_CON1;
    volatile unsigned int DAA_CON2;
    volatile unsigned int DAA_CON3;
    volatile const unsigned int RESERVED1[0x37 - 0x33 - 1];
    volatile unsigned int DAA_CON7;
    volatile unsigned int ADA_CON0;
    volatile unsigned int ADA_CON1;
    volatile unsigned int ADA_CON2;
    volatile unsigned int ADA_CON3;
    volatile unsigned int ADA_CON4;
} JL_ANA_TypeDef;





typedef struct {
    volatile unsigned int CON;
    volatile unsigned int BAUD;
    volatile unsigned int BUF;
    volatile unsigned int ADR;
    volatile unsigned int CNT;
} JL_SPI_TypeDef;
# 362 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/br23.h"
typedef struct {
    volatile unsigned int CON0;
    volatile unsigned int CON1;
    volatile unsigned int BAUD;
    volatile unsigned int BUF;
    volatile unsigned int OTCNT;
    volatile unsigned int TXADR;
    volatile unsigned int TXCNT;
    volatile unsigned int RXSADR;
    volatile unsigned int RXEADR;
    volatile unsigned int RXCNT;
    volatile const unsigned int HRXCNT;
} JL_UART_TypeDef;
# 386 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/br23.h"
typedef struct {
    volatile unsigned int CON0;
    volatile unsigned int BUF;
    volatile unsigned int BAUD;
    volatile unsigned int CON1;
} JL_IIC_TypeDef;





typedef struct {
    volatile unsigned int CON;
    volatile unsigned int DAT0;
    volatile unsigned int DAT1;
    volatile unsigned int BUF;
    volatile unsigned int ADR;
    volatile unsigned int CNT;
} JL_PAP_TypeDef;





typedef struct {
    volatile unsigned int CON;
    volatile const unsigned int SR_CNT;
    volatile unsigned int IO_CON;
    volatile unsigned int DMA_CON;
    volatile unsigned int DMA_LEN;
    volatile unsigned int DAT_ADR;
    volatile unsigned int INF_ADR;
    volatile const unsigned int CSB0;
    volatile const unsigned int CSB1;
    volatile const unsigned int CSB2;
    volatile const unsigned int CSB3;
    volatile const unsigned int CSB4;
    volatile const unsigned int CSB5;
} JL_SS_TypeDef;





typedef struct {
    volatile unsigned int CON;
    volatile unsigned int DAT;
} JL_RDEC_TypeDef;
# 445 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/br23.h"
typedef struct {
    volatile unsigned int CON;
    volatile unsigned int SMR;
    volatile unsigned int ADR;
    volatile unsigned int LEN;
} JL_PLNK_TypeDef;






typedef struct {
    volatile unsigned int CON0;
    volatile unsigned int CON1;
    volatile unsigned int CON2;
    volatile unsigned int CON3;
    volatile unsigned int ADR0;
    volatile unsigned int ADR1;
    volatile unsigned int ADR2;
    volatile unsigned int ADR3;
    volatile unsigned int LEN;
} JL_ALNK_TypeDef;
# 476 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/br23.h"
typedef struct {
    volatile unsigned int(DAC_CON);
    volatile unsigned int(DAC_ADR);
    volatile unsigned int(DAC_LEN);
    volatile unsigned int(DAC_PNS);
    volatile unsigned int(DAC_HRP);
    volatile unsigned int(DAC_SWP);
    volatile unsigned int(DAC_SWN);
    volatile const unsigned int(RESERVED7);
    volatile unsigned int(DAC_VL0);
    volatile unsigned int(DAC_VL1);
    volatile unsigned int(DAC_TM0);
    volatile unsigned int(DAC_TM1);
    volatile short DAC_DTV;
    volatile short RESERVEDah;
    volatile short DAC_DTB;
    volatile short RESERVEDbh;
    volatile unsigned int(DAC_DPD);
    volatile unsigned int(DAC_COP);
    volatile unsigned int(ADC_CON);
    volatile unsigned int(ADC_ADR);
    volatile unsigned int(ADC_LEN);
    volatile unsigned int(ADC_PNS);
    volatile unsigned int(ADC_HWP);
    volatile unsigned int(ADC_SRP);
    volatile unsigned int(ADC_SRN);
} JL_AUDIO_TypeDef;





typedef struct {
    volatile unsigned int TMR0_CON;
    volatile unsigned int TMR0_CNT;
    volatile unsigned int TMR0_PR;
    volatile unsigned int TMR1_CON;
    volatile unsigned int TMR1_CNT;
    volatile unsigned int TMR1_PR;
    volatile unsigned int TMR2_CON;
    volatile unsigned int TMR2_CNT;
    volatile unsigned int TMR2_PR;
    volatile unsigned int TMR3_CON;
    volatile unsigned int TMR3_CNT;
    volatile unsigned int TMR3_PR;
    volatile unsigned int TMR4_CON;
    volatile unsigned int TMR4_CNT;
    volatile unsigned int TMR4_PR;
    volatile unsigned int TMR5_CON;
    volatile unsigned int TMR5_CNT;
    volatile unsigned int TMR5_PR;
    volatile unsigned int TMR6_CON;
    volatile unsigned int TMR6_CNT;
    volatile unsigned int TMR6_PR;
    volatile unsigned int TMR7_CON;
    volatile unsigned int TMR7_CNT;
    volatile unsigned int TMR7_PR;
    volatile unsigned int FPIN_CON;
    volatile unsigned int CH0_CON0;
    volatile unsigned int CH0_CON1;
    volatile unsigned int CH0_CMPH;
    volatile unsigned int CH0_CMPL;
    volatile unsigned int CH1_CON0;
    volatile unsigned int CH1_CON1;
    volatile unsigned int CH1_CMPH;
    volatile unsigned int CH1_CMPL;
    volatile unsigned int CH2_CON0;
    volatile unsigned int CH2_CON1;
    volatile unsigned int CH2_CMPH;
    volatile unsigned int CH2_CMPL;
    volatile unsigned int CH3_CON0;
    volatile unsigned int CH3_CON1;
    volatile unsigned int CH3_CMPH;
    volatile unsigned int CH3_CMPL;
    volatile unsigned int CH4_CON0;
    volatile unsigned int CH4_CON1;
    volatile unsigned int CH4_CMPH;
    volatile unsigned int CH4_CMPL;
    volatile unsigned int CH5_CON0;
    volatile unsigned int CH5_CON1;
    volatile unsigned int CH5_CMPH;
    volatile unsigned int CH5_CMPL;
    volatile unsigned int CH6_CON0;
    volatile unsigned int CH6_CON1;
    volatile unsigned int CH6_CMPH;
    volatile unsigned int CH6_CMPL;
    volatile unsigned int CH7_CON0;
    volatile unsigned int CH7_CON1;
    volatile unsigned int CH7_CMPH;
    volatile unsigned int CH7_CMPL;
    volatile unsigned int MCPWM_CON0;
} JL_MCPWM_TypeDef;





typedef struct {
    volatile unsigned int CON;
    volatile const unsigned int RES;
} JL_ADC_TypeDef;





typedef struct {
    volatile unsigned int RFLT_CON;
} JL_IR_TypeDef;
# 593 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/br23.h"
typedef struct {
    volatile unsigned int CON;
} JL_OSA_TypeDef;





typedef struct {
    volatile unsigned int FIFO;
    volatile unsigned int REG;
} JL_CRC_TypeDef;






typedef struct {
    volatile unsigned int CON;
    volatile unsigned int NUM;
} JL_LRCT_TypeDef;





typedef struct {
    volatile unsigned int CON;
    volatile const unsigned int RESERVED[8 - 0 - 1];
    volatile unsigned int ME;
} JL_EFUSE_TypeDef;





typedef struct {
    volatile const unsigned int R64L;
    volatile const unsigned int R64H;
} JL_RAND_TypeDef;





typedef struct {
    volatile unsigned int CON0;
    volatile unsigned int CON1;
    volatile unsigned int ADR;
} JL_CTM_TypeDef;






typedef struct {
    volatile unsigned int PMU_CON;
    volatile unsigned int RTC_CON;
    volatile unsigned int SPI_CON;
    volatile unsigned int SPI_DAT;
} JL_P33_TypeDef;





typedef struct {
    volatile unsigned int PRI0;
    volatile unsigned int PRI1;
    volatile unsigned int PRI2;
    volatile unsigned int PRI3;
    volatile unsigned int RESERVED0[0x08 - 0x03 - 1];
    volatile unsigned int MSG;
    volatile const unsigned int MSG_CH;
    volatile unsigned int RDL;
    volatile unsigned int RDH;
    volatile unsigned int WRL;
    volatile unsigned int WRH;

} JL_DMA_TypeDef;







typedef struct {
    volatile unsigned int ENCCON ;
    volatile unsigned int ENCKEY ;
    volatile unsigned int ENCADR ;
} JL_PERIENC_TypeDef;





typedef struct {
    volatile unsigned int CON0;
    volatile unsigned int DEC_SRC_ADR;
    volatile unsigned int DEC_DST_ADR;
    volatile unsigned int DEC_PCM_WCNT;
    volatile unsigned int DEC_INBUF_LEN;
    volatile unsigned int ENC_SRC_ADR;
    volatile unsigned int ENC_DST_ADR;
    volatile const unsigned int DEC_DST_BASE;

} JL_SBC_TypeDef;





typedef struct {
    volatile unsigned int CON;
    volatile unsigned int DATIN;
    volatile unsigned int KEY;
    volatile unsigned int ENCRES0;
    volatile unsigned int ENCRES1;
    volatile unsigned int ENCRES2;
    volatile unsigned int ENCRES3;
    volatile unsigned int NONCE;
    volatile unsigned int HEADER;
    volatile unsigned int SRCADR;
    volatile unsigned int DSTADR;
    volatile unsigned int CTCNT;
    volatile unsigned int TAGLEN;
    volatile const unsigned int TAGRES0;
    volatile const unsigned int TAGRES1;
    volatile const unsigned int TAGRES2;
    volatile const unsigned int TAGRES3;
} JL_AES_TypeDef;
# 744 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/br23.h"
typedef struct {
    volatile unsigned int OUT;
    volatile const unsigned int IN;
    volatile unsigned int DIR;
    volatile unsigned int DIE;
    volatile unsigned int PU;
    volatile unsigned int PD;
    volatile unsigned int HD0;
    volatile unsigned int HD;
    volatile unsigned int DIEH;
} JL_PORT_FLASH_TypeDef;
# 768 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/br23.h"
typedef struct {
    volatile unsigned int CON0;
    volatile unsigned int CON1;
} JL_USB_IO_TypeDef;





typedef struct {
    volatile unsigned int CON0;
    volatile unsigned int CON1;
    volatile unsigned int CON2;
    volatile unsigned int CON3;
} JL_WAKEUP_TypeDef;




typedef struct {
    volatile unsigned int CON0;
    volatile unsigned int CON1;
    volatile unsigned int CON2;
    volatile unsigned int CON3;
    volatile unsigned int CON4;
    volatile unsigned int CON5;
} JL_IOMAP_TypeDef;




typedef struct {
    volatile unsigned int CON0;
    volatile unsigned int CON1;
    volatile unsigned int CON2;
    volatile unsigned int CON3;
    volatile unsigned int BRI_PRDL;
    volatile unsigned int BRI_PRDH;
    volatile unsigned int BRI_DUTY0L;
    volatile unsigned int BRI_DUTY0H;
    volatile unsigned int BRI_DUTY1L;
    volatile unsigned int BRI_DUTY1H;
    volatile unsigned int PRD_DIVL;
    volatile unsigned int DUTY0;
    volatile unsigned int DUTY1;
    volatile unsigned int DUTY2;
    volatile unsigned int DUTY3;
    volatile const unsigned int CNT_RD;
} JL_PLED_TypeDef;




typedef struct {
    volatile unsigned int CON0;
    volatile unsigned int SEG_IOEN0;
    volatile unsigned int SEG_IOEN1;
} JL_LCD_TypeDef;
# 7 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/cpu.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/csfr.h" 1
# 39 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/csfr.h"
typedef struct {
    volatile unsigned int CON;
    volatile unsigned int KEY;
} JL_SDTAP_TypeDef;





typedef struct {
    volatile unsigned int MBISTCTL;
    volatile const unsigned int MBISTSOGO;
} JL_MBIS_TypeDef;
# 66 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/csfr.h"
typedef struct {
    volatile unsigned int CON;
    volatile unsigned int TLB1_BEG;
    volatile unsigned int TLB1_END;
} JL_MMU_TypeDef;





typedef struct {
    volatile unsigned int CON;
    volatile unsigned int RING_OSC;
    volatile unsigned int CPASS_CON;
    volatile unsigned int CPASS_ADRH;
    volatile unsigned int CPASS_ADRL;
    volatile unsigned int CPASS_BUF_LAST;
    volatile unsigned int CPREFETCH_ADRH;
    volatile unsigned int CPREFETCH_ADRL;
    volatile const unsigned int CACHE_MSG_CH;
} JL_DSP_TypeDef;




typedef struct {
    volatile unsigned int DSP_BF_CON;
    volatile unsigned int WR_EN;
    volatile const unsigned int MSG;
    volatile unsigned int MSG_CLR;
    volatile unsigned int DSP_EX_LIMH;
    volatile unsigned int DSP_EX_LIML;
    volatile unsigned int PRP_EX_LIMH;
    volatile unsigned int PRP_EX_LIML;
    volatile const unsigned int PRP_MMU_MSG;
    volatile const unsigned int LSB_MMU_MSG_CH;
    volatile const unsigned int PRP_WR_LIMIT_MSG;
    volatile const unsigned int LSB_WR_LIMIT_CH;
    volatile unsigned int DSP_PC_LIMH0;
    volatile unsigned int DSP_PC_LIML0;
    volatile unsigned int DSP_PC_LIMH1;
    volatile unsigned int DSP_PC_LIML1;
    volatile unsigned int PRP_SRM_INV_MSG;
    volatile unsigned int LSB_SRM_INV_CH;
} JL_DEBUG_TypeDef;





typedef struct {
    volatile unsigned int CON;
    volatile unsigned int CADR;
    volatile unsigned int TEST0;
    volatile unsigned int TEST1;
} JL_FFT_TypeDef;
# 149 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/csfr.h"
typedef struct {
              volatile const unsigned int DR00;
              volatile const unsigned int DR01;
              volatile const unsigned int DR02;
              volatile const unsigned int DR03;
              volatile const unsigned int DR04;
              volatile const unsigned int DR05;
              volatile const unsigned int DR06;
              volatile const unsigned int DR07;
              volatile const unsigned int DR08;
              volatile const unsigned int DR09;
              volatile const unsigned int DR10;
              volatile const unsigned int DR11;
              volatile const unsigned int DR12;
              volatile const unsigned int DR13;
              volatile const unsigned int DR14;
              volatile const unsigned int DR15;

              volatile const unsigned int RETI;
              volatile const unsigned int RETE;
              volatile const unsigned int RETX;
              volatile const unsigned int RETS;
              volatile const unsigned int SR04;
              volatile const unsigned int PSR;
              volatile const unsigned int CNUM;
              volatile const unsigned int SR07;
              volatile const unsigned int SR08;
              volatile const unsigned int SR09;
              volatile const unsigned int SR10;
              volatile const unsigned int ICFG;
              volatile const unsigned int USP;
              volatile const unsigned int SSP;
              volatile const unsigned int SP;
              volatile const unsigned int PCRS;

              volatile unsigned int BPCON;
              volatile unsigned int BSP;
              volatile unsigned int BP0;
              volatile unsigned int BP1;
              volatile unsigned int BP2;
              volatile unsigned int BP3;
              volatile unsigned int CMD_PAUSE;
              volatile const unsigned int REV_30_26[0x30 - 0x26 - 1];

              volatile unsigned int PMU_CON;
              volatile const unsigned int REV_34_30[0x34 - 0x30 - 1];
              volatile unsigned int EMU_CON;
              volatile unsigned int EMU_MSG;
              volatile unsigned int EMU_SSP_H;
              volatile unsigned int EMU_SSP_L;
              volatile unsigned int EMU_USP_H;
              volatile unsigned int EMU_USP_L;
              volatile const unsigned int REV_3b_39[0x3b - 0x39 - 1];
              volatile unsigned int TTMR_CON;
              volatile unsigned int TTMR_CNT;
              volatile unsigned int TTMR_PRD;
              volatile unsigned int BANK_CON;
              volatile unsigned int BANK_NUM;

              volatile unsigned int ICFG00;
              volatile unsigned int ICFG01;
              volatile unsigned int ICFG02;
              volatile unsigned int ICFG03;
              volatile unsigned int ICFG04;
              volatile unsigned int ICFG05;
              volatile unsigned int ICFG06;
              volatile unsigned int ICFG07;
              volatile unsigned int ICFG08;
              volatile unsigned int ICFG09;
              volatile unsigned int ICFG10;
              volatile unsigned int ICFG11;
              volatile unsigned int ICFG12;
              volatile unsigned int ICFG13;
              volatile unsigned int ICFG14;
              volatile unsigned int ICFG15;

              volatile unsigned int ICFG16;
              volatile unsigned int ICFG17;
              volatile unsigned int ICFG18;
              volatile unsigned int ICFG19;
              volatile unsigned int ICFG20;
              volatile unsigned int ICFG21;
              volatile unsigned int ICFG22;
              volatile unsigned int ICFG23;
              volatile unsigned int ICFG24;
              volatile unsigned int ICFG25;
              volatile unsigned int ICFG26;
              volatile unsigned int ICFG27;
              volatile unsigned int ICFG28;
              volatile unsigned int ICFG29;
              volatile unsigned int ICFG30;
              volatile unsigned int ICFG31;

              volatile const unsigned int IPND0;
              volatile const unsigned int IPND1;
              volatile const unsigned int IPND2;
              volatile const unsigned int IPND3;
              volatile const unsigned int IPND4;
              volatile const unsigned int IPND5;
              volatile const unsigned int IPND6;
              volatile const unsigned int IPND7;
              volatile unsigned int ILAT_SET;
              volatile unsigned int ILAT_CLR;
              volatile unsigned int IPMASK;
              volatile const unsigned int REV_70_6a[0x70 - 0x6a - 1];

              volatile unsigned int ETM_CON;
              volatile const unsigned int ETM_PC0;
              volatile const unsigned int ETM_PC1;
              volatile const unsigned int ETM_PC2;
              volatile const unsigned int ETM_PC3;
              volatile unsigned int WP0_ADRH;
              volatile unsigned int WP0_ADRL;
              volatile unsigned int WP0_DATH;
              volatile unsigned int WP0_DATL;
              volatile unsigned int WP0_PC;
} JL_TypeDef_q32DSP;
# 275 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/csfr.h"
typedef struct _CPU_REGS {
    unsigned int reti;
    unsigned int rets;
    unsigned int psr;
    unsigned int r0;
    unsigned int r1;
    unsigned int r2;
    unsigned int r3;
    unsigned int r4;
    unsigned int r5;
    unsigned int r6;
    unsigned int r7;
    unsigned int r8;
    unsigned int r9;
    unsigned int r10;
    unsigned int r11;
    unsigned int r12;
    unsigned int r13;
    unsigned int r14;
    unsigned int r15;
} CPU_REGS;
# 8 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/cpu.h" 2



typedef unsigned char u8, bool, BOOL;
typedef char s8;
typedef unsigned short u16;
typedef signed short s16;
typedef unsigned int u32;
typedef signed int s32;
typedef unsigned long long u64;
typedef u32 FOURCC;
typedef long long s64;
typedef unsigned long long u64;
# 56 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/cpu.h"
extern void clr_wdt();
# 66 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/cpu.h"
static inline int current_cpu_id()
{
    return 0;
}


static inline int cpu_in_irq()
{
    int flag;
    __asm__ volatile("%0 = icfg" : "=r"(flag));
    return flag & 0xff;
}

static inline int cpu_irq_disabled()
{
    int flag;
    __asm__ volatile("%0 = icfg" : "=r"(flag));
    return (flag & 0x300) != 0x300 || ((((JL_TypeDef_q32DSP *)((0x100000 + 0xf000) + 0x010000*0))->IPMASK) == 6);
}
# 98 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/cpu.h"
__attribute__((always_inline))
static int data_sat_s16(int ind)
{
    __asm__ volatile(
        " %0 = sat16(%0)(s)  \t\n"
        : "=&r"(ind)
        : "0"(ind)
        :);
    return ind;
}



static inline u32 reverse_u32(u32 data32)
{




    __asm__ volatile("%0 = rev8(%0) \t\n" : "=&r"(data32) : "0"(data32) :);

    return data32;
}

static inline u32 reverse_u16(u16 data16)
{
    u32 retv;




    retv = ((u32)data16) << 16;
    __asm__ volatile("%0 = rev8(%0) \t\n" : "=&r"(retv) : "0"(retv) :);

    return retv;
}

static inline u32 rand32()
{
    return ((JL_RAND_TypeDef *)(0x1e0000 + ((64 * 0x3b + 0x00) * 4)))->R64L;
}
# 148 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/cpu.h"
void p33_soft_reset(void);
static inline void cpu_reset(void)
{

    p33_soft_reset();
}







# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/irq.h" 1




# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/hwi.h" 1
# 68 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/hwi.h"
void interrupt_init();

void request_irq(u8 index, u8 priority, void (*handler)(void), u8 cpu_id);

void unrequest_irq(u8 index);

void bit_clr_ie(unsigned char index);
void bit_set_ie(unsigned char index);
bool irq_read(u32 index);
# 6 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/irq.h" 2
# 161 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/cpu.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/printf.h" 1



# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\bin\\..\\lib\\clang\\4.0.1\\include\\stdarg.h" 1 3 4
# 30 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\bin\\..\\lib\\clang\\4.0.1\\include\\stdarg.h" 3 4
typedef __builtin_va_list va_list;
# 50 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\bin\\..\\lib\\clang\\4.0.1\\include\\stdarg.h" 3 4
typedef __builtin_va_list __gnuc_va_list;
# 5 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/printf.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/typedef.h" 1
# 13 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/typedef.h"
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/cpu.h" 1
# 14 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/typedef.h" 2
# 139 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/typedef.h"
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/errno-base.h" 1
# 140 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/typedef.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\string.h" 1 3
# 10 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\string.h" 3
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wundef"


# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include/_ansi.h" 1 3
# 15 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include/_ansi.h" 3
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wundef"


# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\newlib.h" 1 3
# 19 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include/_ansi.h" 2 3
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/config.h" 1 3



# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\machine/ieeefp.h" 1 3
# 5 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/config.h" 2 3
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/features.h" 1 3
# 6 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/config.h" 2 3
# 20 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include/_ansi.h" 2 3
# 143 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include/_ansi.h" 3
#pragma GCC diagnostic pop
# 14 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\string.h" 2 3
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/reent.h" 1 3
# 14 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/reent.h" 3
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\bin\\..\\lib\\clang\\4.0.1\\include\\stddef.h" 1 3 4
# 51 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\bin\\..\\lib\\clang\\4.0.1\\include\\stddef.h" 3 4
typedef long int ptrdiff_t;
# 62 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\bin\\..\\lib\\clang\\4.0.1\\include\\stddef.h" 3 4
typedef long unsigned int size_t;
# 90 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\bin\\..\\lib\\clang\\4.0.1\\include\\stddef.h" 3 4
typedef int wchar_t;
# 15 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/reent.h" 2 3
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/_types.h" 1 3
# 12 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/_types.h" 3
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\machine/_types.h" 1 3






# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\machine/_default_types.h" 1 3
# 27 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\machine/_default_types.h" 3
typedef signed char __int8_t;

typedef unsigned char __uint8_t;
# 41 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\machine/_default_types.h" 3
typedef short __int16_t;

typedef unsigned short __uint16_t;
# 63 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\machine/_default_types.h" 3
typedef int __int32_t;

typedef unsigned int __uint32_t;
# 89 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\machine/_default_types.h" 3
typedef long long int __int64_t;

typedef long long unsigned int __uint64_t;
# 120 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\machine/_default_types.h" 3
typedef signed char __int_least8_t;

typedef unsigned char __uint_least8_t;
# 146 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\machine/_default_types.h" 3
typedef short __int_least16_t;

typedef unsigned short __uint_least16_t;
# 168 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\machine/_default_types.h" 3
typedef int __int_least32_t;

typedef unsigned int __uint_least32_t;
# 186 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\machine/_default_types.h" 3
typedef long long int __int_least64_t;

typedef long long unsigned int __uint_least64_t;
# 200 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\machine/_default_types.h" 3
typedef long int __intptr_t;

typedef long unsigned int __uintptr_t;
# 8 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\machine/_types.h" 2 3
# 13 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/_types.h" 2 3
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/lock.h" 1 3





typedef int _LOCK_T;
typedef int _LOCK_RECURSIVE_T;
# 14 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/_types.h" 2 3


typedef long _off_t;



typedef short __dev_t;



typedef unsigned short __uid_t;


typedef unsigned short __gid_t;



__extension__ typedef long long _off64_t;







typedef long _fpos_t;
# 55 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/_types.h" 3
typedef long signed int _ssize_t;
# 67 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/_types.h" 3
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\bin\\..\\lib\\clang\\4.0.1\\include\\stddef.h" 1 3 4
# 132 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\bin\\..\\lib\\clang\\4.0.1\\include\\stddef.h" 3 4
typedef int wint_t;
# 68 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/_types.h" 2 3



typedef struct
{
  int __count;
  union
  {
    wint_t __wch;
    unsigned char __wchb[4];
  } __value;
} _mbstate_t;



typedef _LOCK_RECURSIVE_T _flock_t;




typedef void *_iconv_t;
# 16 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/reent.h" 2 3






typedef unsigned long __ULong;
# 38 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/reent.h" 3
struct _reent;






struct _Bigint
{
  struct _Bigint *_next;
  int _k, _maxwds, _sign, _wds;
  __ULong _x[1];
};


struct __tm
{
  int __tm_sec;
  int __tm_min;
  int __tm_hour;
  int __tm_mday;
  int __tm_mon;
  int __tm_year;
  int __tm_wday;
  int __tm_yday;
  int __tm_isdst;
};







struct _on_exit_args {
 void * _fnargs[32];
 void * _dso_handle[32];

 __ULong _fntypes;


 __ULong _is_cxa;
};
# 91 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/reent.h" 3
struct _atexit {
 struct _atexit *_next;
 int _ind;

 void (*_fns[32])(void);
        struct _on_exit_args _on_exit_args;
};
# 115 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/reent.h" 3
struct __sbuf {
 unsigned char *_base;
 int _size;
};
# 179 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/reent.h" 3
struct __sFILE {
  unsigned char *_p;
  int _r;
  int _w;
  short _flags;
  short _file;
  struct __sbuf _bf;
  int _lbfsize;






  void * _cookie;

  int (* _read) (struct _reent *, void *, char *, int);

  int (* _write) (struct _reent *, void *, const char *, int);


  _fpos_t (* _seek) (struct _reent *, void *, _fpos_t, int);
  int (* _close) (struct _reent *, void *);


  struct __sbuf _ub;
  unsigned char *_up;
  int _ur;


  unsigned char _ubuf[3];
  unsigned char _nbuf[1];


  struct __sbuf _lb;


  int _blksize;
  _off_t _offset;






  _flock_t _lock;

  _mbstate_t _mbstate;
  int _flags2;
};
# 285 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/reent.h" 3
typedef struct __sFILE __FILE;



struct _glue
{
  struct _glue *_next;
  int _niobs;
  __FILE *_iobs;
};
# 317 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/reent.h" 3
struct _rand48 {
  unsigned short _seed[3];
  unsigned short _mult[3];
  unsigned short _add;




};
# 569 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/reent.h" 3
struct _reent
{
  int _errno;




  __FILE *_stdin, *_stdout, *_stderr;

  int _inc;
  char _emergency[25];

  int _current_category;
  const char *_current_locale;

  int __sdidinit;

  void (* __cleanup) (struct _reent *);


  struct _Bigint *_result;
  int _result_k;
  struct _Bigint *_p5s;
  struct _Bigint **_freelist;


  int _cvtlen;
  char *_cvtbuf;

  union
    {
      struct
        {
          unsigned int _unused_rand;
          char * _strtok_last;
          char _asctime_buf[26];
          struct __tm _localtime_buf;
          int _gamma_signgam;
          __extension__ unsigned long long _rand_next;
          struct _rand48 _r48;
          _mbstate_t _mblen_state;
          _mbstate_t _mbtowc_state;
          _mbstate_t _wctomb_state;
          char _l64a_buf[8];
          char _signal_buf[24];
          int _getdate_err;
          _mbstate_t _mbrlen_state;
          _mbstate_t _mbrtowc_state;
          _mbstate_t _mbsrtowcs_state;
          _mbstate_t _wcrtomb_state;
          _mbstate_t _wcsrtombs_state;
   int _h_errno;
        } _reent;



      struct
        {

          unsigned char * _nextf[30];
          unsigned int _nmalloc[30];
        } _unused;
    } _new;



  struct _atexit *_atexit;
  struct _atexit _atexit0;



  void (**(_sig_func))(int);




  struct _glue __sglue;
  __FILE __sf[3];
};
# 762 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/reent.h" 3
extern struct _reent *_impure_ptr ;
extern struct _reent *const _global_impure_ptr ;

void _reclaim_reent (struct _reent *);
# 15 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\string.h" 2 3
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/cdefs.h" 1 3
# 45 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/cdefs.h" 3
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\bin\\..\\lib\\clang\\4.0.1\\include\\stddef.h" 1 3 4
# 46 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/cdefs.h" 2 3
# 16 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\string.h" 2 3




# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\bin\\..\\lib\\clang\\4.0.1\\include\\stddef.h" 1 3 4
# 21 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\string.h" 2 3



void * memchr (const void *, int, size_t);
int memcmp (const void *, const void *, size_t);
void * memcpy (void * restrict, const void * restrict, size_t);
void * memmove (void *, const void *, size_t);
void * memset (void *, int, size_t);
char *strcat (char *restrict, const char *restrict);
char *strchr (const char *, int);
int strcmp (const char *, const char *);
int strcoll (const char *, const char *);
char *strcpy (char *restrict, const char *restrict);
size_t strcspn (const char *, const char *);
char *strerror (int);
size_t strlen (const char *);
char *strncat (char *restrict, const char *restrict, size_t);
int strncmp (const char *, const char *, size_t);
char *strncpy (char *restrict, const char *restrict, size_t);
char *strpbrk (const char *, const char *);
char *strrchr (const char *, int);
size_t strspn (const char *, const char *);
char *strstr (const char *, const char *);

char *strtok (char *restrict, const char *restrict);

size_t strxfrm (char *restrict, const char *restrict, size_t);


char *strtok_r (char *restrict, const char *restrict, char **restrict);


int bcmp (const void *, const void *, size_t);
void bcopy (const void *, void *, size_t);
void bzero (void *, size_t);
int ffs (int);
char *index (const char *, int);


void * memccpy (void * restrict, const void * restrict, int, size_t);





void * memrchr (const void *, int, size_t);




char *rindex (const char *, int);

char *stpcpy (char *restrict, const char *restrict);
char *stpncpy (char *restrict, const char *restrict, size_t);

int strcasecmp (const char *, const char *);






char *strdup (const char *);


char *_strdup_r (struct _reent *, const char *);


char *strndup (const char *, size_t);



char *_strndup_r (struct _reent *, const char *, size_t);
# 109 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\string.h" 3
int strerror_r (int, char *, size_t)

             __asm__ ("" "__xpg_strerror_r")

  ;







char * _strerror_r (struct _reent *, int, int, int *);


size_t strlcat (char *, const char *, size_t);
size_t strlcpy (char *, const char *, size_t);


int strncasecmp (const char *, const char *, size_t);



size_t strnlen (const char *, size_t);


char *strsep (char **, const char *);







char *strlwr (char *);
char *strupr (char *);



char *strsignal (int __signo);
# 185 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\string.h" 3
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/string.h" 1 3
# 186 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\string.h" 2 3



#pragma GCC diagnostic pop
# 141 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/typedef.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\strings.h" 1 3
# 10 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\strings.h" 3
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wundef"





# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/types.h" 1 3
# 20 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/types.h" 3
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wundef"
# 66 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/types.h" 3
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/_stdint.h" 1 3
# 19 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/_stdint.h" 3
typedef __int8_t int8_t ;
typedef __uint8_t uint8_t ;




typedef __int16_t int16_t ;
typedef __uint16_t uint16_t ;




typedef __int32_t int32_t ;
typedef __uint32_t uint32_t ;




typedef __int64_t int64_t ;
typedef __uint64_t uint64_t ;



typedef __intptr_t intptr_t;
typedef __uintptr_t uintptr_t;
# 67 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/types.h" 2 3







# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\bin\\..\\lib\\clang\\4.0.1\\include\\stddef.h" 1 3 4
# 75 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/types.h" 2 3
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\machine/types.h" 1 3
# 19 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\machine/types.h" 3
typedef long int __off_t;
typedef int __pid_t;

__extension__ typedef long long int __loff_t;





typedef long __suseconds_t;
# 76 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/types.h" 2 3
# 98 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/types.h" 3
typedef unsigned char u_char;



typedef unsigned short u_short;



typedef unsigned int u_int;



typedef unsigned long u_long;





typedef unsigned short ushort;
typedef unsigned int uint;
typedef unsigned long ulong;



typedef unsigned long clock_t;




typedef long time_t;




typedef long daddr_t;



typedef char * caddr_t;
# 145 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/types.h" 3
typedef unsigned short ino_t;
# 174 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/types.h" 3
typedef _off_t off_t;
typedef __dev_t dev_t;
typedef __uid_t uid_t;
typedef __gid_t gid_t;





typedef int pid_t;







typedef long key_t;

typedef _ssize_t ssize_t;
# 207 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/types.h" 3
typedef unsigned int mode_t __attribute__ ((__mode__ (__SI__)));




typedef unsigned short nlink_t;
# 234 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/types.h" 3
typedef long fd_mask;







typedef struct _types_fd_set {
 fd_mask fds_bits[(((64)+(((sizeof (fd_mask) * 8))-1))/((sizeof (fd_mask) * 8)))];
} _types_fd_set;
# 265 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/types.h" 3
typedef unsigned long clockid_t;




typedef unsigned long timer_t;



typedef unsigned long useconds_t;


typedef __suseconds_t suseconds_t;



typedef __int64_t sbintime_t;
# 517 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/types.h" 3
#pragma GCC diagnostic pop
# 17 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\strings.h" 2 3








int bcmp (const void *, const void *, size_t);
void bcopy (const void *, void *, size_t);
void bzero (void *, size_t);
char *index (const char *, int);
char *rindex (const char *, int);


int ffs (int);
int strcasecmp (const char *, const char *);
int strncasecmp (const char *, const char *, size_t);



#pragma GCC diagnostic pop
# 142 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/typedef.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/malloc.h" 1







typedef enum {
    P_MEMORY_TOTAL,
    P_MEMORY_UNUSED,
    P_MEMORY_USED,
} MEMORY_TYPE;

extern void *malloc(size_t size);
extern void *zalloc(size_t size);
extern void *calloc(size_t count, size_t size);
extern void *realloc(void *rmem, size_t newsize);
extern void free(void *mem);


extern void *kmalloc(size_t size, int flags);
extern void *vmalloc(size_t size);
extern void vfree(void *addr);
extern void *kzalloc(unsigned int len, int a);
extern void kfree(void *p);

extern void malloc_stats(void);

extern void malloc_dump();

void memory_init(void);

void mem_stats(void);

size_t xPortGetFreeHeapSize(void);
size_t xPortGetMinimumEverFreeHeapSize(void);
size_t xPortGetPhysiceMemorySize(void);
# 48 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/malloc.h"
size_t memory_get_size(MEMORY_TYPE type);




void *get_physic_address(u32 page);




void *vmem_get_phy_adr(void *vaddr);
# 143 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/typedef.h" 2
# 159 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/typedef.h"
void delay(unsigned int);

void delay_us(unsigned int);
# 6 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/printf.h" 2


extern int putchar(int a);
extern int puts(const char *out);
void put_u4hex(unsigned char dat);
void put_u8hex(unsigned char dat);
void put_u16hex(unsigned short dat);
void put_u32hex(unsigned int dat);
void put_buf(const u8 *buf, int len);
int printf(const char *format, ...);
int assert_printf(const char *format, ...);
int sprintf(char *out, const char *format, ...);
int vprintf(const char *fmt, __builtin_va_list va);
int vsnprintf(char *, unsigned long, const char *, __builtin_va_list);
int snprintf(char *buf, unsigned long size, const char *fmt, ...);
int print(char **out, char *end, const char *format, va_list args);


int sscanf(const char *buf, const char *fmt, ...);
# 162 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/cpu.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/generic/log.h" 1
# 14 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/generic/log.h"
struct logbuf {
    u16 len;
    u16 buf_len;
    char buf[0];
};
# 95 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/generic/log.h"
int log_output_lock();

void log_output_unlock();

void log_print_time();

void log_early_init(int buf_size);

void log_level(int level);

void log_print(int level, const char *tag, const char *format, ...);

void log_dump(const u8 *buf, int len);

struct logbuf *log_output_start(int len);

void log_output_end(struct logbuf *);

void log_putchar(struct logbuf *lb, char c);

void log_put_u8hex(struct logbuf *lb, unsigned char dat);

void log_putbyte(char);

void log_set_time_offset(int offset);

int log_get_time_offset();



void log_flush();
# 163 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/cpu.h" 2
# 192 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/cpu.h"
extern void local_irq_disable();
extern void local_irq_enable();
extern void __local_irq_enable();
# 242 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/cpu.h"
extern void cpu_assert_debug();
extern const int config_asser;
# 5 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/crc16.h" 1








u16 CRC16(const void *ptr, u32 len);


u16 CRC16_with_initval(const void *ptr, u32 len, u16 i_val);

u16 CRC16_with_code(const void *ptr, u32 len, u16 code);

void spi_crc16_set(u16 crc);
u16 spi_crc16_get(void);

void CrcDecode(void *buf, u16 len);

u16 get_page_efuse(u32 page, u32 delay_cnt);
void init_enc_key(u8 cmd);
u32 get_sfc_enc_key(void);
# 6 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/clock.h" 1





# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/clock_hw.h" 1
# 227 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/clock_hw.h"
enum {
    RCH_EN_250K = 0,
    RCH_EN_16M,
};



enum {
    TS_SEL_IN_MAIN = 0,
    TS_SEL_IN_PAT,
};



enum {
    OSC_CLOCK_IN_BT_OSC = 0,
    OSC_CLOCK_IN_XOSC_FSCK,
    OSC_CLOCK_IN_RTOSC_L,
    OSC_CLOCK_IN_PAT,
};



enum {
    MAIN_CLOCK_IN_RC = 0,

    MAIN_CLOCK_IN_BTOSC = 4,
    MAIN_CLOCK_IN_RESERVED,
    MAIN_CLOCK_IN_RTOSC_L,
    MAIN_CLOCK_IN_PLL,
};


enum {
    SFR_CLOCK_IDLE = 0,
    SFR_CLOCK_ALWAYS_ON,
};







enum {
    USB_CLOCK_IN_PLL48M = 0,
    USB_CLOCK_IN_OSC,
    USB_CLOCK_IN_LSB,
    USB_CLOCK_IN_DISABLE,
};


enum {
    AUDIO_CLOCK_IN_PLL48M = 0,
    AUDIO_CLOCK_IN_OSC,
    AUDIO_CLOCK_IN_LSB,
    AUDIO_CLOCK_IN_DISABLE,
};


enum {
    GPCNT_CLOCK_IN_LSB = 0,
    GPCNT_CLOCK_IN_OSC,
    GPCNT_CLOCK_IN_CAP_MUX,
    GPCNT_CLOCK_IN_CLK_MUX,
    GPCNT_CLOCK_IN_NULL0,
    GPCNT_CLOCK_IN_AUDIO,
    GPCNT_CLOCK_IN_WL,
    GPCNT_CLOCK_IN_USB,
};



enum {
    UART_CLOCK_IN_PLL48M = 0,
    UART_CLOCK_IN_OSC,
    UART_CLOCK_IN_LSB,
    UART_CLOCK_IN_DISABLE,
};


enum {
    BT_CLOCK_IN_PLL48M = 0,
    BT_CLOCK_IN_HSB,
    BT_CLOCK_IN_LSB,
    BT_CLOCK_IN_DISABLE,
};





enum {
    WL2ADC_CLOCK_IN_PLL96M = 0,
    WL2ADC_CLOCK_IN_HSB,
    WL2ADC_CLOCK_IN_LSB,
    WL2ADC_CLOCK_IN_DISABLE,
};



enum {
    WL2DAC_CLOCK_IN_PLL96M = 0,
    WL2DAC_CLOCK_IN_HSB,
    WL2DAC_CLOCK_IN_LSB,
    WL2DAC_CLOCK_IN_DISABLE,
};







enum {
    PLL_SYS_SEL_PLL192M = 0,
    PLL_SYS_SEL_PLL137M,
    PLL_SYS_SEL_PLL320M,
    PLL_SYS_SEL_PLL480M,
};


enum {
    PLL_SYS_DIV1 = 0,
    PLL_SYS_DIV3,
    PLL_SYS_DIV5,
    PLL_SYS_DIV7,

    PLL_SYS_DIV1X2 = 4,
    PLL_SYS_DIV3X2,
    PLL_SYS_DIV5X2,
    PLL_SYS_DIV7X2,

    PLL_SYS_DIV1X4 = 8,
    PLL_SYS_DIV3X4,
    PLL_SYS_DIV5X4,
    PLL_SYS_DIV7X4,

    PLL_SYS_DIV1X8 = 12,
    PLL_SYS_DIV3X8,
    PLL_SYS_DIV5X8,
    PLL_SYS_DIV7X8,
};




enum {
    PLL_ALNK_192M_DIV17 = 0,
    PLL_ALNK_480M_DIV39,
};



enum {
    PLL_APC_SEL_PLL192M = 0,
    PLL_APC_SEL_PLL137M,
    PLL_APC_SEL_PLL107M,
    PLL_APC_SEL_DISABLE,
};


enum {
    PLL_FM_DIV1 = 0,
    PLL_FM_DIV3,
    PLL_FM_DIV5,
    PLL_FM_DIV7,

    PLL_FM_DIV1X2 = 4,
    PLL_FM_DIV3X2,
    PLL_FM_DIV5X2,
    PLL_FM_DIV7X2,

    PLL_FM_DIV1X4 = 8,
    PLL_FM_DIV3X4,
    PLL_FM_DIV5X4,
    PLL_FM_DIV7X4,

    PLL_FM_DIV1X8 = 12,
    PLL_FM_DIV3X8,
    PLL_FM_DIV5X8,
    PLL_FM_DIV7X8,
};
# 422 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/clock_hw.h"
enum {
    PLL_REF_SEL_BTOSC = 0,
    PLL_REF_SEL_RCLK,
};
# 442 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/clock_hw.h"
enum {
    PLL_RSEL_RCLK = 0,
    PLL_RSEL_RCH,
    PLL_RSEL_DPLL_CLK,
    PLL_RSEL_PAT_CLK,
};
# 458 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/clock_hw.h"
enum {
    PLL_DIVn_EN_X2 = 0,
    PLL_DIVn_DIS_DIV1,
    PLL_DIVn_EN2_33,
};
# 480 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/clock_hw.h"
enum {
    GPCNT_CSS_LSB = 0,
    GPCNT_CSS_OSC,
    GPCNT_CSS_CAP_MUX,
    GPCNT_CSS_CLK_MUX,
    GPCNT_CSS_GPCFD,
    GPCNT_CSS_RING,
    GPCNT_CSS_PLL480M,
    GPCNT_CSS_IRFLT,
};






enum {
    GPCNT_GSS_LSB = 0,
    GPCNT_GSS_OSC,
    GPCNT_GSS_CAP_MUX,
    GPCNT_GSS_CLK_MUX,
    GPCNT_GSS_GPCFD,
    GPCNT_GSS_RING,
    GPCNT_GSS_PLL480M,
    GPCNT_GSS_IRFLT,
};
# 7 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/clock.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/clock_define.h" 1
# 8 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/clock.h" 2
# 27 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/clock.h"
typedef enum {
    SYS_ICLOCK_INPUT_BTOSC,
    SYS_ICLOCK_INPUT_RTOSCH,
    SYS_ICLOCK_INPUT_RTOSCL,
    SYS_ICLOCK_INPUT_PAT,
} SYS_ICLOCK_INPUT;

typedef enum {
    PA0_CLOCK_OUTPUT = 0,
    PA0_CLOCK_OUT_BT_OSC,
    PA0_CLOCK_OUT_RTOSCH,
    PA0_CLOCK_OUT_NULL,

    PA0_CLOCK_OUT_LSB = 4,
    PA0_CLOCK_OUT_HSB,
    PA0_CLOCK_OUT_SFC,
    PA0_CLOCK_OUT_PLL,
} PA0_CLK_OUT;

typedef enum {
    PB8_CLOCK_OUTPUT = 0,
    PB8_CLOCK_OUT_RC,
    PB8_CLOCK_OUT_LRC,
    PB8_CLOCK_OUT_NULL,

    PB8_CLOCK_OUT_PLL75M = 4,
    PB8_CLOCK_OUT_XOSC_FSCK,
    PB8_CLOCK_OUT_PLL320,
    PB8_CLOCK_OUT_PLL107,
} PB8_CLK_OUT;




struct clock_critical_handler {
    void (*enter)();
    void (*exit)();
};





extern struct clock_critical_handler clock_critical_handler_begin[];
extern struct clock_critical_handler clock_critical_handler_end[];





int clk_early_init(u8 sys_in, u32 input_freq, u32 out_freq);

int clk_get(const char *name);

int clk_set(const char *name, int clk);

int clk_set_sys_lock(int clk, int lock_en);

void clock_dump(void);

enum sys_clk {
    SYS_24M,
    SYS_48M,
};

enum clk_mode {
    CLOCK_MODE_ADAPTIVE = 0,
    CLOCK_MODE_USR,
};


void sys_clk_set(u8 clk);

void clk_voltage_init(u8 mode, u8 sys_dvdd, u8 pwr_mode, u8 vdc13);

void clk_set_osc_cap(u8 sel_l, u8 sel_r);

void clk_set_default_osc_cap();

u32 clk_get_osc_cap();

void clk_init_osc_cap(u8 sel_l, u8 sel_r);

void clk_init_osc_ldos(u8 ldos);

void clock_reset_lsb_max_freq(u32 max_freq);







void clock_set_sfc_max_freq(u32 dual_max_freq, u32 quad_max_freq);
# 7 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/uart.h" 1








# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\device/uart.h" 1




# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\device/device.h" 1





# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/list.h" 1
# 25 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/list.h"
struct list_head {
    struct list_head *next, *prev;
};
# 122 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/list.h"
static inline int list_empty(const struct list_head *head)
{
    return head->next == head;
}







static inline void __list_add(struct list_head *_new,
                              struct list_head *prev,
                              struct list_head *next)
{
    next->prev = _new;
    _new->next = next;
    _new->prev = prev;
    prev->next = _new;
}
# 152 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/list.h"
static inline void list_add_tail(struct list_head *_new, struct list_head *head)
{
    __list_add(_new, head->prev, head);
}

static inline void __list_del(struct list_head *prev, struct list_head *next)
{
    next->prev = prev;
    prev->next = next;
}

static inline void __list_del_entry(struct list_head *entry)
{
    __list_del(entry->prev, entry->next);
}


static inline void list_del(struct list_head *entry)
{
    __list_del(entry->prev, entry->next);
    entry->next = entry;
    entry->prev = entry;
}
# 186 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/list.h"
static inline void INIT_LIST_HEAD(struct list_head *list)
{
    list->next = list;
    list->prev = list;
}

static inline void list_del_init(struct list_head *entry)
{
    __list_del_entry(entry);
    INIT_LIST_HEAD(entry);
}





static inline void list_move_tail(struct list_head *list,
                                  struct list_head *head)
{
    __list_del(list->prev, list->next);
    list_add_tail(list, head);
}
# 217 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/list.h"
static inline void list_add(struct list_head *new, struct list_head *head)
{
    __list_add(new, head, head->next);
}

static inline int list_is_head(struct list_head *head, struct list_head *member)
{
    return head->next == member;
}
# 7 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\device/device.h" 2

# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/atomic.h" 1



# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/cpu.h" 1
# 5 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/atomic.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/irq.h" 1
# 6 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/atomic.h" 2

typedef struct {
    int counter;
} atomic_t;

static inline int atomic_add_return(int i, atomic_t *v)
{
    int val;
                  ;

    do { local_irq_disable(); do { asm volatile("csync;"); } while (0); }while(0);

    val = v->counter;
    v->counter = val += i;

    do { local_irq_enable(); }while(0);

    return val;
}


static inline int atomic_sub_return(int i, atomic_t *v)
{
    int val;
                  ;

    do { local_irq_disable(); do { asm volatile("csync;"); } while (0); }while(0);

    val = v->counter;
    v->counter = val -= i;

    do { local_irq_enable(); }while(0);

    return val;
}

static inline int atomic_set(atomic_t *v, int i)
{
    int val = 0;
                  ;

    do { local_irq_disable(); do { asm volatile("csync;"); } while (0); }while(0);

    v->counter = i;

    do { local_irq_enable(); }while(0);

    return val;
}
# 9 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\device/device.h" 2

# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\device/ioctl_cmds.h" 1
# 72 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\device/ioctl_cmds.h"
struct ioctl_irq_handler {
    void *priv;
    void *handler;
};
# 11 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\device/device.h" 2


struct dev_node;
struct device;


struct device_operations {
    bool (*online)(const struct dev_node *node);
    int (*init)(const struct dev_node *node, void *);
    int (*open)(const char *name, struct device **device, void *arg);
    int (*read)(struct device *device, void *buf, u32 len, u32);
    int (*write)(struct device *device, void *buf, u32 len, u32);
    int (*seek)(struct device *device, u32 offset, int orig);
    int (*ioctl)(struct device *device, u32 cmd, u32 arg);
    int (*close)(struct device *device);
};

struct dev_node {
    const char *name;
    const struct device_operations *ops;
    void *priv_data;
};


struct device {
    atomic_t ref;
    void *private_data;
    const struct device_operations *ops;
    void *platform_data;
    void *driver_data;
};
# 51 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\device/device.h"
int devices_init();

bool dev_online(const char *name);

void *dev_open(const char *name, void *arg);


int dev_read(void *device, void *buf, u32 len);


int dev_write(void *device, void *buf, u32 len);


int dev_seek(void *device, u32 offset, int orig);


int dev_ioctl(void *device, int cmd, u32 arg);


int dev_close(void *device);


int dev_bulk_read(void *_device, void *buf, u32 offset, u32 len);

int dev_bulk_write(void *_device, void *buf, u32 offset, u32 len);
# 6 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\device/uart.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/ioctl.h" 1
# 7 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\device/uart.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/task.h" 1




# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h" 1
# 15 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\os/os_cpu.h" 1
# 10 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\os/os_cpu.h"
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic\\jiffies.h" 1
# 16 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic\\jiffies.h"
extern volatile unsigned long jiffies;
extern unsigned long jiffies_msec();
extern unsigned long jiffies_half_msec();







extern unsigned char jiffies_unit;
# 11 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\os/os_cpu.h" 2



typedef unsigned short QS;
typedef unsigned int OS_STK;
typedef unsigned int OS_CPU_SR;
typedef unsigned int OS_CPU_DATA;
# 55 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\os/os_cpu.h"
void OSCtxSw(void);

extern void EnableOtherCpu(void) ;



void OSInitTick(u32 hz);

void InstallOSISR(void);

void os_task_dead(const char *task_name);
# 16 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\os/os_error.h" 1






enum {
    OS_NO_ERR = 0,
    OS_TRUE,
    OS_ERR_EVENT_TYPE,
    OS_ERR_PEND_ISR,
    OS_ERR_POST_NULL_PTR,
    OS_ERR_PEVENT_NULL,
    OS_ERR_POST_ISR,
    OS_ERR_QUERY_ISR,
    OS_ERR_INVALID_OPT,
    OS_ERR_TASK_WAITING,
    OS_ERR_PDATA_NULL,
    OS_TIMEOUT,
    OS_TIMER,
    OS_TASKQ,
    OS_TASK_NOT_EXIST,
    OS_ERR_EVENT_NAME_TOO_LONG,
    OS_ERR_FLAG_NAME_TOO_LONG,
    OS_ERR_TASK_NAME_TOO_LONG,
    OS_ERR_PNAME_NULL,
    OS_ERR_TASK_CREATE_ISR,
    OS_MBOX_FULL,
    OS_Q_FULL,
    OS_Q_EMPTY,
    OS_Q_ERR,
    OS_ERR_NO_QBUF,
    OS_PRIO_EXIST,
    OS_PRIO_ERR,
    OS_PRIO_INVALID,
    OS_SEM_OVF,
    OS_TASK_DEL_ERR,
    OS_TASK_DEL_IDLE,
    OS_TASK_DEL_ISR,
    OS_NO_MORE_TCB,
    OS_TIME_NOT_DLY,
    OS_TIME_INVALID_MINUTES,
    OS_TIME_INVALID_SECONDS,
    OS_TIME_INVALID_MILLI,
    OS_TIME_ZERO_DLY,
    OS_TASK_SUSPEND_PRIO,
    OS_TASK_SUSPEND_IDLE,
    OS_TASK_RESUME_PRIO,
    OS_TASK_NOT_SUSPENDED,
    OS_MEM_INVALID_PART,
    OS_MEM_INVALID_BLKS,
    OS_MEM_INVALID_SIZE,
    OS_MEM_NO_FREE_BLKS,
    OS_MEM_FULL,
    OS_MEM_INVALID_PBLK,
    OS_MEM_INVALID_PMEM,
    OS_MEM_INVALID_PDATA,
    OS_MEM_INVALID_ADDR,
    OS_MEM_NAME_TOO_LONG,
    OS_ERR_MEM_NO_MEM,
    OS_ERR_NOT_MUTEX_OWNER,
    OS_TASK_OPT_ERR,
    OS_ERR_DEL_ISR,
    OS_ERR_CREATE_ISR,
    OS_FLAG_INVALID_PGRP,
    OS_FLAG_ERR_WAIT_TYPE,
    OS_FLAG_ERR_NOT_RDY,
    OS_FLAG_INVALID_OPT,
    OS_FLAG_GRP_DEPLETED,
    OS_ERR_PIP_LOWER,
    OS_ERR_MSG_POOL_EMPTY,
    OS_ERR_MSG_POOL_NULL_PTR,
    OS_ERR_MSG_POOL_FULL,

};
# 17 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\os/os_type.h" 1
# 27 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\os/os_type.h"
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/FreeRTOS.h" 1
# 98 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/FreeRTOS.h"
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/FreeRTOSConfig.h" 1
# 85 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/FreeRTOSConfig.h"
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/pi32v2/portmacro.h" 1
# 73 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/pi32v2/portmacro.h"
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\stdint.h" 1 3
# 12 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\stdint.h" 3
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wundef"



# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\sys/_intsup.h" 1 3
# 17 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\stdint.h" 2 3







typedef __int_least8_t int_least8_t;
typedef __uint_least8_t uint_least8_t;




typedef __int_least16_t int_least16_t;
typedef __uint_least16_t uint_least16_t;




typedef __int_least32_t int_least32_t;
typedef __uint_least32_t uint_least32_t;




typedef __int_least64_t int_least64_t;
typedef __uint_least64_t uint_least64_t;
# 54 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\stdint.h" 3
  typedef signed char int_fast8_t;
  typedef unsigned char uint_fast8_t;
# 64 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\stdint.h" 3
  typedef short int_fast16_t;
  typedef unsigned short uint_fast16_t;
# 74 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\stdint.h" 3
  typedef int int_fast32_t;
  typedef unsigned int uint_fast32_t;
# 84 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\stdint.h" 3
  typedef long long int int_fast64_t;
  typedef long long unsigned int uint_fast64_t;
# 133 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\stdint.h" 3
  typedef long long int intmax_t;
# 142 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\stdint.h" 3
  typedef long long unsigned int uintmax_t;
# 488 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\toolchain\\extracted-2.5.2\\C$\\JL\\pi32\\pi32v2-include\\stdint.h" 3
#pragma GCC diagnostic pop
# 74 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/pi32v2/portmacro.h" 2
# 87 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/pi32v2/portmacro.h"
typedef int StackType_t;
typedef long BaseType_t;
typedef unsigned long UBaseType_t;






typedef uint32_t TickType_t;
# 114 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/pi32v2/portmacro.h"
extern void vPortYield() ;


extern int current_cpu_id() ;







void vPortCloseRunningThread(void *pvTaskToDelete, volatile BaseType_t *pxPendYield);
# 134 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/pi32v2/portmacro.h"
void vPortEnterCritical(void);
void vPortExitCritical(void);
# 242 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/pi32v2/portmacro.h"
void vPortGenerateSimulatedInterrupt(uint32_t ulInterruptNumber);
# 253 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/pi32v2/portmacro.h"
void vPortSetInterruptHandler(uint32_t ulInterruptNumber, uint32_t (*pvHandler)(void));



extern void vPortSuppressTicksAndSleep(TickType_t xExpectedIdleTime);
# 86 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/FreeRTOSConfig.h" 2
# 131 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/FreeRTOSConfig.h"
unsigned long ulGetRunTimeCounterValue(void);
void vConfigureTimerForRunTimeStats(void);
void vMainConfigureTimerForRunTimeStats(void);
unsigned long ulMainGetRunTimeCounterValue(void);
# 173 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/FreeRTOSConfig.h"
static inline void vAssertCalled(const char *str, unsigned int ulLine)
{
# 183 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/FreeRTOSConfig.h"
    local_irq_disable();
    printf("%s %d\n", str, ulLine) ;
    while (1);

}
# 99 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/FreeRTOS.h" 2


# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/projdefs.h" 1
# 77 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/projdefs.h"
typedef void (*TaskFunction_t)(void *);
# 102 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/FreeRTOS.h" 2


# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/portable.h" 1
# 87 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/portable.h"
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/deprecated_definitions.h" 1
# 88 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/portable.h" 2
# 133 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/portable.h"
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/mpu_wrappers.h" 1
# 134 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/portable.h" 2
# 144 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/portable.h"
StackType_t *pxPortInitialiseStack(StackType_t *pxTopOfStack, TaskFunction_t pxCode, void *pvParameters) ;



typedef struct HeapRegion {
    uint8_t *pucStartAddress;
    size_t xSizeInBytes;
} HeapRegion_t;
# 164 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/portable.h"
void vPortDefineHeapRegions(const HeapRegion_t *const pxHeapRegions) ;





void *pvPortMalloc(size_t xSize) ;
void vPortFree(void *pv) ;
void vPortInitialiseBlocks(void) ;
size_t xPortGetFreeHeapSize(void) ;
size_t xPortGetMinimumEverFreeHeapSize(void) ;





BaseType_t xPortStartScheduler(void) ;






void vPortEndScheduler(void) ;
# 105 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/FreeRTOS.h" 2
# 874 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/FreeRTOS.h"
struct xSTATIC_LIST_ITEM {
    TickType_t xDummy1;
    void *pvDummy2[ 4 ];
};
typedef struct xSTATIC_LIST_ITEM StaticListItem_t;


struct xSTATIC_MINI_LIST_ITEM {
    TickType_t xDummy1;
    void *pvDummy2[ 2 ];
};
typedef struct xSTATIC_MINI_LIST_ITEM StaticMiniListItem_t;


typedef struct xSTATIC_LIST {
    UBaseType_t uxDummy1;
    void *pvDummy2;
    StaticMiniListItem_t xDummy3;
} StaticList_t;
# 907 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/FreeRTOS.h"
typedef struct xSTATIC_TCB {
    void *pxDummy1;
    UBaseType_t uxDummy;



    StaticListItem_t xDummy3[ 2 ];
    UBaseType_t uxDummy5;
    void *pxDummy6;
    uint8_t ucDummy7[ ( 12 ) ];







    UBaseType_t uxDummy10[ 2 ];


    UBaseType_t uxDummy12[ 2 ];


    void *pxDummy14;
# 946 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/FreeRTOS.h"
    uint8_t uxDummy20;


} StaticTask_t;
# 965 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/FreeRTOS.h"
typedef struct xSTATIC_QUEUE {
    void *pvDummy1[ 3 ];

    union {
        void *pvDummy2;
        UBaseType_t uxDummy2;
    } u;

    StaticList_t xDummy3[ 2 ];
    UBaseType_t uxDummy4[ 3 ];
    uint8_t ucDummy5[ 2 ];


    uint8_t ucDummy6;







    UBaseType_t uxDummy8;
    uint8_t ucDummy9;


} StaticQueue_t;
typedef StaticQueue_t StaticSemaphore_t;
# 1007 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/FreeRTOS.h"
typedef struct xSTATIC_EVENT_GROUP {
    TickType_t xDummy1;
    StaticList_t xDummy2;


    UBaseType_t uxDummy3;



    uint8_t ucDummy4;


} StaticEventGroup_t;
# 1035 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/FreeRTOS.h"
typedef struct xSTATIC_TIMER {
    void *pvDummy1;
    StaticListItem_t xDummy2;
    TickType_t xDummy3;
    UBaseType_t uxDummy4;
    void *pvDummy5[ 2 ];

    UBaseType_t uxDummy6;



    uint8_t ucDummy7;


} StaticTimer_t;
# 28 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\os/os_type.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/semphr.h" 1
# 77 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/semphr.h"
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/queue.h" 1
# 88 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/queue.h"
typedef void *QueueHandle_t;






typedef void *QueueSetHandle_t;






typedef void *QueueSetMemberHandle_t;
# 692 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/queue.h"
BaseType_t xQueueGenericSend(QueueHandle_t xQueue, const void *const pvItemToQueue, TickType_t xTicksToWait, const BaseType_t xCopyPosition) ;
# 821 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/queue.h"
BaseType_t xQueuePeekFromISR(QueueHandle_t xQueue, void *const pvBuffer) ;
# 1013 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/queue.h"
BaseType_t xQueueGenericReceive(QueueHandle_t xQueue, void *const pvBuffer, TickType_t xTicksToWait, const BaseType_t xJustPeek) ;
# 1028 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/queue.h"
UBaseType_t uxQueueMessagesWaiting(const QueueHandle_t xQueue) ;
# 1045 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/queue.h"
UBaseType_t uxQueueSpacesAvailable(const QueueHandle_t xQueue) ;
# 1059 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/queue.h"
void vQueueDelete(QueueHandle_t xQueue) ;
# 1440 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/queue.h"
BaseType_t xQueueGenericSendFromISR(QueueHandle_t xQueue, const void *const pvItemToQueue, BaseType_t *const pxHigherPriorityTaskWoken, const BaseType_t xCopyPosition) ;
BaseType_t xQueueGiveFromISR(QueueHandle_t xQueue, BaseType_t *const pxHigherPriorityTaskWoken) ;
# 1530 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/queue.h"
BaseType_t xQueueReceiveFromISR(QueueHandle_t xQueue, void *const pvBuffer, BaseType_t *const pxHigherPriorityTaskWoken) ;





BaseType_t xQueueIsQueueEmptyFromISR(const QueueHandle_t xQueue) ;
BaseType_t xQueueIsQueueFullFromISR(const QueueHandle_t xQueue) ;
UBaseType_t uxQueueMessagesWaitingFromISR(const QueueHandle_t xQueue) ;
# 1549 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/queue.h"
BaseType_t xQueueCRSendFromISR(QueueHandle_t xQueue, const void *pvItemToQueue, BaseType_t xCoRoutinePreviouslyWoken);
BaseType_t xQueueCRReceiveFromISR(QueueHandle_t xQueue, void *pvBuffer, BaseType_t *pxTaskWoken);
BaseType_t xQueueCRSend(QueueHandle_t xQueue, const void *pvItemToQueue, TickType_t xTicksToWait);
BaseType_t xQueueCRReceive(QueueHandle_t xQueue, void *pvBuffer, TickType_t xTicksToWait);






QueueHandle_t xQueueCreateMutex(const uint8_t ucQueueType) ;
QueueHandle_t xQueueCreateMutexStatic(const uint8_t ucQueueType, StaticQueue_t *pxStaticQueue) ;
QueueHandle_t xQueueCreateCountingSemaphore(const UBaseType_t uxMaxCount, const UBaseType_t uxInitialCount) ;
QueueHandle_t xQueueCreateCountingSemaphoreStatic(const UBaseType_t uxMaxCount, const UBaseType_t uxInitialCount, StaticQueue_t *pxStaticQueue) ;
void *xQueueGetMutexHolder(QueueHandle_t xSemaphore) ;





BaseType_t xQueueTakeMutexRecursive(QueueHandle_t xMutex, TickType_t xTicksToWait) ;
BaseType_t xQueueGiveMutexRecursive(QueueHandle_t pxMutex) ;
# 1639 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/queue.h"
QueueHandle_t xQueueGenericCreate(const UBaseType_t uxQueueLength, const UBaseType_t uxItemSize, const uint8_t ucQueueType) ;
# 1648 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/queue.h"
QueueHandle_t xQueueGenericCreateStatic(const UBaseType_t uxQueueLength, const UBaseType_t uxItemSize, uint8_t *pucQueueStorage, StaticQueue_t *pxStaticQueue, const uint8_t ucQueueType) ;
# 1699 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/queue.h"
QueueSetHandle_t xQueueCreateSet(const UBaseType_t uxEventQueueLength) ;
# 1723 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/queue.h"
BaseType_t xQueueAddToSet(QueueSetMemberHandle_t xQueueOrSemaphore, QueueSetHandle_t xQueueSet) ;
# 1742 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/queue.h"
BaseType_t xQueueRemoveFromSet(QueueSetMemberHandle_t xQueueOrSemaphore, QueueSetHandle_t xQueueSet) ;
# 1778 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/queue.h"
QueueSetMemberHandle_t xQueueSelectFromSet(QueueSetHandle_t xQueueSet, const TickType_t xTicksToWait) ;




QueueSetMemberHandle_t xQueueSelectFromSetFromISR(QueueSetHandle_t xQueueSet) ;


void vQueueWaitForMessageRestricted(QueueHandle_t xQueue, TickType_t xTicksToWait, const BaseType_t xWaitIndefinitely) ;
BaseType_t xQueueGenericReset(QueueHandle_t xQueue, BaseType_t xNewQueue) ;
void vQueueSetQueueNumber(QueueHandle_t xQueue, UBaseType_t uxQueueNumber) ;
UBaseType_t uxQueueGetQueueNumber(QueueHandle_t xQueue) ;
uint8_t ucQueueGetQueueType(QueueHandle_t xQueue) ;

UBaseType_t uxQueueMessagesSet(const QueueHandle_t xQueue, int cnt);
# 78 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/semphr.h" 2

typedef QueueHandle_t SemaphoreHandle_t;
# 29 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\os/os_type.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h" 1
# 78 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/list.h" 1
# 181 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/list.h"
struct xLIST_ITEM {

                        TickType_t xItemValue;
    struct xLIST_ITEM * pxNext;
    struct xLIST_ITEM * pxPrevious;
    void *pvOwner;
    void * pvContainer;

};
typedef struct xLIST_ITEM ListItem_t;

struct xMINI_LIST_ITEM {

                        TickType_t xItemValue;
    struct xLIST_ITEM * pxNext;
    struct xLIST_ITEM * pxPrevious;
};
typedef struct xMINI_LIST_ITEM MiniListItem_t;




typedef struct xLIST {

                        UBaseType_t uxNumberOfItems;
    ListItem_t * pxIndex;
    MiniListItem_t xListEnd;

} List_t;
# 383 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/list.h"
void vListInitialise(List_t *const pxList) ;
# 394 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/list.h"
void vListInitialiseItem(ListItem_t *const pxItem) ;
# 407 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/list.h"
void vListInsert(List_t *const pxList, ListItem_t *const pxNewListItem) ;
# 428 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/list.h"
void vListInsertEnd(List_t *const pxList, ListItem_t *const pxNewListItem) ;
# 443 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/list.h"
UBaseType_t uxListRemove(ListItem_t *const pxItemToRemove) ;
# 79 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h" 2
# 103 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
typedef void *TaskHandle_t;





typedef BaseType_t (*TaskHookFunction_t)(void *);


typedef enum {
    eRunning = 0,
    eReady,
    eBlocked,
    eSuspended,
    eDeleted,
    eInvalid
} eTaskState;


typedef enum {
    eNoAction = 0,
    eSetBits,
    eIncrement,
    eSetValueWithOverwrite,
    eSetValueWithoutOverwrite
} eNotifyAction;




typedef struct xTIME_OUT {
    BaseType_t xOverflowCount;
    TickType_t xTimeOnEntering;
} TimeOut_t;




typedef struct xMEMORY_REGION {
    void *pvBaseAddress;
    uint32_t ulLengthInBytes;
    uint32_t ulParameters;
} MemoryRegion_t;




typedef struct xTASK_PARAMETERS {
    TaskFunction_t pvTaskCode;
    const char *const pcName;
    uint16_t usStackDepth;
    void *pvParameters;
    UBaseType_t uxPriority;
    StackType_t *puxStackBuffer;
    MemoryRegion_t xRegions[ 1 ];
} TaskParameters_t;



typedef struct xTASK_STATUS {
    TaskHandle_t xHandle;
    const char *pcTaskName;
    UBaseType_t xTaskNumber;
    eTaskState eCurrentState;
    UBaseType_t uxCurrentPriority;
    UBaseType_t uxBasePriority;
    uint32_t ulRunTimeCounter;
    StackType_t *pxStackBase;
    uint16_t usStackHighWaterMark;
} TaskStatus_t;


typedef enum {
    eAbortSleep = 0,
    eStandardSleep,
    eNoTasksWaitingTimeout
} eSleepModeStatus;
# 353 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
BaseType_t xTaskCreate(TaskFunction_t pxTaskCode,
                       const char *const pcName,
                       const uint16_t usStackDepth,
                       void *const pvParameters,
                       UBaseType_t uxPriority,
                       TaskHandle_t *const pxCreatedTask) ;
# 469 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
TaskHandle_t xTaskCreateStatic(TaskFunction_t pxTaskCode,
                               const char *const pcName,
                               const uint32_t ulStackDepth,
                               void *const pvParameters,
                               UBaseType_t uxPriority,
                               StackType_t *const puxStackBuffer,
                               StaticTask_t *const pxTaskBuffer) ;
# 595 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
void vTaskAllocateMPURegions(TaskHandle_t xTask, const MemoryRegion_t *const pxRegions) ;
# 636 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
void vTaskDelete(TaskHandle_t xTaskToDelete) ;
# 688 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
void vTaskDelay(const TickType_t xTicksToDelay) ;
# 747 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
void vTaskDelayUntil(TickType_t *const pxPreviousWakeTime, const TickType_t xTimeIncrement) ;
# 772 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
BaseType_t xTaskAbortDelay(TaskHandle_t xTask) ;
# 819 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
UBaseType_t uxTaskPriorityGet(TaskHandle_t xTask) ;







UBaseType_t uxTaskPriorityGetFromISR(TaskHandle_t xTask) ;
# 845 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
eTaskState eTaskGetState(TaskHandle_t xTask) ;
# 901 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
void vTaskGetInfo(TaskHandle_t xTask, TaskStatus_t *pxTaskStatus, BaseType_t xGetFreeStackSpace, eTaskState eState) ;
# 943 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
void vTaskPrioritySet(TaskHandle_t xTask, UBaseType_t uxNewPriority) ;
# 994 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
void vTaskSuspend(TaskHandle_t xTaskToSuspend) ;
# 1043 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
void vTaskResume(TaskHandle_t xTaskToResume) ;
# 1072 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
BaseType_t xTaskResumeFromISR(TaskHandle_t xTaskToResume) ;
# 1105 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
void vTaskStartScheduler(void) ;
# 1161 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
void vTaskEndScheduler(void) ;
# 1212 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
void vTaskSuspendAll(void) ;
# 1266 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
BaseType_t xTaskResumeAll(void) ;
# 1281 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
TickType_t xTaskGetTickCount(void) ;
# 1297 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
TickType_t xTaskGetTickCountFromISR(void) ;
# 1311 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
UBaseType_t uxTaskGetNumberOfTasks(void) ;
# 1324 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
char *pcTaskGetName(TaskHandle_t xTaskToQuery) ;
# 1340 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
TaskHandle_t xTaskGetHandle(const char *pcNameToQuery) ;
# 1361 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
UBaseType_t uxTaskGetStackHighWaterMark(TaskHandle_t xTask) ;
# 1379 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
void vTaskSetApplicationTaskTag(TaskHandle_t xTask, TaskHookFunction_t pxHookFunction) ;







TaskHookFunction_t xTaskGetApplicationTaskTag(TaskHandle_t xTask) ;
# 1414 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
BaseType_t xTaskCallApplicationTaskHook(TaskHandle_t xTask, void *pvParameter) ;
# 1423 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
TaskHandle_t xTaskGetIdleTaskHandle(void) ;
# 1522 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
UBaseType_t uxTaskGetSystemState(TaskStatus_t *const pxTaskStatusArray, const UBaseType_t uxArraySize, uint32_t *const pulTotalRunTime) ;
# 1569 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
void vTaskList(char *pcWriteBuffer) ;
# 1623 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
void vTaskGetRunTimeStats(char *pcWriteBuffer) ;
# 1704 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
BaseType_t xTaskGenericNotify(TaskHandle_t xTaskToNotify, uint32_t ulValue, eNotifyAction eAction, uint32_t *pulPreviousNotificationValue) ;
# 1795 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
BaseType_t xTaskGenericNotifyFromISR(TaskHandle_t xTaskToNotify, uint32_t ulValue, eNotifyAction eAction, uint32_t *pulPreviousNotificationValue, BaseType_t *pxHigherPriorityTaskWoken) ;
# 1872 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
BaseType_t xTaskNotifyWait(uint32_t ulBitsToClearOnEntry, uint32_t ulBitsToClearOnExit, uint32_t *pulNotificationValue, TickType_t xTicksToWait) ;
# 1973 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
void vTaskNotifyGiveFromISR(TaskHandle_t xTaskToNotify, BaseType_t *pxHigherPriorityTaskWoken) ;
# 2042 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
uint32_t ulTaskNotifyTake(BaseType_t xClearCountOnExit, TickType_t xTicksToWait) ;
# 2058 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
BaseType_t xTaskNotifyStateClear(TaskHandle_t xTask);
# 2079 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
BaseType_t xTaskIncrementTick(void) ;
# 2112 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
void vTaskPlaceOnEventList(List_t *const pxEventList, const TickType_t xTicksToWait) ;
void vTaskPlaceOnUnorderedEventList(List_t *pxEventList, const TickType_t xItemValue, const TickType_t xTicksToWait) ;
# 2126 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
void vTaskPlaceOnEventListRestricted(List_t *const pxEventList, TickType_t xTicksToWait, const BaseType_t xWaitIndefinitely) ;
# 2152 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
BaseType_t xTaskRemoveFromEventList(const List_t *const pxEventList) ;
BaseType_t xTaskRemoveFromUnorderedEventList(ListItem_t *pxEventListItem, const TickType_t xItemValue) ;
# 2163 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
int xTaskSwitchContext(void) ;





TickType_t uxTaskResetEventItemValue(void) ;




TaskHandle_t xTaskGetCurrentTaskHandle(void) ;




void vTaskSetTimeOutState(TimeOut_t *const pxTimeOut) ;





BaseType_t xTaskCheckForTimeOut(TimeOut_t *const pxTimeOut, TickType_t *const pxTicksToWait) ;





void vTaskMissedYield(void) ;





BaseType_t xTaskGetSchedulerState(void) ;





void vTaskPriorityInherit(TaskHandle_t const pxMutexHolder) ;





BaseType_t xTaskPriorityDisinherit(TaskHandle_t const pxMutexHolder) ;




UBaseType_t uxTaskGetTaskNumber(TaskHandle_t xTask) ;





void vTaskSetTaskNumber(TaskHandle_t xTask, const UBaseType_t uxHandle) ;
# 2230 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
void vTaskStepTick(const TickType_t xTicksToJump) ;

TickType_t xGetExpectedIdleTime(void) ;
# 2247 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/FreeRTOS/task.h"
eSleepModeStatus eTaskConfirmSleepModeStatus(void) ;





void *pvTaskIncrementMutexHeldCount(void) ;

void vPortStartFirstTask(void) ;


TickType_t xGetExpectedIdleTime(void);

void *uxTaskStack(void *tcb);
# 30 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\os/os_type.h" 2

typedef StaticSemaphore_t OS_SEM, OS_MUTEX;
typedef StaticQueue_t OS_QUEUE;
# 18 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h" 2
# 70 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
void os_init();

void os_start(void);
void os_init_tick(int);
# 89 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_task_create(void (*task)(void *p_arg),
                   void *p_arg,
                   u8 prio,
                   u32 stksize,
                   int qsize,
                   const char *name);
# 104 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
const char *os_current_task();
# 115 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_task_del_req(const char *name);
# 126 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_task_del_res(const char *name);
# 137 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_task_del(const char *name);
# 147 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
void os_time_dly(int time_tick);
# 160 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_taskq_post(const char *name, int argc, ...);
# 172 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_taskq_accept(int argc, int *argv);
# 186 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_taskq_pend(const char *fmt, int *argv, int argc);
int os_task_pend(const char *fmt, int *argv, int argc);
int __os_taskq_pend(int *argv, int argc, int tick);
# 204 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_taskq_post_type(const char *name, int type, int argc, int *argv);
# 218 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_taskq_post_msg(const char *name, int argc, ...);
# 232 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_taskq_post_event(const char *name, int argc, ...);
# 245 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_taskq_del_type(const char *name, int type);
int os_taskq_del(const char *name, int type);
# 255 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_taskq_flush();
# 267 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_sem_create(OS_SEM *, int);
# 278 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_sem_accept(OS_SEM *);
# 290 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_sem_pend(OS_SEM *, int timeout);
# 301 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_sem_post(OS_SEM *);
# 313 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_sem_del(OS_SEM *, int block);
# 325 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_sem_set(OS_SEM *, u16 cnt);
# 336 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_sem_valid(OS_SEM *);
# 347 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_sem_query(OS_SEM *);
# 358 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_mutex_create(OS_MUTEX *);
# 369 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_mutex_accept(OS_MUTEX *);
# 381 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_mutex_pend(OS_MUTEX *, int timeout);
# 392 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_mutex_post(OS_MUTEX *);
# 404 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_mutex_del(OS_MUTEX *, int block);
# 415 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_mutex_valid(OS_MUTEX *);
# 427 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/os/os_api.h"
int os_q_create(OS_QUEUE *pevent, QS size);

int os_q_del(OS_QUEUE *pevent, u8 opt);

int os_q_flush(OS_QUEUE *pevent);

int os_q_pend(OS_QUEUE *pevent, int timeout, void *msg);

int os_q_post(OS_QUEUE *pevent, void *msg);

int os_q_query(OS_QUEUE *pevent);

int os_q_valid(OS_QUEUE *pevent);

int task_queue_post_event(const char *name, void *data, int len);

void *os_task_get_handle(const char *name);
# 6 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/task.h" 2


struct task_info {
    const char *name;
    u8 prio;
    u16 stack_size;
    u16 qsize;
};



typedef OS_SEM sem_t;
typedef OS_MUTEX mutex_t;


int task_create(void (*task)(void *p), void *p, const char *name);


int task_exit(const char *name);

int task_delete(const char *name);

int task_kill(const char *name);

int os_cpu_usage(const char *task_name, int *usage);
# 8 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\device/uart.h" 2







struct uart_outport {
    u8 tx_pin;
    u8 rx_pin;
    u16 value;
};

extern void putbyte(char a);




enum uart_clk_src {
    LSB_CLK,
    OSC_CLK,
    PLL_48M,
};


enum _uart_port_out {

    PORTC_0_1 = 0x00001000,
    PORTG_6_7 = 0x00002000,
    PORTH_12_13 = 0x00003000,
    PORTB_14_15 = 0x00004000,

    PORTC_2_3 = 0x00005000,
    PORTH_2_5 = 0x00006000,
    PORTH_14_15 = 0x00007000,
    PORTC_6_7 = 0x00008000,

    PORTE_0_1 = 0x00009000,
    PORTB_4_3 = 0x0000A000,
    PORTD_9_10 = 0x0000B000,
    PORTD_14_15 = 0x0000C000,

    PORT_REMAP = 0x0000D000,
};

struct uart_platform_data {
    u8 *name;

    u8 irq;
    u8 tx_pin;
    u8 rx_pin;
    u32 flags;
    u32 baudrate;

    enum _uart_port_out port;
    void (*port_remap_func)(void);
    u32 max_continue_recv_cnt;
    u32 idle_sys_clk_cnt;
    enum uart_clk_src clk_src;
};

enum {
    UART_CIRCULAR_BUFFER_WRITE_OVERLAY = -1,
    UART_RECV_TIMEOUT = -2,
    UART_RECV_EXIT = -3,
};
# 95 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\device/uart.h"
struct uart_device {
    char *name;
    const struct uart_operations *ops;
    struct device dev;
    const struct uart_platform_data *priv;
    OS_MUTEX mutex;
};




struct uart_operations {
    int (*init)(struct uart_device *);
    int (*read)(struct uart_device *, void *buf, u32 len);
    int (*write)(struct uart_device *, void *buf, u16 len);
    int (*ioctl)(struct uart_device *, u32 cmd, u32 arg);
    int (*close)(struct uart_device *);
};






extern struct uart_device uart_device_begin[], uart_device_end[];






extern const struct device_operations uart_dev_ops;
# 10 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/uart.h" 2
# 48 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/uart.h"
extern const struct device_operations uart_dev_ops;


extern int uart_init(const struct uart_platform_data *);
# 8 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/uart_dev.h" 1
# 31 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/uart_dev.h"
static inline u32 ut_get_jiffies(void)
{

    return jiffies;




}

static inline u32 ut_msecs_to_jiffies(u32 msecs)
{
    if (msecs >= 10) {
        msecs /= 10;
    } else if (msecs) {
        msecs = 1;
    }
    return msecs;
}


typedef OS_SEM UT_Semaphore ;
static inline void UT_OSSemCreate(UT_Semaphore *sem, u32 count)
{
    os_sem_create(sem, count);
}
static inline void UT_OSSemPost(UT_Semaphore *sem)
{
    os_sem_post(sem);
}
static inline u32 UT_OSSemPend(UT_Semaphore *sem, u32 timeout)
{
    return os_sem_pend(sem, timeout);
}
static inline void UT_OSSemSet(UT_Semaphore *sem, u32 count)
{
    os_sem_set(sem, count);
}
static inline void UT_OSSemClose(UT_Semaphore *sem)
{

}
static inline void ut_sleep()
{
    os_time_dly(1);
}
# 120 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/uart_dev.h"
typedef void (*ut_isr_cbfun)(void *ut_bus, u32 status);
struct uart_platform_data_t {
    u8 tx_pin;
    u8 rx_pin;
    void *rx_cbuf;
    u32 rx_cbuf_size;
    u32 frame_length;
    u32 rx_timeout;
    ut_isr_cbfun isr_cbfun;
    void *argv;
    u32 is_9bit: 1;
    u32 baud: 24;
};




typedef struct {
    u8 *buffer;
    u32 buf_size;
    u32 buf_in;
    u32 buf_out;
} KFIFO;

enum {
    UT_TX = 1,
    UT_RX,
    UT_RX_OT
};




typedef struct {
    ut_isr_cbfun isr_cbfun;
    void *argv;
    void (*putbyte)(char a);
    u8(*getbyte)(u8 *buf, u32 timeout);
    u32(*read)(u8 *inbuf, u32 len, u32 timeout);
    void (*write)(const u8 *outbuf, u32 len);
    void (*set_baud)(u32 baud);
    u32 frame_length;
    u32 rx_timeout;
    u32 txrx_one_io;
    KFIFO kfifo;
    UT_Semaphore sem_rx;
    UT_Semaphore sem_tx;
} uart_bus_t;


const uart_bus_t *uart_dev_open(const struct uart_platform_data_t *arg);
u32 uart_dev_close(uart_bus_t *ut);
# 9 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h" 1
# 12 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
enum {
    CH0_UT0_TX,
    CH0_UT1_TX,
    CH0_T0_PWM_OUT,
    CH0_T1_PWM_OUT,
    CH0_RTOSH_CLK,
    CH0_BTOSC_CLK,
    CH0_PLL_12M,
    CH0_UT2_TX,
    CH0_CH0_PWM_H,
    CH0_CH0_PWM_L,
    CH0_CH1_PWM_H,
    CH0_CH1_PWM_L,
    CH0_CH2_PWM_H,
    CH0_CH2_PWM_L,
    CH0_WLC_BT_FREQ,
    CH0_T3_PWM_OUT,

    CH1_UT0_TX = 0x10,
    CH1_UT1_TX,
    CH1_T0_PWM_OUT,
    CH1_WLC_BT_PRO,
    CH1_RTOSL_CLK,
    CH1_BTOSC_CLK,
    CH1_SPDIF_DO,
    CH1_UT2_TX,
    CH1_CH0_PWM_H,
    CH1_CH0_PWM_L,
    CH1_CH1_PWM_H,
    CH1_CH1_PWM_L,
    CH1_CH2_PWM_H,
    CH1_CH2_PWM_L,
    CH1_T2_PWM_OUT,
    CH1_T3_PWM_OUT,

    CH2_UT1_RTS = 0x20,
    CH2_UT1_TX,
    CH2_WLC_BT_ACTIVE,
    CH2_T1_PWM_OUT,
    CH2_PLNK_SCLK,
    CH2_BTOSC_CLK,
    CH2_PLL_24M,
    CH2_UT2_TX,
    CH2_CH0_PWM_H,
    CH2_CH0_PWM_L,
    CH2_CH1_PWM_H,
    CH2_CH1_PWM_L,
    CH2_CH2_PWM_H,
    CH2_CH2_PWM_L,
    CH2_T2_PWM_OUT,
    CH2_T3_PWM_OUT,
};
# 159 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
enum {
    INPUT_CH0,
    INPUT_CH1,
    INPUT_CH2,
    INPUT_CH3,
};

enum gpio_op_mode {
    GPIO_SET = 1,
    GPIO_AND,
    GPIO_OR,
    GPIO_XOR,
};
enum gpio_direction {
    GPIO_OUT = 0,
    GPIO_IN = 1,
};
struct gpio_reg {
    volatile unsigned int out;
    volatile unsigned int in;
    volatile unsigned int dir;
    volatile unsigned int die;
    volatile unsigned int pu;
    volatile unsigned int pd;
    volatile unsigned int hd0;
    volatile unsigned int hd;
    volatile unsigned int dieh;
};

struct gpio_platform_data {
    unsigned int gpio;
};
# 215 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
void usb_iomode(u32 enable);
# 224 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
int gpio_set_direction(u32 gpio, u32 dir);
# 235 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
int gpio_set_output_value(u32 gpio, u32 dir);
# 247 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
u32 gpio_dir(u32 gpio, u32 start, u32 len, u32 dat, enum gpio_op_mode op);
# 257 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
int gpio_direction_output(u32 gpio, int value);
# 269 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
u32 gpio_out(u32 gpio, u32 start, u32 len, u32 dat);
# 279 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
int gpio_set_pull_up(u32 gpio, int value);
# 292 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
u32 gpio_set_pu(u32 gpio, u32 start, u32 len, u32 dat, enum gpio_op_mode op);
# 302 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
int gpio_set_pull_down(u32 gpio, int value);
# 314 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
u32 gpio_set_pd(u32 gpio, u32 start, u32 len, u32 dat, enum gpio_op_mode op);
# 324 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
u32 gpio_set_hd0(u32 gpio, u32 value);
# 334 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
int gpio_set_hd(u32 gpio, int value);
# 344 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
int gpio_set_die(u32 gpio, int value);
# 354 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
u32 gpio_set_dieh(u32 gpio, u32 value);
# 366 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
u32 gpio_die(u32 gpio, u32 start, u32 len, u32 dat, enum gpio_op_mode op);
# 378 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
u32 gpio_dieh(u32 gpio, u32 start, u32 len, u32 dat, enum gpio_op_mode op);
# 388 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
u32 gpio_output_channle(u32 gpio, u32 clk);
# 397 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
int gpio_read(u32 gpio);
# 406 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
u32 gpio_in(u32 gpio);
# 415 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
u32 gpio_write(u32 gpio, u32 value);
# 424 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
u32 gpio_wakeup0(u32 gpio);
# 433 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
u32 gpio_irflt_in(u32 gpio);
# 442 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
u32 gpio_cap_mux(u32 gpio);
# 454 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
u32 gpio_uart_rx_input(u32 gpio, u32 ut, u32 ch);






u32 gpio_close_uart0(void);






u32 gpio_close_uart1(void);






u32 gpio_close_uart2(void);
# 491 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
u32 gpio_set_uart0(u32 ch);
# 506 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
u32 gpio_set_uart1(u32 ch);
# 521 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
u32 gpio_set_uart2(u32 ch);

enum {
    IRFLT_LSB,
    IRFLT_RC,
    IRFLT_OSC,
    IRFLT_PLL48M,
};
enum {
    IRFLT_DIV1,
    IRFLT_DIV2,
    IRFLT_DIV4,
    IRFLT_DIV8,
    IRFLT_DIV16,
    IRFLT_DIV32,
    IRFLT_DIV64,
    IRFLT_DIV128,
    IRFLT_DIV256,
    IRFLT_DIV512,
    IRFLT_DIV1024,
    IRFLT_DIV2048,
    IRFLT_DIV4096,
    IRFLT_DIV8192,
    IRFLT_DIV16384,
    IRFLT_DIV32768,
};
# 556 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/gpio.h"
u32 gpio_irflt_to_timer(u32 t);


u32 get_gpio(const char *p);
# 10 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/spiflash.h" 1






# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\device/spiflash.h" 1
# 13 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\device/spiflash.h"
struct spi_device;

enum spiflash_bit_mode {
    SPI_2WIRE_MODE,
    SPI_ODD_MODE,
    SPI_DUAL_MODE,
    SPI_QUAD_MODE,
};

enum spiflash_read_mode {
    FAST_READ_OUTPUT_MODE,
    FAST_READ_IO_MODE,
    FAST_READ_IO_CONTINUOUS_READ_MODE,
};

enum sfc_run_mode {

    SFC_READ_DATA_MODE = (1 << 0),
    SFC_FAST_READ_MODE = (1 << 1),

    SFC_FAST_READ_DUAL_IO_NORMAL_READ_MODE = (1 << 2),
    SFC_FAST_READ_DUAL_IO_CONTINUOUS_READ_MODE = (1 << 3),
    SFC_FAST_READ_DUAL_OUTPUT_MODE = (1 << 4),

    SFC_FAST_READ_QUAD_IO_NORMAL_READ_MODE = (1 << 5),
    SFC_FAST_READ_QUAD_IO_CONTINUOUS_READ_MODE = (1 << 6),
    SFC_FAST_READ_QUAD_OUTPUT_MODE = (1 << 7),

};
struct spi_ops {
    int (*set_cs)(int);
    int (*init)(void *);
    u8(*read_byte)(int *err);
    int (*read)(u8 *, u32 len, u8 mode);
    int (*write_byte)(u8 cmd);
    int (*write_cmd)(u8 *cmd, u32 len);
    int (*write)(u8 *, u32 len);
    u8(*get_bit_mode)();
};


struct sf_info {
    u32 id;
    u16 page_size;
    u16 block_size;
    u32 chip_size;
};

enum sf_erase_type {
    SF_SECTOR_ERASE,
    SF_BLOCK_ERASE,
    SF_CHIP_ERASE,
};
# 79 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\device/spiflash.h"
struct spi_device {
    const char *name;
    const struct spi_ops *ops;
};

struct spiflash_platform_data {
    const char *name;
    enum spiflash_read_mode mode;
    enum sfc_run_mode sfc_run_mode;
    void *private_data;
};


struct spiflash {
    struct list_head entry;
    void *device;
    struct device dev;
    struct sf_info info;
    const struct spiflash_platform_data *pd;
    const char *name;
    OS_MUTEX mutext;
    u8 inited;
    u8 read_mode;
    u8 read_cmd_mode;
    u8 write_cmd_mode;
    u8 continuous_read_mode;
};






extern struct spi_device spi_device_begin[];
extern struct spi_device spi_device_end[];




extern struct spiflash *__get_spiflash(const char *name);
# 8 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/spiflash.h" 2
# 20 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/spiflash.h"
extern const struct device_operations spiflash_dev_ops;
extern const struct device_operations sfcflash_dev_ops;
extern const struct device_operations sdfile_dev_ops;
# 11 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/includes.h" 2

# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/power_interface.h" 1
# 14 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/power_interface.h"
extern u32 nvbss_begin;
extern u32 nvbss_length;
extern u32 nvdata_begin;
extern u32 nvdata_size;
extern u32 nvdata_addr;





enum {
    MAGIC_ADDR = 2,
    ENTRY_ADDR = 3,
};
# 45 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/power_interface.h"
enum {
    OSC_TYPE_LRC = 0,
    OSC_TYPE_RTC,
    OSC_TYPE_BT_OSC,
};

enum {
    PWR_NO_CHANGE = 0,
    PWR_LDO33,
    PWR_LDO15,
    PWR_DCDC15,
};

enum {
    LONG_4S_RESET = 0,
    LONG_8S_RESET,
};


enum {
    VDDIOM_VOL_22V = 0,
    VDDIOM_VOL_24V,
    VDDIOM_VOL_26V,
    VDDIOM_VOL_28V,
    VDDIOM_VOL_30V,
    VDDIOM_VOL_32V,
    VDDIOM_VOL_34V,
    VDDIOM_VOL_36V,
};


enum {
    VDDIOW_VOL_21V = 0,
    VDDIOW_VOL_24V,
    VDDIOW_VOL_28V,
    VDDIOW_VOL_32V,
};

struct low_power_param {
    u8 osc_type;
    u32 btosc_hz;
    u8 delay_us;
    u8 config;
    u8 btosc_disable;
    u8 dcdc_port;

    u8 vddiom_lev;
    u8 vddiow_lev;
    u8 pd_wdvdd_lev;
    u8 vddio_keep;
    u8 vdc13_keep;

    u32 osc_delay_us;
    u8 virtual_rtc;
    u8 rtc_clk;
    u32 vir_rtc_trim_time;
    u8 user_nv_timer_en;
    u16 nv_timer_interval;
};






typedef enum {
    PORT_FLT_NULL = 0,
    PORT_FLT_32us,
    PORT_FLT_64us,
    PORT_FLT_128us,
    PORT_FLT_256us,
    PORT_FLT_512us,
    PORT_FLT_1ms,
    PORT_FLT_2ms,
} PORT_FLT;

struct port_wakeup {
    u8 pullup_down_enable;
    u8 edge;
    u8 attribute;
    u8 iomap;
    u8 filter_enable;
};

struct charge_wakeup {
    u8 attribute;
};

struct alarm_wakeup {
    u8 attribute;
};

struct lvd_wakeup {
    u8 attribute;
};

struct sub_wakeup {
    u8 attribute;
};





struct wakeup_param {
    const PORT_FLT filter;
    const struct port_wakeup *port[8];
    const struct port_wakeup *rtc_port[2];
    const struct charge_wakeup *charge;
    const struct alarm_wakeup *alram;
    const struct lvd_wakeup *lvd;
    const struct sub_wakeup *sub;
};

struct reset_param {
    u8 en;
    u8 mode;
    u8 level;
    u8 iomap;
};

struct low_power_operation {

    const char *name;

    u32(*get_timeout)(void *priv);

    void (*suspend_probe)(void *priv);

    void (*suspend_post)(void *priv, u32 usec);

    void (*resume)(void *priv, u32 usec);

    void (*resume_post)(void *priv, u32 usec);

    void (*off_probe)(void *priv);

    void (*off_post)(void *priv, u32 usec);

    void (*on)(void *priv);
};

u32 __tus_carry(u32 x);

u8 __power_is_poweroff(void);

void poweroff_recover(void);

void power_init(const struct low_power_param *param);

u8 power_is_low_power_probe(void);

u8 power_is_low_power_post(void);

void power_set_soft_poweroff(void);

void set_softoff_wakeup_time_ms(u32 ums);

void set_softoff_wakeup_time_sec(u32 sec);

void power_set_mode(u8 mode);

void power_keep_dacvdd_en(u8 en);

void power_set_callback(u8 mode, void (*powerdown_enter)(u8 step), void (*powerdown_exit)(u32), void (*soft_poweroff_enter)(void));

u8 power_is_poweroff_post(void);


void power_set_proweroff(void);

u8 power_reset_source_dump(void);


void low_power_on(void);

void low_power_request(void);

void low_power_exit_request(void);

void low_power_lock(void);

void low_power_unlock(void);

void *low_power_get(void *priv, const struct low_power_operation *ops);

void low_power_put(void *priv);

void low_power_sys_request(void *priv);

void *low_power_sys_get(void *priv, const struct low_power_operation *ops);

void low_power_sys_put(void *priv);

u8 low_power_sys_is_idle(void);

s32 low_power_trace_drift(u32 usec);

void low_power_reset_osc_type(u8 type);

u8 low_power_get_default_osc_type(void);

u8 low_power_get_osc_type(void);


void power_wakeup_index_enable(u8 index);

void power_wakeup_index_disable(u8 index);

void power_wakeup_set_wakeup_io(u8 index, struct port_wakeup *port);

void power_wakeup_init(const struct wakeup_param *param);

void power_wakeup_init_test();

u8 get_wakeup_source(void);

u8 is_ldo5v_wakeup(void);


void p33_soft_reset(void);

void reset_the_wakeup_param(struct wakeup_param *param);


void power_reset_close();

void lrc_debug(u8 a, u8 b);

void sdpg_config(int enable);

void power_set_wvdd(u8 level);

int cpu_reset_by_soft();

void lvd_extern_wakeup_enable(void);

void port_edge_wkup_set_callback(void (*wakeup_callback)(u8 index, u32 gpio));


typedef u8(*idle_handler_t)(void);

struct lp_target {
    char *name;
    idle_handler_t is_idle;
};





extern const struct lp_target lp_target_begin[];
extern const struct lp_target lp_target_end[];
# 13 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/efuse.h" 1




u16 get_chip_id();
u16 get_vbat_trim();
u16 get_vbg_trim();
u8 get_sysdvdd_trim();
u32 get_chip_version();







u16 get_lrc_ws_inc();
u16 get_lrc_ws_init();
u16 get_btosc_ws_inc();
u16 get_btosc_ws_init();
u8 get_lrc_change_mode();

u32 get_boot_flag();
void set_boot_flag(u32 flag);

u32 p33_rd_page(u8 page);
# 14 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/wdt.h" 1
# 21 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/wdt.h"
void wdt_init(u8 time);
void wdt_close(void);
void wdt_clear(void);

void wdt_enable(void);
void wdt_disable(void);

u32 wdt_get_time(void);
# 15 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/timer.h" 1





void delay_2ms(int cnt);
u32 timer_get_sec(void);
u32 timer_get_ms(void);
# 16 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/includes.h" 2
# 2 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\cpu\\br23\\setup.c" 2



# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/debug.h" 1




void ram_protect_close(void);
void debug_init();
void exception_analyze();




void prp_store_rang_limit_set(void *low_addr, void *high_addr, u8 mode);


void dsp_store_rang_limit_set(void *low_addr, void *high_addr, u8 mode);


void bus_inv_expt_enable(u8 enable);


void dsp_ex_inv_enable(u8 enable);


void dsp_of_inv_enable(u8 enable);


void dsp_if_inv_enable(u8 enable);


void peripheral_bus_inv_enable(u8 enable);




void emu_misalign_enable(u8 enable);


void emu_illeg_enable(u8 enable);


void emu_div0_enable(u8 enable);


void emu_fpu_inv_enable(u8 enable);


void emu_fpu_inf_enable(u8 enable);


void emu_fpu_tiny_enable(u8 enable);


void emu_fpu_huge_enable(u8 enable);


void emu_fpu_ine_enable(u8 enable);


void debug_sfr_test();
# 6 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\cpu\\br23\\setup.c" 2

# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/power/p33.h" 1
# 243 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/power/p33.h"
enum {
    SOFT_FLAG_BT_OSC_ENABLE = (1UL << (0)),
    SOFT_FLAG_RTC_OSC_ENABLE = (1UL << (1)),
    SOFT_FLAG_BOOT_SPI_PORTD_A = (1UL << (2)),
    SOFT_FLAG_BOOT_SPI_PORTD_B = (1UL << (3)),
    SOFT_FLAG_BOOT_SPI_ALL = (1UL << (2)) | (1UL << (3)),
    SOFT_FLAG_SWITCH_OSC_CLK = (1UL << (4)),
    SOFT_FLAG_BOOT_OTP = (1UL << (5)),
};
# 285 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/power/p33.h"
u8 p33_buf(u8 buf);

void p33_xor_1byte(u16 addr, u8 data0);

void p33_and_1byte(u16 addr, u8 data0);

void p33_or_1byte(u16 addr, u8 data0);

void p33_tx_1byte(u16 addr, u8 data0);

u8 p33_rx_1byte(u16 addr);

void P33_CON_SET(u16 addr, u8 start, u8 len, u8 data);

void SET_WVDD_LEV(u8 lev);

void RESET_MASK_SW(u8 sw);

void NV_RAM_POWER_GATE(u8 sw);

void close_32K(u8 keep_osci_flag);

__attribute__((always_inline))
static u8 P33_CON_GET(u8 addr)
{
    u8 reg = 0;
    reg = p33_rx_1byte(addr);
    return reg;
}

__attribute__((always_inline))
static void P33_TX_NBIT(u16 addr, u8 data0, u8 en)
{
    if (en) {
        p33_or_1byte(addr, data0);
    } else {
        p33_and_1byte(addr, ~data0);
    }
}

__attribute__((always_inline))
static void P33_CON_DEBUG(void)
{
    u8 i = 0;
    for (i = 0; i < 0x17 + 1; i++) {

    }
}
# 397 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/power/p33.h"
enum {
    ADC_CHANNEL_SEL_VBG = 0,
    ADC_CHANNEL_SEL_VDC13,
    ADC_CHANNEL_SEL_SYSVDD,
    ADC_CHANNEL_SEL_VTEMP,
    ADC_CHANNEL_SEL_PROGF,
    ADC_CHANNEL_SEL_VBAT1_4,
    ADC_CHANNEL_SEL_LDO5V1_4,
    ADC_CHANNEL_SEL_WVDD,
};
# 430 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/power/p33.h"
enum {
    VDC13_VOL_SEL_105V = 0,
    VDC13_VOL_SEL_110V,
    VDC13_VOL_SEL_115V,
    VDC13_VOL_SEL_120V,
    VDC13_VOL_SEL_125V,
    VDC13_VOL_SEL_130V,
    VDC13_VOL_SEL_135V,
    VDC13_VOL_SEL_140V,
};
# 453 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/power/p33.h"
enum {
    BTDCDC_BIAS_HD_SEL_1uA = 0,
    BTDCDC_BIAS_HD_SEL_1P5uA,
    BTDCDC_BIAS_HD_SEL_2uA,
    BTDCDC_BIAS_HD_SEL_2P5uA,
};





enum {
    BTDCDC_OSC_SEL0537MHz = 0,
    BTDCDC_OSC_SEL0789MHz,
    BTDCDC_OSC_SEL1030MHz,
    BTDCDC_OSC_SEL1270MHz,
    BTDCDC_OSC_SEL1720MHz,
    BTDCDC_OSC_SEL1940MHz,
    BTDCDC_OSC_SEL2150MHz,
    BTDCDC_OSC_SEL2360MHz,
};







enum {
    SYSVDD_VOL_SEL_084V = 0,
    SYSVDD_VOL_SEL_087V,
    SYSVDD_VOL_SEL_090V,
    SYSVDD_VOL_SEL_093V,
    SYSVDD_VOL_SEL_096V,
    SYSVDD_VOL_SEL_099V,
    SYSVDD_VOL_SEL_102V,
    SYSVDD_VOL_SEL_105V,
    SYSVDD_VOL_SEL_108V,
    SYSVDD_VOL_SEL_111V,
    SYSVDD_VOL_SEL_114V,
    SYSVDD_VOL_SEL_117V,
    SYSVDD_VOL_SEL_120V,
    SYSVDD_VOL_SEL_123V,
    SYSVDD_VOL_SEL_126V,
    SYSVDD_VOL_SEL_129V,
};
# 529 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/power/p33.h"
enum {
    VLVD_SEL_19V = 0,
    VLVD_SEL_20V,
    VLVD_SEL_21V,
    VLVD_SEL_22V,
    VLVD_SEL_23V,
    VLVD_SEL_24V,
    VLVD_SEL_25V,
    VLVD_SEL_26V,
};
# 610 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/power/p33.h"
void chg_reg_set(u8 addr, u8 start, u8 len, u8 data);
u8 chg_reg_get(u8 addr);
# 761 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/power/p33.h"
enum {
    WLDO_LEVEL_050V = 0,
    WLDO_LEVEL_054V,
    WLDO_LEVEL_058V,
    WLDO_LEVEL_062V,
    WLDO_LEVEL_066V,
    WLDO_LEVEL_070V,
    WLDO_LEVEL_085V,
    WLDO_LEVEL_133V,
};
# 790 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/power/p33.h"
enum {
    CLK_SEL_32K = 1,
    CLK_SEL_12M,
    CLK_SEL_24M,
};
# 8 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\cpu\\br23\\setup.c" 2

# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\timer.h" 1








struct static_sys_timer {
    void (*func)(void *priv);
    void *priv;
    u32 msec;
    u32 jiffies;
};

struct sys_usec_timer {
    void (*func)(void *priv);
    void *priv;
    const char *owner;
    struct sys_cpu_timer *timer;
};
# 31 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\timer.h"
extern struct static_sys_timer static_hi_timer_begin[];
extern struct static_sys_timer static_hi_timer_end[];






struct sys_cpu_timer {
    u8 busy;
    void *priv;
    void (*set)(u32 usec);
    void (*unset)();
};
# 53 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\timer.h"
extern struct sys_cpu_timer sys_cpu_timer_begin[];
extern struct sys_cpu_timer sys_cpu_timer_end[];
# 78 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\timer.h"
u16 sys_timer_add(void *priv, void (*func)(void *priv), u32 msec);
# 87 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\timer.h"
void sys_timer_del(u16);
# 103 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\timer.h"
u16 sys_timeout_add(void *priv, void (*func)(void *priv), u32 msec);
# 112 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\timer.h"
void sys_timeout_del(u16);
# 121 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\timer.h"
void sys_timer_re_run(u16 id);
# 131 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\timer.h"
void sys_timer_set_user_data(u16 id, void *priv);
# 141 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\timer.h"
void *sys_timer_get_user_data(u16 id);







int sys_timer_modify(u16 id, u32 msec);

int sys_usec_timer_add(void *priv, void (*func)(void *priv), u32 usec);

void sys_usec_timer_schedule(struct sys_cpu_timer *);

void sys_usec_timer_set(int _t, u32 usec);

void sys_usec_timer_del(int);

void sys_timer_dump_time(void);

u32 sys_timer_get_ms(void);







void usr_timer_schedule();
# 185 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\timer.h"
u16 usr_timer_add(void *priv, void (*func)(void *priv), u32 msec, u8 priority);
# 201 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\timer.h"
u16 usr_timeout_add(void *priv, void (*func)(void *priv), u32 msec, u8 priority);
# 212 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\timer.h"
int usr_timer_modify(u16 id, u32 msec);
# 222 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\timer.h"
int usr_timeout_modify(u16 id, u32 msec);
# 231 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\timer.h"
void usr_timer_del(u16 id);
# 240 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\timer.h"
void usr_timeout_del(u16 id);
# 251 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\timer.h"
void usr_timer_dump(void);
# 10 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\cpu\\br23\\setup.c" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/init.h" 1
# 10 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/init.h"
typedef int (*initcall_t)(void);
# 11 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\cpu\\br23\\setup.c" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/includes.h" 1





# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/event.h" 1





# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/generic/rect.h" 1








struct position {
    int x;
    int y;
};

struct rect {
    int left;
    int top;
    int width;
    int height;
};
# 30 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/generic/rect.h"
static inline int in_rect(const struct rect *rect, struct position *pos)
{
    if (rect->left <= pos->x && ((rect)->left + (rect)->width) > pos->x) {
        if (rect->top <= pos->y && ((rect)->top + (rect)->height) > pos->y) {
            return 1;
        }
    }
    return 0;
}

__attribute__((section(".ui_ram")))
static inline bool get_rect_cover(const struct rect *a, const struct rect *b, struct rect *c)
{
    int right, bottom;

    c->top = ((a->top) > (b->top) ? (a->top) : (b->top));
    c->left = ((a->left) > (b->left) ? (a->left) : (b->left));
    right = ((((a)->left + (a)->width)) < (((b)->left + (b)->width)) ? (((a)->left + (a)->width)) : (((b)->left + (b)->width)));
    bottom = ((((a)->top + (a)->height)) < (((b)->top + (b)->height)) ? (((a)->top + (a)->height)) : (((b)->top + (b)->height)));

    if ((c->top < bottom) && (c->left < right)) {
        c->width = right - c->left;
        c->height = bottom - c->top;
        return 1;
    }

    return 0;
}


static inline bool get_rect_nocover_l(const struct rect *a, const struct rect *b, struct rect *c)
{
    int right, bottom;

    c->left = ((((a)->left)) < (((b)->left)) ? (((a)->left)) : (((b)->left)));
    c->top = ((((a)->top)) < (((b)->top)) ? (((a)->top)) : (((b)->top)));
    right = ((((a)->left)) > (((b)->left)) ? (((a)->left)) : (((b)->left)));
    bottom = ((((a)->top + (a)->height)) > (((b)->top + (b)->height)) ? (((a)->top + (a)->height)) : (((b)->top + (b)->height)));

    if ((c->top < bottom) && (c->left < right)) {
        c->width = right - c->left;
        c->height = bottom - c->top;
        return 1;
    }

    return 0;
}


static inline bool get_rect_nocover_r(const struct rect *a, const struct rect *b, struct rect *c)
{
    int right, bottom;

    c->left = ((((a)->left + (a)->width)) < (((b)->left + (b)->width)) ? (((a)->left + (a)->width)) : (((b)->left + (b)->width)));
    c->top = ((((a)->top)) < (((b)->top)) ? (((a)->top)) : (((b)->top)));
    right = ((((a)->left + (a)->width)) > (((b)->left + (b)->width)) ? (((a)->left + (a)->width)) : (((b)->left + (b)->width)));
    bottom = ((((a)->top + (a)->height)) > (((b)->top + (b)->height)) ? (((a)->top + (a)->height)) : (((b)->top + (b)->height)));

    if ((c->top < bottom) && (c->left < right)) {
        c->width = right - c->left;
        c->height = bottom - c->top;
        return 1;
    }

    return 0;
}

static inline bool get_rect_nocover_t(const struct rect *a, const struct rect *b, struct rect *c)
{
    int right, bottom;

    c->left = ((((a)->left)) < (((b)->left)) ? (((a)->left)) : (((b)->left)));
    c->top = ((((a)->top)) < (((b)->top)) ? (((a)->top)) : (((b)->top)));
    right = ((((a)->left + (a)->width)) > (((b)->left + (b)->width)) ? (((a)->left + (a)->width)) : (((b)->left + (b)->width)));
    bottom = ((((a)->top)) > (((b)->top)) ? (((a)->top)) : (((b)->top)));

    if ((c->top < bottom) && (c->left < right)) {
        c->width = right - c->left;
        c->height = bottom - c->top;
        return 1;
    }

    return 0;
}

static inline bool get_rect_nocover_b(const struct rect *a, const struct rect *b, struct rect *c)
{
    int right, bottom;

    c->left = ((((a)->left)) < (((b)->left)) ? (((a)->left)) : (((b)->left)));
    c->top = ((((a)->top + (a)->height)) < (((b)->top + (b)->height)) ? (((a)->top + (a)->height)) : (((b)->top + (b)->height)));
    right = ((((a)->left + (a)->width)) > (((b)->left + (b)->width)) ? (((a)->left + (a)->width)) : (((b)->left + (b)->width)));
    bottom = ((((a)->top + (a)->height)) > (((b)->top + (b)->height)) ? (((a)->top + (a)->height)) : (((b)->top + (b)->height)));

    if ((c->top < bottom) && (c->left < right)) {
        c->width = right - c->left;
        c->height = bottom - c->top;
        return 1;
    }

    return 0;
}
# 7 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/event.h" 2
# 98 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/event.h"
enum {
    KEY_EVENT_CLICK,
    KEY_EVENT_LONG,
    KEY_EVENT_HOLD,
    KEY_EVENT_UP,
    KEY_EVENT_DOUBLE_CLICK,
    KEY_EVENT_TRIPLE_CLICK,
    KEY_EVENT_FOURTH_CLICK,
    KEY_EVENT_FIRTH_CLICK,
    KEY_EVENT_USER,
    KEY_EVENT_MAX,
};


enum {
    DEVICE_EVENT_IN,
    DEVICE_EVENT_OUT,
    DEVICE_EVENT_ONLINE,
    DEVICE_EVENT_OFFLINE,
    DEVICE_EVENT_CHANGE,
};

enum {
    TOUCH_EVENT_DOWN,
    TOUCH_EVENT_MOVE,
    TOUCH_EVENT_HOLD,
    TOUCH_EVENT_UP,
    TOUCH_EVENT_CLICK,
    TOUCH_EVENT_DOUBLE_CLICK,
};

enum {
    NET_EVENT_CMD,
    NET_EVENT_DATA,
    NET_EVENT_CONNECTED,
    NET_EVENT_DISCONNECTED,
    NET_EVENT_SMP_CFG_TIMEOUT,
};


struct key_event {
    u8 init;
    u8 type;
    u16 event;
    u32 value;
    u32 tmr;
};

struct ir_event {
    u8 event;
};

struct msg_event {
    u8 event;
    u8 value;
};
# 162 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/event.h"
struct device_event {
    u8 event;
    int value;
};
struct chargestore_event {
    u8 event;
    u8 *packet ;
    u8 size;
};

struct ancbox_event {
    u8 event;
    u32 value;
};

struct soundbox_tool_event {
    u8 event;
    u8 *packet ;
    u8 size;
};

struct net_event {
    u8 event;
    u8 value;
};
struct bt_event {
    u8 event;
    u8 args[7];
    u32 value;
};

struct axis_event {
    u8 event;
    s16 x;
    s16 y;
};

struct codesw_event {
    u8 event;
    s8 value;
};

struct pbg_event {
    u8 event;
    u8 args[3];
};

struct adt_event {
    u8 event;
    u8 args[3];
};

struct uart_event {
    void *ut_bus;
};

struct uart_cmd_event {
    u8 type;
    u8 cmd;
};

struct ai_event {
    u32 value;
};

struct ear_event {
    u8 value;
};

struct rcsp_event {
    u8 event;
    u8 args[6];
    u8 size;
};

struct chargebox_event {
    u8 event;
};

struct matrix_key_event {
    u16 args[6];
    u8 *map;
};

struct touchpad_event {
    u8 gesture_event;
    s8 x;
    s8 y;
};

struct sys_event {
    u16 type;
    u8 consumed;
    void *arg;
    union {
        struct key_event key;
        struct axis_event axis;
        struct codesw_event codesw;



        struct device_event dev;
        struct net_event net;
        struct bt_event bt;
        struct msg_event msg;
        struct chargestore_event chargestore;
        struct soundbox_tool_event soundbox_tool;
        struct ir_event ir;
        struct pbg_event pbg;
        struct uart_event uart;
        struct uart_cmd_event uart_cmd;
        struct ai_event ai;
        struct ear_event ear;
        struct rcsp_event rcsp;
        struct chargebox_event chargebox;
        struct ancbox_event ancbox;
        struct matrix_key_event matrix_key;
        struct touchpad_event touchpad;
        struct adt_event adt;
    } u;
};




struct static_event_handler {
    int event_type;
    void (*handler)(struct sys_event *);
};
# 299 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/event.h"
extern struct static_event_handler sys_event_handler_begin[];
extern struct static_event_handler sys_event_handler_end[];






int register_sys_event_handler(int event_type, int from, u8 priority,
                               void (*handler)(struct sys_event *));


void unregister_sys_event_handler(void (*handler)(struct sys_event *));





void sys_event_notify(struct sys_event *e);

void sys_event_clear(struct sys_event *e);

void sys_key_event_disable();


void sys_key_event_enable();

void sys_key_event_filter_disable();

void sys_key_event_filter_enable();

void sys_touch_event_disable();


void sys_touch_event_enable();





void sys_event_consume(struct sys_event *e);

void sys_key_event_consume(struct key_event *e);





void sys_device_event_consume(struct device_event *e);
# 358 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/event.h"
void sys_key_event_takeover(bool on, bool once);

void sys_touch_event_takeover(bool on, bool once);


int sys_key_event_map(struct key_event *org, struct key_event *new);
int sys_key_event_unmap(struct key_event *org, struct key_event *new);
# 7 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/includes.h" 2

# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/spinlock.h" 1








struct __spinlock {
    volatile u32 rwlock;
};

typedef struct __spinlock spinlock_t;
# 68 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/spinlock.h"
static inline void spin_lock_init(spinlock_t *lock)
{
    lock->rwlock = 0;
}
extern u32 spin_lock_cnt[];


static inline void spin_lock(spinlock_t *lock)
{
    local_irq_disable();


    do { }while(0);
}


static inline void spin_unlock(spinlock_t *lock)
{

    do { }while(0);
    local_irq_enable();
}
# 9 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/includes.h" 2


# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/wait.h" 1







int wait_completion_schedule();

u16 wait_completion(int (*condition)(void), int (*callback)(void *), void *priv);

int wait_completion_del(u16 id);
# 12 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/app_core.h" 1
# 16 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/app_core.h"
enum app_state {
    APP_STA_CREATE,
    APP_STA_START,
    APP_STA_PAUSE,
    APP_STA_RESUME,
    APP_STA_STOP,
    APP_STA_DESTROY,
};

struct application;


struct intent {
    const char *name;
    int action;
    const char *data;
    u32 exdata;
};


struct application_operation {
    int (*state_machine)(struct application *, enum app_state, struct intent *);
    int (*event_handler)(struct application *, struct sys_event *);
};


struct application {
    u8 state;
    int action;
    char *data;
    const char *name;
    struct list_head entry;
    void *private_data;
    const struct application_operation *ops;
};
# 68 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/app_core.h"
void register_app_event_handler(int (*handler)(struct sys_event *));

struct application *get_current_app();

struct application *get_prev_app();

void app_core_back_to_prev_app();

int start_app(struct intent *it);

int start_app_async(struct intent *it, void (*callback)(void *p, int err), void *p);
# 13 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/app_msg.h" 1







int app_task_put_usr_msg(int msg, int arg_num, ...);


void app_task_get_msg(int *msg, int msg_size, int block);


int app_task_put_key_msg(int msg, int value);


void app_task_clear_key_msg();
# 14 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/database.h" 1






struct db_table {
    const char *name;
    u8 value_bits;
    int value;
};


int db_select_buffer(u8 index, char *buffer, int len);

int db_update_buffer(u8 index, char *buffer, int len);

int db_create(const char *store_dev);


int db_create_table(const struct db_table *table, int num);

u32 db_select(const char *table);

int db_update(const char *table, u32 value);

int db_flush();

int db_reset();

int db_erase();
# 15 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/fs/fs.h" 1
# 12 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/fs/fs.h"
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/sys_time.h" 1






struct sys_time {
    u16 year;
    u8 month;
    u8 day;
    u8 hour;
    u8 min;
    u8 sec;
};
# 13 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/fs/fs.h" 2

# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\fs/fs_file_name.h" 1
# 10 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\fs/fs_file_name.h"
typedef struct _LONG_FILE_NAME {
    u16 lfn_cnt;
    char lfn[512];
} LONG_FILE_NAME;

typedef struct _FS_DIR_INFO {
    u32 sclust;
    u16 dir_type;
    u16 fn_type;
    LONG_FILE_NAME lfn_buf;
} FS_DIR_INFO;

typedef struct _FS_DISP_INFO {
    char tpath[128];
    LONG_FILE_NAME file_name;
    LONG_FILE_NAME dir_name;
    u8 update_flag;
} FS_DISP_INFO;

typedef struct _FLASH_FAT_CLUSTINFO {
    u32 sclust2addr;
    u32 endclust2addr;
    u32 file_len;
} FLASH_FAT_CLUSTINFO;
# 15 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/fs/fs.h" 2





# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\fs/sdfile.h" 1








typedef struct sdfile_file_head {
    u16 head_crc;
    u16 data_crc;
    u32 addr;
    u32 len;
    u8 attr;
    u8 res;
    u16 index;
    char name[16];
} SDFILE_FILE_HEAD;
# 48 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\fs/sdfile.h"
struct sdfile_dir {
    u16 file_num;
    struct sdfile_file_head head;
};

enum sdfile_err_table {
    SDFILE_DIR_NOT_EXIST = -0xFF,
    SDFILE_FILE_NOT_EXIST,
    SDFILE_MALLOC_ERR,
    SDFILE_VM_NOT_FIND,
    SDFILE_DATA_CRC_ERR,
    SDFILE_WRITE_AREA_NEED_ERASE_ERR,
    SDFILE_SUSS = 0,
    SDFILE_END,
};





struct sdfile_folder {
    u32 saddr;
    u32 addr;
    u32 len;
};
struct sdfile_scn {
    u8 subpath;
    u8 cycle_mode;
    u8 attr;
    u8 deepth;
    u16 dirCounter;
    u16 fileCounter;
    u16 fileNumber;
    u16 totalFileNumber;
    u16 last_file_number;
    u16 fileTotalInDir;
    u16 fileTotalOutDir;
    u32 sclust_id;
    const char *ftypes;
    struct sdfile_file_head head;
    struct sdfile_folder folder[2];
};


typedef struct sdfile_file_t {
    u32 fptr;
    struct sdfile_file_head head;

    struct sdfile_scn *pscn;

} SDFILE;
# 135 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\fs/sdfile.h"
int sdfile_delete_data(SDFILE *fp);
# 160 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\fs/sdfile.h"
u32 sdfile_get_disk_capacity(void);

u32 sdfile_flash_addr2cpu_addr(u32 offset);

u32 sdfile_cpu_addr2flash_addr(u32 offset);

u32 decode_data_by_user_key_in_sdfile(u16 key, u8 *buff, u16 size, u32 dec_addr, u8 dec_len);

u32 init_norsdfile_hdl(void);
int set_res_startaddr(int offset);
# 21 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/fs/fs.h" 2
# 54 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/fs/fs.h"
enum {
    FS_IOCTL_GET_FILE_NUM,
    FS_IOCTL_FILE_CHECK,
    FS_IOCTL_GET_ERR_CODE,
    FS_IOCTL_FREE_CACHE,
    FS_IOCTL_SET_NAME_FILTER,
    FS_IOCTL_GET_FOLDER_INFO,
    FS_IOCTL_SET_LFN_BUF,
    FS_IOCTL_SET_LDN_BUF,

    FS_IOCTL_SET_EXT_TYPE,
    FS_IOCTL_OPEN_DIR,
    FS_IOCTL_ENTER_DIR,
    FS_IOCTL_EXIT_DIR,
    FS_IOCTL_GET_DIR_INFO,

    FS_IOCTL_GETFILE_BYNAME_INDIR,

    FS_IOCTL_GET_DISP_INFO,

    FS_IOCTL_MK_DIR,
    FS_IOCTL_GET_ENCFOLDER_INFO,

    FS_IOCTL_GET_OUTFLASH_ADDR,

    FS_IOCTL_SAVE_FAT_TABLE,
    FS_IOCTL_GET_FILE_DEEPTH,
};


struct vfs_devinfo;
struct vfscan;
struct vfs_operations;



struct vfs_devinfo {
    void *fd;
    u32 sector_size;
    void *private_data;
};




struct vfs_partition {
    struct vfs_partition *next;
    u32 offset;
    u32 clust_size;
    u32 total_size;
    u8 fs_attr;
    char dir[16];
    void *private_data;
};

struct fiter {
    u32 index;
};

struct ffolder {
    u16 fileStart;
    u16 fileTotal;
};



struct imount {
    int fd;
    const char *path;
    struct vfs_operations *ops;
    struct vfs_devinfo dev;
    struct vfs_partition part;
    struct list_head entry;
    atomic_t ref;
    OS_MUTEX mutex;
    u8 avaliable;
    u8 part_num;
};

struct vfs_attr {
    u8 attr;
    u32 fsize;
    u32 sclust;
    struct sys_time crt_time;
    struct sys_time wrt_time;
};

typedef struct {
    struct imount *mt;
    struct vfs_devinfo *dev;
    struct vfs_partition *part;
    void *private_data;
} FILE;


struct vfscan {
    u8 scan_file;
    u8 subpath;
    u8 scan_dir;
    u8 attr;
    u8 cycle_mode;
    char sort;
    char ftype[20 * 3 + 1];
    u16 file_number;
    u16 file_counter;

    u16 dir_totalnumber;
    u16 musicdir_counter;
    u16 fileTotalInDir;

    void *priv;
    struct vfs_devinfo *dev;
    struct vfs_partition *part;
    char filt_dir[12];
    char fasten_num[8];
    char *fasten_buf;
    char *d_save;
};


struct vfs_operations {
    const char *fs_type;
    int (*mount)(struct imount *, int);
    int (*unmount)(struct imount *);
    int (*format)(struct vfs_devinfo *, struct vfs_partition *);
    int (*fset_vol)(struct vfs_partition *, const char *name);
    int (*fget_free_space)(struct vfs_devinfo *, struct vfs_partition *, u32 *space);
    int (*fopen)(FILE *, const char *path, const char *mode);
    int (*fread)(FILE *, void *buf, u32 len);
    int (*fread_fast)(FILE *, void *buf, u32 len);
    int (*fwrite)(FILE *, void *buf, u32 len);
    int (*fseek)(FILE *, int offset, int);
    int (*fseek_fast)(FILE *, int offset, int);
    int (*flen)(FILE *);
    int (*fpos)(FILE *);
    int (*fcopy)(FILE *, FILE *);
    int (*fget_name)(FILE *, u8 *name, int len);
    int (*fget_path)(FILE *, struct vfscan *, u8 *name, int len, u8 is_relative_path);
    int (*frename)(FILE *, const char *path);
    int (*fclose)(FILE *);
    int (*fdelete)(FILE *);
    int (*fscan)(struct vfscan *, const char *path, u8 max_deepth);
    int (*fscan_interrupt)(struct vfscan *, const char *path, u8 max_deepth, int (*callback)(void));
    void (*fscan_release)(struct vfscan *);
    int (*fsel)(struct vfscan *, int sel_mode, FILE *, int);
    int (*fget_attr)(FILE *, int *attr);
    int (*fset_attr)(FILE *, int attr);
    int (*fget_attrs)(FILE *, struct vfs_attr *);
    int (*fmove)(FILE *file, const char *path_dst, FILE *, int clr_attr);
    int (*ioctl)(void *, int cmd, int arg);
};





static inline struct vfs_partition *vfs_partition_next(struct vfs_partition *p)
{
    struct vfs_partition *n = (struct vfs_partition *)zalloc(sizeof(*n));

    if (n) {
        p->next = n;
    }
    return n;
}


static inline void vfs_partition_free(struct vfs_partition *p)
{
    struct vfs_partition *n = p->next;

    while (n) {
        p = n->next;
        free(n);
        n = p;
    }
}




struct imount *mount(const char *dev_name, const char *path, const char *fs_type,
                     int cache_num, void *dev_arg);

int unmount(const char *path);

int f_format(const char *path, const char *fs_type, u32 clust_size);

int f_free_cache(const char *path);
# 255 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/fs/fs.h"
FILE *fopen(const char *path, const char *mode);

int fread(FILE *file, void *buf, u32 len);

int fwrite(FILE *file, void *buf, u32 len);

int fseek(FILE *file, int offset, int orig);

int fseek_fast(FILE *file, int offset, int orig);

int fread_fast(FILE *file, void *buf, u32 len);

int flen(FILE *file);

int fpos(FILE *file);

int fcopy(const char *format, ...);

int fget_name(FILE *file, u8 *name, int len);

int frename(FILE *file, const char *path);

int fclose(FILE *file);

int fdelete(FILE *file);
int fdelete_by_name(const char *fname);

int fget_free_space(const char *path, u32 *space);
# 297 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/fs/fs.h"
int fget_path(FILE *file, struct vfscan *fscan, u8 *name, int len, u8 is_relative_path);
# 306 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/fs/fs.h"
struct vfscan *fscan(const char *path, const char *arg, u8 max_deepth);

struct vfscan *fscan_interrupt(const char *path, const char *arg, u8 max_deepth, int (*callback)(void));

struct vfscan *fscan_enterdir(struct vfscan *fs, const char *path);

struct vfscan *fscan_exitdir(struct vfscan *fs);

void fscan_release(struct vfscan *fs);

FILE *fselect(struct vfscan *fs, int selt_mode, int arg);

int fdir_exist(const char *dir);

int fdir(FILE *file, const char *arg, char *name, int len, struct fiter *iter);

int fget_attr(FILE *file, int *attr);

int fset_attr(FILE *file, int attr);

int fget_attrs(FILE *file, struct vfs_attr *attr);

struct vfs_partition *fget_partition(const char *path);

int fset_vol(const char *path, const char *name);

int fmove(FILE *file, const char *path_dst, FILE **newFile, int clr_attr);

int fcheck(FILE *file);

int fget_err_code(const char *path);

int fset_name_filter(const char *path, void *name_filter);

int fget_folder(struct vfscan *fs, struct ffolder *arg);

int fset_lfn_buf(struct vfscan *fs, void *arg);
int fset_ldn_buf(struct vfscan *fs, void *arg);

int fset_ext_type(const char *path, void *ext_type);
int fopen_dir_info(const char *path, FILE **pp_file, void *dir_dj);
int fenter_dir_info(FILE *file, void *dir_dj);
int fexit_dir_info(FILE *file);
int fget_dir_info(FILE *file, u32 start_num, u32 total_num, void *buf_info);

int fget_fat_outflash_addr(FILE *file, void *buf_info);

int fget_file_byname_indir(FILE *file, FILE **newFile, void *ext_name);

int fget_disp_info(FILE *file, void *arg);

int fmk_dir(const char *path, char *folder, u8 mode);

int fget_encfolder_info(const char *path, char *folder, char *ext, u32 *last_num, u32 *total_num);

int fname_to_path(char *result, const char *path, const char *fname, int len);

int get_last_num(void);

void set_bp_info(u32 clust, u32 fsize, u32 *flag);
void put_bp_info(void);
# 380 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/fs/fs.h"
int fsave_fat_table(FILE *file, u16 btr, u8 *buf);
# 392 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/fs/fs.h"
void ff_set_DirBaseInfo(void *buf, u16 n);


int fget_deepth(FILE *file);
# 16 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/power_manage.h" 1
# 10 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/power_manage.h"
enum {
    DEVICE_EVENT_POWER_SHUTDOWN = 0x10,
    DEVICE_EVENT_POWER_STARTUP,
    DEVICE_EVENT_POWER_PERCENT,
    DEVICE_EVENT_POWER_CHARGER_IN,
    DEVICE_EVENT_POWER_CHARGER_OUT
};
# 28 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/power_manage.h"
struct sys_power_hal_ops {
    void (*init)(void);
    void (*poweroff)(void *arg);
    int (*wakeup_check)(char *reason, int max_len);
    int (*port_wakeup_config)(const char *port, int enable);
    int (*alarm_wakeup_config)(u32 sec, int enable);
    int (*get_battery_voltage)(void);
    int (*get_battery_percent)(void);
    int (*charger_online)(void);
};

extern const struct sys_power_hal_ops sys_power_hal_ops_begin[];
extern const struct sys_power_hal_ops sys_power_hal_ops_end[];





void sys_power_early_init();



void sys_power_poweroff(void *arg);



void sys_power_shutdown();

int sys_power_set_port_wakeup(const char *port, int enable);

int sys_power_set_alarm_wakeup(u32 sec, int enable);

const char *sys_power_get_wakeup_reason();

void sys_power_clr_wakeup_reason(const char *str);

int sys_power_get_battery_voltage();

int sys_power_get_battery_persent();

int sys_power_is_charging();

int sys_power_charger_online(void);





void sys_power_auto_shutdown_start(u32 dly_secs);
void sys_power_auto_shutdown_pause();
void sys_power_auto_shutdown_resume();
void sys_power_auto_shutdown_clear();
void sys_power_auto_shutdown_stop();


int sys_power_low_voltage(u32 voltage);







void sys_power_low_voltage_shutdown(u32 voltage, u32 dly_secs);





void sys_power_charger_off_shutdown(u32 dly_secs);
# 17 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/syscfg_id.h" 1






struct btif_item {
    u16 id;
    u16 data_len;
};


struct syscfg_operataions {
    int (*init)(void);
    int (*check_id)(u16 item_id);
    int (*read)(u16 item_id, u8 *buf, u16 len);
    int (*write)(u16 item_id, u8 *buf, u16 len);
    int (*dma_write)(u16 item_id, u8 *buf, u16 len);
    int (*read_string)(u16 item_id, u8 *buf, u16 len, u8 ver);
    u8 *(*ptr_read)(u16 item_id, u16 *len);
};
# 40 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/syscfg_id.h"
int syscfg_read(u16 item_id, void *buf, u16 len);

int syscfg_read_btmac_blemac_from_bin(u16 item_id, void *buf, u16 len);

int syscfg_write(u16 item_id, void *buf, u16 len);


int syscfg_dma_write(u16 item_id, void *buf, u16 len);



int syscfg_read_string(u16 item_id, void *buf, u16 len, u8 ver);



u8 *syscfg_ptr_read(u16 item_id, u16 *len);
# 18 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/bank_switch.h" 1
# 171 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/bank_switch.h"
void load_overlay_code(int num);
void bank_syscall_entry(void);
void load_common_code(void);
# 19 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/includes.h" 2



# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/generic/includes.h" 1






# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/ascii.h" 1
# 12 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/ascii.h"
void ASCII_ToLower(void *buf, u32 len);

void ASCII_ToUpper(void *buf, u32 len);

u32 ASCII_StrCmp(const char *src, const char *dst, u32 len);

int ASCII_StrCmpNoCase(const char *src, const char *dst, int len);

void ASCII_IntToStr(void *pStr, u32 intNum, u32 strLen, u32 bufLen);

u32 ASCII_StrToInt(const void *pStr, u32 *pRint, u32 strLen);

u32 ASCII_StrLen(void *str, u32 len);

u32 ASCII_WStrLen(void *str, u32 len);
# 8 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/generic/includes.h" 2



# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/gpio.h" 1








void gpio_port_lock(unsigned int port);

void gpio_port_unlock(unsigned int port);

int __gpio_direction_input(unsigned int gpio);
int gpio_direction_input(unsigned int gpio);

int __gpio_direction_output(unsigned int gpio, int value);
int gpio_direction_output(unsigned int gpio, int value);

int __gpio_set_pull_up(unsigned int gpio, int value);
int gpio_set_pull_up(unsigned int gpio, int value);

int __gpio_set_pull_down(unsigned int gpio, int value);
int gpio_set_pull_down(unsigned int gpio, int value);

int __gpio_set_hd(unsigned int gpio, int value);
int gpio_set_hd(unsigned int gpio, int value);

int __gpio_set_die(unsigned int gpio, int value);
int gpio_set_die(unsigned int gpio, int value);

int __gpio_set_output_clk(unsigned int gpio, int clk);
int gpio_set_output_clk(unsigned int gpio, int clk);

int __gpio_read(unsigned int gpio);
int gpio_read(unsigned int gpio);
# 12 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/generic/includes.h" 2





# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/version.h" 1






typedef int (*version_t)(int);
# 119 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/version.h"
extern version_t lib_version_begin[], lib_version_end[];
# 18 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/generic/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/lbuf.h" 1
# 10 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/lbuf.h"
struct lbuff_head {
    int magic_a;
    struct list_head head;
    struct list_head free;
    spinlock_t lock;
    u8 align;
    u16 priv_len;
    u32 total_size;
    u32 last_addr;
    void *priv;
    int magic_b;
};

struct lbuff_state {
    u32 avaliable;
    u32 fragment;
    u32 max_continue_len;
    int num;
};



struct lbuff_head *lbuf_init(void *buf, u32 len, int align, int priv_head_len);

void *lbuf_alloc(struct lbuff_head *head, u32 len);

void *lbuf_realloc(void *lbuf, int size);

int lbuf_empty(struct lbuff_head *head);

void lbuf_clear(struct lbuff_head *head);

void lbuf_push(void *lbuf, u8 channel_map);

void *lbuf_pop(struct lbuff_head *head, u8 channel);

int lbuf_free(void *lbuf);

void lbuf_free_check(void *lbuf, u32 rets);

u32 lbuf_free_space(struct lbuff_head *head);

void lbuf_state(struct lbuff_head *head, struct lbuff_state *state);

void lbuf_dump(struct lbuff_head *head);

int lbuf_traversal(struct lbuff_head *head);

int lbuf_avaliable(struct lbuff_head *head, int size);

int lbuf_real_size(void *lbuf);

int lbuf_remain_space(struct lbuff_head *head);

void lbuf_inc_ref(void *lbuf);
# 19 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/generic/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/lbuf_lite.h" 1
# 10 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/lbuf_lite.h"
struct lbuff_lite_head {
    int magic_a;
    struct list_head head;
    struct list_head free;
    spinlock_t lock;
    u8 align;
    u16 priv_len;
    u32 total_size;
    u32 last_addr;
    void *priv;
    int magic_b;
};

struct lbuff_lite_state {
    u32 avaliable;
    u32 fragment;
    u32 max_continue_len;
    int num;
};



struct lbuff_lite_head *lbuf_lite_init(void *buf, u32 len, int align, int priv_head_len);

void *lbuf_lite_alloc(struct lbuff_lite_head *head, u32 len);

void *lbuf_lite_realloc(void *lbuf, int size);

void lbuf_lite_free(void *lbuf);

u32 lbuf_lite_free_space(struct lbuff_lite_head *head);

void lbuf_lite_state(struct lbuff_lite_head *head, struct lbuff_lite_state *state);

void lbuf_lite_dump(struct lbuff_lite_head *head);

int lbuf_lite_avaliable(struct lbuff_lite_head *head, int size);
# 20 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/generic/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/circular_buf.h" 1
# 11 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/circular_buf.h"
typedef struct _cbuffer {
    u8 *begin;
    u8 *end;
    u8 *read_ptr;
    u8 *write_ptr;
    u8 *tmp_ptr ;
    u32 tmp_len;
    u32 data_len;
    u32 total_len;
    spinlock_t lock;
} cbuffer_t;


extern void cbuf_init(cbuffer_t *cbuffer, void *buf, u32 size);

extern u32 cbuf_read(cbuffer_t *cbuffer, void *buf, u32 len);

extern u32 cbuf_write(cbuffer_t *cbuffer, void *buf, u32 len);

extern u32 cbuf_is_write_able(cbuffer_t *cbuffer, u32 len);

extern void *cbuf_write_alloc(cbuffer_t *cbuffer, u32 *len);

extern void cbuf_write_updata(cbuffer_t *cbuffer, u32 len);

extern void *cbuf_read_alloc(cbuffer_t *cbuffer, u32 *len);

extern void cbuf_read_updata(cbuffer_t *cbuffer, u32 len);

extern void cbuf_clear(cbuffer_t *cbuffer);

extern u32 cbuf_rewrite(cbuffer_t *cbuffer, void *begin, void *buf, u32 len);

extern void cbuf_discard_prewrite(cbuffer_t *cbuffer);

extern void cbuf_updata_prewrite(cbuffer_t *cbuffer);

extern u32 cbuf_prewrite(cbuffer_t *cbuffer, void *buf, u32 len);

extern void *cbuf_get_writeptr(cbuffer_t *cbuffer);

extern u32 cbuf_get_data_size(cbuffer_t *cbuffer);

extern void *cbuf_get_readptr(cbuffer_t *cbuffer);

extern u32 cbuf_read_goback(cbuffer_t *cbuffer, u32 len);

extern u32 cbuf_get_data_len(cbuffer_t *cbuffer);

extern u32 cbuf_read_alloc_len(cbuffer_t *cbuffer, void *buf, u32 len);

extern void cbuf_read_alloc_len_updata(cbuffer_t *cbuffer, u32 len);
# 21 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/generic/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/index.h" 1
# 11 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/index.h"
int index_of_table8(u8 value, const u8 *table, int table_size);

int index_of_table16(u16 value, const u16 *table, int table_size);

int index_of_table32(u32 value, const u32 *table, int table_size);
# 22 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/generic/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\generic/debug_lite.h" 1




extern void puts_lite(const char *out);
extern void put_buf_lite(void *_buf, u32 len);
extern int printf_lite(const char *format, ...);
# 23 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/generic/includes.h" 2
# 23 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/device/includes.h" 1
# 10 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/device/includes.h"
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\device/key_driver.h" 1







typedef enum __KEY_DRIVER_TYPE {
    KEY_DRIVER_TYPE_IO = 0x0,
    KEY_DRIVER_TYPE_AD,
    KEY_DRIVER_TYPE_RTCVDD_AD,
    KEY_DRIVER_TYPE_IR,
    KEY_DRIVER_TYPE_TOUCH,
    KEY_DRIVER_TYPE_CTMU_TOUCH,
    KEY_DRIVER_TYPE_RDEC,
    KEY_DRIVER_TYPE_SLIDEKEY,
    KEY_DRIVER_TYPE_SOFTKEY,

    KEY_DRIVER_TYPE_MAX,
} KEY_DRIVER_TYPE;
# 30 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\device/key_driver.h"
struct key_driver_para {
    const u32 scan_time;
    u8 last_key;

    u8 filter_value;
    u8 filter_cnt;
    const u8 filter_time;

    const u8 long_time;
    const u8 hold_time;
    u8 press_cnt;

    u8 click_cnt;
    u8 click_delay_cnt;
    const u8 click_delay_time;
    u8 notify_value;
    u8 key_type;
    u8(*get_value)(void);
};


struct key_remap {
    u8 bit_value;
    u8 remap_value;
};

struct key_remap_data {
    u8 remap_num;
    const struct key_remap *table;
};


extern int key_driver_init(void);
# 11 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/device/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\device/iokey.h" 1
# 21 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\device/iokey.h"
struct one_io_key {
    u8 port;
};

struct two_io_key {
    u8 in_port;
    u8 out_port;
};

union key_type {
    struct one_io_key one_io;
    struct two_io_key two_io;
};

struct iokey_port {
    union key_type key_type;
    u8 connect_way;
    u8 key_value;
};

struct iokey_platform_data {
    u8 enable;
    u8 num;
    const struct iokey_port *port;
};


extern int iokey_init(const struct iokey_platform_data *iokey_data);
extern u8 io_get_key_value(void);
# 12 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/device/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\device/irkey.h" 1





struct irkey_platform_data {
    u8 enable;
    u8 port;
};

extern u8 ir_get_key_value(void);
extern int irkey_init(const struct irkey_platform_data *irkey_data);
# 13 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/device/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\device/adkey.h" 1




# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/adc_api.h" 1
# 64 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/adc_api.h"
extern void adc_init();
extern void adc_vbg_init();


extern void adc_pmu_ch_select(u32 ch);
extern void adc_pmu_detect_en(u32 ch);
extern void adc_vdc13_save();
extern void adc_vdc13_restore();


u32 adc_get_value(u32 ch);

u32 adc_add_sample_ch(u32 ch);

u32 adc_remove_sample_ch(u32 ch);

u32 adc_get_voltage(u32 ch);
u32 adc_check_vbat_lowpower();

void check_pmu_voltage(u8 tieup);

extern void adc_enter_occupy_mode(u32 ch);
extern void adc_exit_occupy_mode();
extern u32 adc_occupy_run();
extern u32 adc_get_occupy_value();
u32 adc_sample(u32 ch);
u32 adc_value_to_voltage(u32 adc_vbg, u32 adc_ch_val);

char get_vddiom_trim();
char get_vddiow_trim();
void check_pmu_voltage(u8 tieup);
# 6 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\device/adkey.h" 2




struct adkey_platform_data {
    u8 enable;
    u8 adkey_pin;
    u8 extern_up_en;
    u32 ad_channel;
    u16 ad_value[10];
    u8 key_value[10];
};

struct adkey_rtcvdd_platform_data {
    u8 enable;
    u8 adkey_pin;
    u8 adkey_num;
    u32 ad_channel;
    u32 extern_up_res_value;
    u16 res_value[10];
    u8 key_value[10];
};


extern int adkey_init(const struct adkey_platform_data *adkey_data);
extern u8 ad_get_key_value(void);


extern int adkey_rtcvdd_init(const struct adkey_rtcvdd_platform_data *rtcvdd_adkey_data);
extern u8 adkey_rtcvdd_get_key_value(void);
# 14 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/device/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\device/slidekey.h" 1








struct slidekey_port {
    u8 io;
    u8 io_up_en;
    u32 level;
    u32 ad_channel;
    int msg;
};

struct slidekey_platform_data {
    u8 enable;
    u8 num;
    const struct slidekey_port *port;
};




extern int slidekey_init(const struct slidekey_platform_data *slidekey_data);
# 15 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/device/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\device/touch_key.h" 1




# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/plcnt.h" 1





typedef struct _CTM_KEY_VAR {
    s32 touch_release_buf[3];
    u16 touch_cnt_buf[3];
    s16 FLT1CFG1;
    s16 FLT1CFG2;
    s16 PRESSCFG;
    s16 RELEASECFG0;
    s16 RELEASECFG1;
    s8 FLT0CFG;
    s8 FLT1CFG0;
    u16 touch_key_state;
    u8 touch_init_cnt[3];
} sCTM_KEY_VAR;



int plcnt_init(void *_data);


u8 get_plcnt_value(void);
# 6 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\device/touch_key.h" 2


enum touch_key_clk {
    TOUCH_KEY_OSC_CLK = 0,
    TOUCH_KEY_MUX_IN_CLK,
    TOUCH_KEY_PLL_192M_CLK,
    TOUCH_KEY_PLL_240M_CLK,
};

struct touch_key_port {
    u8 port;
    u8 key_value;
};

struct touch_key_platform_data {
    u8 num;
    u8 clock;
    u8 change_gain;
    s16 press_cfg;
    s16 release_cfg0;
    s16 release_cfg1;
    const struct touch_key_port *port_list;
};



int touch_key_init(const struct touch_key_platform_data *touch_key_data);


u8 touch_key_get_value(void);
# 16 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/device/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\device/rdec_key.h" 1





# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/rdec.h" 1





enum rdec_index {
    RDEC0,
    RDEC1,
    RDEC2,
};

struct rdec_device {
    enum rdec_index index;
    u8 sin_port0;
    u8 sin_port1;
    u8 key_value0;
    u8 key_value1;
};

struct rdec_platform_data {
    u8 enable;
    u8 num;
    const struct rdec_device *rdec;
};
# 33 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\cpu\\br23\\asm/rdec.h"
int rdec_init(const struct rdec_platform_data *user_data);
s8 get_rdec_rdat(int i);
# 7 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\device/rdec_key.h" 2

int rdec_key_init(const struct rdec_platform_data *rdec_key_data);
# 17 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/device/includes.h" 2
# 24 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/includes.h" 2

# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\device/sdio_host_init.h" 1
# 57 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\driver\\device/sdio_host_init.h"
extern void sdio_host_init(unsigned int parm);
extern unsigned char *SDIO_GET_CMD_BUF(void);
extern void SDIO_SET_GRP_PORT(u32 grp, u32 port);
extern void cpu_sdio_host_uninit(void);
extern void sdio_dat1_irq_uninit(void);
extern void sdio_dat1_irq_init(void);
extern void host_set_timing(void *host, unsigned int timing);
extern void mmc_set_bus_width(void *host, unsigned int width);
extern void mmc_set_clock(void *host, unsigned int hz);
extern void SDIO_CONTROLLER_RESET(void);
extern void SDIO_IDLE_CLK_EN(u8 enable) ;
extern void SDIO_CONTROLLER_START(void);
extern void SDIO_CONTROLLER_SET_IRQ(void);
extern void SDIO_SET_4WIRE_MODE(u8 enable);
# 26 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/includes.h" 2

# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/crypto.h" 1
# 34 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/crypto.h"
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/endian.h" 1
# 252 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/endian.h"
u16 _swap16(u16 value);
u32 _swap32(u32 value);
u64 _swap64(u64 value);
# 35 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/crypto.h" 2


typedef int error_t;
# 100 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/crypto.h"
typedef error_t (*HashAlgoCompute)(const void *data, int length, u8 *digest);
typedef void (*HashAlgoInit)(void *context);
typedef void (*HashAlgoUpdate)(void *context, const void *data, int length);
typedef void (*HashAlgoFinal)(void *context, u8 *digest);
# 124 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/crypto.h"
typedef struct {
    u8 digest[1];
} HashContext;






typedef struct {
    const s8 *name;
    const u8 *oid;
    int oidSize;
    int contextSize;
    int blockSize;
    int digestSize;
    HashAlgoCompute compute;
    HashAlgoInit init;
    HashAlgoUpdate update;
    HashAlgoFinal final;
} HashAlgo;
# 28 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/Crypto_hash.h" 1
# 20 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/Crypto_hash.h"
void g_hash_function(u8 *U, u8 *V, u8 *X, u8 *Y, u8 *output);
void f1_hash_function(u8 *U, u8 *V, u8 *X, u8 *Z, u8 *re);
void f2_hash_function(u8 *W, u8 *N1, u8 *N2, u8 *keyID, u8 *A1, u8 *A2, u8 *re);
void f3_hash_function(u8 *W, u8 *N1, u8 *N2, u8 *R, u8 *IOcap, u8 *A1, u8 *A2, u8 *re);
void h2_hash_function(u8 *W, u8 *KeyID, u8 *L, u8 *re);
void h3_hash_function(u8 *W, u8 *keyID, u8 *A1, u8 *A2, u8 *ACO, u8 *re);
void h4_hash_function(u8 *W, u8 *keyID, u8 *A1, u8 *A2, u8 *re);
void h5_hash_function(u8 *W, u8 *R1, u8 *R2, u8 *re);
void SSP_Heap_init(u8 *p, int len);

u32 g_function(u8 *U, u8 *V, u8 *X, u8 *Y);
void f1_function(u8 *U, u8 *V, u8 *X, u8 *Z, u8 *re);
void f2_function(u8 *W, u8 *N1, u8 *N2, u8 *A1, u8 *A2, u8 *re);
void f3_function(u8 *W, u8 *N1, u8 *N2, u8 *R, u8 *IOcap, u8 *A1, u8 *A2, u8 *re);
# 29 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/hmac.h" 1
# 34 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/hmac.h"
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/sha256.h" 1
# 47 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/sha256.h"
typedef struct {
    union {
        u32 h[8];
        u8 digest[32];
    };
    union {
        u32 w[64];
        u8 buffer[64];
    };
    int size;
    u64 totalSize;
} Sha256Context;



extern const HashAlgo sha256HashAlgo;


int sha256Compute(const void *data, int length, u8 *digest);
void sha256Init(Sha256Context *context);
void sha256Update(Sha256Context *context, const void *data, int length);
void sha256Final(Sha256Context *context, u8 *digest);
void sha256ProcessBlock(Sha256Context *context);
# 35 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/hmac.h" 2
# 46 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/hmac.h"
typedef struct {
    const HashAlgo *hash;
    u8 hashContext[sizeof(Sha256Context)];
    u8 key[64];
    u8 digest[32];
} HmacContext;
# 65 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/hmac.h"
error_t hmacCompute(const HashAlgo *hash, const void *key, int keyLength,
                    const void *data, int dataLength, u8 *digest);

void hmacInit(HmacContext *context, const HashAlgo *hash,
              const void *key, int length);

void hmacUpdate(HmacContext *context, const void *data, int length);
void hmacFinal(HmacContext *context, u8 *digest);
# 30 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/includes.h" 2

# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/bigint.h" 1





# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/bigint_impl.h" 1
# 57 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/bigint_impl.h"
typedef u32 comp;
typedef unsigned long long long_comp;
typedef long long slong_comp;






struct _bigint {
    struct _bigint *next;
    short size;
    short max_comps;
    int refs;
    comp *comps;
};

typedef struct _bigint bigint;





typedef struct {
    bigint *active_list;
    bigint *free_list;
    bigint *bi_radix;
    bigint *bi_mod[2];






    bigint *bi_mu[2];

    bigint *bi_normalised_mod[2];
    bigint **g;
    int window;
    int active_count;
    int free_count;




    u8 mod_offset;
    int np_bit;
    char *mem_pool;
    int tol_used;
} BI_CTX;
# 7 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/bigint.h" 2

bigint *alloc(BI_CTX *ctx, int size);
bigint *trim(bigint *bi);
void bi_initialize(BI_CTX *ctx, char *mem_pool);
void bi_terminate(BI_CTX *ctx);
void bi_permanent(bigint *bi);
void bi_depermanent(bigint *bi);
void bi_clear_cache(BI_CTX *ctx);
void bi_free(BI_CTX *ctx, bigint *bi);
bigint *bi_copy(bigint *bi);
bigint *bi_clone(BI_CTX *ctx, const bigint *bi);
void bi_export(BI_CTX *ctx, bigint *bi, u8 *data, int size);
bigint *bi_import(BI_CTX *ctx, const u8 *data, int len);
bigint *int_to_bi(BI_CTX *ctx, comp i);


bigint *bi_add(BI_CTX *ctx, bigint *bia, bigint *bib);
bigint *bi_subtract(BI_CTX *ctx, bigint *bia,
                    bigint *bib, int *is_negative);
bigint *bi_divide(BI_CTX *ctx, bigint *bia, bigint *bim, int is_mod);
bigint *bi_multiply(BI_CTX *ctx, bigint *bia, bigint *bib);
bigint *bi_mod_power(BI_CTX *ctx, bigint *bi, bigint *biexp);
bigint *bi_mod_power2(BI_CTX *ctx, bigint *bi, bigint *bim, bigint *biexp);
int bi_compare(bigint *bia, bigint *bib);
void bi_set_mod(BI_CTX *ctx, bigint *bim, int mod_offset);
void bi_free_mod(BI_CTX *ctx, int mod_offset);
bigint *comp_left_shift(bigint *biR, int num_shifts);
int exp_bit_is_one(bigint *biexp, int offset);
int find_max_exp_index(bigint *biexp);






void bi_wirte_to_byte(bigint *bi, unsigned char *out);
bigint *bi_read_from_byte(BI_CTX *ctx, const unsigned char *buf, int len);
bigint *bi_mod_lshift(BI_CTX *ctx, bigint *x, int shift);
void bi_lshift(BI_CTX *ctx, bigint *x, int shift);
bigint *bi_mod_add(BI_CTX *ctx, bigint *a, bigint *b);
bigint *bi_mod_sub(BI_CTX *ctx, bigint *a, bigint *b);
bigint *bi_mod_sqr(BI_CTX *ctx, bigint *x);
bigint *bi_mod_mul(BI_CTX *ctx, bigint *a, bigint *b);
bigint *bi_mod_inverse(BI_CTX *ctx, bigint *x);



bigint *bi_rshift(bigint *x, int shift);
int bi_is_oneORzero(bigint *x);
# 73 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/bigint.h"
bigint *bi_barrett(BI_CTX *ctx, bigint *bi);





bigint *bi_square(BI_CTX *ctx, bigint *bi);
# 32 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/includes.h" 2


# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/ecdh.h" 1







typedef struct {
    bigint *x;
    bigint *y;
    bigint *z;
    int Z_is_one;
    int Z_is_zero;
} EC_POINT;

struct ECDH_CTX_st {
    BI_CTX ctx;
    EC_POINT G;
    EC_POINT PubKey;
    bigint *ECDHKey;
    bigint *PriKey;
};

typedef struct ECDH_CTX_st ECDH_CTX;


void ecdh_Generate_PublicKey(ECDH_CTX *ecdh_ctx, const unsigned char *PriKey, unsigned char *PubKeyx, unsigned char *PubKeyy);


void ecdh_Compute_DHKey(ECDH_CTX *ecdh_ctx, unsigned char *PublicKeyBx, unsigned char *PublicKeyBy, unsigned char *DHKey);


void ecdh_PublicKey(ECDH_CTX *ecdh_ctx, const unsigned char *PriKey, unsigned char *PubKeyx, unsigned char *PubKeyy);
void ecdh_DHKey(ECDH_CTX *ecdh_ctx, unsigned char *PublicKeyBx, unsigned char *PublicKeyBy, unsigned char *DHKey);



void ecdh_init(ECDH_CTX *ec_ctx, char *bigint_mem_pool);
void ecdh_free(ECDH_CTX *ecdh);
# 35 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/includes.h" 2




# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/micro-ecc/uECC.h" 1
# 103 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/micro-ecc/uECC.h"
typedef int (*uECC_RNG_Function)(uint8_t *dest, unsigned size);
# 115 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/micro-ecc/uECC.h"
void uECC_set_rng(uECC_RNG_Function rng_function);
# 126 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/micro-ecc/uECC.h"
int uECC_make_key(uint8_t public_key[24 * 2], uint8_t private_key[24]);
# 142 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/micro-ecc/uECC.h"
int uECC_shared_secret(const uint8_t public_key[24 * 2],
                       const uint8_t private_key[24],
                       uint8_t secret[24]);
# 161 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/micro-ecc/uECC.h"
int uECC_sign(const uint8_t private_key[24],
              const uint8_t message_hash[24],
              uint8_t signature[24 * 2]);
# 203 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/micro-ecc/uECC.h"
typedef struct uECC_HashContext {
    void (*init_hash)(struct uECC_HashContext *context);
    void (*update_hash)(struct uECC_HashContext *context,
                        const uint8_t *message,
                        unsigned message_size);
    void (*finish_hash)(struct uECC_HashContext *context, uint8_t *hash_result);
    unsigned block_size;
    unsigned result_size;
    uint8_t *tmp;
} uECC_HashContext;
# 233 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/micro-ecc/uECC.h"
int uECC_sign_deterministic(const uint8_t private_key[24],
                            const uint8_t message_hash[24],
                            uECC_HashContext *hash_context,
                            uint8_t signature[24 * 2]);
# 251 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/micro-ecc/uECC.h"
int uECC_verify(const uint8_t public_key[24 * 2],
                const uint8_t hash[24],
                const uint8_t signature[24 * 2]);
# 264 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/micro-ecc/uECC.h"
void uECC_compress(const uint8_t public_key[24 * 2], uint8_t compressed[24 + 1]);
# 275 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/micro-ecc/uECC.h"
void uECC_decompress(const uint8_t compressed[24 + 1], uint8_t public_key[24 * 2]);
# 289 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/micro-ecc/uECC.h"
int uECC_valid_public_key(const uint8_t public_key[24 * 2]);
# 302 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/micro-ecc/uECC.h"
int uECC_compute_public_key(const uint8_t private_key[24],
                            uint8_t public_key[24 * 2]);





int uECC_bytes(void);




int uECC_curve(void);
# 40 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/includes.h" 2

# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/aes_cmac.h" 1




typedef uint8_t sm_key_t[16];
void aes128_calc_cyphertext(const uint8_t key[16], const uint8_t plaintext[16], uint8_t cyphertext[16]);
void aes_cmac_calc_subkeys(sm_key_t k0, sm_key_t k1, sm_key_t k2);
void aes_cmac(sm_key_t aes_cmac, const sm_key_t key, const uint8_t *data, int sm_cmac_message_len);
# 42 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/includes.h" 2
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/rijndael.h" 1
# 11 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/crypto_toolbox/rijndael.h"
int rijndaelSetupEncrypt(uint32_t *rk, const uint8_t *key, int keybits);
int rijndaelSetupDecrypt(uint32_t *rk, const uint8_t *key, int keybits);
void rijndaelEncrypt(const uint32_t *rk, int nrounds, const uint8_t plaintext[16], uint8_t ciphertext[16]);
void rijndaelDecrypt(const uint32_t *rk, int nrounds, const uint8_t ciphertext[16], uint8_t plaintext[16]);
# 43 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system/includes.h" 2
# 12 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\cpu\\br23\\setup.c" 2

# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\target\\br23\\image\\app_config.h" 1
# 31 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\target\\br23\\image\\app_config.h"
void save_spi_port(void);
# 14 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\cpu\\br23\\setup.c" 2
# 24 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\cpu\\br23\\setup.c"
# 1 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\debug.h" 1








void printf_buf(u8 *buf, u32 len);
# 32 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\debug.h"
extern const char log_tag_const_v_SETUP;
extern const char log_tag_const_i_SETUP;
extern const char log_tag_const_d_SETUP;
extern const char log_tag_const_w_SETUP;
extern const char log_tag_const_e_SETUP;
extern const char log_tag_const_c_SETUP;
# 138 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\include_lib\\system\\debug.h"
void watchdog_close(void);
# 25 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\cpu\\br23\\setup.c" 2



extern void sys_timer_init(void);

extern void tick_timer_init(void);

extern void vPortSysSleepInit(void);

extern void reset_source_dump(void);

extern u8 power_reset_source_dump(void);

extern void exception_irq_handler(void);
int __crc16_mutex_init();

extern int __crc16_mutex_init();





void debug_uart_init(const struct uart_platform_data *data);
# 129 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\cpu\\br23\\setup.c"
void cpu_assert_debug()
{

    log_flush();
    local_irq_disable();
    while (1);



}

void timer(void *p)
{

    sys_timer_dump_time();




}

u8 power_reset_src = 0;
extern void sputchar(char c);
extern void sput_buf(const u8 *buf, int len);
void sput_u32hex(u32 dat);
void *vmem_get_phy_adr(void *vaddr);

void test_fun()
{
    wdt_close();
    while (1);

}

__attribute__((section(".volatile_ram_code")))
void __lvd_irq_handler(void)
{
    P33_TX_NBIT(0x11, (1UL << (6)), 1);
}



void load_common_code();
void app_load_common_code()
{



}

u32 stack_magic[4] __attribute__((section(".stack_magic"),used));
u32 stack_magic0[4] __attribute__((section(".stack_magic0"),used));

extern void port_init(void);
extern void lvd_enable(void);

void memory_init(void);
void ld2450_sdk_setup_arch()
{
    memory_init();

    memset(stack_magic, 0x5a, sizeof(stack_magic));
    memset(stack_magic0, 0x5a, sizeof(stack_magic0));

    wdt_init(0x0C);


    port_init();




    clk_init_osc_ldos(3);


    clk_init_osc_cap(0x0a, 0x0a);
    clk_voltage_init(CLOCK_MODE_ADAPTIVE, SYSVDD_VOL_SEL_126V, PWR_LDO15, VDC13_VOL_SEL_140V);


    clk_early_init(7, 24000000, 240000000);

    tick_timer_init();




    debug_uart_init(((void*)0));


    log_early_init(1024);
# 229 "C:\\Users\\mmsyl\\Documents\\HLK-LD2450\\HLK-LD2450_FW\\firmware\\.cache\\sdk\\cpu\\br23\\setup.c"
    printf("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n");
    printf("         setup_arch %s %s \n", "Oct  5 2026", "10:11:30");
    printf("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n");


    clock_dump();




    reset_source_dump();

    power_reset_src = power_reset_source_dump();


    request_irq(0, 2, exception_irq_handler, 0);

    request_irq(1, 2, exception_irq_handler, 0);

    debug_init();




    sys_timer_init();


    save_spi_port();


    __crc16_mutex_init();
}
