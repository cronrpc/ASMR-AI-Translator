#!/usr/bin/env python3
import os
import sys
import shutil

def move_lrc(src_root, dst_root):
    # 递归遍历源目录
    for root, _, files in os.walk(src_root):
        for file in files:
            if file.lower().endswith('.lrc'):
                src_path = os.path.join(root, file)
                # 计算相对路径
                rel_path = os.path.relpath(root, src_root)
                dst_dir = os.path.join(dst_root, rel_path)
                dst_path = os.path.join(dst_dir, file)

                # 确保目标目录存在
                os.makedirs(dst_dir, exist_ok=True)

                # 移动文件（如想复制可改为 shutil.copy2）
                shutil.move(src_path, dst_path)
                print(f"Moved: {src_path} → {dst_path}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("用法: python move_lrc.py <源目录> <目标目录>")
        sys.exit(1)

    src_root = sys.argv[1]
    dst_root = sys.argv[2]

    if not os.path.isdir(src_root):
        print(f"错误: 源目录不存在: {src_root}")
        sys.exit(1)
    if not os.path.isdir(dst_root):
        print(f"错误: 目标目录不存在: {dst_root}")
        sys.exit(1)

    move_lrc(src_root, dst_root)
