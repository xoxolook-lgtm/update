# -*- coding: utf-8 -*-
import os
import subprocess
import sys
import glob

def run(cmd):
    """执行 shell 命令，返回是否成功；失败时退出"""
    print(f"\n▶ 执行: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ 命令失败: {cmd}")
        sys.exit(1)
    return True

def run_capture_list(cmd_args):
    """执行列表命令，捕获输出"""
    result = subprocess.run(cmd_args, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def check_clean_state():
    """检查 Git 仓库是否干净（无冲突、无未完成操作）"""
    git_dir = subprocess.run(["git", "rev-parse", "--git-dir"], capture_output=True, text=True).stdout.strip()
    if not git_dir:
        print("❌ 当前目录不是 Git 仓库")
        return False
    if os.path.exists(os.path.join(git_dir, "rebase-merge")) or os.path.exists(os.path.join(git_dir, "rebase-apply")):
        print("❌ 检测到未完成的 git rebase，请先执行 'git rebase --abort' 或手动解决。")
        return False
    status = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True).stdout
    for line in status.splitlines():
        if line.startswith("UU ") or "needs merge" in line:
            print(f"❌ 检测到未解决的冲突: {line}")
            print("请手动解决冲突，或执行 'git merge --abort' / 'git rebase --abort' 后再运行本脚本。")
            return False
    return True

def delete_apk_from_repo_only():
    """仅从 Git 仓库中删除所有 .apk 文件（保留本地文件），并将 .apk 加入 .gitignore"""
    print("\n🗑️  正在从 Git 仓库中移除所有 .apk 文件（本地文件保留）...")
    returncode, stdout, stderr = run_capture_list(["git", "ls-files", "--", "*.apk"])
    if returncode != 0:
        print("   ⚠️ 无法获取 Git 跟踪的文件列表")
        return
    apk_files = [f.strip() for f in stdout.splitlines() if f.strip()]
    if not apk_files:
        print("   ⚠️ 未找到任何被 Git 跟踪的 .apk 文件，无需删除")
        return

    deleted_count = 0
    for file_path in apk_files:
        returncode, _, stderr = run_capture_list(["git", "rm", "--cached", "--ignore-unmatch", file_path])
        if returncode == 0:
            print(f"   ✓ 已从仓库中移除（本地保留）: {file_path}")
            deleted_count += 1
        else:
            print(f"   ✗ 移除失败 {file_path}: {stderr.strip()}")

    if deleted_count == 0:
        return

    gitignore_path = ".gitignore"
    apk_ignore_line = "*.apk"
    need_add_gitignore = False
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            content = f.read()
        if apk_ignore_line not in content:
            with open(gitignore_path, "a", encoding="utf-8") as f:
                f.write(f"\n{apk_ignore_line}\n")
            need_add_gitignore = True
            print(f"   ✓ 已将 '{apk_ignore_line}' 添加到 .gitignore")
        else:
            print(f"   ✓ .gitignore 已包含 '{apk_ignore_line}'，无需重复添加")
    else:
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write(f"{apk_ignore_line}\n")
        need_add_gitignore = True
        print(f"   ✓ 已创建 .gitignore 并添加 '{apk_ignore_line}'")

    if need_add_gitignore:
        subprocess.run(["git", "add", gitignore_path], check=False)
        print(f"   ✓ 已暂存 .gitignore 的变更")

    print(f"✅ 共从仓库中移除了 {deleted_count} 个 .apk 文件（本地文件已保留）")

