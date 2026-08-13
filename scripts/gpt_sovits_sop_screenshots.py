"""
GPT-SoVITS WebUI 自動化操作 + SOP 截圖腳本 v2 (Playwright)
==========================================================
修正版：正確處理 Gradio 巢狀頁籤結構與輸入框定位。
"""

import asyncio
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# --- 設定 ---
LOCALTUNNEL_URL = "https://curly-planes-read.loca.lt/"
LOCALTUNNEL_PASSWORD = "34.125.74.163"
SCREENSHOT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "北風與太陽", "doc"
)
MODEL_NAME = "lin_zhilin"
AUDIO_DATASET_PATH = "/content/GPT-SoVITS/lin_zhilin_voice"

STEP_WAIT_SHORT = 2
STEP_WAIT_MEDIUM = 5
STEP_WAIT_LONG = 60
STEP_WAIT_TRAIN = 180


async def screenshot(page, name, desc=""):
    path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    await page.screenshot(path=path, full_page=False)
    print(f"  [SCREENSHOT] {name}.png - {desc}")
    return path


async def click_tab(page, text, timeout=10000):
    """點擊 Gradio 頁籤 (role=tab 的 button)"""
    try:
        tab = page.locator(f"button[role='tab']:has-text('{text}')").first
        await tab.wait_for(state="visible", timeout=timeout)
        await tab.click()
        print(f"  [OK] Tab clicked: {text}")
        await asyncio.sleep(1.5)
        return True
    except Exception as e:
        print(f"  [WARN] Tab click failed ({text}): {e}")
        return False


async def click_button(page, text, timeout=10000):
    """點擊一般按鈕"""
    try:
        btn = page.locator(f"button:has-text('{text}')").first
        await btn.wait_for(state="visible", timeout=timeout)
        await btn.scroll_into_view_if_needed()
        await asyncio.sleep(0.3)
        await btn.click()
        print(f"  [OK] Button clicked: {text}")
        return True
    except Exception as e:
        print(f"  [WARN] Button click failed ({text}): {e}")
        return False


async def fill_input_by_label(page, label_text, value, timeout=5000):
    """透過 label 文字找到對應的輸入框並填入值"""
    try:
        # 方法 1: Gradio textarea/input with aria-label
        el = page.locator(f"textarea[aria-label*='{label_text}'], input[aria-label*='{label_text}']").first
        await el.wait_for(state="visible", timeout=timeout)
        await el.click(click_count=3)
        await el.fill(value)
        print(f"  [OK] Filled '{label_text}' with '{value}'")
        return True
    except:
        pass

    try:
        # 方法 2: 找 label 元素，再找同層級/下一個 input/textarea
        label = page.locator(f"label:has-text('{label_text}'), span:has-text('{label_text}')").first
        await label.wait_for(state="visible", timeout=timeout)
        # Gradio 結構: label 和 input 在同一個 parent div 裡
        parent = label.locator("..")
        inp = parent.locator("input[type='text'], textarea").first
        await inp.click(click_count=3)
        await inp.fill(value)
        print(f"  [OK] Filled '{label_text}' with '{value}' (via label)")
        return True
    except:
        pass

    try:
        # 方法 3: 用 placeholder 文字
        el = page.locator(f"input[placeholder*='{label_text}'], textarea[placeholder*='{label_text}']").first
        await el.wait_for(state="visible", timeout=timeout)
        await el.click(click_count=3)
        await el.fill(value)
        print(f"  [OK] Filled '{label_text}' with '{value}' (via placeholder)")
        return True
    except Exception as e:
        print(f"  [WARN] Fill failed for '{label_text}': {e}")
        return False


async def wait_log(seconds, msg):
    print(f"  [WAIT] {msg} ({seconds}s)...")
    await asyncio.sleep(seconds)


async def debug_page_structure(page, context=""):
    """列出頁面上所有可見的 tab buttons 與 buttons，用於除錯"""
    print(f"\n  [DEBUG] Page structure ({context}):")
    
    # 列出所有 tab
    tabs = page.locator("button[role='tab']")
    tab_count = await tabs.count()
    print(f"    Tabs ({tab_count}):")
    for i in range(tab_count):
        tab = tabs.nth(i)
        text = await tab.inner_text()
        selected = await tab.get_attribute("aria-selected")
        visible = await tab.is_visible()
        print(f"      [{i}] '{text.strip()}' selected={selected} visible={visible}")

    # 列出可見的按鈕 (前 20 個)
    buttons = page.locator("button:not([role='tab'])")
    btn_count = await buttons.count()
    print(f"    Buttons ({btn_count}, showing first 20):")
    for i in range(min(btn_count, 20)):
        btn = buttons.nth(i)
        try:
            text = await btn.inner_text()
            visible = await btn.is_visible()
            if visible and text.strip():
                print(f"      [{i}] '{text.strip()[:60]}'")
        except:
            pass
    print()


