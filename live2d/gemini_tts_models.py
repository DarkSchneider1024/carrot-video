# -*- coding: utf-8 -*-
"""List the Gemini models this API key can use for speech (TTS).   python live2d/gemini_tts_models.py"""
import json, os, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_video import gemini_key
url = 'https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000'
res = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={'x-goog-api-key': gemini_key()})).read())
names = [m['name'].split('/')[-1] for m in res.get('models', [])]
print('TTS models:', [n for n in names if 'tts' in n.lower()])
print('flash models:', [n for n in names if 'flash' in n.lower()])
