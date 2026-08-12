"""
Explicit UTF-8 Path Video Renderer
Target Output: C:\\GitRoot\\CarrotStudio\\carrot-video\\北風與太陽\\video\\北風與太陽_1080p.mp4
"""

import os
import sys
import json
import shutil
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

target_dir = os.path.abspath("北風與太陽/video")
os.makedirs(target_dir, exist_ok=True)

target_mp4 = os.path.join(target_dir, "北風與太陽_1080p.mp4")
script_json = os.path.abspath(".agents/skills/fairytale_video_generator/examples/sample_story.json")

print(f"🎬 [UTF-8 Video Renderer] Target MP4 Path: {target_mp4}")

# Run CLI rendering engine
cmd = [
    sys.executable,
    ".agents/skills/fairytale_video_generator/scripts/render_fairytale_video.py",
    "--script", script_json,
    "--output", target_mp4
]

print(f"Executing: {' '.join(cmd)}")
res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')

print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)

if os.path.exists(target_mp4):
    size = os.path.getsize(target_mp4)
    print(f"✅ SUCCESS: Video file successfully rendered to '{target_mp4}' ({size} bytes)!")
else:
    print(f"❌ ERROR: Video file was NOT found at '{target_mp4}'.")
