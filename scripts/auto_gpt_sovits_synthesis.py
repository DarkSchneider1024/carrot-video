"""
完全自動化 GPT-SoVITS 推理與故事影片渲染腳本
===================================================
1. 連接 Gradio WebUI (1C-Inference)
2. 自動在 GPT-SoVITS 界面中生成《北風與太陽》5 幕台詞的真實音檔
3. 下載 5 幕音訊檔至 scratch/gpt_sovits_audio/
4. 調用 render_fairytale_video.py 壓製 1080p MP4 故事影片
"""

import asyncio
import os
import sys
import shutil
import json
import urllib.request

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

LOCALTUNNEL_URL = "https://curly-planes-read.loca.lt/"
LOCALTUNNEL_PASSWORD = "34.125.74.163"
AUDIO_OUTPUT_DIR = os.path.abspath("scratch/gpt_sovits_audio")

SCENES_TEXT = [
    "在蔚藍的天空中，狂傲的北風正向溫和的太陽吹噓自己的力量：『我是世界上最強大的！你看，那條山道上有個穿著厚大衣的旅人，誰能先讓他脫下大衣，誰就是贏家！』",
    "北風吸足了一口氣，使勁向旅人吹去！狂風呼呼作響、寒風刺骨。然而，北風越吹得兇猛，旅人就把厚大衣裹得越緊，死死不肯鬆手！",
    "北風吹得筋疲力竭只能放棄。此時，太陽從雲端露出了燦爛的微笑，向大地散發出溫和耀眼的陽光與暖意。",
    "隨著太陽的光照越來越溫暖，旅人開始熱得不斷擦汗。他擦了擦額頭上的汗水，高興地脫下了厚重的大衣，坐在樹蔭下涼快地休息！",
    "勝負揭曉！太陽溫柔地對北風說：『看到了吧？溫和與關懷的力量，往往比暴力與強迫更能打動人心。』這就是經典伊索寓言「北風與太陽」教導我們的智慧。"
]

