#!/usr/bin/env python3
import sys

def has_non_bmp_char(line: str) -> bool:
    # 判断该行是否存在码位大于 U+FFFF 的字符（即非BMP）
    return any(ord(ch) > 0xFFFF for ch in line)

def scan_file(filepath: str):
    try:
        # 使用 utf-8-sig 自动兼容带 BOM 的 UTF-8 文件
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            found = False
            for line_no, line in enumerate(f, start=1):
                if has_non_bmp_char(line):
                    # 输出格式：文件名:行号: 原始内容（保留原换行符）
                    sys.stdout.write(f"{filepath}:{line_no}: {line}")
                    found = True
            if not found:
                print(f"✅ 未在 {filepath} 中发现非BMP字符。", file=sys.stderr)
    except FileNotFoundError:
        print(f"❌ 错误：文件 '{filepath}' 不存在", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 读取文件出错: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python3 find_non_bmp.py <文件名>", file=sys.stderr)
        sys.exit(1)
    scan_file(sys.argv[1])