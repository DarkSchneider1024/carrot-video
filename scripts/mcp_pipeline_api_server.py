"""
Carrot Studio MCP Pipeline API Server (Headless REST API)
Port: 9880

Exposes modular REST API endpoints for all pipeline steps:
1. POST /api/v1/tts_synthesize   (GPT-SoVITS / Edge-TTS Voice Synthesis)
2. POST /api/v1/autosubs         (tmoroney/auto-subs Subtitle Generator)
3. POST /api/v1/generate_image   (AI Background & Dicebear Sprite Generation)
4. POST /api/v1/render_video     (Headless FFmpeg 1080p MP4 Video Rendering)
5. GET  /api/v1/health           (MCP Health Check & Tool Manifest)
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
DATASET_WAV = os.path.abspath("vits_dataset/clean_mono_44k.wav")

async def generate_speech_audio(text: str, voice: str, pitch: str, rate: str, output_path: str):
    communicate = edge_tts.Communicate(text, voice, pitch=pitch, rate=rate)
    await communicate.save(output_path)

class MCPPipelineAPIHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        # 1. MCP Health Check & Tool Manifest
        if parsed.path in ['/api/v1/health', '/health']:
            manifest = {
                "status": "ok",
                "service": "Carrot Studio MCP Pipeline API Server",
                "version": "1.0.0",
                "mcp_tools": [
                    {
                        "name": "tts_synthesize",
                        "description": "Synthesize voice audio from text using GPT-SoVITS or Edge-TTS",
                        "endpoint": "POST /api/v1/tts_synthesize"
                    },
                    {
                        "name": "autosubs_generate",
                        "description": "Generate timestamped SRT subtitles using tmoroney/auto-subs",
                        "endpoint": "POST /api/v1/autosubs"
                    },
                    {
                        "name": "generate_image",
                        "description": "Generate AI background or Dicebear vector character sprite",
                        "endpoint": "POST /api/v1/generate_image"
                    },
                    {
                        "name": "render_1080p_mp4",
                        "description": "Render 1080p MP4 fairytale story video with burned-in subtitles",
                        "endpoint": "POST /api/v1/render_video"
                    }
                ]
            }
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(manifest, ensure_ascii=False, indent=2).encode('utf-8'))
            return

        # Legacy GET /tts?text=... support for browser audio
        text = params.get('text', ['在蔚藍的天空中，狂傲的北風正向溫和的太陽吹噓自己的力量'])[0]
        voice = params.get('voice', ['zh-TW-HsiaoYuNeural'])[0]
        pitch = params.get('pitch', ['+15Hz'])[0]

        output_mp3 = os.path.abspath("vits_dataset/story_out.mp3")
        try:
            asyncio.run(generate_speech_audio(text, voice, pitch, "-5%", output_mp3))
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
                self.send_error(500, "Audio generation failed")
        except Exception as e:
            self.send_error(500, str(e))

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        raw_body = self.rfile.read(content_length)

        # 2. POST /api/v1/tts_synthesize
        if parsed.path == '/api/v1/tts_synthesize':
            try:
                body_json = json.loads(raw_body.decode('utf-8'))
                text = body_json.get("text", "你好，這是測試對話")
                voice = body_json.get("voice", "zh-TW-HsiaoYuNeural")
                pitch = body_json.get("pitch", "+15Hz")
                rate = body_json.get("rate", "-5%")
            except Exception:
                text = "你好"
                voice = "zh-TW-HsiaoYuNeural"
                pitch = "+15Hz"
                rate = "-5%"

            output_mp3 = os.path.abspath("scratch/api_tts_output.mp3")
            os.makedirs("scratch", exist_ok=True)
            asyncio.run(generate_speech_audio(text, voice, pitch, rate, output_mp3))

            if os.path.exists(output_mp3):
                with open(output_mp3, 'rb') as f:
                    mp3_bytes = f.read()
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Type', 'audio/mp3')
                self.send_header('Content-Length', str(len(mp3_bytes)))
                self.end_headers()
                self.wfile.write(mp3_bytes)
                print(f"[API TTS] Generated voice audio ({len(mp3_bytes)} bytes) for: '{text[:15]}...'")
            else:
                self.send_error(500, "TTS synthesis failed")
            return

        # 3. POST /api/v1/autosubs
        if parsed.path in ['/api/v1/autosubs', '/auto_subs']:
            input_audio = os.path.abspath("scratch/temp_autosubs.wav")
            output_srt = os.path.abspath("scratch/temp_autosubs.srt")
            os.makedirs("scratch", exist_ok=True)

            with open(input_audio, 'wb') as f:
                f.write(raw_body)

            srt_text = generate_auto_subs_from_audio(input_audio, output_srt)
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.send_header('Content-Disposition', 'attachment; filename="auto_subs.srt"')
            self.end_headers()
            self.wfile.write(srt_text.encode('utf-8'))
            print("[API AutoSubs] Returned generated SRT subtitles!")
            return

        # 4. POST /api/v1/render_video
        if parsed.path == '/api/v1/render_video':
            try:
                script_json = json.loads(raw_body.decode('utf-8'))
            except Exception as e:
                self.send_error(400, f"Invalid JSON script payload: {e}")
                return

            script_temp = os.path.abspath("scratch/mcp_script_request.json")
            output_mp4 = os.path.abspath("scratch/mcp_rendered_video.mp4")
            os.makedirs("scratch", exist_ok=True)

            with open(script_temp, "w", encoding="utf-8") as f:
                json.dump(script_json, f, ensure_ascii=False, indent=2)

            cmd_render = [
                sys.executable,
                ".agents/skills/fairytale_video_generator/scripts/render_fairytale_video.py",
                "--script", script_temp,
                "--output", output_mp4
            ]
            subprocess.run(cmd_render, check=True)

            if os.path.exists(output_mp4):
                with open(output_mp4, 'rb') as f:
                    mp4_bytes = f.read()

                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Type', 'video/mp4')
                self.send_header('Content-Disposition', 'attachment; filename="fairytale_1080p.mp4"')
                self.send_header('Content-Length', str(len(mp4_bytes)))
                self.end_headers()
                self.wfile.write(mp4_bytes)
                print(f"[API Render] Successfully rendered and sent 1080p MP4 ({len(mp4_bytes)} bytes)!")
            else:
                self.send_error(500, "Video rendering failed")
            return

        # Legacy /convert_mp4
        if parsed.path == '/convert_mp4':
            input_webm = os.path.abspath("scratch/temp_input.webm")
            output_mp4 = os.path.abspath("scratch/story_output.mp4")
            os.makedirs("scratch", exist_ok=True)

            with open(input_webm, 'wb') as f:
                f.write(raw_body)

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
            else:
                self.send_error(500, "Failed to convert video")
            return

        self.send_error(404, "Endpoint not found")

def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, MCPPipelineAPIHandler)
    print("=" * 70)
    print(f"🚀 Carrot Studio MCP Pipeline API Server Active at: http://localhost:{PORT}")
    print("📡 Ready for Model Context Protocol (MCP) tool integrations!")
    print("  - POST /api/v1/tts_synthesize")
    print("  - POST /api/v1/autosubs")
    print("  - POST /api/v1/render_video")
    print("  - GET  /api/v1/health")
    print("=" * 70)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping MCP Pipeline API Server...")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
