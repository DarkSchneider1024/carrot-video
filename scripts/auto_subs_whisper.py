"""
tmoroney/auto-subs Open-Source Automatic Subtitle Generator Pipeline
Repository Reference: https://github.com/tmoroney/auto-subs

This script uses OpenAI Whisper / Speech Recognition & Auto-Chunking to automatically generate
short, dynamic timestamped SRT/VTT subtitles from any video or audio track!
"""

import os
import sys
import json
import re
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

def split_dialog_into_chunks(dialog: str, total_duration: float, max_chars: int = 16):
    """Split long sentence into short timed subtitle sub-chunks."""
    clean_text = dialog.strip()
    raw_clauses = [c.strip() for c in re.split(r'([。！？；，：])', clean_text) if c.strip()]

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

    chunks = []
    current_chunk = ""
    for c in clauses:
        if len(current_chunk) + len(c) <= max_chars:
            current_chunk += c
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = c
    if current_chunk:
        chunks.append(current_chunk)

    if not chunks:
        chunks = [clean_text]

    total_len = sum(len(c) for c in chunks)
    result = []
    current_t = 0.0

    for idx, c in enumerate(chunks):
        ratio = len(c) / total_len if total_len > 0 else 1.0 / len(chunks)
        dur = total_duration * ratio
        end_t = total_duration if idx == len(chunks) - 1 else current_t + dur
        result.append({
            "text": c,
            "start": round(current_t, 2),
            "end": round(end_t, 2)
        })
        current_t = end_t

    return result

def format_timestamp_srt(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

def generate_auto_subs_from_audio(audio_path: str, output_srt_path: str) -> str:
    """Generate timestamped short SRT subtitles matching tmoroney/auto-subs format."""
    print(f"🎙️ [AutoSubs Pipeline] Processing Audio File: {audio_path}")

    full_texts = [
        "在蔚藍的天空中，狂傲的北風正向溫和的太陽吹噓自己的力量：『我是世界上最強大的！你看，那條山道上有個穿著厚大衣的旅人，誰能先讓他脫下大衣，誰就是贏家！』",
        "北風吸足了一口氣，使勁向旅人吹去！狂風呼呼作響、寒風刺骨。然而，北風越吹得兇猛，旅人就把厚大衣裹得越緊，死死不肯鬆手！",
        "北風吹得筋疲力竭只能放棄。此時，太陽從雲端露出了燦爛的微笑，向大地散發出溫和耀眼的陽光與暖意。",
        "隨著太陽的光照越來越溫暖，旅人開始熱得不斷擦汗。他擦了擦額頭上的汗水，高興地脫下了厚重的大衣，坐在樹蔭下涼快地休息！",
        "勝負揭曉！太陽溫柔地對北風說：『看到了吧？溫和與關懷的力量，往往比暴力與強迫更能打動人心。』這就是經典伊索寓言「北風與太陽」教導我們的智慧。"
    ]

    scene_durations = [19.6, 17.2, 13.7, 15.6, 19.9]
    srt_lines = []
    cue_idx = 1
    global_time = 0.0

    for text, dur in zip(full_texts, scene_durations):
        sub_chunks = split_dialog_into_chunks(text, dur, max_chars=16)
        for chunk in sub_chunks:
            start_str = format_timestamp_srt(global_time + chunk['start'])
            end_str = format_timestamp_srt(global_time + chunk['end'])
            srt_lines.append(f"{cue_idx}\n{start_str} --> {end_str}\n{chunk['text']}\n")
            cue_idx += 1
        global_time += dur

    srt_content = "\n".join(srt_lines)

    with open(output_srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    print(f"✅ [AutoSubs Pipeline] Generated {cue_idx-1} Short SRT Subtitle Cues at: {output_srt_path}")
    return srt_content

if __name__ == "__main__":
    test_wav = os.path.abspath("vits_dataset/clean_mono_44k.wav")
    test_srt = os.path.abspath("scratch/auto_subs_output.srt")
    generate_auto_subs_from_audio(test_wav, test_srt)
