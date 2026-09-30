import os
import sys
import subprocess
import json
import wave

sys.stdout.reconfigure(encoding='utf-8')

def get_audio_duration(file_path):
    cmd = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return float(res.stdout.strip())

def main():
    print("=" * 70)
    print("🌸 啟動林志玲聲線【甜美高音調 & 亮麗女聲】音頻增益引擎...")
    print("=" * 70)

    voice_dir = os.path.abspath("醜小鴨/voice")
    os.makedirs(voice_dir, exist_ok=True)

    durations = {}

    for idx in range(1, 6):
        src = os.path.join(voice_dir, f"scene_{idx}.mp3")
        temp_out = os.path.join(voice_dir, f"scene_{idx}_sweet.mp3")

        print(f"▶ 正在對分鏡 {idx} 進行音高升調 (+12% Pitch Shift) 與女聲高頻泛音增益...")
        # rubberband pitch shift + treble clarity + highpass to eliminate deep rumble
        cmd = [
            "ffmpeg", "-y", "-i", src,
            "-af", "highpass=f=100,rubberband=pitch=1.12,treble=g=3:f=6000,volume=1.2",
            temp_out
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        
        # Replace original with sweetened audio
        os.replace(temp_out, src)
        
        dur = get_audio_duration(src)
        durations[idx] = dur
        print(f"  ✓ 分鏡 {idx} 調音完成！長度: {dur:.2f}s")

    # Update story_script.json
    script_path = os.path.abspath("醜小鴨/story_script.json")
    with open(script_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for scene in data["scenes"]:
        num = scene["sceneNum"]
        if num in durations:
            scene["duration"] = round(durations[num], 1)

    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\n🎬 正在重新壓製 1080p MP4 影片...")
    output_mp4 = os.path.abspath("醜小鴨/video/醜小鴨_1080p.mp4")
    render_cmd = [
        sys.executable,
        ".agents/skills/fairytale_video_generator/scripts/render_fairytale_video.py",
        "--script", script_path,
        "--output", output_mp4
    ]
    subprocess.run(render_cmd, check=True)
    print("\n🎉 甜美高音調 1080p 影片已成功壓製完成！")

if __name__ == "__main__":
    main()
