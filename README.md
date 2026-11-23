视频转OLED取模工具 使用说明
概述
这是一套完整的视频到OLED显示的解决方案，包括：

video_converter.py: Python视频转换工具，将视频转换为OLED可用的C格式
OLED_PlayVideo(): STM32 OLED驱动库中新增的视频播放函数
video.c: 转换工具生成的视频数据文件
工作原理
数据格式
分辨率: 128×64像素
位深度: 1位（单色）
排列方式: 页式(page-based)
分为8页，每页8行(共64行)
每页128字节(每列1字节)
索引: index = x + page * width
位位置: bit = y % 8 (LSB在上)
点亮条件: bit = 1
转换流程
视频读取 → 2. 帧提取(按时间戳) → 3. 灰度化 → 4. 二值化 → 5. 页式编码 → 6. C数据生成
使用步骤
1. 准备环境
bash


# 安装依赖
pip install opencv-python numpy

# 检查opencv是否安装成功
python -c "import cv2; print(cv2.__version__)"
2. 转换视频
bash


# 基本用法
python video_converter.py input.mp4

# 指定输出文件和帧率
python video_converter.py input.mp4 video.c 5

# 参数说明
# 参数1: 输入视频文件路径 (必需)
# 参数2: 输出C文件路径 (可选, 默认: video.c)
# 参数3: 提取帧率 (可选, 默认: 5 fps)
3. 将生成的video.c添加到STM32工程
将 video.c 复制到STM32工程的 Core/Src 目录
在工程中编译包含该文件
4. 在STM32代码中使用
c


#include "oled.h"

int main(void) {
    // ... 初始化代码 ...
    OLED_Init();
    
    // 播放视频 - 全屏播放
    OLED_PlayVideo(&video, 0, 0, OLED_COLOR_NORMAL);
    
    // 其他用法示例：
    // OLED_PlayVideo(&video, 0, 0, OLED_COLOR_REVERSED);  // 反色播放
    // OLED_PlayVideo(&video, 32, 0, OLED_COLOR_NORMAL);   // 右上角播放
    
    return 0;
}
参数说明
OLED_PlayVideo 函数
c


void OLED_PlayVideo(const Video *v, uint8_t x, uint8_t y, OLED_ColorMode color);
参数	说明
v	Video结构体指针(由video.c提供)
x	播放起始横坐标 (0-127)
y	播放起始纵坐标 (0-63)
color	颜色模式: OLED_COLOR_NORMAL(黑底白字) 或 OLED_COLOR_REVERSED(白底黑字)
Video结构体字段
c


typedef struct Video {
    uint8_t w;              // 帧宽度 (128)
    uint8_t h;              // 帧高度 (64)
    uint8_t fps;            // 播放帧率 (5-30推荐)
    uint16_t frameCount;    // 总帧数
    const uint8_t *data_8;  // 帧数据指针
} Video;
转换参数优化
帧率选择
帧率	优点	缺点	适用场景
2-3 fps	文件小，播放流畅	可能卡顿感强	文字/简单动画
5 fps	平衡方案	文件中等大小	一般视频(推荐)
10 fps	播放流畅	文件较大	快速动作
15+ fps	高清流畅	文件很大，可能超过MCU内存	高端MCU
二值化阈值
脚本使用固定阈值128(中等亮度)进行二值化。如需调整：

编辑 video_converter.py 第156行
增大阈值: 更多黑色
减小阈值: 更多白色
python


_, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
#                               ^^^ 改这里 (0-255)
生成文件示例
转换后的 video.c 结构：

c


/**
 * @file video.c
 * @brief 视频帧数据 - 自动生成
 * @note 帧数: 50
 * @note 分辨率: 128x64
 * @note 帧率: 5 fps
 * @note 每帧大小: 1024 字节
 * @note 总数据量: 51200 字节 (50.00 KB)
 * @note 预计播放时长: 10.00 秒
 */

#include <stdint.h>
#include "font.h"

// 视频帧数据 (所有帧连续存储)
const uint8_t videoData[] = {
    // 帧 0-4
    0x00, 0x00, 0x00, ...
    ...
};

// 视频结构体
const Video video = {
    .w = 128,
    .h = 64,
    .fps = 5,
    .frameCount = 50,
    .data_8 = videoData
};
时间同步说明
OLED_PlayVideo 使用绝对时间节拍播放：

以 HAL_GetTick() 为基准时间
每帧应该显示的时间: frame_time = (frame_index + 1) * 1000 / fps
自动扣除绘制和传输耗时，确保帧率稳定
常见问题
Q: 转换后文件太大，STM32内存不足
A:

降低帧率: python video_converter.py video.mp4 video.c 3
缩短视频时长
使用STM32H7或L476等更大内存的MCU
Q: 播放时闪烁或卡顿
A:

检查I2C速度是否足够快(建议400kHz以上)
确认系统时钟配置正确
降低帧率或使用 x=0, y=0 全屏播放(速度最快)
Q: 画面显示反了
A:

检查二值化结果: 编辑脚本调整阈值
尝试使用 OLED_COLOR_REVERSED 参数
Q: "No module named 'cv2'"
A:

bash


pip install opencv-python
# 或者
pip install -i https://pypi.tsinghua.edu.cn/simple opencv-python
STM32工程集成检查清单
 video.c 已添加到 Core/Src/
 工程编译无错误
 oled.h 中有 OLED_PlayVideo 函数声明
 oled.c 中有 OLED_PlayVideo 函数实现
 font.h 中有 Video 结构体定义
 video.c 中有 const Video video 外部声明
性能指标
以 128×64 / 5fps 为例：

指标	值
每帧大小	1024 字节
10秒视频	~50 KB
30秒视频	~150 KB
1分钟视频	~300 KB
I2C传输时间(1帧@400kHz)	~25ms
帧显示间隔	200ms (5fps)
许可证
MIT License - 自由使用和修改

技术支持
如有问题，请检查：

Python脚本输出的错误信息
STM32编译日志
OLED初始化是否成功
I2C通信是否正常
