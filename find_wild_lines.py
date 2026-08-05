#!/usr/bin/env python3
# find_wild_lines.py
import sys

def is_base_line(parts):
    """判断是否为 BASE 行（末尾两列为 '--' 和 'BASE'）"""
    return len(parts) >= 5 and parts[-2] == "--" and parts[-1] == "BASE"

def main():
    # 支持从文件或标准输入读取
    if len(sys.argv) > 1:
        f = open(sys.argv[1], 'r', encoding='utf-8')
    else:
        f = sys.stdin

    current_base = None
    line_num = 0

    for line in f:
        line_num += 1
        line = line.rstrip('\n')
        if not line.strip():          # 跳过空行
            continue

        parts = line.split('\t')
        if len(parts) < 2:            # 格式错误行，忽略
            continue

        if is_base_line(parts):
            current_base = parts[1]   # 更新当前原形
        else:
            base = parts[1]           # 非BASE行的原形
            if current_base is not None and base != current_base:
                print(f"{line_num}: {line}")
            elif current_base is None:
                # 文件开头没有 BASE 时，也标记出来
                print(f"{line_num}: [NO BASE] {line}")

    if f != sys.stdin:
        f.close()

if __name__ == "__main__":
    main()