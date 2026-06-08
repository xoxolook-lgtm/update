import os
import subprocess

# ========== 请根据实际修改 ==========
TARGET_FILE = "blbl-v1.0.140-debug.apk"  # 你的APK文件名
COMMIT_MSG  = "更新APP安装包"
BRANCH      = "master"           # 当前分支固定为master
# ===================================

def run_cmd(cmd):
    try:
        subprocess.run(cmd, shell=True, check=True, encoding="utf-8")
        return True
    except subprocess.CalledProcessError:
        return False

if __name__ == "__main__":
    print("===== 开始推送 APK 到 Gitee =====")

    # 添加指定文件
    print(f"1. 添加文件: {TARGET_FILE}")
    run_cmd(f'git add "{TARGET_FILE}"')

    # 提交
    print("2. 提交变更")
    run_cmd(f'git commit -m "{COMMIT_MSG}"')

    # 推送到远程
    print(f"3. 推送到 {BRANCH} 分支")
    if run_cmd(f"git push origin {BRANCH}"):
        print("\n✅ 推送成功！")
    else:
        print("\n❌ 推送失败，请检查网络或文件状态")

    input("\n按回车键退出...")