#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
按每行中 "st:" 后面的内容排序，若相同则按前面的内容排序。
用法: python sort_lines.py input.txt output.txt
"""

import sys
import argparse


def sort_lines(input_file, output_file, encoding='utf-8'):
    """
    读取输入文件的所有行（去除行尾换行符），按自定义规则排序：
    1. 主键：每行中 "st:" 之后的部分（按Unicode码点）
    2. 次键：每行中 "st:" 之前的部分（按Unicode码点）
    然后写入输出文件（每行加上换行符）。
    """
    try:
        with open(input_file, 'r', encoding=encoding) as fin:
            # 读取所有行，去除末尾的换行符（保留其他空白）
            lines = [line.rstrip('\n') for line in fin]

        # 自定义排序键函数
        def sort_key(line):
            # 如果行中包含 "st:"，拆分成前后两部分
            if 'st:' in line:
                before, after = line.split('st:', 1)
                return (after, before)   # 先按 after，再按 before
            else:
                # 没有 "st:" 的行放在最后（可自行调整）
                return (line, '')        # 或 ('', line) 根据需求

        # 按自定义键排序
        lines.sort(key=sort_key)

        with open(output_file, 'w', encoding=encoding) as fout:
            for line in lines:
                fout.write(line + '\n')

        print(f"排序完成，结果已写入 {output_file}")

    except FileNotFoundError:
        print(f"错误: 输入文件 '{input_file}' 不存在")
        sys.exit(1)
    except PermissionError:
        print(f"错误: 没有权限读取 '{input_file}' 或写入 '{output_file}'")
        sys.exit(1)
    except Exception as e:
        print(f"发生错误: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="按每行中 'st:' 前后的内容排序（先后面，再前面）"
    )
    parser.add_argument('input', help="输入文件路径")
    parser.add_argument('output', help="输出文件路径")
    parser.add_argument(
        '--encoding', default='utf-8',
        help="文件编码（默认：utf-8）"
    )
    args = parser.parse_args()

    sort_lines(args.input, args.output, args.encoding)


if __name__ == '__main__':
    main()