def add_all_apk_files():
    """强制添加当前目录下所有 .apk 文件到 Git 索引（忽略 .gitignore）"""
    print("\n📦 正在查找本地所有 .apk 文件...")
    apk_files = glob.glob("**/*.apk", recursive=True)
    if not apk_files:
        print("   ⚠️ 未找到任何 .apk 文件，无需添加")
        return

    added_count = 0
    for file_path in apk_files:
        # 使用 git add -f 强制添加
        result = subprocess.run(["git", "add", "-f", file_path], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✓ 已添加到暂存区: {file_path}")
            added_count += 1
        else:
            print(f"   ✗ 添加失败 {file_path}: {result.stderr.strip()}")
    print(f"✅ 共添加了 {added_count} 个 .apk 文件到暂存区")

def main():
    print("=" * 50)
    print("   GitHub 推送工具（合并远程变更，不强制覆盖）")
    print("=" * 50)

    if not check_clean_state():
        input("按回车退出...")
        return

    print("\n【更新逻辑说明】")
    print("1. 设置远程仓库地址为 SSH 格式")
    print("2. 可选：从仓库中删除所有 .apk 文件（本地保留）")
    print("3. 可选：强制添加本地所有 .apk 文件（上传到服务器）")
    print("4. 添加其他变更文件（仅新增和修改，忽略普通删除）")
    print("5. 提交变更")
    print("6. 拉取远程并合并（rebase），然后推送（非强制）")
    print("-" * 50)

    # 询问删除 APK
    while True:
        choice_del = input("\n🔧 是否从 Git 仓库中删除所有 .apk 文件（本地文件保留）？\n   1 - 删除仓库中的 .apk\n   2 - 跳过\n请选择 (1/2): ").strip()
        if choice_del in ('1', '2'):
            break
        print("❌ 输入无效，请重新输入 1 或 2")
    delete_apk = (choice_del == '1')

    # 询问上传 APK
    while True:
        choice_add = input("\n📤 是否强制添加本地所有 .apk 文件（上传到服务器）？\n   1 - 添加所有 .apk 并上传\n   2 - 跳过\n请选择 (1/2): ").strip()
        if choice_add in ('1', '2'):
            break
        print("❌ 输入无效，请重新输入 1 或 2")
    upload_apk = (choice_add == '1')

    REMOTE_URL = "git@github.com:xoxolook-lgtm/update.git"
    BRANCH = "main"

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"\n工作目录: {os.getcwd()}")

    if delete_apk:
        delete_apk_from_repo_only()

    print("\n1/7 设置远程仓库地址...")
    run(f"git remote set-url origin {REMOTE_URL}")

    print("\n2/7 切换到 main 分支...")
    run(f"git checkout {BRANCH}")

    print("\n3/7 添加文件（忽略普通删除）...")
    run("git add --ignore-removal .")
    if os.path.exists("update.json"):
        run("git add -f update.json")
    else:
        print("   ⚠️ update.json 不存在，跳过强制添加")

    if upload_apk:
        add_all_apk_files()

    # 检查是否有变更需要提交
    status = subprocess.run("git diff --cached --quiet", shell=True)
    if status.returncode != 0:
        print("\n4/7 提交本地变更...")
        run('git commit -m "update from local"')
    else:
        print("\n4/7 没有需要提交的本地变更，跳过提交。")

    print("\n5/7 拉取远程更新并合并（避免覆盖远程文件）...")
    run(f"git fetch origin {BRANCH}")

    # 暂存未暂存更改（保留已暂存内容）
    status_output = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True).stdout.strip()
    stashed = False
    if status_output:
        print("⚠️ 发现未暂存的更改，正在自动暂存（不影响已暂存的内容）...")
        stash_result = subprocess.run(
            ["git", "stash", "push", "--keep-index", "-m", "auto stash before rebase"],
            capture_output=True, text=True
        )
        if stash_result.returncode != 0:
            print("❌ 暂存失败，请手动处理。")
            print(stash_result.stderr)
            input("按回车退出...")
            return
        stashed = True
        print("   ✓ 未暂存更改已临时保存")

    print("正在将本地提交变基到远程分支...")
    result = subprocess.run(["git", "rebase", f"origin/{BRANCH}"], capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ 变基时发生冲突！")
        if stashed:
            subprocess.run(["git", "stash", "drop"], capture_output=True, text=True)
            print("   已丢弃临时存储")
        print("请手动解决冲突后运行 'git rebase --continue' 再重新运行本脚本。")
        print("或运行 'git rebase --abort' 放弃本次操作。")
        print(f"错误信息：{result.stderr}")
        input("按回车退出...")
        return
    else:
        print("✅ 变基成功，本地历史已更新。")

    if stashed:
        print("丢弃之前暂存的更改（本地未暂存的删除不会影响本次推送）...")
        subprocess.run(["git", "stash", "drop"], capture_output=True, text=True)
        print("   ✓ 已丢弃临时存储")

    print("\n6/7 正在推送至远程仓库...")
    run(f"git push origin {BRANCH}")

    print("\n7/7 完成！")
    print("\n✅ 按回车退出...")
    input()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"异常: {e}")
        input("按回车退出...")