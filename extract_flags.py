#!/usr/bin/env python3
import sys

def extract_flags_from_line(line: str) -> str | None:
    """
    从一行字典内容中提取 flag 组合。
    格式：单词/flag组合  或  单词/flag组合/其他（但通常只有一个斜杠）
    如果行中没有斜杠，或斜杠后为空，则返回 None。
    """
    line = line.strip()
    if not line:
        return None
    # 使用 rpartition 从右侧分割，以防单词中含有 '/'（但通常不会）
    word, sep, flag_part = line.rpartition('/')
    if sep and flag_part:
        return flag_part
    return None

def main():
    flags = set()
    
    # 从标准输入或命令行指定的文件读取
    if len(sys.argv) > 1:
        # 如果有参数，当作文件名处理
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            for line in f:
                flag_part = extract_flags_from_line(line)
                if flag_part:
                    flags.add(flag_part)
    else:
        # 否则从标准输入读取
        for line in sys.stdin:
            flag_part = extract_flags_from_line(line)
            if flag_part:
                flags.add(flag_part)
    
    # 输出所有不同的 flag 组合，排序后每行一个
    for flag in sorted(flags):
        print(flag)

if __name__ == '__main__':
    main()