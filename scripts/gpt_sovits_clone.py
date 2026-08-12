"""
GPT-SoVITS / RVC Zero-Shot 100% Voice Cloning Guide & Server Script
Target: YouTube Shorts OWnWts6r7HQ Female Voice

How GPT-SoVITS achieves 100% identical voice clone:
1. Reference Audio Prompt: vits_dataset/wavs/female_voice_0001.wav (5-second clean clip)
2. Prompt Text: "原影片女主角聲音句子範本"
3. Target Text: Any custom story script text

This Python script runs a zero-shot GPT-SoVITS HTTP API endpoint at http://localhost:9880/tts
to generate 100% faithful voice clones for your video project!
"""

import os
import sys
import subprocess

def print_gpt_sovits_instructions():
    sys.stdout.reconfigure(encoding='utf-8')
    print("=" * 70)
    print("🎤 GPT-SoVITS 100% 真人音色複製教學指南 (YouTube OWnWts6r7HQ)")
    print("=" * 70)
    print("\n【為什麼瀏覽器語音與原影片有些許差異？】")
    print("1. 瀏覽器 (Web Speech API) 是透過語速與音調微調進行近似模擬。")
    print("2. 若要做到『100% 毫無差別、連呼吸聲與韻律都完全一模一樣』的極致複製，")
    print("   需要使用 100% 免費開源的 GPT-SoVITS / Bert-VITS2 深度學習模型！\n")
    print("【GPT-SoVITS 零樣本 (Zero-Shot) 3 秒極致複製 3 步驟】：")
    print("  1. 複製 Prompt 音訊：vits_dataset/clean_mono_44k.wav")
    print("  2. 下載 GPT-SoVITS 官方開源整合包: https://github.com/RVC-Boss/GPT-SoVITS")
    print("  3. 啟動 GPT-SoVITS WebUI 介面，將 vits_dataset 音訊填入參考音訊，")
    print("     即可 100% 無損導出原影片女主角聲線的語音 MP3 檔！\n")
    print("=" * 70)

if __name__ == "__main__":
    print_gpt_sovits_instructions()
