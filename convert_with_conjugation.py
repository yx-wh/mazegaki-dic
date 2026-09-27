import re
import sys

input_file = "ipadic.maze.csv"
output_file = "mazegaki_st.txt"
part_file = "ja_JP.part.txt"

def is_kana_only(s):
    return re.fullmatch(r'[ぁ-ん]+', s) is not None

def is_kanji_only(s):
    return re.fullmatch(r'[\u4e00-\u9faf]+', s) is not None

def get_word_type(base, pos):
    """根据品詞判断类型，返回用于标记的键"""
    if '形容詞' in pos:
        return 'adj1'          # 形容詞
    if '形動' in pos:
        return 'adj2'          # 形動（不是副词）
    if '動詞' in pos:
        if '五段' in pos:
            return 'v5'
        elif '一段' in pos:
            return 'v1'
        elif 'サ変' in pos:
            return 'vs'
    return 'other'

# Hunspell 词缀标记
MARKERS = {
    'v5':   '5A5I5T5E5OBDUYUBubKN',
    'v1':   '1KBDUyUbKN',
    'vs':   '3A3a3I3E3e',
    'adj1': 'GRGESASGSOXKXQXrXO',   # 形容詞
    'adj2': 'sosgsasnsi',             # 形動（そう/すぎ/さ + な/に）
}


def load_yn_bases(path=part_file):
    """收集 part.txt 里带 YN 标志的词，作为「YN 向下传播」的源头。

    YN = ja_JP.aff 里的「い形容词不规则活用」，只在 part.txt 手工标注
    （ない / 無い / 亡い / よい / 良い / かっこよい / 気持ち良い /
    こない / 来ない / 〜無い 复合词 …），目前 110 条。

    交ぜ書き写法（情けない → 情け無い）由本脚本生成，必须跟着原形一起带 YN，
    否则「情けなさそう」「気持ちよさそう」这种只在 ない/無い/よい 系才成立的
    形式会丢。反过来，危ない 这种单个语素的词不是任何 無い 原形的交ぜ書き，
    天然不在传播链上，不会被误加（它的 〜そう 形是无さ 的 危なそう）。

    注意 aff 是 `FLAG long`，标志按两字符一组解析，不能用子串匹配
    （比如 GRGESASGSOXKXQXrXO 里本没有 YN，但 XAxaxixI 之类拼接可能碰巧撞出）。
    """
    bases = set()
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                head = line.split(" ", 1)[0].strip()
                if not head:
                    continue
                word, _, flags = head.partition("/")
                pairs = [flags[i:i + 2] for i in range(0, len(flags), 2)]
                if "YN" in pairs:
                    bases.add(word)
    except OSError as exc:
        print(f"[warn] 读 {path} 失败，YN 传播已跳过: {exc}", file=sys.stderr)
    return bases


YN_BASES = load_yn_bases()


# --- 补发「不在 part.txt 的 BASE 词」--------------------------------------
# CSV 的 BASE 行只记录原形、从不输出（设计上假定它们已在 part.txt）。
# 但有 1 万多个 BASE 词不在 part.txt，于是它们只当别人的 st: 终点、自己不是词条，
# 连带它们的活用形也进不了词典（味付けた 还原不了）。
# 例外：IME 专用的交ぜ書き置換形（う余曲折 / 金太郎あめ）不该当 hunspell 词目 ——
# 不会有辞典以「う余曲折」为索引。判据与 ja_fix_mazegaki_chain.py 一致。

KANJI_RE = re.compile(r'[\u4e00-\u9faf]')
KANA_RE = re.compile(r'[ぁ-んァ-ヴー]')


def _is_subseq(sub, full) -> bool:
    it = iter(full)
    return all(c in it for c in sub)


def load_part_words(path=part_file):
    words = set()
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                head = line.split(" ", 1)[0].strip()
                if head:
                    words.add(head.partition("/")[0])
    except OSError as exc:
        print(f"[warn] 读 {path} 失败: {exc}", file=sys.stderr)
    return words


def load_ime_dirt(path=input_file):
    """混写 BASE + 从未作为交ぜ書き出现过 + 汉字是同读音更全形式的子序列 → IME 脏数据。"""
    bases, by_reading, variants = {}, {}, set()
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.rstrip("\n")
                if not line:
                    continue
                p = line.split("\t")
                if line.endswith("--\tBASE"):
                    if len(p) >= 4:
                        bases[p[1]] = p[3]
                        by_reading.setdefault(p[3], []).append(p[1])
                elif len(p) >= 4:
                    variants.add(p[0])
    except OSError as exc:
        print(f"[warn] 读 {path} 失败: {exc}", file=sys.stderr)
        return set()
    dirt = set()
    for w, rd in bases.items():
        if not (KANJI_RE.search(w) and KANA_RE.search(w)) or w in variants:
            continue
        kw = KANJI_RE.findall(w)
        for sib in by_reading.get(rd, ()):
            if sib == w:
                continue
            ks = KANJI_RE.findall(sib)
            if len(ks) > len(kw) and _is_subseq(kw, ks):
                dirt.add(w)
                break
    return dirt


PART_WORDS = load_part_words()
IME_DIRT = load_ime_dirt()


# 注：人工批注的映射（あいさつ回り -> 挨拶回り 等 69 条）已由
# scripts/ja_apply_manual_to_csv.py patch 进 ipadic.maze.csv，
# 数据自包含，这里不再需要读映射表。


