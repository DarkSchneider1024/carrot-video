"""
渲染北風與太陽影片並精確複製覆蓋到「北風與太陽/video/」資料夾中，解決 Windows 中文路徑編碼混淆問題
"""

import os
import sys
import shutil
import json

sys.path.append(os.path.abspath(".agents/skills/fairytale_video_generator/scripts"))
from render_fairytale_video import generate_fairytale_mp4

def main():
    print("=" * 60)
    print("🚀 開始渲染最新『林志琳』語音版《北風與太陽》故事影片...")
    print("=" * 60)

    # 1. 載入腳本
    script_path = os.path.abspath("北風與太陽/story_script.json")
    with open(script_path, "r", encoding="utf-8") as f:
        script_data = json.load(f)

    # 設定林志琳 Profile 聲音參數
    script_data["voice"] = "zh-TW-HsiaoYuNeural"
    script_data["pitch"] = "+15Hz"
    script_data["rate"] = "-5%"

    # 2. 臨時渲染路徑
    temp_output_dir = os.path.abspath("scratch/output")
    os.makedirs(temp_output_dir, exist_ok=True)
    temp_mp4 = os.path.join(temp_output_dir, "rendered_video.mp4")

    # 3. 執行渲染
    generate_fairytale_mp4(script_data, temp_mp4)

    # 4. 精確複製到正宗「北風與太陽/video/」資料夾
    target_dir = os.path.abspath("北風與太陽/video")
    os.makedirs(target_dir, exist_ok=True)

    target_file_1 = os.path.join(target_dir, "北風與太陽_1080p.mp4")
    target_file_2 = os.path.join(target_dir, "北風與太陽_ai_sprite_1080p.mp4")

    print(f"📦 正在將影片覆蓋至目標路徑 1: {target_file_1}")
    shutil.copyfile(temp_mp4, target_file_1)

    print(f"📦 正在將影片覆蓋至目標路徑 2: {target_file_2}")
    shutil.copyfile(temp_mp4, target_file_2)

    print("\n✅ 所有影片更新完成！")
    print(f"檔案 1 大小: {os.path.getsize(target_file_1)} bytes")
    print(f"檔案 2 大小: {os.path.getsize(target_file_2)} bytes")

if __name__ == "__main__":
    main()
