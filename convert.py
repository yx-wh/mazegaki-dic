import re

input_file = "ipadic.maze.csv"
output_file = "mazegaki_st.txt"

def is_kana_only(s):
    # 只包含平假名、片假名、长音符、浊点等
    return re.fullmatch(r'[ぁ-んァ-ヶー－]+', s) is not None

def is_kanji_only(s):
    # 只包含 CJK 统一汉字
    return re.fullmatch(r'[\u4e00-\u9faf]+', s) is not None

with open(input_file, "r", encoding="utf-8") as f_in, \
     open(output_file, "w", encoding="utf-8") as f_out:
    
    current_base = None
    for line in f_in:
        line = line.strip()
        if not line:
            continue
        
        # 检测 BASE 行：行尾是否包含 "-- BASE"
        if line.endswith("-- BASE"):
            parts = line.split("\t")
            if len(parts) >= 2:
                current_base = parts[1]  # 原形
            continue
        
        # 非 BASE 行，解析
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        
        form = parts[0]   # 交ぜ書き表記
        base = parts[1]   # 原形（理论上应与 current_base 相同）
        
        # 如果 current_base 未设置，使用 base 作为原形（容错）
        target_base = current_base if current_base else base
        
        # 跳过纯假名
        if is_kana_only(form):
            continue
        
        # 跳过纯汉字（即原形本身或全汉字变体）
        if is_kanji_only(form):
            continue
        
        # 如果是混合写法且与原形不同，生成 st:
        if form != target_base:
            f_out.write(f"{form} st:{target_base}\n")
