import re
import sys

input_file = "ipadic.maze.csv"
output_file = "mazegaki_st.txt"

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

with open(input_file, "r", encoding="utf-8") as f_in, \
     open(output_file, "w", encoding="utf-8") as f_out:
    
    current_base = None
    current_pos = None
    
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
            f_out.write(f"{form}/{marker} st:{target_base}\n")
        else:
            # 没有标记类型时，仍然输出 st: 映射
            f_out.write(f"{form} st:{target_base}\n")
