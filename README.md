# 🥕 Carrot Studio — 童話故事影片生成器

> 一鍵從文字劇本自動生成 1080p 童話故事影片，包含 AI 配音、自動字幕與角色動畫。  
> 完全本地端執行，免費開源，無需訂閱任何雲端服務。

---

## 📖 專案簡介

**Carrot Studio** 是一套以 AI 驅動的影片自動生成管線，特別針對 YouTube 童話故事短片製作。  
只需提供故事劇本 JSON，系統即可自動完成：

1. 🎙️ **AI 語音合成** — Edge-TTS / GPT-SoVITS 生成中文配音
2. 💬 **AutoSubs 自動字幕** — Whisper 語音辨識 + 動態字幕分段燒錄
3. 🎨 **AI 背景與角色圖片** — 自動生成或使用現有素材
4. 🎬 **FFmpeg 1080p 影片壓製** — 完整故事 MP4 一鍵輸出

---

## 🛠️ 技術堆疊

| 層次 | 技術 |
|------|------|
| 前端框架 | [React 18](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/) + [Vite](https://vitejs.dev/) |
| 3D 渲染 | [Three.js](https://threejs.org/) |
| 語音合成 | [edge-tts](https://github.com/rany2/edge-tts) |
| 字幕生成 | [tmoroney/auto-subs](https://github.com/tmoroney/auto-subs) + [OpenAI Whisper](https://github.com/openai/whisper) |
| 影片壓製 | [FFmpeg](https://ffmpeg.org/) |
| AI 代理協議 | [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) |

---

## 🌟 引用的開源專案

### 🔤 [tmoroney/auto-subs](https://github.com/tmoroney/auto-subs)
> **本地端自動字幕生成工具**，支援 DaVinci Resolve、Premiere Pro 與 After Effects。

本專案借鑒 auto-subs 的核心設計理念：
- 以 **OpenAI Whisper** 進行本地端語音辨識，生成精確時間戳 SRT 字幕
- 字幕**自動分段切分**（每段最多 16 字），逐句動態出現於畫面
- 高對比度硬字幕燒錄（黃色字體、黑色描邊 4px、深色藥丸背景）
- 整合到 `scripts/auto_subs_whisper.py` 與 MCP Pipeline API

### 🌲 [image-to-3d / img2threejs](https://github.com/nicktarnold/img2threejs)
> **圖片轉 Three.js 3D 場景工具**，將 2D 靜態圖片轉換為可操控的 3D 視覺效果。

本專案整合於：
- `src/components/Img2ThreeJSStudio.tsx` — 圖片轉 Three.js 3D 空間映射
- `src/components/RealImg2ThreeJSStudio.tsx` — 搭配真實圖片輸入的進階 3D 場景
- `src/components/Full3DModelStudio.tsx` — 完整 3D 模型場景工作室

### ⚡ [Vite](https://vitejs.dev/)
> **極速前端建置工具**，原生 ESM 模組 + HMR 熱更新。

- 使用 [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react)（Oxc 編譯器）
- 開發模式：`npm run dev`
- 生產建置：`npm run build`

### 🗣️ [rany2/edge-tts](https://github.com/rany2/edge-tts)
> **微軟 Edge TTS 非官方 Python 客戶端**，支援多語言神經網路語音。

本專案使用以下語音模型：
- `zh-TW-HsiaoYuNeural` — 台灣女聲（小玉）
- `zh-TW-YunJheNeural` — 台灣男聲（雲哲）

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

修改 `.agents/skills/fairytale_video_generator/examples/sample_story.json` 填入故事劇本，然後執行：

```powershell
& "C:\Users\gueiw\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe" `
  .agents/skills/fairytale_video_generator/scripts/render_fairytale_video.py `
  --script .agents/skills/fairytale_video_generator/examples/sample_story.json `
  --output "C:\GitRoot\CarrotStudio\carrot-video\北風與太陽\video\北風與太陽_1080p.mp4"
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
│   │   ├── DicebearStudio.tsx        # 角色動畫工作室
│   │   ├── Img2ThreeJSStudio.tsx     # 圖片轉 Three.js（img2threejs 整合）
│   │   ├── RealImg2ThreeJSStudio.tsx # 真實圖片 3D 場景
│   │   ├── Full3DModelStudio.tsx     # 完整 3D 模型工作室
│   │   └── VisualStudioPlayer.tsx    # 影片預覽播放器
│   └── services/
│       └── ttsService.ts    # TTS 語音服務封裝
├── scripts/
│   ├── mcp_server.py                 # MCP JSON-RPC 2.0 Stdio Server
│   ├── mcp_pipeline_api_server.py    # REST API Server（Port 9880）
│   ├── auto_subs_whisper.py          # auto-subs Whisper 字幕生成
│   └── gpt_sovits_server.py          # GPT-SoVITS 語音克隆伺服器
├── .agents/
│   └── skills/
│       └── fairytale_video_generator/
│           ├── SKILL.md              # AI Agent Skill 規範
│           ├── scripts/
│           │   └── render_fairytale_video.py  # 無頭影片生成引擎
│           └── examples/
│               └── sample_story.json          # 故事劇本範例
├── public/
│   └── assets/              # 背景圖與角色素材
└── 北風與太陽/
    ├── video/               # 生成的影片輸出
    └── doc/                 # 影片生成規格文件
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
