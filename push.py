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

    # ===== 配置区 =====
    REMOTE_URL = "git@github.com:xoxolook-lgtm/update.git"
    BRANCH = "main"
    # =================

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"工作目录: {os.getcwd()}")

    print("\n1/4 设置远程仓库地址...")
    run(f"git remote set-url origin {REMOTE_URL}")

    print("\n2/4 拉取远程最新代码...")
    run(f"git fetch origin {BRANCH}")

    print("\n3/4 添加文件...")
    run("git add -A")
    run("git add -f update.json")   # 强制更新

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