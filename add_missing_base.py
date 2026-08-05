#!/usr/bin/env python3
import sys

def is_base_line(parts):
    """判断是否为已标记的 BASE 行（最后两列为 '--' 和 'BASE'）"""
    return len(parts) >= 5 and parts[-2] == "--" and parts[-1] == "BASE"

def process_line(line):
    line = line.rstrip('\n')
    if not line.strip():          # 保留空行
        return line
    parts = line.split('\t')
    # 只对非BASE行且第1列 == 第2列的行追加BASE标记
    if not is_base_line(parts) and len(parts) >= 2 and parts[0] == parts[1]:
        line += "\t--\tBASE"
    return line

def main():
    # 用法：python3 add_missing_base.py [输入文件]
    filename = sys.argv[1] if len(sys.argv) > 1 else "ipadic.maze.csv"
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            print(process_line(line))

if __name__ == "__main__":
    main()