# -*- coding: utf-8 -*-
"""
实验三：豆瓣电影/小说 TOP50 数据抽取与入库全流程
✅ ① txt → Excel
✅ ② txt → SQLite
✅ ③ Excel → SQLite
✅ ④ 从 SQLite 读取并打印数据
"""

import re
import pandas as pd
import sqlite3

# ==============================
# 第一步：解析 douban_top50.txt
# ==============================
print("🔍 正在解析 douban_top50.txt...")

with open('douban_top50.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# 按分隔线切分条目
parts = content.split('------------------------------------------------------------')
entries = [part.strip() for part in parts if '《' in part and '链接:' in part]

data = []
for entry in entries:
    # 提取 rank
    rank_match = re.search(r'【(\d+)】', entry)
    rank = int(rank_match.group(1)) if rank_match else None
    
    # 提取 title
    title_match = re.search(r'《([^》]+)》', entry)
    title = title_match.group(1).strip() if title_match else ""
    
    # 提取 url
    url_match = re.search(r'链接:\s*(https?://[^\s]+)', entry)
    url = url_match.group(1).strip() if url_match else ""
    
    # 提取评论（处理多行）
    comments_text = ""
    if '用户短评:' in entry:
        comment_start = entry.find('用户短评:') + len('用户短评:')
        comments_block = entry[comment_start:].strip()
        comment_lines = []
        for line in comments_block.split('\n'):
            line = line.strip()
            if line and re.match(r'\d+\.\s*', line):
                text = re.sub(r'^\d+\.\s*', '', line)
                comment_lines.append(text)
        comments_text = '; '.join(comment_lines)
    
    if rank is not None:
        data.append({
            'rank': rank,
            'title': title,
            'url': url,
            'comments': comments_text
        })

df = pd.DataFrame(data)
df = df.sort_values('rank').reset_index(drop=True)
print(f"✅ 成功解析 {len(df)} 条电影记录")

# ==============================
# ① txt → Excel
# ==============================
excel_file = 'douban_top50_movies.xlsx'
df.to_excel(excel_file, index=False)
print(f"\n✅ ① 已将 txt 数据导入 结构化表格 '{excel_file}'")

# ==============================
# ② txt → SQLite (数据库 A)
# ==============================
db_from_txt = 'douban_from_txt.db'
conn1 = sqlite3.connect(db_from_txt)
df.to_sql('movies', conn1, if_exists='replace', index=False)
conn1.close()
print(f"✅ ② 已将 txt 数据导入 SQLite 数据库 '{db_from_txt}' 表 'movies'")

# ==============================
# ③ Excel → SQLite (数据库 B)
# ==============================
# 从 Excel 重新读取数据
df_from_excel = pd.read_excel(excel_file)

# 写入新的 SQLite 数据库（模拟 Excel 作为中间格式导入 SQL）
db_from_excel = 'douban_from_excel.db'
conn2 = sqlite3.connect(db_from_excel)
df_from_excel.to_sql('movies', conn2, if_exists='replace', index=False)
conn2.close()
print(f"✅ ③ 已将 Excel 数据导入 SQLite 数据库 '{db_from_excel}' 表 'movies'")

# 验证数据一致性
if len(df) == len(df_from_excel):
    print("✅ ③ 验证：Excel 与原始数据条目数一致")
else:
    print("⚠️ ③ 警告：数据条目数不一致！")

# ==============================
# ④ 从 SQL 读取并打印（以 txt 导入的库为例）
# ==============================
print("\n📚 ④ 从 SQLite 数据库读取数据（前10部）：")
conn_read = sqlite3.connect(db_from_txt)
query_df = pd.read_sql_query("SELECT rank, title, url FROM movies ORDER BY rank", conn_read)

for _, row in query_df.head(10).iterrows():
    print(f"[{row['rank']:02d}] {row['title']}")
    print(f"     链接: {row['url']}\n")

conn_read.close()

# ==============================
# 最终提示
# ==============================
print("=" * 60)
print("🎉 实验流程圆满完成！")
print(f"📁 生成文件：")
print(f"   - Excel: {excel_file}")
print(f"   - SQLite (from txt): {db_from_txt}")
print(f"   - SQLite (from Excel): {db_from_excel}")
print("\n💡 提示：可用 DB Browser for SQLite 打开 .db 文件查看表格结构。")