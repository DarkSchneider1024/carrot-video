"""
GPT-SoVITS 真正 TTS 合成介面除錯與自動合成腳本
===================================================
1. 開啟 WebUI 1C-Inference
2. 選擇 lin_zhilin 模型並開啟 TTS Inference 介面
3. 深入定位真正的「目標文字框」與「合成語音按鈕」
4. 自動生成 5 幕全新的 GPT-SoVITS 語音檔並下載
"""

import asyncio
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

LOCALTUNNEL_URL = "https://curly-planes-read.loca.lt/"
LOCALTUNNEL_PASSWORD = "34.125.74.163"

async def debug_tts():
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080}, locale="zh-TW")
        page = await context.new_page()

        print("🌐 連接 WebUI...")
        await page.goto(LOCALTUNNEL_URL, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)

        content = await page.content()
        if "Friendly Reminder" in content:
            print("🔑 Localtunnel 密碼...")
            try:
                inp = page.locator("input[type='text']").first
                await inp.fill(LOCALTUNNEL_PASSWORD)
                btn = page.locator("button").first
                await btn.click()
            except:
                await page.keyboard.press("Enter")
            await asyncio.sleep(4)

        # 切到 1-GPT-SOVITS-TTS -> 1C-Inference
        print("切換到 1C-Inference...")
        tab1 = page.locator("button[role='tab']:has-text('1-GPT-SOVITS-TTS')").first
        await tab1.click()
        await asyncio.sleep(1.5)

        tab1c = page.locator("button[role='tab']:has-text('1C-Inference')").first
        await tab1c.click()
        await asyncio.sleep(1.5)

        # 刷新模型列表
        refresh_btn = page.locator("button:has-text('refreshing model paths'), button:has-text('刷新')").first
        if await refresh_btn.is_visible():
            await refresh_btn.click()
            print("已點擊刷新模型列表...")
            await asyncio.sleep(2)

        # 點擊 Open TTS Inference WebUI
        open_btn = page.locator("button:has-text('Open TTS Inference WebUI')").first
        if await open_btn.is_visible():
            await open_btn.click()
            print("已點擊 Open TTS Inference WebUI，等待介面開啟...")
            await asyncio.sleep(5)

        # 印出開啟後的 DOM 結構
        print("\n🔍 搜尋頁面上所有可用的按鈕、文字框與音訊元件...")
        
        textareas = await page.locator("textarea").all()
        print(f"找到 {len(textareas)} 個 textarea:")
        for i, ta in enumerate(textareas):
            try:
                vis = await ta.is_visible()
                dis = await ta.is_disabled()
                placeholder = await ta.get_attribute("placeholder") or ""
                label = await ta.get_attribute("aria-label") or ""
                val = await ta.input_value()
                print(f"  [{i}] visible={vis} disabled={dis} label='{label}' placeholder='{placeholder}' val='{val[:20]}'")
            except Exception as e:
                print(f"  [{i}] error: {e}")

        buttons = page.locator("button").all()
        print(f"\n找到 {len(await buttons)} 個 button (前 30 個):")
        for i, b in enumerate((await buttons)[:30]):
            try:
                vis = await b.is_visible()
                txt = await b.inner_text()
                if vis and txt.strip():
                    print(f"  [{i}] '{txt.strip()[:40]}'")
            except:
                pass

        await asyncio.sleep(5)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_tts())
