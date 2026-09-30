import requests
import json
import time

url = "https://reid-avi-lying-something.trycloudflare.com"
password = ""

session = requests.Session()
# Set localtunnel bypass headers
session.headers.update({
    "Bypass-Tunnel-Reminder": "true",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
})

print(f"Connecting to {url}...")

# 1. Test GET /
try:
    r = session.get(url, timeout=20)
    print(f"GET / status: {r.status_code}")
    print(f"GET / text preview: {r.text[:300]}")
except Exception as e:
    print(f"GET / error: {e}")

# 2. Test GET /docs (FastAPI Swagger)
try:
    r_docs = session.get(f"{url}/docs", timeout=15)
    print(f"GET /docs status: {r_docs.status_code}")
except Exception as e:
    print(f"GET /docs error: {e}")

# 3. Test POST /tts
payload = {
    "text": "你好，這是測試對話",
    "text_lang": "zh",
    "ref_audio_path": "/content/GPT-SoVITS/lin_zhilin_voice/clean_mono_44k.wav",
    "prompt_text": "在蔚藍的天空中，狂傲的北風正向溫和的太陽吹噓自己的力量",
    "prompt_lang": "zh"
}

try:
    print("Sending POST /tts request...")
    t0 = time.time()
    r_tts = session.post(f"{url}/tts", json=payload, timeout=60)
    print(f"POST /tts status: {r_tts.status_code}, time: {time.time()-t0:.2f}s, size: {len(r_tts.content)} bytes")
    if r_tts.status_code == 200:
        with open("scratch/colab_test.wav", "wb") as f:
            f.write(r_tts.content)
        print("✓ Saved scratch/colab_test.wav successfully!")
except Exception as e:
    print(f"POST /tts error: {e}")
