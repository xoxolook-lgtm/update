import os
import subprocess
import sys

def run_cmd(cmd):
    print(f"执行: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"命令执行失败: {cmd}")
        sys.exit(1)
    return result

def main():
    print("========================================")
    print(" GitHub 自动推送工具（已适配你的仓库）")
    print("========================================")

    # ======================
    # 已自动配置你的 GitHub
    # ======================
    remote_url = "https://github.com/xoxolook-lgtm/update.git"
    branch = "master"

    # 切换到当前脚本目录
    script_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_path)

    # 1. 设置远程仓库为 GitHub
    print("\n==> 切换远程仓库到 GitHub...")
    run_cmd(f'git remote set-url origin {remote_url}')

    # 2. 添加所有文件
    print("\n==> 添加文件...")
    run_cmd("git add .")

    # 3. 提交
    print("\n==> 提交更新...")
    run_cmd('git commit -m "自动更新"')

    # 4. 推送到 GitHub
    print("\n==> 推送到 GitHub...")
    run_cmd(f"git push origin {branch}")

    print("\n✅ 推送成功！已上传到 GitHub！")
    print("访问你的 Pages 地址：")
    print(f"https://xoxolook-lgtm.github.io/update/")

if __name__ == "__main__":
    main()