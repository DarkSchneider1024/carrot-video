"""
GPT-SoVITS WebUI 自動化操作錄影版 (Playwright)
==============================================
只截圖 + 錄影，不執行長時間等待的訓練步驟。
產出：一個完整操作流程的 WebM 影片 + 關鍵步驟截圖。
"""

import asyncio
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# --- 設定 ---
LOCALTUNNEL_URL = "https://curly-planes-read.loca.lt/"
LOCALTUNNEL_PASSWORD = "34.125.74.163"
DOC_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "北風與太陽", "doc"
)
VIDEO_DIR = os.path.join(DOC_DIR, "recordings")
MODEL_NAME = "lin_zhilin"
AUDIO_PATH = "/content/GPT-SoVITS/lin_zhilin_voice"


async def screenshot(page, name, desc=""):
    path = os.path.join(DOC_DIR, f"{name}.png")
    await page.screenshot(path=path, full_page=False)
    print(f"  [SCREENSHOT] {name}.png - {desc}")
    return path


async def click_tab(page, text, timeout=10000):
    try:
        tab = page.locator(f"button[role='tab']:has-text('{text}')").first
        await tab.wait_for(state="visible", timeout=timeout)
        await tab.click()
        print(f"  [OK] Tab: {text}")
        await asyncio.sleep(1.5)
        return True
    except Exception as e:
        print(f"  [WARN] Tab failed ({text}): {e}")
        return False


async def click_button(page, text, timeout=8000):
    try:
        btn = page.locator(f"button:has-text('{text}')").first
        await btn.wait_for(state="visible", timeout=timeout)
        await btn.scroll_into_view_if_needed()
        await asyncio.sleep(0.3)
        await btn.click()
        print(f"  [OK] Button: {text}")
        return True
    except Exception as e:
        print(f"  [WARN] Button failed ({text}): {e}")
        return False


async def fill_by_label(page, label, value, timeout=5000):
    try:
        el = page.locator(f"textarea[aria-label*='{label}'], input[aria-label*='{label}']").first
        await el.wait_for(state="visible", timeout=timeout)
        await el.click(click_count=3)
        await el.fill(value)
        print(f"  [OK] Fill '{label}' = '{value}'")
        return True
    except:
        pass
    try:
        label_el = page.locator(f"label:has-text('{label}'), span:has-text('{label}')").first
        await label_el.wait_for(state="visible", timeout=timeout)
        parent = label_el.locator("..")
        inp = parent.locator("input[type='text'], textarea").first
        await inp.click(click_count=3)
        await inp.fill(value)
        print(f"  [OK] Fill '{label}' = '{value}' (via label)")
        return True
    except Exception as e:
        print(f"  [WARN] Fill failed '{label}': {e}")
        return False


