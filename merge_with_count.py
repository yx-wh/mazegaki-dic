#!/usr/bin/env python3
"""
merge_with_count.py - 将文件 a 和 b 合并为 c，并在 c 开头写入总行数。
用法: python merge_with_count.py a b c
"""

import sys

def merge_simple(file_a, file_b, file_c):
    # 读取全部行
    with open(file_a, 'r', encoding='utf-8') as fa:
        lines_a = fa.readlines()
    with open(file_b, 'r', encoding='utf-8') as fb:
        lines_b = fb.readlines()
    
    total = len(lines_a) + len(lines_b) + 1
    
    with open(file_c, 'w', encoding='utf-8') as fc:
        fc.write(str(total) + '\n')   # 第一行：总行数
        fc.writelines(lines_a)        # 接着是 a 的内容
        fc.writelines(lines_b)        # 最后是 b 的内容

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("用法: python merge_with_count.py <文件a> <文件b> <文件c>", file=sys.stderr)
        sys.exit(1)
    merge_simple(sys.argv[1], sys.argv[2], sys.argv[3])