async def run():
    from playwright.async_api import async_playwright

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    shots = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=200)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="zh-TW"
        )
        page = await context.new_page()

        # =================================================================
        # Phase 0: Localtunnel 密碼驗證
        # =================================================================
        print("\n" + "=" * 60)
        print("Phase 0: Localtunnel")
        print("=" * 60)

        await page.goto(LOCALTUNNEL_URL, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(STEP_WAIT_SHORT)

        content = await page.content()
        if "Friendly Reminder" in content or "loca.lt" in await page.title():
            print("  [INFO] Localtunnel password page detected")
            shots.append(await screenshot(page, "step0a_localtunnel", "Localtunnel 密碼驗證頁"))

            try:
                inp = page.locator("input[type='text']").first
                await inp.fill(LOCALTUNNEL_PASSWORD)
                btn = page.locator("button").first
                await btn.click()
                print("  [OK] Password submitted")
            except:
                await page.keyboard.press("Enter")
            await asyncio.sleep(STEP_WAIT_MEDIUM)

        try:
            await page.wait_for_selector("text=GPT-SoVITS", timeout=15000)
            print("  [OK] WebUI loaded!")
        except:
            print("  [WARN] WebUI load timeout, continuing...")

        await asyncio.sleep(STEP_WAIT_SHORT)
        shots.append(await screenshot(page, "step0b_webui_loaded", "GPT-SoVITS WebUI 主畫面"))

        # 偵測頁面結構
        await debug_page_structure(page, "initial load")

        # =================================================================
        # Step 1: 設定模型名稱
        # =================================================================
        print("=" * 60)
        print("Step 1: Set model name")
        print("=" * 60)

        # 先切到 1-GPT-SOVITS-TTS 頁籤，因為模型名稱在那裡
        await click_tab(page, "1-GPT-SOVITS-TTS")
        await asyncio.sleep(STEP_WAIT_SHORT)

        # 偵測子頁籤結構
        await debug_page_structure(page, "after clicking 1-GPT-SOVITS-TTS")

        # 嘗試用多種方式找到模型名稱輸入框
        filled = False
        # 先嘗試 aria-label
        filled = await fill_input_by_label(page, "Experiment", MODEL_NAME)
        if not filled:
            filled = await fill_input_by_label(page, "model name", MODEL_NAME)
        if not filled:
            # 備用：找第一個值為 "xxx" 的 input
            all_inputs = page.locator("input[type='text'], input:not([type]), textarea")
            count = await all_inputs.count()
            print(f"  [DEBUG] Found {count} text inputs")
            for i in range(min(count, 10)):
                inp = all_inputs.nth(i)
                try:
                    val = await inp.input_value()
                    visible = await inp.is_visible()
                    print(f"    [{i}] value='{val}' visible={visible}")
                    if visible and val == "xxx":
                        await inp.click(click_count=3)
                        await inp.fill(MODEL_NAME)
                        filled = True
                        print(f"  [OK] Model name set to '{MODEL_NAME}' (via xxx fallback)")
                        break
                except:
                    pass

        await asyncio.sleep(STEP_WAIT_SHORT)
        shots.append(await screenshot(page, "step1_model_name_set", f"Model name = {MODEL_NAME}"))

        # =================================================================
        # Step 2: 0-Fetch Datasets (切片 + ASR)
        # =================================================================
        print("\n" + "=" * 60)
        print("Step 2: Fetch Datasets (Slice + ASR)")
        print("=" * 60)

        await click_tab(page, "0-Fetch Datasets")
        await asyncio.sleep(STEP_WAIT_SHORT)

        # 完整頁面截圖（含所有 section）
        shots.append(await screenshot(page, "step2a_overview", "0-Fetch Datasets 全覽"))

        # 嘗試填入音訊路徑到 0b 的 input
        await fill_input_by_label(page, "Audio slicer input", AUDIO_DATASET_PATH)
        if not await fill_input_by_label(page, "slicer input", AUDIO_DATASET_PATH, timeout=2000):
            # 嘗試 Input folder path (0c 的路徑)
            await fill_input_by_label(page, "Input folder path", AUDIO_DATASET_PATH, timeout=2000)

        await asyncio.sleep(1)
        shots.append(await screenshot(page, "step2b_path_filled", "已填入音訊路徑"))

        # --- 0b: Open Speech Slicing ---
        print("\n  --- 0b: Speech Slicing ---")
        slice_ok = await click_button(page, "Open Speech Slicing")
        if slice_ok:
            shots.append(await screenshot(page, "step2c_slice_clicked", "已點擊 Open Speech Slicing"))
            await wait_log(STEP_WAIT_LONG, "Waiting for slicing")
            shots.append(await screenshot(page, "step2d_slice_done", "切片完成"))

        # --- 0c: Open Speech Recognition ---
        print("\n  --- 0c: Speech Recognition (ASR) ---")
        asr_ok = await click_button(page, "Open Speech Recognition")
        if asr_ok:
            shots.append(await screenshot(page, "step2e_asr_clicked", "已點擊 Open Speech Recognition"))
            await wait_log(STEP_WAIT_LONG, "Waiting for ASR")
            shots.append(await screenshot(page, "step2f_asr_done", "ASR 完成"))

        # =================================================================
        # Step 3: 1-GPT-SOVITS-TTS > 子頁籤
        # =================================================================
        print("\n" + "=" * 60)
        print("Step 3: GPT-SoVITS Training Pipeline")
        print("=" * 60)

        # 回到 1-GPT-SOVITS-TTS 主頁籤
        await click_tab(page, "1-GPT-SOVITS-TTS")
        await asyncio.sleep(STEP_WAIT_SHORT)

        # --- 3A: 1A-Dataset Formatting Tool ---
        print("\n  --- 1A: Dataset Formatting ---")
        if await click_tab(page, "1A-Dataset Formatting Tool"):
            shots.append(await screenshot(page, "step3a_1A_formatting", "1A-Dataset Formatting Tool"))

            # 1Aa
            if await click_button(page, "1Aa-Tokenization"):
                shots.append(await screenshot(page, "step3b_1Aa_clicked", "1Aa Tokenization 執行中"))
                await wait_log(STEP_WAIT_LONG, "Waiting for BERT extraction")
                shots.append(await screenshot(page, "step3c_1Aa_done", "1Aa Tokenization 完成"))

            # 1Ab
            if await click_button(page, "1Ab-SoVITS"):
                shots.append(await screenshot(page, "step3d_1Ab_clicked", "1Ab SoVITS Feature 執行中"))
                await wait_log(STEP_WAIT_LONG, "Waiting for SoVITS feature extraction")
                shots.append(await screenshot(page, "step3e_1Ab_done", "1Ab SoVITS Feature 完成"))

        # --- 3B: 1B-Fine-Tuning ---
        print("\n  --- 1B: Fine-Tuning ---")
        if await click_tab(page, "1B-Fine-Tuning"):
            shots.append(await screenshot(page, "step3f_1B_finetuning", "1B-Fine-Tuning 頁籤"))

            await debug_page_structure(page, "1B Fine-Tuning tab")

            # SoVITS Training
            if await click_button(page, "Start SoVITS Training"):
                shots.append(await screenshot(page, "step3g_sovits_started", "SoVITS 訓練開始"))
                await wait_log(STEP_WAIT_TRAIN, "Waiting for SoVITS training")
                shots.append(await screenshot(page, "step3h_sovits_done", "SoVITS 訓練完成"))

            # GPT Training
            if await click_button(page, "Start GPT Training"):
                shots.append(await screenshot(page, "step3i_gpt_started", "GPT 訓練開始"))
                await wait_log(STEP_WAIT_TRAIN, "Waiting for GPT training")
                shots.append(await screenshot(page, "step3j_gpt_done", "GPT 訓練完成"))

        # --- 3C: 1C-Inference ---
        print("\n  --- 1C: Inference ---")
        if await click_tab(page, "1C-Inference"):
            shots.append(await screenshot(page, "step4a_1C_inference", "1C-Inference 頁籤"))

            await click_button(page, "Refresh")
            await asyncio.sleep(STEP_WAIT_MEDIUM)
            shots.append(await screenshot(page, "step4b_model_refreshed", "模型列表已重新整理"))

            await click_button(page, "Open TTS Inference WebUI")
            await asyncio.sleep(STEP_WAIT_MEDIUM)
            shots.append(await screenshot(page, "step4c_tts_opened", "TTS 推理介面已開啟"))

        # =================================================================
        # Done
        # =================================================================
        print("\n" + "=" * 60)
        print(f"Done! {len(shots)} screenshots saved to {SCREENSHOT_DIR}")
        print("=" * 60)
        for i, s in enumerate(shots):
            print(f"  {i+1}. {os.path.basename(s)}")

        await browser.close()

    return shots


if __name__ == "__main__":
    shots = asyncio.run(run())
    print(f"\nTotal: {len(shots)} screenshots saved.")
