---
name: fairytale_video_generator
description: Autonomous end-to-end 1080p MP4 fairytale story video creation pipeline decoupled from UI. Incorporates image asset synthesis, GPT-SoVITS/Edge-TTS voice cloning, AutoSubs short dynamic subtitle auto-chunking & burning (max 16 chars per cue), Sprite Sheet character animation (3x3 grid → GIF → FFmpeg composite), and FFmpeg 1080p 60fps MP4 video rendering whenever requested by the user.
---

# 🎬 Autonomous Fairytale Video Generator Skill (UI-Decoupled Pipeline)

This skill enables the agent to autonomously generate complete, production-ready 1080p MP4 fairytale videos from any user prompt or story request without needing the browser UI!

---

## 🌟 Key Features

### 1. AutoSubs 字幕自動短化切分 (Auto-Chunking v2)
如果對話字幕過長（超過 16 字），系統會自動將字幕依句號/逗號切分為動態短字幕（嚴格 ≤ 16 字/段），並在每段之間插入 **0.2 秒空白間隔**，避免畫面出現一整坨冗長字幕或字幕切換閃爍！

### 2. 分角色動畫模式 (Per-Character Motion Profiles)
每個角色依角色名稱自動套用不同的 FFmpeg 動態公式：

| 角色關鍵字 | 動畫模式 | 說明 |
|-----------|---------|------|
| `north_wind` | 左右猛吹搖擺 | X 振幅 25px / 1.5Hz |
| `warm_sun` | 慢速脈動輝煌 | Y 振幅 18px / 0.8Hz |
| `traveler_coat` | 走路上下跳動 | abs(sin) Y 12px / 2.2Hz |
| `traveler_rest` | 點頭擦汗搖晃 | XY 小幅 / 1.0Hz |

### 3. 🎭 Sprite Sheet 精靈圖動畫（新功能）
角色 `charImage` 可以是 `.gif` 動畫檔，FFmpeg 會以 `-ignore_loop 0 -stream_loop -1` 無限循環播放 GIF 幀，呈現**真實逐幀動畫**而非數學函數模擬。

**精靈圖生成流程：**
```
1. AI 生成 3×3 精靈圖 (或用單張圖生成)
       ↓ scripts/make_demo_sprite_sheet.py
2. 生成 9 幀不同姿態 PNG (旋轉/縮放/翻轉)
   → public/assets/{char}_sprite.png (NxN 格)
       ↓ scripts/generate_sprite_animation.py
3. 切割 9 幀 + 合成動畫 GIF (8fps)
   → public/assets/{char}_anim.gif
       ↓ render_fairytale_video.py
4. FFmpeg 渲染：GIF 無限循環疊合背景
   → 1080p MP4 with sprite animation
```

---

## 🚀 How to Execute Video Generation

Whenever the user asks:
- "幫我做一部三隻小豬的影片"
- "請幫我生成龜兔賽跑的 1080p 故事影片"
- "幫我產出一段童話短片"

Follow these 5 autonomous steps:

---

### Step 1: Write Story JSON Script
Write `scratch/story_script.json` with fields:
- `storyTitle`: 故事標題
- `voice`: `zh-TW-HsiaoYuNeural`（女聲）或 `zh-TW-YunJheNeural`（男聲）
- `pitch`: 如 `+15Hz` 或 `-10Hz`
- `scenes[]`: 每幕包含 `dialog`、`bgImage`、`charImage`（可為 `.gif`）、`duration`、`characterName`

---

### Step 2: Ensure Image Assets Exist
Check if `public/assets/bg_*.png` and character images exist.  
If new characters needed:
- Use `generate_image` to create character PNG
- Use sprite sheet pipeline below to generate animated GIF

---

### Step 3: (Optional) Generate Sprite Sheet Animation for Character
If a character needs **frame-based GIF animation**:

```powershell
# A) 從單張圖生成 3×3 精靈圖
& "python.exe" scripts/make_demo_sprite_sheet.py `
  --input public/assets/{char}.png `
  --output public/assets/{char}_sprite.png `
  --rows 3 --cols 3 --frame-size 512

# B) 切割精靈圖 → 9 幀 → 動畫 GIF
& "python.exe" scripts/generate_sprite_animation.py `
  --sprite public/assets/{char}_sprite.png `
  --rows 3 --cols 3 --fps 8 `
  --output public/assets/{char}_anim.gif `
  --size 480
```

Then set `"charImage": "public/assets/{char}_anim.gif"` in the story JSON.

---

### Step 4: Run Headless Video Engine
```powershell
& "C:\Users\gueiw\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe" `
  .agents/skills/fairytale_video_generator/scripts/render_fairytale_video.py `
  --script scratch/story_script.json `
  --output "C:\GitRoot\CarrotStudio\carrot-video\北風與太陽\video\北風與太陽_1080p.mp4"
```

This engine automatically:
1. Synthesizes voice audio per scene (Edge-TTS / GPT-SoVITS)
2. Applies per-character motion profile (Sin() for PNG, GIF loop for animated sprites)
3. Auto-chunks subtitles ≤16 chars with 0.2s gap, burns high-contrast text onto video
4. Composites background + character + audio + subtitles → 1080p H.264 MP4

---

### Step 5: Present Final MP4 Artifact
After rendering completes, provide a direct file link:
`[video/北風與太陽_1080p.mp4](file:///C:/GitRoot/CarrotStudio/carrot-video/%E5%8C%97%E9%A2%A8%E8%88%87%E5%A4%AA%E9%99%BD/video/%E5%8C%97%E9%A2%A8%E8%88%87%E5%A4%AA%E9%99%BD_1080p.mp4)`

---

## 📁 Key Script Reference

| 腳本 | 功能 |
|------|------|
| `.agents/skills/fairytale_video_generator/scripts/render_fairytale_video.py` | 主渲染引擎（支援 PNG/GIF 角色） |
| `scripts/make_demo_sprite_sheet.py` | 單張圖 → 3×3 精靈圖 PNG |
| `scripts/generate_sprite_animation.py` | 精靈圖 → 切幀 → 動畫 GIF |
| `scripts/mcp_server.py` | MCP JSON-RPC 2.0 Stdio Server |
| `scripts/mcp_pipeline_api_server.py` | REST API Server (Port 9880) |
