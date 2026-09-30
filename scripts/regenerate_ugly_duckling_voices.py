import os
import sys
import json
import shutil
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

# Import our pure GPT-SoVITS synthesizer
sys.path.append(os.path.abspath(".agents/skills/fairytale_video_generator/scripts"))
sys.path.append(os.path.abspath("scripts"))
from render_fairytale_video import synthesize_scene_audio, generate_fairytale_mp4
from export_ugly_duckling_srt import export_srt_and_voices

def regenerate_all_voices():
    print("=" * 70)
    print("🎙️ 正在使用 Google Colab GPT-SoVITS 深度學習模型重新生成《醜小鴨》全劇語音...")
    print("=" * 70)
    
    script_path = "醜小鴨/story_script.json"
    with open(script_path, "r", encoding="utf-8") as f:
        script_data = json.load(f)
        
    script_data["voice"] = "林志琳"
    
    voice_dir = os.path.abspath("醜小鴨/voice")
    temp_dir = os.path.abspath("scratch/cli_render_temp")
    os.makedirs(voice_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)
    
    scenes = script_data.get("scenes", [])
    for idx, sc in enumerate(scenes, 1):
        dialog = sc.get("dialog", "")
        out_mp3 = os.path.join(voice_dir, f"scene_{idx}.mp3")
        temp_mp3 = os.path.join(temp_dir, f"scene_{idx}.mp3")
        
        print(f"\n[分鏡 {idx}/{len(scenes)}] 角色: {sc.get('characterName')}")
        print(f"  台詞: '{dialog[:30]}...'")
        
        synthesize_scene_audio(
            text=dialog,
            voice="林志琳",
            pitch="+15Hz",
            rate="-5%",
            output_mp3=out_mp3
        )
        
        if os.path.exists(out_mp3):
            shutil.copyfile(out_mp3, temp_mp3)
            print(f"  ✓ 分鏡 {idx} 語音已更新: {out_mp3} ({os.path.getsize(out_mp3)} bytes)")
            
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script_data, f, ensure_ascii=False, indent=2)
        
    print("\n[Step 2/3] 重新計算時間軸並更新 SRT 字幕...")
    export_srt_and_voices()
    
    print("\n[Step 3/3] 重新壓製《醜小鴨》1080p 60fps MP4 故事影片...")
    output_mp4 = os.path.abspath("醜小鴨/video/醜小鴨_1080p.mp4")
    generate_fairytale_mp4(script_data, output_mp4)
    
    # Copy to artifact folder
    brain_mp4 = r"C:\Users\gueiw\.gemini\antigravity-ide\brain\ca6881a9-e145-4695-a6f4-c5cef51359bf\ugly_duckling_1080p.mp4"
    if os.path.exists(output_mp4):
        shutil.copyfile(output_mp4, brain_mp4)
        
    print("=" * 70)
    print(f"🎉《醜小鴨》全劇語音與 1080p 影片重新生成完成！")
    print(f"檔案位置: {output_mp4}")
    print("=" * 70)

if __name__ == "__main__":
    regenerate_all_voices()
