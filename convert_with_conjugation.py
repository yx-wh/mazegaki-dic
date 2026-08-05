import re
import sys

input_file = "ipadic.maze.csv"
output_file = "mazegaki_st.txt"

def is_kana_only(s):
    return re.fullmatch(r'[ぁ-ん]+', s) is not None

def is_kanji_only(s):
    return re.fullmatch(r'[\u4e00-\u9faf]+', s) is not None

def get_word_type(base, pos):
    """根据品詞和原形判断类型"""
    if '形容詞' in pos:
        return 'adj'
    if '動詞' in pos:
        if '五段' in pos:
            return 'v5'
        elif '一段' in pos:
            return 'v1'
    return 'other'  # 名词、サ変、カ変等

def gen_adj_forms(word):
    """形容词：原形、～く、～か"""
    stem = word[:-1]  # 去掉末尾的い
    return {
        'terminal': word,
        'base_ka': stem + 'か',  # 「か」形（过去/推量词干）：暑か（暑かった、暑かろう）
        'rentai_old': stem + 'き',   # 文语连体形（例：大きき）
        'renyou': stem + 'く',
        'kere': stem + 'けれ',
        'meishi': stem + 'さ'    # 名词化（例：高さ）
    }

def gen_v5_forms(word):
    """五段动词：6种词干"""
    stem = word[:-1]
    last = word[-1]   # 末尾假名
    # 活用表
    table = {
        'く': ('か', 'き', 'く', 'け', 'こ', 'い'),
        'ぐ': ('が', 'ぎ', 'ぐ', 'げ', 'ご', 'い'),
        'す': ('さ', 'し', 'す', 'せ', 'そ', 'し'),
        'つ': ('た', 'ち', 'つ', 'て', 'と', 'っ'),
        'ぬ': ('な', 'に', 'ぬ', 'ね', 'の', 'ん'),
        'ぶ': ('ば', 'び', 'ぶ', 'べ', 'ぼ', 'ん'),
        'む': ('ま', 'み', 'む', 'め', 'も', 'ん'),
        'る': ('ら', 'り', 'る', 'れ', 'ろ', 'っ'),
        'う': ('わ', 'い', 'う', 'え', 'お', 'っ'),
    }
    if last not in table:
        return {}
    mizen, renyou, terminal, katei, suiryou, onbin = table[last]
    return {
        'mizen': stem + mizen,     # 未然形
        'renyou': stem + renyou,   # 連用形
        'terminal': stem + terminal, # 終止形（辞書形）
        'katei': stem + katei,     # 仮定形
        'suiryou': stem + suiryou, # 推量形
        'onbin': stem + onbin,     # 音便連用形
    }

def gen_v1_forms(word):
    """一段动词：原形、連用形（去掉る）"""
    stem = word[:-1]  # 去掉结尾的る
    return {
        'terminal': word,
        'renyou': stem
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
        base = parts[1]      # 原形（应与 current_base 一致）
        pos = parts[2]       # 品詞
        
        # 使用 BASE 记录的品詞（若有），否则用当前行的
        word_type = get_word_type(base, current_pos if current_pos else pos)
        target_base = current_base if current_base else base
        
        # 跳过纯假名或纯汉字（避免冗余）
        if is_kana_only(form) or is_kanji_only(form):
            continue
       
        # ---------- 关键修改 ----------
        if word_type in ('adj', 'v5', 'v1'):
            # 动词/形容词：生成原形 + 活用形
            if word_type == 'adj':
                forms = gen_adj_forms(form)
            elif word_type == 'v5':
                forms = gen_v5_forms(form)
                if target_base == "行く" and 'onbin' in forms:
                    forms['onbin'] = forms['terminal'][:-1] + 'っ'  # 将原形末尾的"く"换成"っ"
            elif word_type == 'v1':
                forms = gen_v1_forms(form)
            
            # 🔹 去重：使用 set 去除重复值
            unique_forms = set(forms.values())
            for val in unique_forms:
                if val == target_base:
                    continue
                if is_kana_only(val) or is_kanji_only(val):
                    continue
                f_out.write(f"{val} st:{target_base}\n")
        else:
            # 其他词性（名词、サ変、カ変等）：只生成原形映射
            if form != target_base:
                f_out.write(f"{form} st:{target_base}\n")

