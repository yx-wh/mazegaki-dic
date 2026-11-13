#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add_homonym_flag.py - 给「同一 head 出现多行」的每一行补一个未定义旗标（默认 Zz）。

背景（hunspell 1.7.3–1.7.6 的 HashMgr 去重 bug）：
    HashMgr::add_word() 遇到「同 head、无 affix flag」时一律当重复词跳过，
    但不比较 HENTRY_DATA（morph / st:），于是
        青み st:青味
        青み st:青身
    只留第一行，青身 静默消失。spell() 仍为 true，查不出来。
    上游 cca6830（2026-11-12）已修，但要等 1.7.7 才铺开；
    Debian/Ubuntu/Fedora/Arch/Homebrew 目前都还是 1.7.6。

做法（同 hunspell_zh_CN 的 /Xx）：
    - Zz 必须在 .aff 里【未定义】。它只起「这一行有 flag」的作用，
      让 add_word() 走 next_homonym 分支，不派生任何词形；
    - FLAG long 下必须两字符，否则会被 decode_flags() 截断；
    - 只对多行 head 补，单行 head 不动（省字节）。
    注意：日文 ja_JP.aff 里的 Xx / xx 是形容词规则（非空壳），不能借用，
    所以另取 Zz。

用法:
    python add_homonym_flag.py ja_JP.dic            # dry-run，只报告
    python add_homonym_flag.py ja_JP.dic --apply    # 落盘（自动 .bak）

退役条件:
    等 1.7.3–1.7.6 全部退出使用（含各发行版 LTS），把本脚本从生成流水线删掉即可，
    不要留在生成链里。
"""

import argparse
import os
import re
import shutil
import sys

DEFAULT_FLAG = "Zz"


def parse_body_line(line):
    """'head/flags st:target' -> (head, flags, ' st:target')；空行返回 None。"""
    if not line:
        return None
    headfield, sep, morph = line.partition(" ")
    head, _slash, flags = headfield.partition("/")
    rest = (sep + morph) if sep else ""
    return head, flags, rest


def has_flag(flags, tag):
    """FLAG long：按两字符一组比较。"""
    return any(flags[i:i + 2] == tag for i in range(0, len(flags) - 1, 2))


def aff_defines(aff_path, tag):
    if not aff_path or not os.path.exists(aff_path):
        return False
    pat = re.compile(r"^(?:SFX|PFX)\s+(\S+)\s+[YN]\s+\d+")
    with open(aff_path, encoding="utf-8") as f:
        for line in f:
            m = pat.match(line)
            if m and m.group(1) == tag:
                return True
    return False


def guess_aff(dic_path):
    d = os.path.dirname(os.path.abspath(dic_path))
    for cand in (os.path.join(d, "..", "hunspell_ja_JP", "ja_JP.aff"),
                 os.path.join(d, "ja_JP.aff")):
        if os.path.exists(cand):
            return cand
    return None


def main():
    ap = argparse.ArgumentParser(description="给多行 head 补同形异义旗标")
    ap.add_argument("dic")
    ap.add_argument("--flag", default=DEFAULT_FLAG, help="两字符、且在 .aff 中未定义")
    ap.add_argument("--aff", default=None, help="用于校验旗标未定义")
    ap.add_argument("--apply", action="store_true", help="落盘（默认 dry-run）")
    args = ap.parse_args()

    tag = args.flag
    if len(tag) != 2:
        sys.exit(f"[错误] FLAG long 要求两字符，得到 {tag!r}")

    aff = args.aff or guess_aff(args.dic)
    if aff_defines(aff, tag):
        sys.exit(f"[错误] {aff} 已定义旗标 {tag!r}，它必须保持未定义")
    if aff:
        print(f"[info] 校验 aff: {aff}（{tag} 未定义 ✓）")
    else:
        print(f"[warn] 未找到 .aff，跳过「{tag} 必须未定义」校验", file=sys.stderr)

    with open(args.dic, encoding="utf-8") as f:
        lines = f.read().split("\n")
    header, body = lines[0], lines[1:]

    recs = [parse_body_line(l) for l in body]
    group = {}
    for i, r in enumerate(recs):
        if r is not None:
            group.setdefault(r[0], []).append(i)
    multi = {h: idxs for h, idxs in group.items() if len(idxs) > 1}

    touched = added = already = 0
    changed = []
    for head, idxs in multi.items():
        for i in idxs:
            _, flags, rest = recs[i]
            touched += 1
            if has_flag(flags, tag):
                already += 1
            else:
                added += 1
                recs[i] = (head, flags + tag, rest)
                changed.append((head, flags or "(空)", flags + tag))

    print(f"条目行 {sum(1 for r in recs if r)} | head 数 {len(group)} | 多行 head {len(multi)}")
    print(f"涉及行 {touched} | 本次补 {added} | 已有 {already}")

    if added == 0:
        print("无需改动（幂等）")
        return

    print("样例:")
    for head, before, after in changed[:8]:
        print(f"   {head}: {before} -> {after}")

    if not args.apply:
        print("\n[dry-run] 未写入。加 --apply 落盘。")
        return

    new_body = []
    for orig, r in zip(body, recs):
        if r is None:
            new_body.append(orig)
            continue
        head, flags, rest = r
        new_body.append(f"{head}/{flags}{rest}" if flags else f"{head}{rest}")

    bak = args.dic + ".bak"
    shutil.copy2(args.dic, bak)
    with open(args.dic, "w", encoding="utf-8") as f:
        f.write("\n".join([header] + new_body))
    print(f"已写入 {args.dic}（备份 {bak}）")


if __name__ == "__main__":
    main()
