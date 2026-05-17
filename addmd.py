import glob
import os
import shutil
from datetime import date

# 当前日期
today = date.today()
date_str = f"{today.year}.{today.month}.{today.day}"

# 匹配已有文件
pattern = f"{date_str}.*.md"
files = glob.glob(pattern)

# 提取最大序号（若无文件，max_num 保持 0）
max_num = 0
for f in files:
    parts = f.split('.')
    if len(parts) >= 2:
        try:
            num = int(parts[-2])
            if num > max_num:
                max_num = num
        except ValueError:
            pass

# 将已有文件全部移入 archive 文件夹
if files:
    os.makedirs("archive", exist_ok=True)
    for f in files:
        shutil.move(f, os.path.join("archive", f))

# 新建文件（无文件时自动从 1 开始）
new_num = max_num + 1
new_filename = f"{date_str}.{new_num}.md"
open(new_filename, 'w').close()

# 构造本次要写入 readme.md 开头的链接行
new_lines = []
for f in files:
    new_lines.append(f"archive/{f}\n")
new_lines.append(f"{new_filename}\n")

# 读取 readme.md 原有内容（若不存在则设为空字符串）
original_content = ""
if os.path.exists("readme.md"):
    with open("readme.md", "r", encoding="utf-8") as rm:
        original_content = rm.read()

# 将新内容写入开头，后接原有内容
with open("readme.md", "w", encoding="utf-8") as rm:
    rm.writelines(new_lines)
    rm.write(original_content)