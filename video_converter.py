#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频取模工具 - 将视频转换为OLED可用的C数组格式
支持将视频以指定帧率提取并转换为128x64单色位图
"""

import cv2
import numpy as np
import os
import sys
from pathlib import Path

class VideoToOLED:
    def __init__(self, video_path, output_path="video.c", fps=5, width=128, height=64):
        """
        初始化视频转换器
        :param video_path: 输入视频路径
        :param output_path: 输出C文件路径
        :param fps: 目标帧率（每秒提取帧数）
        :param width: OLED宽度
        :param height: OLED高度
        """
        self.video_path = video_path
        self.output_path = output_path
        self.target_fps = fps
        self.oled_width = width
        self.oled_height = height
        self.frames_data = []
        
    def extract_frames(self):
        """从视频中提取帧并转换为OLED格式"""
        print(f"正在打开视频: {self.video_path}")
        cap = cv2.VideoCapture(self.video_path)
        
        if not cap.isOpened():
            print(f"错误: 无法打开视频文件 {self.video_path}")
            return False
        
        # 获取视频信息
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / video_fps if video_fps > 0 else 0
        
        print(f"视频信息:")
        print(f"  原始帧率: {video_fps:.2f} fps")
        print(f"  总帧数: {total_frames}")
        print(f"  时长: {duration:.2f} 秒")
        print(f"  目标帧率: {self.target_fps} fps")
        
        # 计算需要提取的总帧数
        target_frame_count = int(duration * self.target_fps)
        print(f"  预计提取: {target_frame_count} 帧")
        
        extracted_count = 0
        
        # 按时间戳提取帧
        for i in range(target_frame_count):
            # 计算应该提取的时间点（秒）
            timestamp = i / self.target_fps
            # 转换为帧号
            frame_number = int(timestamp * video_fps)
            
            # 定位到指定帧
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()
            
            if not ret:
                print(f"  警告: 无法读取第 {frame_number} 帧，跳过")
                continue
            
            # 转换为OLED格式
            oled_data = self.convert_frame_to_oled(frame)
            self.frames_data.append(oled_data)
            extracted_count += 1
            
            if extracted_count % 10 == 0:
                print(f"  已提取 {extracted_count}/{target_frame_count} 帧...")
        
        cap.release()
        print(f"提取完成! 共提取 {extracted_count} 帧")
        print(f"预计播放时长: {extracted_count / self.target_fps:.2f} 秒")
        return True
    
    def convert_frame_to_oled(self, frame):
        """
        将OpenCV帧转换为OLED格式
        OLED格式: 页式排列，1位深度，阳码(bit=1点亮)
        排列: index = x + page*width, bit = y%8, LSB在上
        """
        # 调整大小到OLED分辨率
        resized = cv2.resize(frame, (self.oled_width, self.oled_height), 
                            interpolation=cv2.INTER_AREA)
        
        # 转换为灰度图
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        
        # 二值化处理（阈值可调整，128为中等亮度）
        _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
        
        # 转换为OLED页式排列格式
        # OLED有8页，每页8行，共64行
        oled_data = []
        pages = self.oled_height // 8  # 8页
        
        for page in range(pages):
            for col in range(self.oled_width):
                byte_val = 0
                for bit in range(8):
                    y = page * 8 + bit
                    # 如果像素亮（>127），则设置对应位为1（LSB在上，bit 0对应y%8=0）
                    if binary[y, col] > 127:
                        byte_val |= (1 << bit)
                oled_data.append(byte_val)
        
        return oled_data
    
    def generate_c_file(self):
        """生成C源文件"""
        if not self.frames_data:
            print("错误: 没有帧数据可以生成")
            return False
        
        print(f"\n正在生成C文件: {self.output_path}")
        
        frame_size = len(self.frames_data[0])
        total_bytes = frame_size * len(self.frames_data)
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            # 文件头注释
            f.write("/**\n")
            f.write(" * @file video.c\n")
            f.write(" * @brief 视频帧数据 - 自动生成\n")
            f.write(f" * @note 帧数: {len(self.frames_data)}\n")
            f.write(f" * @note 分辨率: {self.oled_width}x{self.oled_height}\n")
            f.write(f" * @note 帧率: {self.target_fps} fps\n")
            f.write(f" * @note 每帧大小: {frame_size} 字节\n")
            f.write(f" * @note 总数据量: {total_bytes} 字节 ({total_bytes/1024:.2f} KB)\n")
            f.write(f" * @note 预计播放时长: {len(self.frames_data) / self.target_fps:.2f} 秒\n")
            f.write(" * @note 数据格式: 页式排列 (index = x + page*width, bit = y%8, LSB在上, bit=1点亮)\n")
            f.write(" */\n\n")
            
            f.write("#include <stdint.h>\n")
            f.write('#include "font.h"\n\n')
            
            # 将所有帧数据写入一个连续数组
            f.write("// 视频帧数据 (所有帧连续存储)\n")
            f.write("const uint8_t videoData[] = {\n")
            
            byte_count = 0
            for frame_idx, frame_data in enumerate(self.frames_data):
                if frame_idx % 5 == 0:  # 每5帧添加注释
                    f.write(f"    // 帧 {frame_idx}-{min(frame_idx+4, len(self.frames_data)-1)}\n")
                
                # 每行16个字节
                for j in range(0, len(frame_data), 16):
                    line_data = frame_data[j:j+16]
                    hex_str = ", ".join(f"0x{byte:02X}" for byte in line_data)
                    f.write(f"    {hex_str},\n")
                    byte_count += len(line_data)
            
            f.write("};\n\n")
            
            # 生成Video结构体实例
            f.write("// 视频结构体\n")
            f.write("const Video video = {\n")
            f.write(f"    .w = {self.oled_width},\n")
            f.write(f"    .h = {self.oled_height},\n")
            f.write(f"    .fps = {self.target_fps},\n")
            f.write(f"    .frameCount = {len(self.frames_data)},\n")
            f.write(f"    .data_8 = videoData\n")
            f.write("};\n")
        
        file_size = os.path.getsize(self.output_path)
        print(f"C文件生成成功!")
        print(f"  文件大小: {file_size / 1024:.2f} KB")
        print(f"  数据大小: {total_bytes / 1024:.2f} KB")
        print(f"  文件开销: {(file_size - total_bytes) / 1024:.2f} KB")
        return True
    
    def run(self):
        """运行转换流程"""
        print("=" * 60)
        print("视频转OLED取模工具")
        print("=" * 60)
        
        if not os.path.exists(self.video_path):
            print(f"错误: 视频文件不存在: {self.video_path}")
            return False
        
        # 提取帧
        if not self.extract_frames():
            return False
        
        # 生成C文件
        if not self.generate_c_file():
            return False
        
        print("\n" + "=" * 60)
        print("转换完成!")
        print(f"请将 {self.output_path} 添加到STM32工程的 Core/Src 目录")
        print("调用示例:")
        print("  OLED_PlayVideo(&video, 0, 0, OLED_COLOR_NORMAL);")
        print("=" * 60)
        return True


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python video_converter.py <视频文件路径> [输出文件路径] [帧率]")
        print("示例: python video_converter.py input.mp4 video.c 5")
        print("\n参数说明:")
        print("  视频文件路径: 输入视频文件(.mp4, .avi等)")
        print("  输出文件路径: 输出C文件路径 (默认: video.c)")
        print("  帧率: 提取帧率 (默认: 5 fps)")
        sys.exit(1)
    
    video_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "video.c"
    fps = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    
    converter = VideoToOLED(video_path, output_path, fps)
    success = converter.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
