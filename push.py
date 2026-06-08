# -*- coding: utf-8 -*-
import os
import subprocess
import sys

def run(cmd):
    print(f"\n▶ 执行: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ 命令失败: {cmd}")
        return False
    return True

def main():
    print("=" * 50)
    print("      GitHub 自动推送工具（SSH版）")
    print("=" * 50)
    
    # ========== 逻辑说明 ==========
    print("\n【更新逻辑说明】")
    print("1. 设置远程仓库地址为 SSH 格式")
    print("2. 拉取远程 main 分支的最新代码（避免冲突）")
    print("3. 添加变更文件（忽略删除操作）：")
    print("   - 执行 git add . （添加所有新增和修改的文件，不记录删除）")
    print("   - 执行 git add -f update.json（强制覆盖 update.json，即使被 .gitignore 忽略）")
    print("4. 检查暂存区是否有变更：")
    print("   - 如果有变更 → 提交（commit）并推送（push）到 GitHub")
    print("   - 如果没有变更 → 直接尝试推送（可能本地已有未推送的提交）")
    print("5. 提示完成，按回车退出")
    print("-" * 50)
    
    # ===== 配置区 =====
    REMOTE_URL = "git@github.com:xoxolook-lgtm/update.git"
    BRANCH = "main"
    # =================

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"\n工作目录: {os.getcwd()}")

    print("\n1/4 设置远程仓库地址...")
    run(f"git remote set-url origin {REMOTE_URL}")

    print("\n2/4 拉取远程最新代码...")
    run(f"git fetch origin {BRANCH}")

    print("\n3/4 添加文件...")
    # 使用 git add . 只添加新增和修改，忽略删除操作
    run("git add .")
    # 强制添加 update.json（如果文件存在）
    if os.path.exists("update.json"):
        run("git add -f update.json")
    else:
        print("   ⚠️ update.json 不存在，跳过强制添加")

    print("\n4/4 提交并推送...")
    # 检查是否有变更
    status = subprocess.run("git diff --cached --quiet", shell=True)
    if status.returncode != 0:
        run('git commit -m "auto update"')
        run(f"git push origin {BRANCH}")
    else:
        # 可能已有未推送的提交
        run(f"git push origin {BRANCH}")

    print("\n✅ 完成！按回车退出...")
    input()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"异常: {e}")
        input("按回车退出...")