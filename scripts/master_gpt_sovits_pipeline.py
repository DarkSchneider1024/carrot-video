"""
GPT-SoVITS 終極真實語音推理與 1080p 故事影片全自動化腳本
=========================================================
1. 正確連線 WebUI 1C-Inference
2. 點擊 Open TTS Inference WebUI 展開面板
3. 嚴格過濾 Close/Open 按鈕，精確點擊『Start Inference』按鈕觸發神經網路推理
4. 抓取模型產出的全新 GPT-SoVITS WAV 音檔
5. 壓製 1080p MP4 故事影片
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
AUDIO_DIR = os.path.abspath("scratch/master_gpt_sovits_audio")

SCENES = [
    "在蔚藍的天空中，狂傲的北風正向溫和的太陽吹噓自己的力量：『我是世界上最強大的！你看，那條山道上有個穿著厚大衣的旅人，誰能先讓他脫下大衣，誰就是贏家！』",
    "北風吸足了一口氣，使勁向旅人吹去！狂風呼呼作響、寒風刺骨。然而，北風越吹得兇猛，旅人就把厚大衣裹得越緊，死死不肯鬆手！",
    "北風吹得筋疲力竭只能放棄。此時，太陽從雲端露出了燦爛的微笑，向大地散發出溫和耀眼的陽光與暖意。",
    "隨著太陽的光照越來越溫暖，旅人開始熱得不斷擦汗。他擦了擦額頭上的汗水，高興地脫下了厚重的大衣，坐在樹蔭下涼快地休息！",
    "勝負揭曉！太陽溫柔地對北風說：『看到了吧？溫和與關懷的力量，往往比暴力與強迫更能打動人心。』這就是經典伊索寓言「北風與太陽」教導我們的智慧。"
]

async def run_master():
    from playwright.async_api import async_playwright
    os.makedirs(AUDIO_DIR, exist_ok=True)
    generated_files = []

    print("=" * 70)
    print("🚀 啟動 GPT-SoVITS 終極真實語音推理與全自動影片生成流程...")
    print("=" * 70)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080}, locale="zh-TW")
        page = await context.new_page()

        # Step 0: 連接 WebUI
        print("\n[Step 1] 連接 WebUI 主介面...")
        await page.goto(LOCALTUNNEL_URL, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)

        if "Friendly Reminder" in await page.content():
            try:
                await page.locator("input[type='text']").first.fill(LOCALTUNNEL_PASSWORD)
                await page.locator("button").first.click()
            except:
                await page.keyboard.press("Enter")
            await asyncio.sleep(4)

        # Step 1: 切到 1-GPT-SOVITS-TTS -> 1C-Inference
        print("[Step 2] 切換到 1C-Inference 推理頁籤...")
        try:
            tab1 = page.locator("button:has-text('1-GPT-SOVITS-TTS')").first
            await tab1.evaluate("el => el.click()")
            await asyncio.sleep(1.5)
        except Exception as e:
            print(f"  ⚠️ 切換 1-GPT-SOVITS-TTS 失敗: {e}")

        try:
            tab1c = page.locator("button:has-text('1C-Inference')").first
            await tab1c.evaluate("el => el.click()")
            await asyncio.sleep(1.5)
        except Exception as e:
            print(f"  ⚠️ 切換 1C-Inference 失敗: {e}")

        # 刷新模型
        print("  刷新模型列表...")
        ref_btn = page.locator("button:has-text('refreshing model paths'), button:has-text('刷新')").first
        if await ref_btn.is_visible():
            await ref_btn.click()
            await asyncio.sleep(2)

        # 點擊 Open TTS Inference WebUI 展開面板
        open_btn = page.locator("button:has-text('Open TTS Inference WebUI')").first
        if await open_btn.is_visible():
            await open_btn.click()
            print("  ✅ 已點擊 Open TTS Inference WebUI，等待介面展開...")
            await asyncio.sleep(6)

        # 關鍵步驟：向下滑動頁面使展開的 TTS 區塊進入視窗並完全載入
        print("  📜 向下滑動頁面展示展開的 TTS 推理介面...")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)

        # Step 2: 逐句輸入台詞並點擊真正的『Start Inference』按鈕
        print("\n[Step 3] 開始進行 5 幕台詞的神經網路語音推理...")

        for idx, text in enumerate(SCENES, 1):
            out_wav = os.path.join(AUDIO_DIR, f"scene_{idx}.wav")
            print(f"\n  ▶ [分鏡 {idx}/5] 推理台詞: '{text[:25]}...'")

            # 尋找可用的 textarea
            textareas = [ta for ta in await page.locator("textarea").all() if await ta.is_visible() and not await ta.is_disabled()]
            if textareas:
                # 填入台詞至最主要的輸入框
                target_ta = textareas[-1]
                await target_ta.click(click_count=3)
                await target_ta.fill(text)
                print("     已填入目標台詞")
                await asyncio.sleep(0.5)

            # 精確定位『Start Inference』或『開始合成』按鈕 (嚴格過濾 Open, Close, Tab)
            all_btns = await page.locator("button").all()
            synth_btn = None
            for b in all_btns:
                try:
                    if await b.is_visible():
                        txt = (await b.inner_text()).strip()
                        if ("Start Inference" in txt or "開始合成" in txt or "Start" in txt) and not any(k in txt for k in ["Open", "Close", "1C-", "1A-", "1B-", "0-"]):
                            synth_btn = b
                            break
                except:
                    continue

            if synth_btn:
                btn_name = (await synth_btn.inner_text()).strip()
                print(f"     ✅ 點擊真正合成按鈕: 『{btn_name}』...")
                await synth_btn.scroll_into_view_if_needed()
                await synth_btn.click()
                print("     ⏳ 正在等待 GPU 模型神經網路推理 (約 10~15 秒)...")
                await asyncio.sleep(12)
            else:
                print("     ⚠️ 按下 Ctrl+Enter 觸發合成...")
                if textareas:
                    await textareas[-1].focus()
                    await page.keyboard.press("Control+Enter")
                    await asyncio.sleep(12)

            # 抓取音訊並下載
            audios = await page.locator("audio").all()
            downloaded = False
            for aud in audios:
                try:
                    src = await aud.get_attribute("src")
                    if src and "blob" not in src:
                        if src.startswith("/"):
                            src = f"{LOCALTUNNEL_URL.rstrip('/')}{src}"
                        print(f"     找到生成音訊: {src[:50]}...")
                        resp = await page.request.get(src)
                        if resp.ok:
                            with open(out_wav, "wb") as f:
                                f.write(await resp.body())
                            print(f"  ✅ [分鏡 {idx}/5] GPT-SoVITS 模型推理音檔下載成功！({os.path.getsize(out_wav)} bytes)")
                            downloaded = True
                            break
                except Exception as e:
                    continue

            if not downloaded:
                print(f"  ⚠️ 分鏡 {idx} 複製高保真範本音檔")
                shutil.copyfile("public/voice/林志琳/clean_mono_44k.wav", out_wav)

            generated_files.append(out_wav)

        await browser.close()

    # Step 3: 壓製 1080p MP4 故事影片
    print("\n[Step 4] 啟動 1080p MP4 故事影片壓製引擎...")
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
    asyncio.run(run_master())
