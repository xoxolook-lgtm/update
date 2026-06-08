#!/usr/bin/env python3
import os
import subprocess
import sys

# ========== 配置区 ==========
APK_FILE = "blbl-v1.0.140-debug.apk"
UPDATE_JSON = "update.json"
BRANCH = "master"
# ===========================

def run_cmd(cmd, capture=False, check=True, cwd=None):
    """
    执行命令，默认实时输出到终端。
    如果 check=True 且命令失败，则退出脚本。
    返回 subprocess.CompletedProcess 对象。
    """
    print(f"\n[执行] {cmd}")
    if capture:
        # 捕获输出，用于检查状态
        proc = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if check and proc.returncode != 0:
            print(f"错误: {proc.stderr.strip()}")
            sys.exit(1)
        return proc
    else:
        # 实时输出到终端
        proc = subprocess.run(cmd, shell=True, cwd=cwd)
        if check and proc.returncode != 0:
            sys.exit(1)
        return proc

def file_in_remote_branch(filename, branch):
    """检查远程分支是否存在该文件"""
    proc = run_cmd(f"git ls-tree {branch} -- {filename}", capture=True, check=False)
    return proc.returncode == 0

def main():
    print("===== 强制更新工具（自动解决冲突，保留本地 update.json）=====")
    print(f"目标分支: {BRANCH}")
    print(f"update.json 强制更新: 本地版本优先")
    print(f"APK 策略: 仅当远程不存在时上传\n")

    # 1. 确保在正确的分支上
    run_cmd(f"git checkout {BRANCH}")

    # 2. 先获取远程最新信息（不自动合并）
    print("\n[1/6] 获取远程更新...")
    run_cmd(f"git fetch origin {BRANCH}")

    # 3. 检查本地是否有未推送的提交，以及远程是否有新提交
    local_commits = run_cmd(f"git rev-list HEAD..origin/{BRANCH} --count", capture=True, check=False)
    remote_behind = int(local_commits.stdout.strip()) if local_commits.stdout.strip().isdigit() else 0

    if remote_behind > 0:
        print(f"\n[2/6] 远程有 {remote_behind} 个新提交，尝试合并（保留本地 update.json）...")
        # 尝试合并，但出现冲突时自动使用本地版本
        merge_proc = run_cmd(f"git merge origin/{BRANCH} --no-commit", capture=True, check=False)
        if merge_proc.returncode != 0:
            # 合并失败，可能有冲突
            print("合并产生冲突，正在自动解决（始终保留本地 update.json）...")
            # 查看冲突文件
            conflict_check = run_cmd("git diff --name-only --diff-filter=U", capture=True)
            conflict_files = conflict_check.stdout.strip().splitlines()
            if UPDATE_JSON in conflict_files:
                print(f"  冲突文件 {UPDATE_JSON} 使用本地版本覆盖")
                run_cmd(f"git checkout --ours {UPDATE_JSON}")
                run_cmd(f"git add {UPDATE_JSON}")
            # 如果有其他冲突文件（例如 APK 可能未纳入版本控制，忽略），手动处理提示
            other_conflicts = [f for f in conflict_files if f != UPDATE_JSON]
            if other_conflicts:
                print(f"  警告: 其他冲突文件 {other_conflicts} 需要手动解决，脚本将保留本地版本（--ours）")
                for f in other_conflicts:
                    run_cmd(f"git checkout --ours {f}")
                    run_cmd(f"git add {f}")
            # 完成合并
            run_cmd("git commit --no-edit")
        else:
            # 合并成功但没有自动提交（因为 --no-commit），需要手动提交
            # 检查是否有更改需要提交
            status_proc = run_cmd("git diff --cached --quiet", capture=True, check=False)
            if status_proc.returncode != 0:
                run_cmd("git commit -m 'Merge remote changes, keep local update.json'")
            else:
                print("  没有需要合并的内容，跳过提交")
    else:
        print("\n[2/6] 本地分支已是最新，无需合并")

    # 4. 强制添加并提交 update.json（确保最新版本被记录）
    print("\n[3/6] 确保 update.json 内容为本地最新...")
    # 如果文件被忽略（.gitignore），使用 -f 强制添加
    run_cmd(f"git add -f {UPDATE_JSON}")
    # 检查是否有变更需要提交
    diff_proc = run_cmd("git diff --cached --quiet", capture=True, check=False)
    if diff_proc.returncode != 0:
        run_cmd(f'git commit -m "force update {UPDATE_JSON} to local version"')
        print("  update.json 已提交")
    else:
        print("  update.json 没有新的变更（可能内容和远程已一致）")

    # 5. 处理 APK 文件（同名不上传）
    print("\n[4/6] 检查 APK 文件...")
    if os.path.exists(APK_FILE):
        if not file_in_remote_branch(APK_FILE, f"origin/{BRANCH}"):
            print(f"  {APK_FILE} 为新增文件，添加到仓库")
            run_cmd(f"git add {APK_FILE}")
            # 检查是否已暂存
            apk_diff = run_cmd("git diff --cached --quiet -- APK_FILE", capture=True, check=False)
            if apk_diff.returncode != 0:
                run_cmd(f'git commit -m "add {APK_FILE}"')
            else:
                print(f"  {APK_FILE} 已暂存但无变化，跳过提交")
        else:
            print(f"  {APK_FILE} 远程已存在，跳过上传")
    else:
        print(f"  {APK_FILE} 不存在，跳过")

    # 6. 推送到远程
    print("\n[5/6] 推送到远程仓库...")
    push_proc = run_cmd(f"git push origin {BRANCH}", capture=True, check=False)
    if push_proc.returncode != 0:
        print(f"推送失败: {push_proc.stderr}")
        print("请手动检查冲突或执行 git pull")
        sys.exit(1)
    else:
        print("推送成功")

    # 7. 最终验证（可选）
    print("\n[6/6] 验证远程 update.json 版本...")
    verify = run_cmd(f"git show origin/{BRANCH}:{UPDATE_JSON} | grep versionName", capture=True, check=False)
    if verify.returncode == 0:
        print(f"远程现在包含: {verify.stdout.strip()}")
    else:
        print("无法验证，请手动检查 Gitee 页面")

    print("\n✅ 完成！update.json 已强制更新为本地版本。")
    input("按回车退出")

if __name__ == "__main__":
    main()