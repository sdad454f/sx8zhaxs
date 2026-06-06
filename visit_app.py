# 文件名: visit_app.py
from playwright.sync_api import sync_playwright
import time
import os

def get_urls_from_env():
    """
    从环境变量 URL_LIST 中读取 URL 列表。
    多个 URL 使用换行或逗号分隔。
    """
    raw = os.getenv("URL_LIST", "").strip()

    if not raw:
        print("❌ [错误] 环境变量 URL_LIST 未设置或为空。")
        return []

    # 支持换行或逗号分隔
    parts = raw.replace(",", "\n").split("\n")

    url_list = []
    for line in parts:
        clean = line.strip()
        if clean and not clean.startswith("#"):
            url_list.append(clean)

    return url_list


def run():
    # 1. 从环境变量读取 URL 列表
    target_urls = get_urls_from_env()

    if not target_urls:
        print("❌ 未找到任何 URL，程序结束。")
        return

    print(f"📋 已加载 {len(target_urls)} 个目标站点。\n")

    with sync_playwright() as p:
        # 启动浏览器（无头模式）
        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        )

        for idx, url in enumerate(target_urls, 1):
            print(f"--- [{idx}/{len(target_urls)}] 正在访问:  ---")

            page = context.new_page()

            try:
                # 打开页面
                page.goto(url, timeout=60000)

                print("页面加载中...（等待 15 秒）")
                page.wait_for_timeout(15000)

                # 检测 “Sleep Mode” 按钮
                try:
                    wake_btn = page.get_by_role("button", name="Yes, get this app back up")

                    if wake_btn.is_visible(timeout=5000):
                        print("🚨 检测到 Sleep Mode！正在点击唤醒按钮...")
                        wake_btn.click()
                        print("按钮已点击，等待应用恢复（40 秒）...")
                        page.wait_for_timeout(40000)
                    else:
                        print("✅ 应用已处于激活状态。")
                        page.wait_for_timeout(5000)

                except Exception:
                    print("未找到唤醒按钮，视为正常状态。")
                print(f"检查完成。\n")

            except Exception as e:
                print(f"❌ 访问 时发生错误: \n")

            finally:
                page.close()

        browser.close()
        print("所有任务已完成。")


if __name__ == "__main__":
    run()
