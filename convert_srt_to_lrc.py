#!/usr/bin/env python3
import os
import sys
import re

def srt_time_to_lrc_time(srt_time):
    """
    将 SRT 格式时间 00:01:23,456 转换为 LRC 格式 [01:23.45]
    （保留到百分之一秒）
    """
    match = re.match(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})", srt_time)
    if not match:
        return "[00:00.00]"
    hours, minutes, seconds, millis = match.groups()
    total_minutes = int(hours) * 60 + int(minutes)
    return f"[{total_minutes:02}:{seconds}.{int(millis)//10:02}]"

def convert_srt_to_lrc(srt_path, lrc_path):
    with open(srt_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    lrc_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # 跳过序号行
        if line.isdigit():
            i += 1
            continue

        # 时间行
        time_match = re.match(r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})", line)
        if time_match:
            start_time = srt_time_to_lrc_time(time_match.group(1))
            i += 1
            text_lines = []
            while i < len(lines) and lines[i].strip() != "":
                text_lines.append(lines[i].strip())
                i += 1
            if text_lines:
                lrc_lines.append(f"{start_time}{' '.join(text_lines)}")
        else:
            i += 1

    with open(lrc_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lrc_lines))

    print(f"Converted: {srt_path} -> {lrc_path}")

def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".srt"):
                srt_path = os.path.join(root, file)
                lrc_path = os.path.join(root, os.path.splitext(file)[0] + ".lrc")
                convert_srt_to_lrc(srt_path, lrc_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"用法: python {sys.argv[0]} <目录路径>")
        sys.exit(1)

    target_dir = sys.argv[1]
    if not os.path.isdir(target_dir):
        print("错误：目录不存在")
        sys.exit(1)

    process_directory(target_dir)
