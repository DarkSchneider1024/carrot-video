# ==============================================================================
# 🥕 CarrotStudio x GPT-SoVITS Google Colab 一鍵全自動超完整版 (HuggingFace 官方源)
# ==============================================================================
import os, sys, time, subprocess, re

print("=" * 70)
print("🚀 開始 GPT-SoVITS 深度學習語音伺服器 全自動極速部署...")
print("=" * 70)

# 1. 檢查並下載 GPT-SoVITS 專案庫
if not os.path.exists("/content/GPT-SoVITS"):
    print("\n[1/5] 📥 下載 GPT-SoVITS 核心程式庫...")
    subprocess.run(["git", "clone", "https://github.com/RVC-Boss/GPT-SoVITS.git", "/content/GPT-SoVITS"], check=True)
else:
    print("\n[1/5] ✅ GPT-SoVITS 專案已存在。")

%cd /content/GPT-SoVITS

# 2. 安裝依賴環境
print("\n[2/5] 📦 安裝 Python 核心依賴（約需 1~2 分鐘）...")
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "opencc-python-reimplemented", "huggingface_hub", "fastapi", "uvicorn", "soundfile", "torchaudio", "einops", "transformers", "jieba_fast", "g2p_en"], check=False)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"], check=False)

# 3. 自動從 HuggingFace 下載官方全套預訓練模型
pretrained_dir = "/content/GPT-SoVITS/GPT_SoVITS/pretrained_models"
os.makedirs(pretrained_dir, exist_ok=True)
print("\n[3/5] 📥 從 HuggingFace 下載 GPT-SoVITS 官方基礎模型（若已存在會秒速略過）...")
from huggingface_hub import snapshot_download
snapshot_download(repo_id="lj1995/GPT-SoVITS", local_dir=pretrained_dir)
print("  ✓ 基礎模型下載完成！")

# 4. 安裝 Cloudflare Tunnel 穿透工具
print("\n[4/5] 🌐 安裝 Cloudflare 高速穿透工具...")
if not os.path.exists("cloudflared-linux-amd64.deb"):
    subprocess.run(["wget", "-q", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb"], check=False)
subprocess.run(["dpkg", "-i", "cloudflared-linux-amd64.deb"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

# 5. 啟動 API 伺服器並即時擷取印出 Cloudflare 網址
print("\n[5/5] 🚀 啟動 GPT-SoVITS FastAPI 語音推理伺服器 (Port 9880)...")
api_proc = subprocess.Popen([
    sys.executable, "api_v2.py",
    "-a", "0.0.0.0",
    "-p", "9880",
    "-c", "GPT_SoVITS/configs/tts_infer.yaml"
])

# 等待伺服器就緒
print("⏳ 等待神經網路模型載入...")
for i in range(15):
    time.sleep(1)
    try:
        import socket
        with socket.create_connection(("127.0.0.1", 9880), timeout=1):
            print(f"🎉 API 伺服器已成功在 Port 9880 啟動並就緒！(耗時 {i+1} 秒)")
            break
    except Exception:
        continue

print("\n🌐 正在連線 Cloudflare 並擷取專屬網址...")
tunnel_proc = subprocess.Popen(["cloudflared", "tunnel", "--url", "http://127.0.0.1:9880"], stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)

tunnel_url = None
for line in tunnel_proc.stderr:
    match = re.search(r'(https://[a-zA-Z0-9-]+\.trycloudflare\.com)', line)
    if match:
        tunnel_url = match.group(1)
        print("\n" + "=" * 70)
        print(f"🎉 您的專屬 Cloudflare API 網址已成功生成：")
        print(f"👉 {tunnel_url}")
        print("=" * 70 + "\n")
        break

# 保持穿透連線
tunnel_proc.wait()
