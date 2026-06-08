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
    print("   GitHub 强制推送工具（以本地为准）")
    print("=" * 50)
    
    print("\n【更新逻辑说明】")
    print("1. 设置远程仓库地址为 SSH 格式")
    print("2. 不拉取远程代码（忽略远程领先情况）")
    print("3. 添加变更文件（仅新增和修改，忽略删除）：")
    print("   - git add --ignore-removal .")
    print("   - git add -f update.json（强制覆盖）")
    print("4. 提交变更（如果有）")
    print("5. 强制推送到 GitHub（--force-with-lease）")
    print("   ⚠️ 远程分支将被本地内容完全覆盖，远程独有的提交会丢失")
    print("   ✅ 本地删除的文件不会被推送删除（因为忽略删除操作）")
    print("-" * 50)
    
    # ===== 配置区 =====
    REMOTE_URL = "git@github.com:xoxolook-lgtm/update.git"
    BRANCH = "main"
    # =================

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"\n工作目录: {os.getcwd()}")

    print("\n1/4 设置远程仓库地址...")
    run(f"git remote set-url origin {REMOTE_URL}")

    # 确保在正确的分支
    print("\n2/4 切换到 main 分支...")
    run(f"git checkout {BRANCH}")

    print("\n3/4 添加文件（忽略删除）...")
    # 只添加新增和修改，忽略删除
    run("git add --ignore-removal .")
    if os.path.exists("update.json"):
        run("git add -f update.json")
    else:
        print("   ⚠️ update.json 不存在，跳过强制添加")

    # 检查是否有变更需要提交
    status = subprocess.run("git diff --cached --quiet", shell=True)
    if status.returncode != 0:
        print("\n4/4 提交并强制推送...")
        run('git commit -m "force update from local"')
        # 使用 --force-with-lease 更安全（如果远程有未预期的更新会拒绝）
        run(f"git push --force-with-lease origin {BRANCH}")
    else:
        # 无本地变更，但可能本地有未推送的提交（例如之前遗留的）
        print("\n4/4 尝试强制推送已有提交...")
        run(f"git push --force-with-lease origin {BRANCH}")

    print("\n✅ 完成！按回车退出...")
    input()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"异常: {e}")
        input("按回车退出...")