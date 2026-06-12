# -*- coding: utf-8 -*-
import os
import subprocess
import sys
import glob

def run(cmd):
    """执行 shell 命令，返回是否成功"""
    print(f"\n▶ 执行: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ 命令失败: {cmd}")
        return False
    return True

def run_capture(cmd_args):
    """执行命令（列表形式），返回 (returncode, stdout, stderr)"""
    result = subprocess.run(cmd_args, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def delete_apk_from_repo_only():
    """
    仅从 Git 仓库中删除所有 .apk 文件（保留本地文件），并将 .apk 加入 .gitignore
    """
    print("\n🗑️  正在从 Git 仓库中移除所有 .apk 文件（本地文件保留）...")

    # 获取所有被 Git 跟踪的 .apk 文件
    returncode, stdout, stderr = run_capture(["git", "ls-files", "--", "*.apk"])
    if returncode != 0:
        print("   ⚠️ 无法获取 Git 跟踪的文件列表")
        return
    apk_files = [f.strip() for f in stdout.splitlines() if f.strip()]
    if not apk_files:
        print("   ⚠️ 未找到任何被 Git 跟踪的 .apk 文件，无需删除")
        return

    deleted_count = 0
    for file_path in apk_files:
        # 使用 git rm --cached 仅删除索引中的记录，保留工作区文件
        returncode, _, stderr = run_capture(["git", "rm", "--cached", "--ignore-unmatch", file_path])
        if returncode == 0:
            print(f"   ✓ 已从仓库中移除（本地保留）: {file_path}")
            deleted_count += 1
        else:
            print(f"   ✗ 移除失败 {file_path}: {stderr.strip()}")

    if deleted_count == 0:
        return

    # 确保 .gitignore 中包含 *.apk 忽略规则
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
        # 暂存 .gitignore 的修改
        subprocess.run(["git", "add", gitignore_path], check=False)
        print(f"   ✓ 已暂存 .gitignore 的变更")

    print(f"✅ 共从仓库中移除了 {deleted_count} 个 .apk 文件（本地文件已保留）")

def main():
    print("=" * 50)
    print("   GitHub 推送工具（合并远程变更，不强制覆盖）")
    print("=" * 50)

    print("\n【更新逻辑说明】")
    print("1. 设置远程仓库地址为 SSH 格式")
    print("2. 拉取远程最新代码并与本地合并（避免覆盖远程独有文件）")
    print("3. 可选：仅从仓库中删除所有 .apk 文件（本地保留），并自动加入 .gitignore")
    print("4. 添加变更文件（仅新增和修改，忽略普通删除）：")
    print("   - git add --ignore-removal .")
    print("   - git add -f update.json（强制覆盖）")
    print("5. 提交变更（如果有）")
    print("6. 推送变更到 GitHub（非强制，若远程有冲突会停止）")
    print("-" * 50)

    # ===== 询问是否从仓库中删除所有 .apk 文件 =====
    while True:
        choice = input("\n🔧 是否从 Git 仓库中删除所有 .apk 文件（本地文件保留）？\n   1 - 仅删除仓库中的 .apk\n   2 - 跳过\n请选择 (1/2): ").strip()
        if choice in ('1', '2'):
            break
        print("❌ 输入无效，请重新输入 1 或 2")
    delete_apk = (choice == '1')

    # ===== 配置区 =====
    REMOTE_URL = "git@github.com:xoxolook-lgtm/update.git"
    BRANCH = "main"
    # =================

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"\n工作目录: {os.getcwd()}")

    # 如果需要删除仓库中的 .apk，在 git 操作前执行
    if delete_apk:
        delete_apk_from_repo_only()

    print("\n1/5 设置远程仓库地址...")
    run(f"git remote set-url origin {REMOTE_URL}")

    # 确保在正确的分支
    print("\n2/5 切换到 main 分支...")
    run(f"git checkout {BRANCH}")

    print("\n3/5 添加文件（忽略普通删除）...")
    run("git add --ignore-removal .")
    if os.path.exists("update.json"):
        run("git add -f update.json")
    else:
        print("   ⚠️ update.json 不存在，跳过强制添加")

    # 检查是否有变更需要提交
    status = subprocess.run("git diff --cached --quiet", shell=True)
    if status.returncode != 0:
        print("\n4/5 提交本地变更...")
        if not run('git commit -m "update from local"'):
            print("❌ 提交失败，退出")
            input("按回车退出...")
            return
    else:
        print("\n4/5 没有需要提交的本地变更，跳过提交。")

    # 拉取远程更新并合并（使用 rebase 保持历史线性）
    print("\n5/5 拉取远程更新并合并（避免覆盖远程文件）...")
    # 先 fetch
    if not run(f"git fetch origin {BRANCH}"):
        print("❌ 获取远程更新失败")
        input("按回车退出...")
        return

    # 尝试 rebase，如果有冲突则停止
    print("正在将本地提交变基到远程分支...")
    result = subprocess.run(f"git rebase origin/{BRANCH}", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ 变基时发生冲突！")
        print("请手动解决冲突后运行 'git rebase --continue' 再重新运行本脚本。")
        print("或运行 'git rebase --abort' 放弃本次操作。")
        print(f"错误信息：{result.stderr}")
        input("按回车退出...")
        return
    else:
        print("✅ 变基成功，本地历史已更新。")

    # 推送（不带 --force）
    print("正在推送至远程仓库...")
    if not run(f"git push origin {BRANCH}"):
        print("❌ 推送失败，可能是远程有新的更新或网络问题。")
        input("按回车退出...")
        return

    print("\n✅ 完成！按回车退出...")
    input()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"异常: {e}")
        input("按回车退出...")