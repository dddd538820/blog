import glob
import os
import shutil
from datetime import date
from openai import OpenAI

# 配置客户端（可放在函数外全局复用）
client = OpenAI(base_url="http://127.0.0.1:22217/v1", api_key="sk-687bb30e28aa348f2448b39fbadfa9dc1730ab6be0952766")

def generate_title(text: str, model: str = "deepseek-default") -> str:
    """根据输入文本生成标题"""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": f"请为以下文本生成一个标题，只返回标题文本本身，不要加任何前缀、引号或解释：\n{text}"}
        ],
        temperature=0.7,
        max_tokens=50,
        extra_body={"thinking": {"type": "disabled"}}
    )
    return response.choices[0].message.content.strip()

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
new_lines.append(f"[{new_filename}]({new_filename})<br>\n")
for f in files:
    # 获取原文件内容到临时变量（从 archive 中读取）
    archive_path = os.path.join("archive", f)
    with open(archive_path, 'r', encoding='utf-8') as file:
        file_content = file.read()
    # 生成标题并构造链接行
    title = generate_title(file_content)
    print(f"Generated title for {f}: {title}")
    new_lines.append(f"{title}<br>\n")
    new_lines.append(f"[{f}](archive/{f})<br>\n")


# # 读取 readme.md 原有内容（若不存在则设为空字符串）
# original_content = ""
# if os.path.exists("readme.md"):
#     with open("readme.md", "r", encoding="utf-8") as rm:
#         original_content = rm.read()

# # 将新内容写入开头，后接原有内容
# with open("readme.md", "w", encoding="utf-8") as rm:
#     rm.writelines(new_lines)
#     rm.write(original_content)
# 按行读取 readme.md 原有内容（若不存在则设为空列表）
original_lines = []
if os.path.exists("readme.md"):
    with open("readme.md", "r", encoding="utf-8") as rm:
        original_lines = rm.readlines()  # 保留换行符

# 去除 new_lines 中与 original_lines 完全相同的行
# filtered_new_lines = [line for line in new_lines if line not in original_lines]

# 将过滤后的新内容加在原有内容之前写入
with open("readme.md", "w", encoding="utf-8") as rm:
    rm.writelines(new_lines)
    rm.writelines(original_lines[1:])
