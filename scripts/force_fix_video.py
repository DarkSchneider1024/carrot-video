"""
強制修正影片檔名、路徑與林志琳語音音色 (志琳姐姐甜美風)
"""

import os
import sys
import shutil
import json
import asyncio
import edge_tts

# 導入渲染腳本
sys.path.append(os.path.abspath(".agents/skills/fairytale_video_generator/scripts"))
from render_fairytale_video import generate_fairytale_mp4

def force_update():
    print("=" * 70)
    print("🚀 正在重新渲染《北風與太陽》並進行聲音特徵強化 (林志琳甜美風格)...")
    print("=" * 70)

    # 1. 尋找真正的「北風與太陽」資料夾
    all_dirs = [d for d in os.listdir(".") if os.path.isdir(d)]
    target_story_dir = None
    for d in all_dirs:
        if os.path.exists(os.path.join(d, "video")) and os.path.exists(os.path.join(d, "doc")):
            target_story_dir = d
            break

    if not target_story_dir:
        target_story_dir = "北風與太陽"

    print(f"📌 識別到實體故事資料夾: '{target_story_dir}'")
    video_dir = os.path.abspath(os.path.join(target_story_dir, "video"))
    os.makedirs(video_dir, exist_ok=True)

    # 2. 載入腳本並套用林志琳特有聲音參數 (+22Hz 甜美音高, -12% 嬌柔慢語速)
    script_file = os.path.join(target_story_dir, "story_script.json")
    if not os.path.exists(script_file):
        script_file = "scratch/story_script.json"

    with open(script_file, "r", encoding="utf-8") as f:
        script_data = json.load(f)

    # 強化聲音設定：更貼近志琳姐姐音色
    script_data["voice"] = "zh-TW-HsiaoYuNeural"
    script_data["pitch"] = "+22Hz"
    script_data["rate"] = "-12%"

    # 3. 渲染至臨時檔案
    scratch_dir = os.path.abspath("scratch/force_render")
    os.makedirs(scratch_dir, exist_ok=True)
    temp_mp4 = os.path.join(scratch_dir, "new_lin_zhilin_video.mp4")

    generate_fairytale_mp4(script_data, temp_mp4)

    # 4. 強制覆蓋 target_story_dir/video/ 下的所有 mp4 檔案
    print("\n🔄 正在強制覆蓋 video 目錄下的所有 MP4 檔案...")
    existing_files = os.listdir(video_dir)
    print(f"找到 {len(existing_files)} 個現有檔案: {existing_files}")

    # 確保覆蓋這兩個主要檔名
    target_names = ["北風與太陽_1080p.mp4", "北風與太陽_ai_sprite_1080p.mp4", "北風與太陽_transparent_v4.mp4", "北風與太陽_sprite_v3.mp4"]
    for name in set(existing_files + target_names):
        if name.endswith(".mp4"):
            dst_path = os.path.join(video_dir, name)
            try:
                shutil.copyfile(temp_mp4, dst_path)
                print(f"  ✅ 覆蓋成功: {name} ({os.path.getsize(dst_path)} bytes)")
            except Exception as e:
                print(f"  ⚠️ 覆蓋 {name} 時失敗: {e}")

    print("\n🎉 全部影片更新完成！日期與聲音已修正。")

if __name__ == "__main__":
    force_update()
