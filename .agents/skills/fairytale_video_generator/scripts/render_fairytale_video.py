"""
CLI Headless Fairytale Video Generator Engine (Decoupled from UI)
Part of the 'fairytale_video_generator' Skill

Combines:
1. Story Script Parsing (Scenes, Dialogs, Voice Options)
2. AI Image Asset Mapping (Backgrounds & 4 Transparent AI Character Sprites)
3. GPT-SoVITS / Edge-TTS Voice Synthesis (Per-scene MP3 audio)
4. Per-Character Motion Profiles:
   - 北風 (north_wind):   left-right sway (sin X, amplitude 25px, speed 1.5Hz)
   - 太陽 (warm_sun):     radial pulse / slow spin (scale pulsing via sin Y, speed 0.8Hz)
   - 穿衣路人 (traveler_coat): walking bob (sin Y bounce, amplitude 12px, speed 2.2Hz)
   - 脫衣路人 (traveler_rest): nod/wipe motion (sin X+Y small, 1.0Hz)
   - default: gentle sway (sin X, amplitude 20px, 1.2Hz)
5. AutoSubs Subtitle Auto-Chunking & Burning (max 16 chars, 0.2s gap between chunks)
6. FFmpeg 1080p 60fps MP4 Rendering
"""

import os
import sys
import json
import shutil
import re
import asyncio
import subprocess
import argparse
import edge_tts

sys.stdout.reconfigure(encoding='utf-8')

# ---------------------------------------------------------------------------
# Per-character motion profile table
# Key: substring to match in charImage filename (lowercase)
# Value: (overlay_x_expr, overlay_y_expr, description)
# ---------------------------------------------------------------------------
CHARACTER_MOTION_PROFILES = {
    "north_wind": (
        # Fierce left-right sway (large amplitude, medium speed)
        "(W-w)/2 + sin(2*PI*t*1.5)*25",
        "(H-h)/2 + 30 + sin(2*PI*t*3.0)*8",
        "北風：左右猛吹搖擺"
    ),
    "warm_sun": (
        # Radial pulse / slow gentle drift
        "(W-w)/2 + sin(2*PI*t*0.4)*10",
        "(H-h)/2 + 20 + sin(2*PI*t*0.8)*18",
        "太陽：慢速脈動輝煌"
    ),
    "traveler_coat": (
        # Walking forward bob — slight X drift + strong Y bounce
        "(W-w)/2 + sin(2*PI*t*1.1)*12",
        "(H-h)/2 + 30 + abs(sin(2*PI*t*2.2))*12",
        "穿衣路人：走路跳動"
    ),
    "traveler_rest": (
        # Tired nod + wipe gesture — small motions
        "(W-w)/2 + sin(2*PI*t*1.0)*8",
        "(H-h)/2 + 25 + sin(2*PI*t*1.8)*10",
        "脫衣路人：點頭擦汗"
    ),
}

DEFAULT_MOTION = (
    "(W-w)/2 + sin(2*PI*t*1.2)*20",
    "(H-h)/2 + 20 + sin(2*PI*t*2.4)*15",
    "預設：輕柔搖擺"
)


def get_motion_profile(char_img_path: str):
    """Match charImage filename to a per-character motion profile."""
    fname = os.path.basename(char_img_path).lower()
    for key, profile in CHARACTER_MOTION_PROFILES.items():
        if key in fname:
            return profile
    return DEFAULT_MOTION


