import base64
import os

wav_path = "public/voice/林志琳/prompt_clip_5s.wav"
with open(wav_path, "rb") as f:
    b64_data = base64.b64encode(f.read()).decode("ascii")

colab_code = f'''# ==============================================================================
# 🥕 CarrotStudio x GPT-SoVITS Google Colab 終極一鍵自包含腳本 (自帶林志玲音訊)
# ==============================================================================
import os, sys, time, subprocess, re, base64

print("=" * 70)
print("🚀 開始 GPT-SoVITS 深度學習語音伺服器 全自動極速部署...")
print("=" * 70)

# 1. 檢查並下載 GPT-SoVITS 專案庫
if not os.path.exists("/content/GPT-SoVITS"):
    print("\\n[1/5] 📥 下載 GPT-SoVITS 核心程式庫...")
    subprocess.run(["git", "clone", "https://github.com/RVC-Boss/GPT-SoVITS.git", "/content/GPT-SoVITS"], check=True)
else:
    print("\\n[1/5] ✅ GPT-SoVITS 專案已存在。")

%cd /content/GPT-SoVITS

# 2. 自動寫入林志玲 4.8 秒乾淨提示詞音檔 (內嵌 Base64，絕不 404)
print("\\n[2/5] 🎙️ 準備林志玲高保真提示詞音訊...")
b64_audio = """{b64_data}"""
with open("/content/GPT-SoVITS/lin_zhilin.wav", "wb") as f:
    f.write(base64.b64decode(b64_audio))
print("  ✓ 林志玲參考音檔已成功寫入: /content/GPT-SoVITS/lin_zhilin.wav")

# 3. 安裝依賴環境
print("\\n[3/5] 📦 安裝 Python 核心依賴...")
subprocess.run([sys.executable, "-m", "pip", "install", "opencc-python-reimplemented", "huggingface_hub", "fastapi", "uvicorn", "soundfile", "torchaudio", "einops", "transformers", "jieba_fast", "g2p_en", "ffmpeg-python", "cn2an", "pytorch-lightning", "x-transformers", "torchdiffeq", "pypinyin", "split-lang", "fast-langdetect", "onnxruntime", "wordsegment", "LangSegment", "scipy", "librosa"], check=True)

# 4. 下載官方模型 (若已下載過會秒速略過)
pretrained_dir = "/content/GPT-SoVITS/GPT_SoVITS/pretrained_models"
os.makedirs(pretrained_dir, exist_ok=True)
os.makedirs(os.path.join(pretrained_dir, "fast_langdetect"), exist_ok=True)
print("\\n[4/5] 📥 檢查 GPT-SoVITS 官方基礎模型...")
from huggingface_hub import snapshot_download
snapshot_download(repo_id="lj1995/GPT-SoVITS", local_dir=pretrained_dir)
print("  ✓ 基礎模型準備就緒！")

# 4.5 配置修改與代碼精準 Patch (強制全精度 FP32，防止 GPU 報錯)
yaml_path = "GPT_SoVITS/configs/tts_infer.yaml"
if os.path.exists(yaml_path):
    with open(yaml_path, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace("is_half: true", "is_half: false")
    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  ✓ [4.5a] tts_infer.yaml → is_half: false")

if os.path.exists("api_v2.py"):
    with open("api_v2.py", "r", encoding="utf-8") as f:
        api_code = f.read()
    
    inject_fp32 = """tts_pipeline = TTS(tts_config)
print(">>> [PATCH] 正在將所有 TTS 子神經網路模型 (含 cnhuhbert.model) 強制轉為 FP32...")
for attr in ['t2s_model', 'vits_model', 'bert_model', 'cnhuhbert_model', 'sr_model']:
    sub_m = getattr(tts_pipeline, attr, None)
    if sub_m is not None:
        if hasattr(sub_m, 'model') and sub_m.model is not None and hasattr(sub_m.model, 'float'):
            sub_m.model = sub_m.model.float()
        if hasattr(sub_m, 'float'):
            setattr(tts_pipeline, attr, sub_m.float())
print(">>> [PATCH] ✅ 全部模型已成功強制轉為 float32 (FP32)！")"""
    
    if "tts_pipeline = TTS(tts_config)" in api_code and "sub_m.model.float()" not in api_code:
        api_code = api_code.replace("tts_pipeline = TTS(tts_config)", inject_fp32)
        with open("api_v2.py", "w", encoding="utf-8") as f:
            f.write(api_code)
        print("  ✓ [4.5b] api_v2.py 已成功植入 FP32 深度精度轉換程式碼")

# 5. 安裝 Cloudflare 工具並啟動 API
print("\\n[5/5] 🚀 啟動 API 伺服器與 Cloudflare 穿透...")
if not os.path.exists("cloudflared-linux-amd64.deb"):
    subprocess.run(["wget", "-q", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb"], check=False)
subprocess.run(["dpkg", "-i", "cloudflared-linux-amd64.deb"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

# 開啟日誌檔案，記錄 API 伺服器的輸出與錯誤
log_file = open("api.log", "w", encoding="utf-8")
api_proc = subprocess.Popen([
    sys.executable, "-u", "api_v2.py",
    "-a", "0.0.0.0",
    "-p", "9880",
    "-c", "GPT_SoVITS/configs/tts_infer.yaml"
], stdout=log_file, stderr=log_file)

print("⏳ 等待神經網路模型載入 (最多等待 120 秒)...")
ready = False
for i in range(120):
    time.sleep(1)
    try:
        import socket
        with socket.create_connection(("127.0.0.1", 9880), timeout=1):
            print(f"🎉 API 伺服器已在 Port 9880 就緒！(耗時 {{i+1}} 秒)")
            ready = True
            break
    except Exception:
        continue

if not ready:
    print("\\n⚠️ 偵測到 API 伺服器未能在 Port 9880 啟動，以下為 api.log 錯誤訊息：")
    log_file.close()
    if os.path.exists("api.log"):
        with open("api.log", "r", encoding="utf-8") as lf:
            print(lf.read())
    else:
        print("未找到 api.log 檔案！")

print("\\n🌐 正在連線 Cloudflare 並擷取專屬網址...")
tunnel_proc = subprocess.Popen(["cloudflared", "tunnel", "--url", "http://127.0.0.1:9880"], stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)

for line in tunnel_proc.stderr:
    match = re.search(r'(https://[a-zA-Z0-9-]+\\.trycloudflare\\.com)', line)
    if match:
        tunnel_url = match.group(1)
        print("\\n" + "=" * 70)
        print("🎉 您的專屬 Cloudflare API 網址已成功生成：")
        print(f"👉 {{tunnel_url}}")
        print("=" * 70 + "\\n")
        break

tunnel_proc.wait()
'''

with open("scripts/colab_standalone_code.py", "w", encoding="utf-8") as f:
    f.write(colab_code)

print("Generated scripts/colab_standalone_code.py successfully!")
