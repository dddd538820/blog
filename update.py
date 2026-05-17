from git import Repo
import subprocess
import os

def add_br_to_md(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    with open(file_path, 'w', encoding='utf-8') as f:
        for i, line in enumerate(lines):
            stripped = line.rstrip('\n')
            if stripped.lstrip().startswith('#'):
                f.write(line)
            else:
                # 为了使vsc正确解析标题
                # 检查下一行是否存在且为标题行
                next_is_heading = False
                if i + 1 < len(lines):
                    next_stripped = lines[i+1].rstrip('\n')
                    if next_stripped.lstrip().startswith('#'):
                        next_is_heading = True
                # 条件：当前行是空行或仅包含<br>，并且下一行是标题
                if (stripped.strip() == '' or stripped.strip() == '<br>') and next_is_heading:
                    f.write('\n')  # 视为空行，只写入换行符
                else:
                    if not stripped.rstrip().endswith('<br>'):
                        f.write(stripped.rstrip() + '<br>\n')
                    else:
                        f.write(line)

def get_local_md_files(repo_path):
    repo = Repo(repo_path)
    unstaged = [item.a_path for item in repo.index.diff(None) if item.a_path.endswith('.md')]
    untracked = [f for f in repo.untracked_files if f.endswith('.md')]
    return unstaged + untracked

repo_path = '.'
md_files = get_local_md_files(repo_path)
print(md_files)

for md in md_files:
    #排除unstaged中被删掉的
    if os.path.exists(md):
        add_br_to_md(md)
    else:
        md_files.remove(md)

def run_git_in_powershell(git_command):
    ps_command = f"powershell -Command \"{git_command}\""
    result = subprocess.run(ps_command, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr

cmd = f'git add . ; git commit -m "update: {", ".join(md_files)}" ; git push -u origin main'
print(f"Running command: {cmd}")
cmd = cmd.replace('"', '\\"')
out, err = run_git_in_powershell(cmd)
print(out)
if err:
    print(err)