def split_dialog_into_chunks(dialog: str, total_duration: float, max_chars: int = 16, gap: float = 0.2):
    """
    AutoSubs Subtitle Auto-Chunking Algorithm (Enhanced v2):
    - Splits on Chinese punctuation: 。！？；，：
    - Strictly enforces max_chars per chunk (hard cap)
    - Inserts 0.2s silent gap between consecutive subtitle chunks
    - Time is distributed proportionally by character count
    """
    clean_text = dialog.strip()
    # Split by punctuation but keep the punctuation attached
    raw_clauses = [c.strip() for c in re.split(r'([。！？；，：])', clean_text) if c.strip()]

    # Merge punctuation back onto preceding clause
    clauses = []
    i = 0
    while i < len(raw_clauses):
        clause = raw_clauses[i]
        if i + 1 < len(raw_clauses) and raw_clauses[i+1] in '。！？；，：':
            clause += raw_clauses[i+1]
            i += 2
        else:
            i += 1
        if clause:
            clauses.append(clause)

    # Hard-cap enforcement: if any clause > max_chars, slice it
    final_clauses = []
    for clause in clauses:
        while len(clause) > max_chars:
            final_clauses.append(clause[:max_chars])
            clause = clause[max_chars:]
        if clause:
            final_clauses.append(clause)

    # Group small clauses together up to max_chars
    chunks = []
    current_chunk = ""
    for c in final_clauses:
        if len(current_chunk) + len(c) <= max_chars:
            current_chunk += c
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = c
    if current_chunk:
        chunks.append(current_chunk)

    if not chunks:
        chunks = [clean_text[:max_chars]]

    # Distribute time proportionally, with gap between chunks
    n = len(chunks)
    total_gap = gap * (n - 1) if n > 1 else 0
    usable_duration = max(total_duration - total_gap, total_duration * 0.8)
    total_len = sum(len(c) for c in chunks)

    result = []
    current_t = 0.0
    for idx, c in enumerate(chunks):
        ratio = len(c) / total_len if total_len > 0 else 1.0 / n
        dur = usable_duration * ratio
        start_t = current_t
        end_t = start_t + dur
        if idx == n - 1:
            end_t = total_duration  # last chunk fills to end
        result.append({
            "text": c,
            "start": round(start_t, 3),
            "end": round(end_t, 3)
        })
        current_t = end_t + (gap if idx < n - 1 else 0)

    return result


async def synthesize_scene_audio(text: str, voice: str, pitch: str, output_mp3: str):
    """Synthesize scene audio via edge-tts."""
    communicate = edge_tts.Communicate(text, voice, pitch=pitch)
    await communicate.save(output_mp3)


