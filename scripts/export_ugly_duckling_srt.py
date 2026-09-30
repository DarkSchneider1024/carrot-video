import os
import shutil
import json
import subprocess
import re

sys_reconf = True
try:
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

def split_dialog_into_chunks(dialog: str, total_duration: float, max_chars: int = 16, gap: float = 0.2):
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

    final_clauses = []
    for clause in clauses:
        while len(clause) > max_chars:
            final_clauses.append(clause[:max_chars])
            clause = clause[max_chars:]
        if clause:
            final_clauses.append(clause)

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
            end_t = total_duration
        result.append({
            "text": c,
            "start": start_t,
            "end": end_t
        })
        current_t = end_t + (gap if idx < n - 1 else 0)

    return result

def format_srt_time(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

def export_srt_and_voices():
    script_path = "醜小鴨/story_script.json"
    srt_path = "醜小鴨/醜小鴨_字幕.srt"
    voice_dir = "醜小鴨/voice"
    temp_dir = "scratch/cli_render_temp"
    
    os.makedirs(voice_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    srt_lines = []
    cue_idx = 1
    running_time = 0.0
    
    for idx, scene in enumerate(data.get("scenes", []), 1):
        dialog = scene.get("dialog", "")
        temp_audio = os.path.join(temp_dir, f"scene_{idx}.mp3")
        target_audio = os.path.join(voice_dir, f"scene_{idx}.mp3")
        
        if os.path.exists(temp_audio):
            shutil.copyfile(temp_audio, target_audio)
            
        cmd_dur = ["ffmpeg", "-i", target_audio]
        res = subprocess.run(cmd_dur, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        dur = scene.get("duration", 9.0)
        stderr_str = res.stderr.decode("utf-8", errors="ignore")
        for line in stderr_str.split("\n"):
            if "Duration" in line:
                parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
                dur = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2]) + 0.3
                break
                
        chunks = split_dialog_into_chunks(dialog, dur)
        for chunk in chunks:
            start_str = format_srt_time(running_time + chunk["start"])
            end_str = format_srt_time(running_time + chunk["end"])
            txt = chunk["text"]
            
            srt_lines.append(f"{cue_idx}\n{start_str} --> {end_str}\n{txt}\n\n")
            cue_idx += 1
            
        running_time += dur
        
    with open(srt_path, "w", encoding="utf-8") as f:
        f.writelines(srt_lines)
        
    print(f"✓ Exported SRT subtitle: {srt_path}")
    print(f"✓ Saved voice files to: {voice_dir}")

if __name__ == "__main__":
    export_srt_and_voices()
