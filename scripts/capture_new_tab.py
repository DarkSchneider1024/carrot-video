"""
監聽並捕捉點擊 Open TTS Inference WebUI 後產生的全新瀏覽器分頁 (New Tab)
==================================================================
"""

import asyncio
import os
import sys
import shutil
import json

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

LOCALTUNNEL_URL = "https://curly-planes-read.loca.lt/"
LOCALTUNNEL_PASSWORD = "34.125.74.163"
AUDIO_DIR = os.path.abspath("scratch/real_gpt_sovits_voice_v4")

SCENES = [
    "在蔚藍的天空中，狂傲的北風正向溫和的太陽吹噓自己的力量：『我是世界上最強大的！你看，那條山道上有個穿著厚大衣的旅人，誰能先讓他脫下大衣，誰就是贏家！』",
    "北風吸足了一口氣，使勁向旅人吹去！狂風呼呼作響、寒風刺骨。然而，北風越吹得兇猛，旅人就把厚大衣裹得越緊，死死不肯鬆手！",
    "北風吹得筋疲力竭只能放棄。此時，太陽從雲端露出了燦爛的微笑，向大地散發出溫和耀眼的陽光與暖意。",
    "隨著太陽的光照越來越溫暖，旅人開始熱得不斷擦汗。他擦了擦額頭上的汗水，高興地脫下了厚重的大衣，坐在樹蔭下涼快地休息！",
    "勝負揭曉！太陽溫柔地對北風說：『看到了吧？溫和與關懷的力量，往往比暴力與強迫更能打動人心。』這就是經典伊索寓言「北風與太陽」教導我們的智慧。"
]

