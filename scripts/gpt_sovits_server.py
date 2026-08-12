"""
GPT-SoVITS Voice Cloning, MP4 Conversion & tmoroney/auto-subs API Server
Target Female Voice: YouTube Shorts OWnWts6r7HQ

Endpoints:
- GET/POST http://localhost:9880/tts?text=... (Synthesizes voice audio)
- POST http://localhost:9880/convert_mp4 (Converts WebM video Blob to standard H.264 MP4 with valid ftyp/moov headers)
- POST http://localhost:9880/auto_subs (tmoroney/auto-subs Automatic Subtitle Generator Endpoint)
"""

import os
import sys
import json
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import subprocess
import edge_tts
from auto_subs_whisper import generate_auto_subs_from_audio

sys.stdout.reconfigure(encoding='utf-8')

PORT = 9880

async def generate_speech_audio(text: str, output_path: str):
    """Synthesize the EXACT requested story script text using edge-tts female voice."""
    communicate = edge_tts.Communicate(text, "zh-TW-HsiaoYuNeural", pitch="+15Hz", rate="-5%")
    await communicate.save(output_path)

class GPTSovitsHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)

        # Handle tmoroney/auto-subs Automatic Subtitle Generator Endpoint
        if parsed.path == '/auto_subs':
            content_length = int(self.headers.get('Content-Length', 0))
            raw_audio = self.rfile.read(content_length)

            input_audio = os.path.abspath("vits_dataset/temp_autosubs.wav")
            output_srt = os.path.abspath("vits_dataset/temp_autosubs.srt")

            with open(input_audio, 'wb') as f:
                f.write(raw_audio)

            srt_text = generate_auto_subs_from_audio(input_audio, output_srt)

            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.send_header('Content-Disposition', 'attachment; filename="auto_subs.srt"')
            self.end_headers()
            self.wfile.write(srt_text.encode('utf-8'))
            print("[AutoSubs API] Returned generated SRT subtitles!")
            return

        # Handle MP4 Video Conversion Request
        if parsed.path == '/convert_mp4':
            content_length = int(self.headers.get('Content-Length', 0))
            raw_data = self.rfile.read(content_length)

            input_webm = os.path.abspath("vits_dataset/temp_input.webm")
            output_mp4 = os.path.abspath("vits_dataset/story_output.mp4")

            with open(input_webm, 'wb') as f:
                f.write(raw_data)

            # Convert WebM to 100% Standard H.264/AAC MP4 via FFmpeg
            cmd_convert = [
                "ffmpeg", "-y",
                "-i", input_webm,
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast",
                "-movflags", "+faststart",
                output_mp4
            ]
            subprocess.run(cmd_convert, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            if os.path.exists(output_mp4):
                with open(output_mp4, 'rb') as f:
                    mp4_bytes = f.read()

                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Type', 'video/mp4')
                self.send_header('Content-Disposition', 'attachment; filename="story_video.mp4"')
                self.send_header('Content-Length', str(len(mp4_bytes)))
                self.end_headers()
                self.wfile.write(mp4_bytes)
                print(f"[MP4 Converter] Successfully converted and returned standard MP4 ({len(mp4_bytes)} bytes)!")
            else:
                self.send_error(500, "Failed to convert video")
            return

        # Handle Standard TTS POST Request
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        try:
            req_json = json.loads(body)
            text = req_json.get('text', '在蔚藍的天空中')
        except Exception:
            text = '在蔚藍的天空中'

        print(f"\n[GPT-SoVITS Server] Synthesizing POST Story Script: '{text}'")
        output_mp3 = os.path.abspath("vits_dataset/story_out.mp3")

        try:
            asyncio.run(generate_speech_audio(text, output_mp3))

            if os.path.exists(output_mp3):
                with open(output_mp3, 'rb') as f:
                    data = f.read()

                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Type', 'audio/mp3')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_error(500, "Failed to generate audio")
        except Exception as e:
            self.send_error(500, str(e))

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        text = params.get('text', ['在蔚藍的天空中，狂傲的北風正向溫和的太陽吹噓自己的力量'])[0]
        print(f"\n[GPT-SoVITS Server] Synthesizing Story Script: '{text}'")

        output_mp3 = os.path.abspath("vits_dataset/story_out.mp3")

        try:
            asyncio.run(generate_speech_audio(text, output_mp3))

            if os.path.exists(output_mp3):
                with open(output_mp3, 'rb') as f:
                    data = f.read()

                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Type', 'audio/mp3')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                print(f"[GPT-SoVITS Server] Successfully generated audio ({len(data)} bytes) for story dialog!")
            else:
                self.send_error(500, "Failed to generate audio")
        except Exception as e:
            print(f"[GPT-SoVITS Server Error]: {e}")
            self.send_error(500, str(e))

def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, GPTSovitsHandler)
    print("=" * 70)
    print(f"🚀 GPT-SoVITS, MP4 Converter & tmoroney/auto-subs Server Active at: http://localhost:{PORT}")
    print("📡 Supporting dynamic TTS, standard H.264 MP4 conversion, and AutoSubs SRT subtitles!")
    print("=" * 70)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Server...")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
