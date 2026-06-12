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

def delete_all_apk_and_stage_removal():
    """
    递归删除当前目录下所有 .apk 文件，并使用 git rm 记录删除（如果文件被跟踪）
    """
    print("\n🗑️  正在删除所有 .apk 文件...")
    apk_files = glob.glob("**/*.apk", recursive=True)
    if not apk_files:
        print("   ⚠️ 未找到任何 .apk 文件，无需删除")
        return

    deleted_count = 0
    for file_path in apk_files:
        # 尝试用 git rm 删除（同时删除工作区和暂存区记录）
        # 如果文件未被跟踪，git rm 会失败，此时只物理删除文件
        result = subprocess.run(
            ["git", "rm", "--ignore-unmatch", "-f", file_path],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"   ✓ 已从 Git 删除并移除文件: {file_path}")
            deleted_count += 1
        else:
            # 文件可能未被跟踪，直接物理删除
            try:
                os.remove(file_path)
                print(f"   ✓ 已删除未跟踪的文件: {file_path}")
                deleted_count += 1
            except Exception as e:
                print(f"   ✗ 删除失败 {file_path}: {e}")

    print(f"✅ 共删除了 {deleted_count} 个 .apk 文件（Git 删除记录已暂存）")

def main():
    print("=" * 50)
    print("   GitHub 强制推送工具（以本地为准）")
    print("=" * 50)

    print("\n【更新逻辑说明】")
    print("1. 设置远程仓库地址为 SSH 格式")
    print("2. 不拉取远程代码（忽略远程领先情况）")
    print("3. 可选：删除所有 .apk 文件后再上传（远程也将被删除）")
    print("4. 添加变更文件（仅新增和修改，忽略删除，但 .apk 删除特殊处理）：")
    print("   - git add --ignore-removal .")
    print("   - git add -f update.json（强制覆盖）")
    print("5. 提交变更（如果有）")
    print("6. 强制推送到 GitHub（--force）")
    print("   ⚠️ 远程分支将被本地内容完全覆盖，远程独有的提交会丢失")
    print("   ✅ 除 .apk 外，本地删除的其他文件不会被推送删除（因为忽略删除操作）")
    print("-" * 50)

    # ===== 新增：询问是否删除所有 .apk 文件 =====
    while True:
        choice = input("\n🔧 是否删除所有 .apk 文件后再上传更新？\n   1 - 删除所有 .apk\n   2 - 跳过\n请选择 (1/2): ").strip()
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

    # 如果需要删除 apk，在 git 操作前执行
    if delete_apk:
        delete_all_apk_and_stage_removal()

    print("\n1/4 设置远程仓库地址...")
    run(f"git remote set-url origin {REMOTE_URL}")

    # 确保在正确的分支
    print("\n2/4 切换到 main 分支...")
    run(f"git checkout {BRANCH}")

    print("\n3/4 添加文件（忽略除 .apk 以外的删除）...")
    # 只添加新增和修改，忽略删除（但 .apk 的删除已在之前通过 git rm 暂存）
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
        run(f"git push --force origin {BRANCH}")
    else:
        # 无本地变更，但可能本地有未推送的提交（例如之前遗留的）
        print("\n4/4 尝试强制推送已有提交...")
        run(f"git push --force origin {BRANCH}")

    print("\n✅ 完成！按回车退出...")
    input()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"异常: {e}")
        input("按回车退出...")