import csv

# 输入和输出文件名
input_file = "ipadic.maze.csv"
output_file = "ipadic.maze.sorted.csv"

# 列索引（假设列顺序为 A, B, C, D, E, F）
# 排序优先级：C(2), D(3), B(1), A(0)
sort_indices = (2, 3, 1, 0)  # 按升序

with open(input_file, 'r', newline='', encoding='utf-8') as fin, \
     open(output_file, 'w', newline='', encoding='utf-8') as fout:
    
    reader = csv.reader(fin, delimiter='\t')
    writer = csv.writer(fout, delimiter='\t')
    
    # 读取标题行（如果有）
    #try:
    #    header = next(reader)
    #except StopIteration:
    #    header = None
    
    # 读取所有数据行
    rows = list(reader)
    
    # 排序：按指定列依次升序
    rows.sort(key=lambda row: (row[2], row[3], row[1], row[0]))
    
    # 写入输出
    #if header:
    #    writer.writerow(header)
    writer.writerows(rows)

print(f"排序完成，结果保存至 {output_file}")