async def run():
    from playwright.async_api import async_playwright

    os.makedirs(DOC_DIR, exist_ok=True)
    os.makedirs(VIDEO_DIR, exist_ok=True)

    async with async_playwright() as p:
        # 啟動瀏覽器，開啟錄影功能
        browser = await p.chromium.launch(headless=False, slow_mo=400)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="zh-TW",
            record_video_dir=VIDEO_DIR,
            record_video_size={"width": 1920, "height": 1080}
        )
        page = await context.new_page()

        print("\n" + "=" * 60)
        print("Phase 0: Connect to WebUI")
        print("=" * 60)

        await page.goto(LOCALTUNNEL_URL, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)

        # Localtunnel 密碼處理
        content = await page.content()
        if "Friendly Reminder" in content:
            print("  [INFO] Localtunnel password page")
            await screenshot(page, "rec_step0_password", "Localtunnel 密碼頁")
            try:
                inp = page.locator("input[type='text']").first
                await inp.fill(LOCALTUNNEL_PASSWORD)
                btn = page.locator("button").first
                await btn.click()
            except:
                await page.keyboard.press("Enter")
            await asyncio.sleep(5)

        try:
            await page.wait_for_selector("text=GPT-SoVITS", timeout=15000)
            print("  [OK] WebUI loaded!")
        except:
            print("  [WARN] WebUI load timeout")

        await asyncio.sleep(2)
        await screenshot(page, "rec_step0_loaded", "WebUI 載入完成")

        # =================================================================
        # Step 1: 設定模型名稱
        # =================================================================
        print("\n" + "=" * 60)
        print("Step 1: Set model name")
        print("=" * 60)

        await click_tab(page, "1-GPT-SOVITS-TTS")
        await asyncio.sleep(2)
        await fill_by_label(page, "Experiment", MODEL_NAME)
        await asyncio.sleep(1)
        await screenshot(page, "rec_step1_model", "Model = lin_zhilin")

        # =================================================================
        # Step 2: 0-Fetch Datasets
        # =================================================================
        print("\n" + "=" * 60)
        print("Step 2: Fetch Datasets")
        print("=" * 60)

        await click_tab(page, "0-Fetch Datasets")
        await asyncio.sleep(2)
        await screenshot(page, "rec_step2a_overview", "Fetch Datasets 總覽")

        # 填入音訊路徑
        await fill_by_label(page, "Audio slicer input", AUDIO_PATH)
        await asyncio.sleep(1)
        await screenshot(page, "rec_step2b_path", "已填入音訊路徑")

        # 向下捲動展示完整頁面
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1.5)
        await screenshot(page, "rec_step2c_bottom", "頁面底部 ASR 區塊")

        # 捲回頂部
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)

        # =================================================================
        # Step 3: 1-GPT-SOVITS-TTS 子頁籤巡覽
        # =================================================================
        print("\n" + "=" * 60)
        print("Step 3: GPT-SoVITS TTS sub-tabs tour")
        print("=" * 60)

        await click_tab(page, "1-GPT-SOVITS-TTS")
        await asyncio.sleep(2)

        # 1A-Dataset Formatting Tool
        await click_tab(page, "1A-Dataset Formatting Tool")
        await asyncio.sleep(2)
        await screenshot(page, "rec_step3a_1A", "1A-Dataset Formatting")

        # 向下滾動展示 BERT / SSL / Semantics 區塊
        await page.evaluate("window.scrollBy(0, 500)")
        await asyncio.sleep(1.5)
        await screenshot(page, "rec_step3b_features", "特徵提取區塊")

        await page.evaluate("window.scrollBy(0, 500)")
        await asyncio.sleep(1.5)
        await screenshot(page, "rec_step3c_more", "更多特徵提取")

        # 1B-Fine-Tuning
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)
        await click_tab(page, "1B-Fine-Tuning")
        await asyncio.sleep(2)
        await screenshot(page, "rec_step3d_1B", "1B-Fine-Tuning 上半部")

        # 向下滾動展示 GPT Training
        await page.evaluate("window.scrollBy(0, 400)")
        await asyncio.sleep(1.5)
        await screenshot(page, "rec_step3e_gpt", "GPT Training 區塊")

        # 1C-Inference
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)
        await click_tab(page, "1C-Inference")
        await asyncio.sleep(2)
        await screenshot(page, "rec_step4_inference", "1C-Inference 推理")

        # 最後停留 2 秒讓影片有完整結尾
        await asyncio.sleep(2)

        print("\n" + "=" * 60)
        print("Done! Closing browser and saving video...")
        print("=" * 60)

        # 關閉 context 觸發影片儲存
        await context.close()
        await browser.close()

    # 列出產生的影片
    print(f"\nVideo directory: {VIDEO_DIR}")
    for f in os.listdir(VIDEO_DIR):
        fpath = os.path.join(VIDEO_DIR, f)
        size_mb = os.path.getsize(fpath) / (1024 * 1024)
        print(f"  {f} ({size_mb:.1f} MB)")

    return VIDEO_DIR


if __name__ == "__main__":
    video_dir = asyncio.run(run())
    print(f"\nVideo saved to: {video_dir}")