def generate_fairytale_mp4(script_data: dict, output_mp4_path: str):
    print("=" * 70)
    print(f"🎬 啟動 CLI 自動童話影片生成引擎 v2 (分角色動畫 + AutoSubs 分次字幕)...")
    print(f"📖 故事名稱: {script_data.get('storyTitle', '童話故事')}")
    print("=" * 70)

    work_dir = os.path.abspath("scratch/cli_render_temp")
    os.makedirs(work_dir, exist_ok=True)

    scenes = script_data.get("scenes", [])
    voice_id = script_data.get("voice", "zh-TW-HsiaoYuNeural")
    pitch = script_data.get("pitch", "+15Hz")

    concat_list_path = os.path.join(work_dir, "concat.txt")
    temp_final_mp4 = os.path.join(work_dir, "temp_final_render.mp4")
    concat_lines = []

    # Windows Font Path for Traditional Chinese Subtitles
    font_path = "C\\:/Windows/Fonts/msjh.ttc" if os.name == "nt" else "Arial"

    for idx, scene in enumerate(scenes, 1):
        dialog = scene.get("dialog", "")
        bg_img = os.path.abspath(scene.get("bgImage", "public/assets/bg_mountain.png"))
        char_img = os.path.abspath(scene.get("charImage", "public/assets/north_wind.png"))
        duration = scene.get("duration", 6.0)
        char_name = scene.get("characterName", "")

        scene_audio = os.path.join(work_dir, f"scene_{idx}.mp3")
        scene_mp4 = os.path.join(work_dir, f"scene_{idx}.mp4")

        # Resolve per-character motion profile
        motion_x, motion_y, motion_desc = get_motion_profile(char_img)
        print(f"\n[分鏡 {idx}/{len(scenes)}] 角色: {char_name} | 動畫: {motion_desc}")

        print(f"  ▶ 步驟 1/3 — 語音合成: '{dialog[:25]}...'")
        asyncio.run(synthesize_scene_audio(dialog, voice_id, pitch, scene_audio))

        # Measure actual audio duration via FFmpeg
        cmd_dur = ["ffmpeg", "-i", scene_audio]
        res = subprocess.run(cmd_dur, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        audio_dur = duration
        for line in res.stderr.split("\n"):
            if "Duration" in line:
                parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
                audio_dur = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2]) + 0.3
                break

        # AutoSubs v2: strict 16-char chunks with 0.2s gap
        sub_chunks = split_dialog_into_chunks(dialog, audio_dur, max_chars=16, gap=0.2)
        print(f"  ▶ 步驟 2/3 — 字幕分 {len(sub_chunks)} 段（每段 ≤16字，間距 0.2s）")

        # Build drawtext filters for each subtitle chunk
        drawtext_filters = []
        for chunk in sub_chunks:
            txt = (chunk['text']
                   .replace("'", "")
                   .replace(":", " ")
                   .replace(",", " ")
                   .replace("\n", " ")
                   .replace("『", "「")
                   .replace("』", "」"))
            t_start = chunk['start']
            t_end = chunk['end']
            drawtext_filters.append(
                f"drawtext=fontfile='{font_path}'"
                f":text='{txt}'"
                f":x=(w-text_w)/2"
                f":y=h-130"
                f":fontsize=40"
                f":fontcolor=yellow"
                f":bordercolor=black"
                f":borderw=5"
                f":box=1:boxcolor=black@0.5:boxborderw=10"
                f":enable='between(t,{t_start},{t_end})'"
            )

        # Build per-character motion overlay expression
        char_motion = f"overlay=x='{motion_x}':y='{motion_y}'"

        # Detect if character image is an animated GIF sprite
        is_gif = char_img.lower().endswith(".gif")

        # Compose FFmpeg filter_complex
        # GIF input: [1:v] already contains looping frames — scale + overlay directly
        # PNG input: static image, apply sin() motion via overlay expressions
        if is_gif:
            # For GIF, scale the animated frames and composite over background
            filter_chain = (
                f"[0:v]scale=1920:1080[bg];"
                f"[1:v]scale=480:480[char];"
                f"[bg][char]{char_motion}[v0];"
            )
        else:
            filter_chain = f"[0:v]scale=1920:1080[bg];[1:v]scale=480:480[char];[bg][char]{char_motion}[v0];"

        for i, dt in enumerate(drawtext_filters):
            in_v = f"v{i}"
            out_v = f"v{i+1}" if i < len(drawtext_filters) - 1 else "outv"
            filter_chain += f"[{in_v}]{dt}[{out_v}];"
        filter_chain = filter_chain.rstrip(";")

        anim_mode = "Sprite GIF Animation" if is_gif else "Sin() Motion"
        print(f"  ▶ 步驟 3/3 — FFmpeg 渲染分鏡 {idx} ({audio_dur:.1f}s) [{anim_mode}]...")

        if is_gif:
            # GIF input: use -ignore_loop 0 -stream_loop -1 to loop GIF for scene duration
            cmd_render_scene = [
                "ffmpeg", "-y",
                "-loop", "1", "-i", bg_img,
                "-ignore_loop", "0", "-stream_loop", "-1", "-i", char_img,
                "-i", scene_audio,
                "-filter_complex", filter_chain,
                "-map", "[outv]", "-map", "2:a",
                "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k",
                "-t", str(audio_dur),
                scene_mp4
            ]
        else:
            cmd_render_scene = [
                "ffmpeg", "-y",
                "-loop", "1", "-i", bg_img,
                "-loop", "1", "-i", char_img,
                "-i", scene_audio,
                "-filter_complex", filter_chain,
                "-map", "[outv]", "-map", "2:a",
                "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k",
                "-t", str(audio_dur),
                scene_mp4
            ]
        res_scene = subprocess.run(cmd_render_scene, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if not os.path.exists(scene_mp4):
            print(f"  ✗ Scene {idx} FFmpeg Error:\n{res_scene.stderr[-600:]}")
            raise RuntimeError(f"FFmpeg failed to render scene_{idx}.mp4")

        print(f"  ✓ 分鏡 {idx} 渲染完成")
        concat_lines.append(f"file 'scene_{idx}.mp4'\n")

    with open(concat_list_path, "w", encoding="utf-8") as f:
        f.writelines(concat_lines)

    print(f"\n[最終步驟] 拼接全劇 1080p 影片中...")
    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_list_path,
        "-c", "copy",
        temp_final_mp4
    ]
    res_concat = subprocess.run(cmd_concat, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if not os.path.exists(temp_final_mp4):
        print(f"FFmpeg Concat Error: {res_concat.stderr[-600:]}")
        raise RuntimeError("FFmpeg concat failed to generate temp_final_mp4")

    dest_dir = os.path.dirname(os.path.abspath(output_mp4_path))
    if dest_dir:
        os.makedirs(dest_dir, exist_ok=True)

    shutil.copy(temp_final_mp4, output_mp4_path)

    print("=" * 70)
    print(f"🎉 影片生成完成！分角色動畫 1080p MP4 已寫入: {output_mp4_path}")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Headless Fairytale Video Generator Engine v2 — Per-Character Animation Profiles"
    )
    parser.add_argument("--script", required=True, help="Path to story JSON script specification")
    parser.add_argument("--output", default="output_fairytale.mp4", help="Output MP4 file path")
    args = parser.parse_args()

    if os.path.exists(args.script):
        with open(args.script, "r", encoding="utf-8") as f:
            script_dict = json.load(f)
        generate_fairytale_mp4(script_dict, os.path.abspath(args.output))
    else:
        print(f"Error: Script file '{args.script}' not found.")
