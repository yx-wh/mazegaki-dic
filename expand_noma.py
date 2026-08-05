import re

input_file = "mazegaki_st.txt"
output_file = "mazegaki_st_expanded.txt"

def expand_noma(text):
    """将字符串中的『々』替换为前一个字符"""
    result = []
    for i, ch in enumerate(text):
        if ch == '々' and i > 0:
            result.append(text[i-1])  # 用前一个字符替代
        else:
            result.append(ch)
    return ''.join(result)

with open(input_file, "r", encoding="utf-8") as f_in, \
     open(output_file, "w", encoding="utf-8") as f_out:
    
    for line in f_in:
        line = line.strip()
        if not line:
            continue
        
        # 格式：form st:target
        if " st:" not in line:
            f_out.write(line + "\n")
            continue
        
        # 分割
        parts = line.split(" st:", 1)  # 只分割一次，保留 target
        form = parts[0].strip()
        target = parts[1].strip()
        
        # 检查 target 中是否包含 々
        if '々' in target:
            new_target = expand_noma(target)
            f_out.write(f"{form} st:{new_target}\n")
        else:
            f_out.write(line + "\n")
