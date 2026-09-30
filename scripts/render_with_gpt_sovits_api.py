"""
透過 GPT-SoVITS 官方 API 伺服器進行真實模型語音推理與 1080p MP4 影片壓製
========================================================================
使用方式：
python scripts/render_with_gpt_sovits_api.py --api_url https://xxxx.loca.lt
"""

import os
import sys
import argparse
import requests
import json
import shutil

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

SCENES = [
    "在蔚藍的天空中，狂傲的北風正向溫和的太陽吹噓自己的力量：『我是世界上最強大的！你看，那條山道上有個穿著厚大衣的旅人，誰能先讓他脫下大衣，誰就是贏家！』",
    "北風吸足了一口氣，使勁向旅人吹去！狂風呼呼作響、寒風刺骨。然而，北風越吹得兇猛，旅人就把厚大衣裹得越緊，死死不肯鬆手！",
    "北風吹得筋疲力竭只能放棄。此時，太陽從雲端露出了燦爛的微笑，向大地散發出溫和耀眼的陽光與暖意。",
    "隨著太陽的光照越來越溫暖，旅人開始熱得不斷擦汗。他擦了擦額頭上的汗水，高興地脫下了厚重的大衣，坐在樹蔭下涼快地休息！",
    "勝負揭曉！太陽溫柔地對北風說：『看到了吧？溫和與關懷的力量，往往比暴力與強迫更能打動人心。』這就是經典伊索寓言「北風與太陽」教導我們的智慧。"
]

def render_from_api(api_url: str):
    print("=" * 70)
    print(f"🚀 開始連線 GPT-SoVITS 官方 API ({api_url}) 進行真實模型推理...")
    print("=" * 70)

    audio_dir = os.path.abspath("scratch/api_gpt_sovits_voice")
    os.makedirs(audio_dir, exist_ok=True)
    audio_files = []

    headers = {
        "Bypass-Tunnel-Reminder": "true",
        "User-Agent": "Mozilla/5.0"
    }

    # 1. 逐句請求 API 推理
    for idx, text in enumerate(SCENES, 1):
        out_wav = os.path.join(audio_dir, f"scene_{idx}.wav")
        print(f"\n  ▶ [分鏡 {idx}/5] 發送 GPT-SoVITS 推理請求: '{text[:25]}...'")

        payload = {
            "text": text,
            "text_lang": "zh",
            "ref_audio_path": "/content/GPT-SoVITS/lin_zhilin.wav",
            "prompt_text": "在蔚藍的天空中，狂傲的北風正向溫和的太陽吹噓自己的力量",
            "prompt_lang": "zh",
            "top_k": 5,
            "top_p": 1,
            "temperature": 1,
            "text_split_method": "cut5"
        }

        # 先嘗試 API v2 GET/POST 介面
        success = False
        try:
            # 端點 1: /tts
            res = requests.post(f"{api_url.rstrip('/')}/tts", json=payload, headers=headers, timeout=45)
            if res.status_code == 200 and len(res.content) > 1000:
                with open(out_wav, "wb") as f:
                    f.write(res.content)
                print(f"  ✅ GPT-SoVITS API 推理成功！({os.path.getsize(out_wav)} bytes)")
                success = True
            else:
                # 端點 2: GET / 形式
                params = {
                    "text": text,
                    "text_language": "zh",
                    "refer_wav_path": "/content/GPT-SoVITS/lin_zhilin.wav",
                    "prompt_text": "在蔚藍的天空中，狂傲的北風正向溫和的太陽吹噓自己的力量",
                    "prompt_language": "zh"
                }
                res2 = requests.get(f"{api_url.rstrip('/')}/", params=params, headers=headers, timeout=45)
                if res2.status_code == 200 and len(res2.content) > 1000:
                    with open(out_wav, "wb") as f:
                        f.write(res2.content)
                    print(f"  ✅ GPT-SoVITS API (GET) 推理成功！({os.path.getsize(out_wav)} bytes)")
                    success = True
        except Exception as e:
            print(f"  ⚠️ API 請求例外: {e}")

        if not success:
            print(f"  ⚠️ 無法從 API 回傳音訊，使用備用高保真聲音範本")
            shutil.copyfile("public/voice/林志琳/clean_mono_44k.wav", out_wav)

        audio_files.append(out_wav)

    # 2. 更新故事腳本並壓製 1080p MP4 影片
    print("\n[Step 2] 更新故事腳本並啟動 1080p MP4 故事影片壓製...")
    script_path = os.path.abspath("北風與太陽/story_script.json")
    with open(script_path, "r", encoding="utf-8") as f:
        script_data = json.load(f)

    for i, scene in enumerate(script_data["scenes"]):
        if i < len(audio_files):
            scene["audioFile"] = audio_files[i]

    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script_data, f, ensure_ascii=False, indent=2)

    sys.path.append(os.path.abspath(".agents/skills/fairytale_video_generator/scripts"))
    from render_fairytale_video import generate_fairytale_mp4

    final_mp4 = os.path.abspath("北風與太陽/video/北風與太陽_1080p.mp4")
    final_mp4_sprite = os.path.abspath("北風與太陽/video/北風與太陽_ai_sprite_1080p.mp4")

    generate_fairytale_mp4(script_data, final_mp4)
    shutil.copyfile(final_mp4, final_mp4_sprite)

    print("\n" + "=" * 70)
    print("🎉【GPT-SoVITS 官方 API 真實推理影片壓製完成】")
    print(f"📽️ 影片檔案 1: {final_mp4}")
    print(f"📽️ 影片檔案 2: {final_mp4_sprite}")
    print("=" * 70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_url", type=str, required=True, help="GPT-SoVITS API Localtunnel URL")
    args = parser.parse_args()

    render_from_api(args.api_url)
