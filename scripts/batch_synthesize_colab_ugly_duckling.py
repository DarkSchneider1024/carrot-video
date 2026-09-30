import os
import sys
import json
import time
import requests
import shutil
import argparse

sys.stdout.reconfigure(encoding='utf-8')

DEFAULT_API_URL = "https://lou-homepage-creek-lakes.trycloudflare.com"

SCENES = [
    "在陽光明媚的農莊湖畔，母鴨媽媽孵化出了一群金黃色的小鴨，但最後一顆特別大的蛋裡，卻跳出了一隻灰撲撲又笨拙的小鴨子。",
    "因為長得和大家不一樣，農場裡的動物們都嘲笑並排擠他：『你長得好奇怪呀！』難過的醜小鴨只好低著頭，悄悄離開了家鄉。",
    "寒冷的冬天來臨了，刺骨的狂風下起大雪。醜小鴨在結冰的湖面上瑟瑟發抖，但他依然堅強地撐過了這段艱難的歲月。",
    "春天終於回到了大地，湖水清澈明亮。醜小鴨低頭看著水中的倒影，驚訝地發現自己不再是灰小鴨，而是一隻擁有潔白羽翼的優雅天鵝！",
    "一群美麗的天鵝向他游來，親切地歡迎他加入。這隻曾經飽受嘲笑的醜小鴨，終於自信地展翅高飛，迎向屬於他的燦爛幸福！"
]

def run_batch_inference(api_url=DEFAULT_API_URL):
    api_url = api_url.rstrip("/")
    print("=" * 70)
    print(f"🚀 開始透過 Google Colab Cloudflare API ({api_url}) 進行全劇神經網路語音推理 (方案1：自然輕快高音質)...")
    print("=" * 70)

    headers = {
        "Bypass-Tunnel-Reminder": "true",
        "User-Agent": "Mozilla/5.0"
    }

    voice_dir = os.path.abspath("醜小鴨/voice")
    temp_dir = os.path.abspath("scratch/cli_render_temp")
    os.makedirs(voice_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)

    for idx, text in enumerate(SCENES, 1):
        out_wav = os.path.join(voice_dir, f"scene_{idx}.wav")
        out_mp3 = os.path.join(voice_dir, f"scene_{idx}.mp3")
        temp_wav = os.path.join(temp_dir, f"scene_{idx}.wav")
        temp_mp3 = os.path.join(temp_dir, f"scene_{idx}.mp3")
        print(f"\n▶ [分鏡 {idx}/5] 正在生成台詞: '{text[:25]}...'")

        payload = {
            "text": text,
            "text_lang": "zh",
            "ref_audio_path": "/content/GPT-SoVITS/lin_zhilin.wav",
            "prompt_text": "在蔚藍的天空中，狂傲的北風正向溫和的太陽吹噓自己的力量",
            "prompt_lang": "zh",
            "top_k": 5,
            "top_p": 1.0,
            "temperature": 0.65,
            "speed_factor": 1.15,
            "text_split_method": "cut1",
            "media_type": "wav"
        }

        t0 = time.time()
        resp = requests.post(f"{api_url}/tts", json=payload, headers=headers, timeout=90)
        if resp.status_code == 200 and len(resp.content) > 1000:
            with open(out_wav, "wb") as f:
                f.write(resp.content)
            with open(out_mp3, "wb") as f:
                f.write(resp.content)
            shutil.copyfile(out_wav, temp_wav)
            shutil.copyfile(out_mp3, temp_mp3)
            print(f"  ✅ GPT-SoVITS 推理成功！耗時 {time.time()-t0:.2f}s, 音訊大小: {len(resp.content)} bytes")
        else:
            print(f"  ⚠️ 推理失敗 (狀態碼 {resp.status_code}): {resp.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_url", default=DEFAULT_API_URL, help="Cloudflare API URL")
    args = parser.parse_args()
    run_batch_inference(args.api_url)