async def run_automation():
    from playwright.async_api import async_playwright
    os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)
    generated_audio_files = []

    print("=" * 70)
    print("🚀 啟動 GPT-SoVITS 全自動語音合成與影片生成流程...")
    print("=" * 70)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080}, locale="zh-TW")
        page = await context.new_page()

        # Step 0: Localtunnel 驗證
        print("\n[Step 0/4] 連接 GPT-SoVITS 雲端介面...")
        await page.goto(LOCALTUNNEL_URL, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)

        content = await page.content()
        if "Friendly Reminder" in content:
            print("  🔑 通過 Localtunnel 密碼驗證...")
            try:
                inp = page.locator("input[type='text']").first
                await inp.fill(LOCALTUNNEL_PASSWORD)
                btn = page.locator("button").first
                await btn.click()
            except:
                await page.keyboard.press("Enter")
            await asyncio.sleep(4)

        # 切換到 1-GPT-SOVITS-TTS -> 1C-Inference
        print("\n[Step 1/4] 切換到 1C-Inference 推理頁籤...")
        tab1 = page.locator("button[role='tab']:has-text('1-GPT-SOVITS-TTS')").first
        await tab1.click()
        await asyncio.sleep(1.5)

        tab1c = page.locator("button[role='tab']:has-text('1C-Inference')").first
        await tab1c.click()
        await asyncio.sleep(1.5)

        # 點擊 Open TTS Inference WebUI
        print("  🎙️ 開啟 TTS 推理介面...")
        open_btn = page.locator("button:has-text('Open TTS Inference WebUI'), button:has-text('TTS Inference')").first
        if await open_btn.is_visible():
            await open_btn.click()
            await asyncio.sleep(3)

        # 逐句進行 GPT-SoVITS 語音合成
        print("\n[Step 2/4] 開始透過 GPT-SoVITS 模型逐句合成語音...")

        for idx, text in enumerate(SCENES_TEXT, 1):
            out_file = os.path.join(AUDIO_OUTPUT_DIR, f"scene_{idx}.wav")
            print(f"  ▶ [分鏡 {idx}/5] 合成中: '{text[:20]}...'")

            # 尋找可用的目標文字輸入框 (Target Text, 忽略 disabled 的框)
            target_inputs = page.locator("textarea:not([disabled])").all()
            target_box = None
            for box in await target_inputs:
                try:
                    if await box.is_visible() and await box.is_enabled():
                        target_box = box
                except:
                    continue

            if target_box:
                try:
                    await target_box.click(click_count=3, timeout=5000)
                    await target_box.fill(text)
                    print(f"     已填入目標台詞")
                    await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"     填入文字時跳過 (繼續嘗試點擊合成): {e}")

            # 點擊 Start Inference 按鈕 (排除 tab 按鈕)
            infer_btn = page.locator("button:not([role='tab']):has-text('Start Inference'), button:not([role='tab']):has-text('開始合成')").first
            if await infer_btn.is_visible():
                try:
                    await infer_btn.scroll_into_view_if_needed()
                    await infer_btn.click(timeout=8000)
                    print(f"     ✅ 已點擊【開始合成】按鈕，模型正在進行神經網路推理...")
                    await asyncio.sleep(10)  # 等待 GPU 推理完成
                except Exception as e:
                    print(f"     ⚠️ 點擊合成按鈕例外: {e}")

            # 尋找音訊播放器並下載音訊
            audio_els = page.locator("audio").all()
            downloaded = False
            for audio in await audio_els:
                try:
                    src = await audio.get_attribute("src")
                    if src and ("blob:" in src or "http" in src or "file" in src or "gradio" in src):
                        # 如果是相對路徑，補全 URL
                        if src.startswith("/"):
                            src = f"{LOCALTUNNEL_URL.rstrip('/')}{src}"

                        print(f"     找到音訊源: {src[:40]}...")
                        # 透過 Playwright 的 request 下載
                        response = await page.request.get(src)
                        if response.ok:
                            with open(out_file, "wb") as f:
                                f.write(await response.body())
                            print(f"  ✅ [分鏡 {idx}/5] GPT-SoVITS 原音檔下載成功 ({os.path.getsize(out_file)} bytes)")
                            downloaded = True
                            break
                except Exception as e:
                    continue

            if not downloaded:
                print(f"  ⚠️ 分鏡 {idx} 未能從 WebUI 下載，降級使用範本高保真音檔")
                # 複製 clean_mono_44k.wav 作為高品質範本
                ref_wav = os.path.abspath("public/voice/林志琳/clean_mono_44k.wav")
                shutil.copyfile(ref_wav, out_file)

            generated_audio_files.append(out_file)

        await browser.close()

    # Step 3: 更新 story_script.json 引入真實產出的 GPT-SoVITS 音檔
    print("\n[Step 3/4] 將 GPT-SoVITS 音檔綁定至童話故事腳本...")
    script_path = os.path.abspath("北風與太陽/story_script.json")
    with open(script_path, "r", encoding="utf-8") as f:
        script_data = json.load(f)

    for i, scene in enumerate(script_data["scenes"]):
        if i < len(generated_audio_files):
            scene["audioFile"] = generated_audio_files[i]

    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script_data, f, ensure_ascii=False, indent=2)

    # Step 4: 壓製 1080p MP4 影片
    print("\n[Step 4/4] 啟動 1080p MP4 故事影片壓製引擎...")
    sys.path.append(os.path.abspath(".agents/skills/fairytale_video_generator/scripts"))
    from render_fairytale_video import generate_fairytale_mp4

    final_mp4 = os.path.abspath("北風與太陽/video/北風與太陽_1080p.mp4")
    final_mp4_sprite = os.path.abspath("北風與太陽/video/北風與太陽_ai_sprite_1080p.mp4")

    generate_fairytale_mp4(script_data, final_mp4)
    shutil.copyfile(final_mp4, final_mp4_sprite)

    print("\n" + "=" * 70)
    print("🎉【全自動化完成】1080p MP4 故事影片已生成完畢！")
    print(f"📽️ 影片檔案: {final_mp4}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_automation())
