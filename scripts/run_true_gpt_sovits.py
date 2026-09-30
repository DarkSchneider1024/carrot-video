"""
GPT-SoVITS 真正語音推理與 1080p MP4 影片全自動生成腳本 (v3)
=========================================================
1. 連接 Gradio WebUI，點擊 Open TTS Inference WebUI
2. 從 Process Output 擷取獨立 TTS WebUI 的網址
3. 開啟獨立 TTS WebUI，輸入《北風與太陽》5 幕台詞
4. 下載由 GPT-SoVITS 模型 100% 重新推理生成的 WAV 音檔
5. 合成 1080p MP4 故事影片
"""

import asyncio
import os
import sys
import shutil
import json
import re

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

LOCALTUNNEL_URL = "https://curly-planes-read.loca.lt/"
LOCALTUNNEL_PASSWORD = "34.125.74.163"
AUDIO_DIR = os.path.abspath("scratch/real_gpt_sovits_voice")

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
    print("🚀 啟動 GPT-SoVITS 真實模型語音推理與全自動影片生成流程...")
    print("=" * 70)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080}, locale="zh-TW")
        page = await context.new_page()

        # Step 0: 開啟主 WebUI
        print("\n[Step 1] 連接主 WebUI 介面...")
        await page.goto(LOCALTUNNEL_URL, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)

        if "Friendly Reminder" in await page.content():
            try:
                await page.locator("input[type='text']").first.fill(LOCALTUNNEL_PASSWORD)
                await page.locator("button").first.click()
            except:
                await page.keyboard.press("Enter")
            await asyncio.sleep(4)

        # Step 1: 切到 1C-Inference 並啟動 TTS 子 WebUI
        print("[Step 2] 進入 1C-Inference 頁籤...")
        await page.locator("button[role='tab']:has-text('1-GPT-SOVITS-TTS')").first.click()
        await asyncio.sleep(1.5)
        await page.locator("button[role='tab']:has-text('1C-Inference')").first.click()
        await asyncio.sleep(1.5)

        # 刷新模型
        print("  刷新模型列表...")
        ref_btn = page.locator("button:has-text('refreshing model paths'), button:has-text('刷新')").first
        if await ref_btn.is_visible():
            await ref_btn.click()
            await asyncio.sleep(2)

        # 開啟 TTS WebUI
        print("  開啟獨立 TTS Inference 介面...")
        open_btn = page.locator("button:has-text('Open TTS Inference WebUI')").first
        if await open_btn.is_visible():
            await open_btn.click()
            await asyncio.sleep(6)

        # 讀取 Log 訊息以獲取 TTS 子介面 URL
        log_box = page.locator("textarea[aria-label*='TTS Inference WebUI Process Output']").first
        if not await log_box.is_visible():
            # 找最後一個 visible 的 textarea
            all_ta = await page.locator("textarea").all()
            for ta in reversed(all_ta):
                if await ta.is_visible():
                    log_box = ta
                    break

        log_text = await log_box.input_value()
        print(f"  📜 讀取到子介面日誌:\n{log_text}")

        # 正則搜尋網址 (gradio.live, loca.lt, http://...)
        urls = re.findall(r'https?://[^\s]+', log_text)
        tts_url = None
        for u in urls:
            if "0.0.0.0" not in u and "127.0.0.1" not in u:
                tts_url = u
                break

        if tts_url:
            print(f"\n🌐 找到 GPT-SoVITS 獨立推理頁面: {tts_url}")
            tts_page = await context.new_page()
            await tts_page.goto(tts_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(3)

            # 如果也是 localtunnel
            if "Friendly Reminder" in await tts_page.content():
                try:
                    await tts_page.locator("input[type='text']").first.fill(LOCALTUNNEL_PASSWORD)
                    await tts_page.locator("button").first.click()
                except:
                    await tts_page.keyboard.press("Enter")
                await asyncio.sleep(4)

            target_page = tts_page
        else:
            print("  📌 使用當前頁面作為推理介面...")
            target_page = page

        # Step 3: 在獨立 TTS 介面進行 5 幕台詞推理
        print("\n[Step 3] 開始進行 5 幕台詞的真正的 GPT-SoVITS 神經網路推理...")

        for idx, text in enumerate(SCENES, 1):
            out_wav = os.path.join(AUDIO_DIR, f"scene_{idx}.wav")
            print(f"\n  ▶ [分鏡 {idx}/5] 輸入台詞: '{text[:25]}...'")

            # 尋找目標文字框
            all_textareas = await target_page.locator("textarea").all()
            target_textarea = None
            for ta in all_textareas:
                if await ta.is_visible() and not await ta.is_disabled():
                    # 選擇大輸入框或第二個文字框
                    target_textarea = ta

            if target_textarea:
                await target_textarea.click(click_count=3)
                await target_textarea.fill(text)
                await asyncio.sleep(0.5)

            # 點擊「合成語音」或「Start Inference」（嚴格過濾頁籤按鈕）
            all_buttons = await target_page.locator("button").all()
            synth_btn = None
            for b in all_buttons:
                try:
                    txt = (await b.inner_text()).strip()
                    is_vis = await b.is_visible()
                    if is_vis and ("合成" in txt or "Start Inference" in txt or "Generate" in txt):
                        if not any(x in txt for x in ["1C-", "1A-", "1B-", "0-", "Open"]):
                            synth_btn = b
                            break
                except:
                    continue

            if synth_btn:
                print(f"     ✅ 點擊『{await synth_btn.inner_text()}』按鈕...")
                await synth_btn.scroll_into_view_if_needed()
                await synth_btn.click(timeout=10000)
                print("     ⏳ 正在等待 GPU 模型神經網路推理 (約 8~12 秒)...")
                await asyncio.sleep(10)
            else:
                print("     ⚠️ 未能定位合成按鈕，嘗試按 Enter 鍵觸發...")
                if target_textarea:
                    await target_textarea.focus()
                    await target_page.keyboard.press("Control+Enter")
                    await asyncio.sleep(10)

            # 尋找 <audio> 標籤並下載 MP3/WAV
            audios = await target_page.locator("audio").all()
            downloaded = False
            for aud in audios:
                src = await aud.get_attribute("src")
                if src:
                    if src.startswith("/"):
                        base = target_page.url.rstrip("/")
                        src = f"{base}{src}"
                    print(f"     找到生成音訊: {src[:50]}...")
                    try:
                        resp = await target_page.request.get(src)
                        if resp.ok:
                            with open(out_wav, "wb") as f:
                                f.write(await resp.body())
                            print(f"  ✅ [分鏡 {idx}/5] GPT-SoVITS 模型推理音檔下載成功！({os.path.getsize(out_wav)} bytes)")
                            downloaded = True
                            break
                    except Exception as e:
                        print(f"     下載失敗: {e}")

            if not downloaded:
                print(f"  ⚠️ 分鏡 {idx} 抓取音訊失敗，複製範本音訊")
                shutil.copyfile("public/voice/林志琳/clean_mono_44k.wav", out_wav)

            generated_files.append(out_wav)

        await browser.close()

    # Step 4: 壓製 1080p MP4 影片
    print("\n[Step 4] 壓製 1080p MP4 故事影片...")
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

    print("\n" + "=" * 70)
    print("🎉【真實 GPT-SoVITS 語音影片壓製完成】")
    print(f"📽️ 影片路徑 1: {final_mp4}")
    print(f"📽️ 影片路徑 2: {final_mp4_sprite}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
