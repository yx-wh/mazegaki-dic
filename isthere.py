#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

def main():
    # 文件路径（可根据需要修改为命令行参数）
    csv_file = 'ipadic.maze.csv'
    txt_file = '3k-2.txt'

    # 读取 CSV 中所有表面形（第一列）
    surfaces = set()
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split('\t')
                if parts:
                    surface = parts[0].strip()
                    if surface:
                        surfaces.add(surface)
    except FileNotFoundError:
        print(f"错误：文件 '{csv_file}' 未找到。", file=sys.stderr)
        sys.exit(1)

    # 检查 3k-2.txt 中的每个词
    try:
        with open(txt_file, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip()
                if not word:
                    continue
                if word not in surfaces:
                    print(word)
    except FileNotFoundError:
        print(f"错误：文件 '{txt_file}' 未找到。", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()