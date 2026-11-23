/**
 * @file font.h
 * @brief 字库/图片数据结构定义
 * @note  适配 STM32 HAL 工程：仅依赖 C 标准库 <stdint.h>，
 *        不再引入 8051(STC) 的 config.h / main.h，避免 uint32_t 等类型重复定义。
 * @note  字模数据使用 const 存放，链接时位于 Flash(.rodata)，无需 8051 的 code 关键字。
 */
#ifndef __FONT_H
#define __FONT_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

/**
 * @brief ASCII 字体结构体
 * @note  chars 指向连续字模区，第 n 个字符(char = ' ' + n)的字模起始地址为
 *        chars + n * ((h + 7) / 8) * w，每个字节代表垂直方向 8 个像素。
 */
typedef struct ASCIIFont {
  uint8_t h;              // 字高度
  uint8_t w;              // 字宽度
  const uint8_t *chars;   // 字模数据
} ASCIIFont;

/**
 * @brief 字体结构体
 * @note  字库前4字节存储utf8编码 剩余字节存储字模数据
 * @note  字库数据可以使用波特律动LED取模助手生成(https://led.baud-dance.com)
 */
typedef struct Font {
  uint8_t h;              // 字高度
  uint8_t w;              // 字宽度
  const uint8_t *chars;   // 字库 字库前4字节存储utf8编码 剩余字节存储字模数据
  uint8_t len;            // 字库长度 超过256则请改为uint16_t
  const ASCIIFont *ascii; // 缺省ASCII字体 当字库中没有对应字符且需要显示ASCII字符时使用
} Font;

/**
 * @brief 图片结构体
 * @note  图片数据可以使用波特律动LED取模助手生成(https://led.baud-dance.com)
 */
typedef struct Image {
  uint8_t w;             // 图片宽度
  uint8_t h;             // 图片高度
  const uint8_t *data_8; // 图片数据
} Image;

/**
 * @brief 视频结构体 (由 video_converter.py 生成于 video.c)
 * @note  data_8 为连续存放的帧数据, 每帧 ((h + 7) / 8) * w 字节, 排列方式与 Image 相同
 *        (页式: index = x + page * w, bit = y % 8, LSB 在上, bit=1 点亮)
 */
typedef struct Video {
  uint8_t w;              // 帧宽度
  uint8_t h;              // 帧高度
  uint8_t fps;            // 播放帧率
  uint16_t frameCount;    // 总帧数
  const uint8_t *data_8;  // 帧数据 共 frameCount * ((h + 7) / 8) * w 字节
} Video;

extern const Video video; /* 视频数据(video.c) */
extern const ASCIIFont afont8x6;
extern const ASCIIFont afont12x6;
extern const ASCIIFont afont16x8;
extern const ASCIIFont afont24x12;
extern const Font font16x16;
extern const Image bilibiliImg;
extern const Image imgBelly; /* 64x64 示例图片(image.c) */

#ifdef __cplusplus
}
#endif

#endif /* __FONT_H */
