# Live2D（Inochi2D）動畫短片流程：Vyond 風格

這條流程取代原本「GPT 生圖加上 Ken Burns 鏡頭」的做法。它包含以下三部分：
- 角色：用 Python 筆刷程式畫出分層 PSD，再綁成 Inochi2D 骨架（.inp）。
- 畫面：用 WebGL 舞台把多層視差背景、多個角色和鏡頭運動組合起來。
- 影音：用 edge-tts 配音，依音量自動對嘴，最後由 FFmpeg 輸出 MP4 並燒入字幕。

## 目錄

| 路徑 | 內容 |
| --- | --- |
| `engine/brush.py`, `engine/girl.py` | 筆刷引擎和 `Part` 繪圖指令（來自 gimp-test） |
| `engine/build_psd.py` | `python live2d/engine/build_psd.py <角色> [--quick]`：輸出 PSD、預覽圖和零件總表 |
| `engine/rig.py` | `python live2d/engine/rig.py <角色>`：依角色模組裡的 `RIG` 產生 .inp、.inx 和 puppet.json |
| `characters/*.py` | 角色定義，目前有 `girl_v4`、`red_hood`（小紅帽）、`wolf`（大野狼） |
| `backgrounds.py` | 分層背景，包含 sky / far / mid / ground / fg，並寫出 `layers.json`（含視差係數） |
| `player/inochi-lite.js` | Inochi2D 0.8 的輕量 WebGL 播放器 |
| `player/stage.js`, `render.html` | 舞台：負責視差背景、多角色、鏡頭、走路循環、手勢、眨眼、呼吸和對嘴 |
| `make_video.py` | 讀劇本 JSON，依序做配音、對嘴、時間軸、渲染和合成，最後輸出 MP4 |

產出放在故事資料夾，例如 `小紅帽/`：
- `characters/`
- `backgrounds/`
- `voice/`（TTS 快取）
- `timeline.json`
- `subtitles.ass`
- `video/*.mp4`

## 一鍵產生

```bash
python live2d/make_video.py 小紅帽/story_live2d.json               # 完整輸出
python live2d/make_video.py 小紅帽/story_live2d.json --no-render   # 只做配音和時間軸（檢查長度）
python live2d/make_video.py 小紅帽/story_live2d.json --frames 900:901   # 只渲染單張影格，輸出到 _frames/ 預覽
```

- 渲染用的是系統的 Edge（Playwright `channel=msedge`），不需要另外下載瀏覽器。要改用別的瀏覽器，設環境變數 `RENDER_BROWSER=chrome`。
- 即時預覽：在 carrot-video 根目錄開一個 http server，瀏覽 `live2d/player/render.html?timeline=/小紅帽/timeline.json&play=0`。

## 劇本格式（`story_live2d.json`）

- `voices`：每個說話者的 edge-tts 聲音、語速和音高。之後換成 GPT-SoVITS 只要改 `make_video.synth()`。
- `cast`：角色 id 對應到哪個骨架，以及畫面上的身高（px）。
- `scenes[]`：每一幕包含以下欄位。
  - `bg`：背景名稱。
  - `camera`：關鍵影格 `{at: 0..1, x, y, zoom}`。`at` 是這一幕長度的比例。
  - `actors`：初始站位 `{id, x, y, look}`，x、y 是 ground 圖層的像素座標，y 是腳底。
  - `beats`：台詞依序播放，每句之間相隔 `gap` 秒。每句的 `do` 欄位可以指定以下動作，這些動作會在該句開始時觸發：
    - `walk_to`：走到某個 x，可加 `speed`。
    - `gesture`：`shy`、`explain`、`sly`、`point`、`happy`。
    - `look`：頭轉向，-1 到 1。
    - `nod`：點頭。

## 九軸與自然轉身

- **正面九軸**：正面骨架的頭部是九軸，左右 ±30°、上下 ±20°。
  - 設定在角色模組的 `RIG['head3d']`，由 `engine/rig.py` 算出 9 個關鍵形態。
  - 檢查方式：`python live2d/pose_sheet.py <inp> out.png`。
- **側面骨架**：側面 `*_side.py` 由 `engine/rig_side.py` 做出有關節的骨架，走路時使用。
- **轉身**：頭先用九軸轉 30°，接著正面和側面交叉淡化 0.16 秒（整張合成），停下來時反過來做一次。

## 已知限制（試作版）

- 手臂的 Swing 角度只有大約 ±6°（再大肩膀會破圖），手勢偏含蓄。
- 對嘴是依音量推算嘴巴開合，沒有分辨母音的嘴型。
