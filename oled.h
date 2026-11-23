/**
 * @file oled.h
 * @brief 波特律动OLED驱动(SSD1306) 头文件
 * @note  适配 STM32 HAL 工程：
 *        1. 使用 <stdint.h> 中的标准整数类型，不再依赖 8051(STC) 的 config.h；
 *        2. 通过 "main.h" 获得 HAL 基础类型；
 *        3. 函数原型统一加 void / 参数类型，符合 C 标准，避免旧式声明告警；
 *        4. 补充 oled.c 中已实现但原来未声明的接口(OLED_Send/OLED_SetColorMode 等)。
 */
#ifndef __OLED_H__
#define __OLED_H__

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <string.h> /* oled.c 中使用了 memcpy / memset / memcmp */

#include "main.h"
#include "font.h"

/**
 * @brief 颜色模式
 * @note  OLED_COLOR_NORMAL  : 正常模式 黑底白字
 *        OLED_COLOR_REVERSED: 反色模式 白底黑字
 */
typedef enum {
  OLED_COLOR_NORMAL = 0, // 正常模式 黑底白字
  OLED_COLOR_REVERSED    // 反色模式 白底黑字
} OLED_ColorMode;

/* ========================== 底层通信 ========================== */
void OLED_Send(uint8_t *data_8, uint8_t len);
void OLED_SendCmd(uint8_t cmd);

/* ========================== 显示控制 ========================== */
void OLED_Init(void);
void OLED_DisPlay_On(void);
void OLED_DisPlay_Off(void);
void OLED_SetColorMode(OLED_ColorMode mode);

/* ========================== 显存操作 ========================== */
void OLED_NewFrame(void);
void OLED_ShowFrame(void);
void OLED_SetPixel(uint8_t x, uint8_t y, OLED_ColorMode color);
void OLED_SetByte_Fine(uint8_t page, uint8_t column, uint8_t data_8, uint8_t start, uint8_t end, OLED_ColorMode color);
void OLED_SetByte(uint8_t page, uint8_t column, uint8_t data_8, OLED_ColorMode color);
void OLED_SetBits_Fine(uint8_t x, uint8_t y, uint8_t data_8, uint8_t len, OLED_ColorMode color);
void OLED_SetBits(uint8_t x, uint8_t y, uint8_t data_8, OLED_ColorMode color);
void OLED_SetBlock(uint8_t x, uint8_t y, const uint8_t *data_8, uint8_t w, uint8_t h, OLED_ColorMode color);

/* ========================== 图形绘制 ========================== */
void OLED_DrawLine(uint8_t x1, uint8_t y1, uint8_t x2, uint8_t y2, OLED_ColorMode color);
void OLED_DrawRectangle(uint8_t x, uint8_t y, uint8_t w, uint8_t h, OLED_ColorMode color);
void OLED_DrawFilledRectangle(uint8_t x, uint8_t y, uint8_t w, uint8_t h, OLED_ColorMode color);
void OLED_DrawTriangle(uint8_t x1, uint8_t y1, uint8_t x2, uint8_t y2, uint8_t x3, uint8_t y3, OLED_ColorMode color);
void OLED_DrawFilledTriangle(uint8_t x1, uint8_t y1, uint8_t x2, uint8_t y2, uint8_t x3, uint8_t y3, OLED_ColorMode color);
void OLED_DrawCircle(uint8_t x, uint8_t y, uint8_t r, OLED_ColorMode color);
void OLED_DrawFilledCircle(uint8_t x, uint8_t y, uint8_t r, OLED_ColorMode color);
void OLED_DrawEllipse(uint8_t x, uint8_t y, uint8_t a, uint8_t b, OLED_ColorMode color);
void OLED_DrawImage(uint8_t x, uint8_t y, const struct Image *img, OLED_ColorMode color);

/* ========================== 视频播放 ========================== */
void OLED_PlayVideo(const Video *v, uint8_t x, uint8_t y, OLED_ColorMode color);

/* ========================== 文字绘制 ========================== */
void OLED_PrintASCIIChar(uint8_t x, uint8_t y, char ch, const struct ASCIIFont *font, OLED_ColorMode color);
void OLED_PrintASCIIString(uint8_t x, uint8_t y, char *str, const struct ASCIIFont *font, OLED_ColorMode color);
void OLED_PrintString(uint8_t x, uint8_t y, char *str, const struct Font *font, OLED_ColorMode color);

/* ========================== 测试 ========================== */
void OLED_Test(void);

#ifdef __cplusplus
}
#endif

#endif /* __OLED_H__ */
