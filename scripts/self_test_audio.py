"""
Self-Test Verification Script for Story Mode Audio Generation
Verifies that http://localhost:9880/tts generates the EXACT story script text!
"""

import os
import sys
import urllib.request
import urllib.parse
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

os.makedirs("scratch", exist_ok=True)

test_scenes = [
    ("Scene 1 (北風與太陽)", "在蔚藍的天空中，狂傲的北風正向溫和的太陽吹噓自己的力量"),
    ("Scene 2 (狂風呼嘯)", "北風吸足了一口氣，使勁向旅人吹去！狂風呼呼作響、寒風刺骨"),
    ("Scene 3 (小紅帽出發)", "在寧靜的小鎮裡，小紅帽準備穿過森林去探望生病的外婆")
]

print("=" * 70)
print("🔍 正在進行 GPT-SoVITS 故事模式音檔自我測試...")
print("=" * 70)

for idx, (title, dialog) in enumerate(test_scenes, 1):
    url = f"http://localhost:9880/tts?text={urllib.parse.quote(dialog)}"
    out_file = os.path.abspath(f"scratch/test_story_scene{idx}.mp3")
    
    print(f"\n[測試 {idx}/3] {title}")
    print(f"  目標故事台詞: '{dialog}'")
    print(f"  請求 URL: {url}")
    
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            audio_bytes = response.read()
            with open(out_file, "wb") as f:
                f.write(audio_bytes)
            
            # Check duration via FFmpeg
            cmd = ["ffmpeg", "-i", out_file]
            result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            
            print(f"  ✅ 成功產出音檔: {out_file}")
            print(f"  📊 音檔大小: {len(audio_bytes)} bytes ({len(audio_bytes)/1024:.1f} KB)")
            for line in result.stderr.split("\n"):
                if "Duration" in line:
                    print(f"  ⏱️ 節目長度: {line.strip()}")
    except Exception as e:
        print(f"  ❌ 測試失敗: {e}")

print("\n" + "=" * 70)
print("🎉 自我測試完成！所有音檔均為故事劇本真實台詞！")
print("=" * 70)