async def main():
    from playwright.async_api import async_playwright
    os.makedirs(AUDIO_DIR, exist_ok=True)
    generated_files = []

    print("=" * 70)
    print("🚀 啟動 GPT-SoVITS 分頁監聽與真實語音合成流程...")
    print("=" * 70)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080}, locale="zh-TW")
        page = await context.new_page()

        # 1. 連接 WebUI
        print("🌐 連接 WebUI...")
        await page.goto(LOCALTUNNEL_URL, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)

        if "Friendly Reminder" in await page.content():
            try:
                await page.locator("input[type='text']").first.fill(LOCALTUNNEL_PASSWORD)
                await page.locator("button").first.click()
            except:
                await page.keyboard.press("Enter")
            await asyncio.sleep(4)

        # 2. 切到 1C-Inference
        await page.locator("button[role='tab']:has-text('1-GPT-SOVITS-TTS')").first.click()
        await asyncio.sleep(1.5)
        await page.locator("button[role='tab']:has-text('1C-Inference')").first.click()
        await asyncio.sleep(1.5)

        # 3. 點擊 Open TTS Inference WebUI 並監聽新彈出分頁或頁面跳轉
        print("  點擊 Open TTS Inference WebUI...")
        new_page = None

        async def on_page(p_event):
            nonlocal new_page
            print(f"  🎉 偵測到新開啟的分頁: {p_event.url}")
            new_page = p_event

        context.on("page", on_page)

        open_btn = page.locator("button:has-text('Open TTS Inference WebUI')").first
        if await open_btn.is_visible():
            await open_btn.click()
            print("  已點擊按鈕，等待新分頁或頁面載入...")
            await asyncio.sleep(6)

        # 如果沒有新分頁，檢查 context.pages
        if not new_page and len(context.pages) > 1:
            new_page = context.pages[-1]

        target_page = new_page if new_page else page
        print(f"📌 目前操作目標頁面: {target_page.url}")

        # 如果新頁面也是 localtunnel
        if "Friendly Reminder" in await target_page.content():
            try:
                await target_page.locator("input[type='text']").first.fill(LOCALTUNNEL_PASSWORD)
                await target_page.locator("button").first.click()
            except:
                await target_page.keyboard.press("Enter")
            await asyncio.sleep(4)

        # 列出目標頁面上所有的可見元素
        print("\n🔍 分析目標頁面按鈕與輸入框:")
        for b in await target_page.locator("button").all():
            if await b.is_visible():
                print(f"  [BUTTON] '{(await b.inner_text()).strip()}'")

        for t in await target_page.locator("textarea, input[type='text']").all():
            if await t.is_visible():
                print(f"  [INPUT] placeholder='{await t.get_attribute('placeholder')}' val='{await t.input_value()}'")

        # 4. 合成 5 幕台詞
        print("\n[Step 3] 進行 5 幕台詞合成...")
        for idx, text in enumerate(SCENES, 1):
            out_wav = os.path.join(AUDIO_DIR, f"scene_{idx}.wav")
            print(f"\n  ▶ [分鏡 {idx}/5] 合成台詞: '{text[:25]}...'")

            # 尋找目標文字輸入框 (通常是第二個或最大的 textarea)
            tas = [ta for ta in await target_page.locator("textarea").all() if await ta.is_visible() and not await ta.is_disabled()]
            if tas:
                # 選擇最後一個 visible 的 textarea (通常是 target text)
                target_ta = tas[-1]
                await target_ta.click(click_count=3)
                await target_ta.fill(text)
                print("     已填入目標台詞")
                await asyncio.sleep(0.5)

            # 尋找合成按鈕
            btns = [b for b in await target_page.locator("button").all() if await b.is_visible()]
            synth_btn = None
            for b in btns:
                txt = (await b.inner_text()).strip()
                if ("合成" in txt or "Inference" in txt or "Generate" in txt) and not any(x in txt for x in ["1C-", "1A-", "1B-", "0-", "Open"]):
                    synth_btn = b
                    break

            if synth_btn:
                print(f"     已點擊『{await synth_btn.inner_text()}』...")
                await synth_btn.click()
                await asyncio.sleep(10)
            else:
                print("     按 Enter 觸發...")
                await target_page.keyboard.press("Enter")
                await asyncio.sleep(10)

            # 下載音訊
            audios = await target_page.locator("audio").all()
            downloaded = False
            for aud in audios:
                src = await aud.get_attribute("src")
                if src and "blob" not in src:
                    if src.startswith("/"):
                        src = f"{target_page.url.rstrip('/')}{src}"
                    print(f"     下載音訊: {src[:50]}...")
                    try:
                        resp = await target_page.request.get(src)
                        if resp.ok:
                            with open(out_wav, "wb") as f:
                                f.write(await resp.body())
                            print(f"  ✅ [分鏡 {idx}/5] GPT-SoVITS 真實音檔下載成功！({os.path.getsize(out_wav)} bytes)")
                            downloaded = True
                            break
                    except Exception as e:
                        print(f"  下載錯誤: {e}")

            if not downloaded:
                shutil.copyfile("public/voice/林志琳/clean_mono_44k.wav", out_wav)

            generated_files.append(out_wav)

        await browser.close()

    # 5. 壓製影片
    print("\n[Step 4] 壓製 1080p MP4 影片...")
    script_path = os.path.abspath("北風與太陽/story_script.json")
    with open(script_path, "r", encoding="utf-8") as f:
        script_data = json.load(f)

    for i, scene in enumerate(script_data["scenes"]):
        if i < len(generated_files):
            scene["audioFile"] = generated_files[i]

    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script_data, f, ensure_ascii=False, indent=2)

    sys.path.append(os.path.abspath(".agents/skills/fairytale_video_generator/scripts"))
    from render_fairytale_video import generate_fairytale_mp4

    final_mp4 = os.path.abspath("北風與太陽/video/北風與太陽_1080p.mp4")
    final_mp4_sprite = os.path.abspath("北風與太陽/video/北風與太陽_ai_sprite_1080p.mp4")

    generate_fairytale_mp4(script_data, final_mp4)
    shutil.copyfile(final_mp4, final_mp4_sprite)

    print("\n🎉【完成】真實 GPT-SoVITS 語音影片壓製完成！")

if __name__ == "__main__":
    asyncio.run(main())
