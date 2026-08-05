#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

def extract_kanji(line: str) -> str | None:
    """
    从形如「假名【汉字】」的行中提取【】内的汉字/词汇部分。
    若未找到完整的【】对，返回 None。
    """
    start = line.find('【')
    end = line.find('】')
    if start != -1 and end != -1 and start < end:
        return line[start + 1:end]
    return None

def main():
    # 读取查询词列表（3k-4.txt 的每一行）
    queries = []
    try:
        with open('3k-4.txt', 'r', encoding='utf-8') as f:
            for line in f:
                q = line.strip()
                if q:   # 忽略空行
                    queries.append(q)
    except FileNotFoundError:
        print("错误：找不到文件 3k-4.txt", file=sys.stderr)
        sys.exit(1)

    # 读取 3k-b.txt，建立“汉字 → 对应行列表”的映射
    b_dict = {}
    try:
        with open('3k-b.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                kanji = extract_kanji(line)
                if kanji is not None:
                    b_dict.setdefault(kanji, []).append(line)
    except FileNotFoundError:
        print("错误：找不到文件 3k-b.txt", file=sys.stderr)
        sys.exit(1)

    # 逐条查询并输出所有匹配行
    for q in queries:
        if q in b_dict:
            for match in b_dict[q]:
                print(match)

if __name__ == '__main__':
    main()