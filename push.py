import os
import subprocess
import sys
import time

def run_cmd(cmd):
    print(f"\n▶ 执行: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"\n❌ 命令失败: {cmd}")
        return False
    return True

def main():
    os.system("title 推送到 GitHub —— 不闪退版")
    print("=" * 50)
    print("      GitHub 自动推送工具（稳定不闪退）")
    print("=" * 50)
    time.sleep(0.5)

    # ====================
    # 你的 GitHub 信息
    # ====================
    remote_url = "https://github.com/xoxolook-lgtm/update.git"
    branch = "master"

    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    except:
        pass

    # 1. 切换远程到 GitHub
    print("\n1/5 切换远程仓库到 GitHub...")
    if not run_cmd(f'git remote set-url origin {remote_url}'):
        input("\n出错！按回车退出")
        return

    # 2. 拉取最新（防止冲突）
    print("\n2/5 同步远程最新代码...")
    run_cmd(f'git pull origin {branch} --allow-unrelated-histories')

    # 3. 添加文件
    print("\n3/5 添加所有文件...")
    run_cmd("git add .")

    # 4. 提交
    print("\n4/5 提交更新...")
    run_cmd('git commit -m "update files"')

    # 5. 推送
    print("\n5/5 推送到 GitHub...")
    if run_cmd(f"git push origin {branch}"):
        print("\n✅ 推送成功！")
        print("🌍 访问地址：")
        print("https://xoxolook-lgtm.github.io/update/")
    else:
        print("\n❌ 推送失败！")

    # 不闪退！
    print("\n按回车键退出...")
    input()

if __name__ == "__main__":
    main()