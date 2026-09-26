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

with open(input_file, "r", encoding="utf-8") as f_in, \
     open(output_file, "w", encoding="utf-8") as f_out:
    
    current_base = None
    current_pos = None
    yn_hits = 0
    
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
        else:
            # 没有标记类型时，仍然输出 st: 映射
            f_out.write(f"{form} st:{target_base}\n")

print(f"[info] YN 源头 {len(YN_BASES)} 条；本轮传播到 {yn_hits} 条交ぜ書き写法",
      file=sys.stderr)
