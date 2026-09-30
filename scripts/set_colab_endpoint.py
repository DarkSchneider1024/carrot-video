"""
Google Colab GPT-SoVITS Tunnel Bridge & Endpoint Configurator
=============================================================
Allows quick setting and verification of your Google Colab GPT-SoVITS URL:
Notebook: https://colab.research.google.com/drive/1zcn_jg7OGypbi9Te5PZeInJc4s--Ok5G?hl=zh-tw

Usage:
  python scripts/set_colab_endpoint.py --url https://your-tunnel-url.loca.lt
"""

import os
import sys
import json
import argparse
import requests

sys.stdout.reconfigure(encoding='utf-8')

CONFIG_PATH = os.path.abspath("config/gpt_sovits_config.json")

def update_colab_endpoint(url: str, password: str = None, test: bool = True):
    print("=" * 70)
    print("🔗 設定 Google Colab GPT-SoVITS 雲端推理解耦端點...")
    print(f"📖 Colab 訓練筆記本: https://colab.research.google.com/drive/1zcn_jg7OGypbi9Te5PZeInJc4s--Ok5G?hl=zh-tw")
    print(f"🎯 新 API 端點: {url}")
    print("=" * 70)

    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    else:
        cfg = {"engine": "gpt_sovits_colab"}

    clean_url = url.rstrip("/")
    cfg["api_endpoint"] = clean_url
    if password:
        cfg["localtunnel_password"] = password

    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

    print(f"✅ 已成功更新設定檔: {CONFIG_PATH}")

    if test:
        print("\n🧪 正在測試連線與語音推理...")
        headers = {
            "Bypass-Tunnel-Reminder": "true",
            "User-Agent": "Mozilla/5.0"
        }
        test_payload = {
            "text": "測試 Google Colab 神經網路語音推理連線成功！",
            "text_lang": "zh",
            "ref_audio_path": "/content/GPT-SoVITS/lin_zhilin.wav",
            "prompt_text": "在蔚藍的天空中，狂傲的北風正向溫和的太陽吹噓自己的力量",
            "prompt_lang": "zh"
        }

        try:
            resp = requests.post(f"{clean_url}/tts", json=test_payload, headers=headers, timeout=30)
            if resp.status_code == 200:
                print(f"🎉 連線測試成功！回傳音訊大小: {len(resp.content)} bytes")
            else:
                print(f"⚠️ 伺服器回傳狀態碼: {resp.status_code}")
        except Exception as e:
            print(f"⚠️ 目前連線測試未完成 ({e})。請確認 Colab 服務正在執行中。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set Google Colab GPT-SoVITS endpoint")
    parser.add_argument("--url", required=True, help="Google Colab Localtunnel / ngrok API URL")
    parser.add_argument("--password", default="34.125.74.163", help="Localtunnel password if needed")
    parser.add_argument("--no-test", action="store_true", help="Skip connection test")
    args = parser.parse_args()

    update_colab_endpoint(args.url, args.password, test=not args.no_test)
