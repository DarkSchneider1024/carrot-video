# -*- coding: utf-8 -*-
"""Launcher for the Gemini-voiced 小紅帽 video (started from gemini_*.bat so no non-ASCII paths live in the .bat).
   python live2d/run_gemini.py models | voices | render"""
import os, subprocess, sys, shutil, platform
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STORY = os.path.join(ROOT, '小紅帽', 'story_noodle_gemini.json')
mode = sys.argv[1] if len(sys.argv) > 1 else 'models'
print('python', sys.executable, platform.python_version(), '| ffmpeg', shutil.which('ffmpeg'), flush=True)
for mod in ('numpy', 'PIL', 'playwright', 'edge_tts'):
    try:
        __import__(mod); print('ok', mod)
    except Exception as e:
        print('MISSING', mod, e)
os.chdir(ROOT)
if mode == 'models':
    sys.exit(subprocess.call([sys.executable, '-u', os.path.join(HERE, 'gemini_tts_models.py')]))
args = [sys.executable, '-u', os.path.join(HERE, 'make_video.py'), STORY]
if mode == 'voices':
    args.append('--no-render')
sys.exit(subprocess.call(args))
