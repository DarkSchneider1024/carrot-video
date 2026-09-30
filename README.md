# 🥕 Carrot Studio — 童話故事影片生成器

> 一鍵從文字劇本自動生成 1080p 童話故事影片，包含 AI 配音、自動字幕與角色動畫。  
> 完全本地端執行，免費開源，無需訂閱任何雲端服務。

---

## 📖 專案簡介

**Carrot Studio** 是一套以 AI 驅動的影片自動生成管線，特別針對 YouTube 童話故事短片製作。  
只需提供故事劇本 JSON，系統即可自動完成：

1. 🎨 **Live2D / Inochi2D 角色**：用 Python 筆刷畫出分層 PSD，再綁成 Inochi2D 骨架（九軸轉頭、眨眼、對嘴、手勢）
2. 🎙️ **Gemini 3.8 Flash TTS 配音**：每個角色一個聲音與語氣指示；旁白是卡洛兒姐姐（Aoede）
3. 💬 **字幕**：依配音時間自動分段燒錄（每段 ≤16 字）
4. 🎬 **WebGL 舞台 + FFmpeg**：多層視差背景、鏡頭運動、走路，輸出 1080p MP4

完整流程見 [`live2d/README.md`](live2d/README.md)，頻道成片（片頭、片名卡、正片、卡洛兒姐姐結語、片尾）見
`carrot-entertainment/.claude/skills/carrot-story-video-pipeline/SKILL.md`。

---

## 🛠️ 技術堆疊

| 層次 | 技術 |
|------|------|
| 前端框架 | [React 18](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/) + [Vite](https://vitejs.dev/) |
| 3D 渲染 | [Three.js](https://threejs.org/) |
| 語音模型 | Gemini 3.8 Flash TTS（`gemini-3.8-flash-tts`，金鑰讀 `.env` 的 `GEMINI_API_KEY`） |
| 角色動畫 | Inochi2D（自寫 WebGL 播放器）+ Playwright 渲染 |
| 字幕生成 | [tmoroney/auto-subs](https://github.com/tmoroney/auto-subs) + [OpenAI Whisper](https://github.com/openai/whisper) |
| 影片壓製 | [FFmpeg](https://ffmpeg.org/) |
| AI 代理協議 | [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) |

---

## 🌟 語音：Gemini 3.8 Flash TTS

- 劇本 `voices` 裡寫 `"engine": "gemini"`、`voice`（例如 Aoede、Leda、Puck）和 `style`（中文語氣指示）。
- 同一個聲音的台詞會合併成一次請求再切開（免費額度一天約 10 次請求），結果依文字雜湊快取在故事資料夾的 `voice/`。

---

## 🚀 快速開始

### 前端開發環境

```bash
# 安裝依賴
npm install

# 啟動開發伺服器
npm run dev

# 生產建置
npm run build
```

### 影片生成後端 API

```bash
# 安裝 Python 依賴
pip install edge-tts openai-whisper

# 啟動 MCP Pipeline API Server（Port 9880）
python scripts/mcp_pipeline_api_server.py
```

---

## 🎬 一鍵生成童話影片

```bash
python live2d/make_video.py 青蛙王子/story_frog.json --no-render   # 只做配音和時間軸（檢查長度）
python live2d/make_video.py 青蛙王子/story_frog.json --frames "5s,60s"   # 抽幾格檢查
python live2d/make_video.py 青蛙王子/story_frog.json               # 完整輸出到 青蛙王子/video/
```

---

## 📡 MCP Pipeline API 端點

| 方法 | 路徑 | 說明 |
|------|------|------|
| `GET` | `/api/v1/health` | 健康檢查 & 工具清單 |
| `POST` | `/api/v1/tts_synthesize` | 語音合成（Edge-TTS） |
| `POST` | `/api/v1/autosubs` | 自動字幕生成（Whisper） |
| `POST` | `/api/v1/render_video` | 渲染 1080p MP4 影片 |

---

## 📁 專案目錄結構

```
carrot-video/
├── src/
│   ├── components/          # React UI 元件
│   │   ├── Img2ThreeJSStudio.tsx     # 圖片轉 Three.js（img2threejs 整合）
│   │   ├── Full3DModelStudio.tsx     # 完整 3D 模型工作室
│   │   └── VisualStudioPlayer.tsx    # 影片預覽播放器
│   └── services/
│       └── ttsService.ts    # TTS 語音服務封裝
├── scripts/
│   ├── mcp_server.py                 # MCP JSON-RPC 2.0 Stdio Server
│   ├── mcp_pipeline_api_server.py    # REST API Server（Port 9880）
│   └── auto_subs_whisper.py          # auto-subs Whisper 字幕生成
├── live2d/                  # Live2D 動畫管線（角色、骨架、背景、舞台、make_video.py）
├── public/
│   └── assets/              # 前端用的背景圖與角色素材
├── 小紅帽/                   # 故事資料夾：劇本、角色、背景、配音快取、video/
└── 青蛙王子/
```

---

## 📜 開源授權

本專案採用 **MIT License** 開源授權。  
引用的第三方專案各自遵循其原始授權條款。

| 專案 | 授權 |
|------|------|
| [tmoroney/auto-subs](https://github.com/tmoroney/auto-subs) | MIT |
| [rany2/edge-tts](https://github.com/rany2/edge-tts) | GPL-3.0 |
| [openai/whisper](https://github.com/openai/whisper) | MIT |
| [Vite](https://vitejs.dev/) | MIT |
| [Three.js](https://threejs.org/) | MIT |

---

> Made with ❤️ by Carrot Studio
