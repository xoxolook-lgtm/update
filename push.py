import os
import subprocess
import sys

# ====================== 【你只需要改这里】 ======================
APK_FILE = "blbl-v1.0.139-debug.apk"  # 你的APK文件名
COMMIT_MSG = "更新APK安装包"   # 提交信息
# =================================================================

def run_cmd(cmd):
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def main():
    print("🔨 开始一键推送 APK 到 Gitee...\n")

    # 检查文件是否存在
    if not os.path.exists(APK_FILE):
        print(f"❌ 错误：找不到 {APK_FILE}")
        input("按回车退出...")
        return

    # 1. 添加APK
    print("1. 添加 APK 文件...")
    ok, _ = run_cmd(f'git add "{APK_FILE}"')
    if not ok:
        print("❌ 添加失败")
        input("按回车退出...")
        return

    # 2. 提交
    print("2. 提交中...")
    ok, _ = run_cmd(f'git commit -m "{COMMIT_MSG}"')
    if not ok:
        print("❌ 提交失败（可能没有变化）")

    # 3. 推送（自动兼容 main / master 分支）
    print("3. 推送到 Gitee...")
    ok, out = run_cmd("git push origin main")
    if not ok:
        ok, out = run_cmd("git push origin master")
        if not ok:
            print("❌ 推送失败：", out)
            input("按回车退出...")
            return

    print("\n✅ 恭喜！APK 已成功推送到 Gitee！")
    input("按回车退出...")

if __name__ == "__main__":
    main()