#!/usr/bin/env python3
"""
dedup_sorted.py - 从已排序的文件中删除重复行（连续重复），只保留一个。

用法:
    python dedup_sorted.py 输入文件 [输出文件]

如果未指定输出文件，结果将打印到标准输出（stdout）。
"""

import sys

def write_unique_lines(infile, outfile):
    """
    从 infile 读取已排序的行，将连续重复的行过滤掉，仅保留第一个，
    并将结果写入 outfile。
    """
    prev_line = None
    first = True

    for line in infile:
        if first:
            # 第一行直接写入
            outfile.write(line)
            prev_line = line
            first = False
        else:
            # 仅当当前行与上一行不同时才写入
            if line != prev_line:
                outfile.write(line)
                prev_line = line

def main():
    if len(sys.argv) < 2:
        print("用法: python dedup_sorted.py 输入文件 [输出文件]", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as outfile:
                    write_unique_lines(infile, outfile)
            else:
                write_unique_lines(infile, sys.stdout)
    except FileNotFoundError:
        print(f"错误: 文件 '{input_file}' 不存在。", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"发生错误: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()