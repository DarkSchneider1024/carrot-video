"""
測試 Gradio Client API 觀測 GPT-SoVITS 暴露的所有端點
"""

import sys
from gradio_client import Client

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

LOCALTUNNEL_URL = "https://curly-planes-read.loca.lt/"

def test_api():
    print(f"📡 正在連接 Gradio Client API ({LOCALTUNNEL_URL})...")
    try:
        # localtunnel 需要帶 header 或 bypass，如果 gradio_client 被擋，我們觀察它的 view_api()
        client = Client(LOCALTUNNEL_URL, headers={"Bypass-Tunnel-Reminder": "true"})
        print("✅ Client 連接成功！查看 API 列表:")
        client.view_api()
    except Exception as e:
        print(f"⚠️ 連接失敗: {e}")

if __name__ == "__main__":
    test_api()