# --- 旧字体 -> 新字体 ------------------------------------------------------
# 辞典只收新字体（与える / 挙げる / 元の木阿弥），旧字体形（與える / 擧げる /
# 元の木阿彌）查不到。用 opencc 的 t2jp 补一条 st: 指过去，划词时就能跳到
# 辞典收得着的写法。
#
# 必须加护栏：opencc 有反向错误（疎外 -> 疏外、疎開 -> 疏開，日语标准是 疎），
# 所以只在「新字体形确实是 part.txt 已有词目、且旧字体形不是」时才生成 ——
# 这样 缺(在 part.txt) 之类会被自动排除。
try:
    from opencc import OpenCC as _OpenCC
    _T2JP = _OpenCC("t2jp")
except Exception as exc:                                   # pragma: no cover
    print(f"[warn] opencc 不可用，旧字体映射已跳过: {exc}", file=sys.stderr)
    _T2JP = None


def shinjitai(word: str) -> str:
    """旧字体/繁体 -> 日本新字体。opencc 不收的异体（擧）会原样返回。"""
    return _T2JP.convert(word) if _T2JP is not None else word

with open(input_file, "r", encoding="utf-8") as f_in, \
     open(output_file, "w", encoding="utf-8") as f_out:
    
    current_base = None
    current_pos = None
    yn_hits = 0
    missing_bases = {}      # 不在 part.txt 的 BASE 词 -> 品詞
    emitted = set()         # 本轮已写出的交ぜ書き形
    old_hits = 0            # 旧字体 -> 新字体 映射条数
    
    for line in f_in:
        line = line.strip()
        if not line:
            continue
        
        # BASE 行：记录原形和品詞
        if line.endswith("--\tBASE"):
            parts = line.split("\t")
            if len(parts) >= 3:
                current_base = parts[1]
                current_pos = parts[2]
            # 原本只记录、不输出；这里顺手记下「不在 part.txt 的 BASE 词」，
            # 循环结束后补发（见文件末尾）
            if (len(parts) >= 3 and current_base not in PART_WORDS
                    and current_base not in IME_DIRT):
                missing_bases.setdefault(current_base, current_pos)
            continue
        
        # 非 BASE 行
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        
        form = parts[0]      # 交ぜ書き表記
        pos = parts[2]       # 品詞（备用）
        
        # 确定词类型和最终目标原形
        word_type = get_word_type(current_base, current_pos if current_pos else pos)
        target_base = current_base if current_base else parts[1]
        
        # 跳过：纯假名、纯汉字、与目标原形相同
        if is_kana_only(form) or is_kanji_only(form):
            continue
        if form == target_base:
            continue
        
        ## 如果有对应的词缀标记，先输出带标记的行
        #if word_type in MARKERS:
        #    marker = MARKERS[word_type]
        #    f_out.write(f"{form}/{marker}\n")
        #
        ## 输出 st: 映射行
        #f_out.write(f"{form} st:{target_base}\n")
        # 如果有对应的词缀标记，输出带标记 + st: 的行
        if word_type in MARKERS:
            marker = MARKERS[word_type]
            # 原形带 YN（ない/無い/よい 系不规则活用）=> 交ぜ書き写法也要带，
            # 否则只有 〜なさそう / 〜よさそう 这类形式会丢。标志与 st: 同行，
            # 派生形式才能拿到词干。
            if target_base in YN_BASES:
                marker += "YN"
                yn_hits += 1
            f_out.write(f"{form}/{marker} st:{target_base}\n")
            emitted.add(form)
            # 交ぜ書き形里若含旧字体，再补一条指向新字体写法的
            if shinjitai(form) not in (form, target_base) \
                    and shinjitai(form) in PART_WORDS and form not in PART_WORDS:
                f_out.write(f"{form}/{marker} st:{shinjitai(form)}\n")
                old_hits += 1
        else:
            # 没有标记类型时，仍然输出 st: 映射
            f_out.write(f"{form} st:{target_base}\n")
            emitted.add(form)
            if shinjitai(form) not in (form, target_base) \
                    and shinjitai(form) in PART_WORDS and form not in PART_WORDS:
                f_out.write(f"{form} st:{shinjitai(form)}\n")
                old_hits += 1

    # 补发「不在 part.txt 的 BASE 词」：它们自己不是词条，连带活用形也进不来。
    # 跳过 IME 交ぜ書き置換形，以及本轮已作为交ぜ書き写出的（那种已有 st: 指向原形）。
    added = 0
    for word, pos in missing_bases.items():
        if word in emitted:
            continue
        marker = MARKERS.get(get_word_type(word, pos), "")
        new = shinjitai(word)
        if new != word and new in PART_WORDS and word not in PART_WORDS:
            # 旧字体形本身：直接指到新字体形，辞典才收得着
            f_out.write(f"{word}/{marker} st:{new}\n" if marker
                        else f"{word} st:{new}\n")
            old_hits += 1
        else:
            f_out.write(f"{word}/{marker}\n" if marker else f"{word}\n")
        added += 1

print(f"[info] YN 源头 {len(YN_BASES)} 条；本轮传播到 {yn_hits} 条交ぜ書き写法",
      file=sys.stderr)
print(f"[info] 补发缺失 BASE 词 {added} 条"
      f"（IME 混写脏数据已排除 {len(IME_DIRT)} 条）", file=sys.stderr)
print(f"[info] 旧字体 -> 新字体 映射 {old_hits} 条"
      f"（opencc t2jp，带 part.txt 护栏）", file=sys.stderr)

