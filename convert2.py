#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re

def extract_kanji_parts(col2):
    """从第二列提取括号内的汉字序列，去掉括号后按空格分割"""
    # 尝试匹配常见括号对
    patterns = [
        r'【(.*?)】',
        r'（(.*?)）',
        r'\((.*?)\)',
        r'\[(.*?)\]',
        r'｛(.*?)｝'
    ]
    for pat in patterns:
        m = re.search(pat, col2)
        if m:
            return m.group(1).split()
    # 没有括号则直接分割
    return col2.split()

def process_line(line):
    line = line.strip()
    if not line:
        return []
    parts = line.split('\t')
    if len(parts) < 3:
        return []   # 忽略格式错误的行

    furigana_str = parts[0]
    kanji_with_brackets = parts[1]
    pos = parts[2]

    furigana_list = furigana_str.split()
    kanji_list = extract_kanji_parts(kanji_with_brackets)

    if len(furigana_list) != len(kanji_list):
        # 长度不匹配时，可尝试截断或跳过，这里简单跳过
        sys.stderr.write(f"警告：假名与汉字 token 数不一致，跳过：{line}\n")
        return []

    n = len(furigana_list)
    all_furigana = ''.join(furigana_list)
    all_kanji = ''.join(kanji_list)

    output_lines = []
    # 生成 0 ~ 2^n-1，按位决定选择，0=汉字，1=假名
    for i in range(1 << n):
        chosen = []
        for j in range(n):
            # 从高位到低位对应第 j 个 token
            if (i >> (n - 1 - j)) & 1:
                chosen.append(furigana_list[j])
            else:
                chosen.append(kanji_list[j])
        combined = ''.join(chosen)

        # 基础输出字段
        fields = [combined, all_kanji, pos, all_furigana]

        # 全汉字组合（i == 0）额外添加 -- 和 BASE
        if i == 0:
            fields.extend(['--', 'BASE'])

        output_lines.append('\t'.join(fields))

    return output_lines

def main():
    if len(sys.argv) > 1:
        # 从文件读取
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            lines = f.readlines()
    else:
        # 从标准输入读取
        lines = sys.stdin.readlines()

    for line in lines:
        for out in process_line(line):
            print(out)

if __name__ == '__main__':
    main()