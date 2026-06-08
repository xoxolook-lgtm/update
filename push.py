# -*- coding: utf-8 -*-
import os
import subprocess
import sys

def run(cmd, capture=False):
    """执行命令，可选捕获输出，返回 (成功标志, 输出字符串)"""
    print(f"\n▶ 执行: {cmd}")
    if capture:
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if proc.returncode != 0:
            print(f"❌ 命令失败: {cmd}")
            print(f"   错误信息: {proc.stderr.strip()}")
            return False, proc.stderr.strip()
        return True, proc.stdout.strip()
    else:
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
    print("2. 拉取远程 main 分支的最新代码（git fetch）")
    print("3. 自动合并远程分支（git merge）")
    print("   - 若 update.json 冲突，保留本地版本")
    print("4. 清除暂存区中的删除标记，避免误删远程文件")
    print("5. 添加变更文件（仅新增和修改，忽略删除）：")
    print("   - git add --ignore-removal .")
    print("   - git add -f update.json（强制覆盖）")
    print("6. 提交并推送（如果没有新变更则仅尝试推送已有提交）")
    print("7. 完成")
    print("-" * 50)
    
    # ===== 配置区 =====
    REMOTE_URL = "git@github.com:xoxolook-lgtm/update.git"
    BRANCH = "main"
    # =================

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"\n工作目录: {os.getcwd()}")

    print("\n1/6 设置远程仓库地址...")
    run(f"git remote set-url origin {REMOTE_URL}")

    print("\n2/6 拉取远程最新代码...")
    run(f"git fetch origin {BRANCH}")

    # 3. 合并远程分支（自动合并，若冲突则本地 update.json 优先）
    print("\n3/6 合并远程变更...")
    # 先尝试合并，不自动提交（以便冲突处理）
    success, out = run(f"git merge origin/{BRANCH} --no-commit", capture=True)
    if not success:
        # 合并失败，可能有冲突
        print("合并产生冲突，正在自动解决（保留本地 update.json）...")
        # 查看冲突文件列表
        ok, conflict_files = run("git diff --name-only --diff-filter=U", capture=True)
        if ok and conflict_files:
            conflict_list = conflict_files.splitlines()
            if "update.json" in conflict_list:
                print("  冲突文件 update.json 使用本地版本覆盖")
                run("git checkout --ours update.json")
                run("git add update.json")
            # 其他冲突文件（如果有）也保留本地版本
            other_conflicts = [f for f in conflict_list if f != "update.json"]
            if other_conflicts:
                print(f"  警告: 其他冲突文件 {other_conflicts} 保留本地版本")
                for f in other_conflicts:
                    run(f"git checkout --ours {f}")
                    run(f"git add {f}")
            # 完成合并提交
            run("git commit --no-edit")
        else:
            print("无法获取冲突文件列表，请手动处理后重试")
            input("按回车退出...")
            return
    else:
        # 合并成功，检查是否有变更需要提交（合并产生的变更）
        status_merge = subprocess.run("git diff --cached --quiet", shell=True)
        if status_merge.returncode != 0:
            run("git commit -m 'Merge remote changes'")
        else:
            print("  没有需要合并的内容")

    # 4. 清除暂存区中的删除标记（避免误删远程文件）
    print("\n4/6 清除暂存区中的删除标记...")
    run("git reset --mixed HEAD")

    # 5. 添加文件（忽略删除操作）
    print("\n5/6 添加变更文件（忽略删除）...")
    run("git add --ignore-removal .")
    if os.path.exists("update.json"):
        run("git add -f update.json")
    else:
        print("   ⚠️ update.json 不存在，跳过强制添加")

    # 6. 提交并推送
    print("\n6/6 提交并推送...")
    status = subprocess.run("git diff --cached --quiet", shell=True)
    if status.returncode != 0:
        run('git commit -m "auto update"')
        run(f"git push origin {BRANCH}")
    else:
        # 可能已有未推送的提交（例如合并产生的提交）
        run(f"git push origin {BRANCH}")

    print("\n✅ 完成！按回车退出...")
    input()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"异常: {e}")
        input("按回车退出...")