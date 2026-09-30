# -*- coding: utf-8 -*-
"""Launcher for the classic 小紅帽 (with the huntsman), Gemini-voiced (started from classic_*.bat).
   python live2d/run_classic.py voices | render"""
import os, subprocess, sys, shutil, platform
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STORY = os.path.join(ROOT, '小紅帽', 'story_classic.json')
mode = sys.argv[1] if len(sys.argv) > 1 else 'voices'
print('python', sys.executable, platform.python_version(), '| ffmpeg', shutil.which('ffmpeg'), flush=True)
os.chdir(ROOT)
args = [sys.executable, '-u', os.path.join(HERE, 'make_video.py'), STORY]
if mode == 'voices':
    args.append('--no-render')
sys.exit(subprocess.call(args))
