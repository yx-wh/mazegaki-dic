#!/usr/bin/env python3
import sys

def main():
    bases = {}  # key: base, value: (pos, yomi)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        # 分离行号和内容（格式：248242: わ野	上野	地名	わの）
        if ':' in line:
            content = line.split(':', 1)[1].strip()
        else:
            content = line
        parts = content.split('\t')
        if len(parts) < 4:
            continue
        base = parts[1]
        pos = parts[2]
        yomi = parts[3]
        # 同一个 base 只保留一次（假设 pos 和 yomi 相同）
        if base not in bases:
            bases[base] = (pos, yomi)

    # 输出 BASE 行
    for base, (pos, yomi) in bases.items():
        print(f"{base}\t{base}\t{pos}\t{yomi}\t--\tBASE")

if __name__ == "__main__":
    main()