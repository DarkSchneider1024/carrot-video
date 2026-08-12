"""
Carrot Studio Model Context Protocol (MCP) Server
Standard MCP Server Protocol Implementation (JSON-RPC 2.0 via Stdio)

Tools exposed to LLM Agent:
1. `generate_fairytale_video` : Render a 1080p MP4 fairytale video with voice & subtitles.
2. `synthesize_story_voice`  : Synthesize voice audio for a dialog line.
3. `generate_autosubs`        : Generate timestamped SRT subtitles from audio/script.
"""

import sys
import json
import asyncio
import subprocess
import os

sys.stdout.reconfigure(encoding='utf-8')

TOOLS_MANIFEST = [
    {
        "name": "generate_fairytale_video",
        "description": "Render a complete 1080p MP4 fairytale story video from a script with automatic voice synthesis and burned-in AutoSubs subtitles.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "storyTitle": {"type": "string", "description": "Title of the fairytale story"},
                "voice": {"type": "string", "description": "Voice ID e.g. zh-TW-HsiaoYuNeural or zh-TW-YunJheNeural"},
                "pitch": {"type": "string", "description": "Voice pitch adjustment e.g. +15Hz"},
                "scenes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "sceneNum": {"type": "integer"},
                            "dialog": {"type": "string"},
                            "bgImage": {"type": "string"},
                            "charImage": {"type": "string"},
                            "duration": {"type": "number"}
                        },
                        "required": ["dialog"]
                    }
                },
                "output_path": {"type": "string", "description": "Output MP4 file path"}
            },
            "required": ["storyTitle", "scenes"]
        }
    },
    {
        "name": "synthesize_story_voice",
        "description": "Synthesize custom voice audio (MP3/WAV) from a dialog string.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Dialog text to speak"},
                "voice": {"type": "string", "description": "Voice model ID"},
                "pitch": {"type": "string", "description": "Pitch e.g. +15Hz"}
            },
            "required": ["text"]
        }
    }
]

def handle_mcp_request(request: dict) -> dict:
    method = request.get("method")
    req_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "carrot-studio-mcp-server",
                    "version": "1.0.0"
                }
            }
        }

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": TOOLS_MANIFEST
            }
        }

    elif method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "generate_fairytale_video":
            output_path = os.path.abspath(args.get("output_path", "scratch/mcp_fairytale_video.mp4"))
            script_temp = os.path.abspath("scratch/mcp_call_script.json")
            os.makedirs("scratch", exist_ok=True)

            with open(script_temp, "w", encoding="utf-8") as f:
                json.dump(args, f, ensure_ascii=False, indent=2)

            cmd_render = [
                sys.executable,
                ".agents/skills/fairytale_video_generator/scripts/render_fairytale_video.py",
                "--script", script_temp,
                "--output", output_path
            ]
            subprocess.run(cmd_render, check=True)

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"✅ 1080p MP4 Video successfully rendered by MCP Server at: {output_path}"
                        }
                    ]
                }
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method '{method}' not found"}
    }

def main():
    print("🚀 Carrot Studio MCP (Model Context Protocol) Stdio Server Started", file=sys.stderr)
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            resp = handle_mcp_request(req)
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {e}"}
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
