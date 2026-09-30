# 🥕 Carrot Studio — 童話故事影片生成器

> 一鍵從文字劇本自動生成 1080p 童話故事影片，包含 AI 配音、自動字幕與角色動畫。  
> 完全本地端執行，免費開源，無需訂閱任何雲端服務。

---

## 📖 專案簡介

**Carrot Studio** 是一套以 AI 驅動的影片自動生成管線，特別針對 YouTube 童話故事短片製作。  
只需提供故事劇本 JSON，系統即可自動完成：

1. 🎙️ **深度神經網路語音合成** — 100% 採用 **Google Colab GPT-SoVITS** 零樣本真人音色複製（完全廢棄原生 Edge-TTS）
2. 💬 **AutoSubs 自動字幕** — Whisper 語音辨識 + 動態字幕分段燒錄（嚴格 ≤16 字）
3. 🎨 **AI 背景與角色圖片** — 自動生成加粗黑框防誤切 Sticker Sprite
4. 🎬 **FFmpeg 1080p 影片壓製** — 完整故事 MP4 一鍵輸出

---

## 🛠️ 技術堆疊

| 層次 | 技術 |
|------|------|
| 前端框架 | [React 18](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/) + [Vite](https://vitejs.dev/) |
| 3D 渲染 | [Three.js](https://threejs.org/) |
| 語音模型 | [Google Colab GPT-SoVITS](https://colab.research.google.com/drive/1zcn_jg7OGypbi9Te5PZeInJc4s--Ok5G?hl=zh-tw) (100% 真人音色複製) |
| 字幕生成 | [tmoroney/auto-subs](https://github.com/tmoroney/auto-subs) + [OpenAI Whisper](https://github.com/openai/whisper) |
| 影片壓製 | [FFmpeg](https://ffmpeg.org/) |
| AI 代理協議 | [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) |

---

## 🌟 核心語音架構：Google Colab GPT-SoVITS 深度學習語音複製

本專案已**全面廢棄原生的 Edge-TTS**，改採基於 [Google Colab GPT-SoVITS 訓練筆記本](https://colab.research.google.com/drive/1zcn_jg7OGypbi9Te5PZeInJc4s--Ok5G?hl=zh-tw) 的 100% 高保真零樣本語音推理：

- **訓練與推理解耦**：利用 Google Colab GPU 執行大模型推理，透過 API / Localtunnel 傳回音訊
- **專屬音色**：支援林志玲（林志琳）等專屬真人聲線，包含呼吸與語調起伏
- **快速切換端點**：
  ```powershell
  python scripts/set_colab_endpoint.py --url https://your-colab-tunnel.loca.lt
  ```

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
