import React from 'react';
import { Server, Activity, Volume2, Video, Subtitles, CheckCircle, Terminal, Code, Cpu } from 'lucide-react';

export const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Header */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md px-6 py-4 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-500 via-indigo-500 to-amber-500 flex items-center justify-center text-white shadow-lg shadow-purple-500/20">
            <Cpu className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h1 className="text-lg font-bold bg-gradient-to-r from-purple-400 via-pink-300 to-amber-200 bg-clip-text text-transparent">
              Carrot Studio MCP Pipeline API Server
            </h1>
            <p className="text-xs text-slate-400">Headless API Pipeline & Model Context Protocol (MCP) Tools</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
            <Activity className="w-3.5 h-3.5" />
            MCP Server 運作中 (Port 9880)
          </span>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-6xl mx-auto w-full p-6 space-y-6">
        {/* Banner */}
        <div className="bg-gradient-to-r from-purple-950/60 via-slate-900 to-indigo-950/60 border border-purple-500/30 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
          <div className="relative z-10 space-y-2">
            <div className="flex items-center gap-2 text-amber-400 font-bold text-xs">
              <Terminal className="w-4 h-4" />
              解耦 UI 獨立 pipeline 核心架構
            </div>
            <h2 className="text-2xl font-bold text-white">前端介面已移出，核心轉化為標準 MCP REST/RPC API</h2>
            <p className="text-sm text-slate-300 leading-relaxed max-w-3xl">
              所有影片生成、GPT-SoVITS 語音複製、AutoSubs 自動字幕與 1080p MP4 FFmpeg 壓製流程現已全數封裝為獨立 API 與 MCP 工具（Model Context Protocol），可直接與 LLM Agent / AI 助手對接！
            </p>
          </div>
        </div>

        {/* API Endpoints & MCP Tools Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Tool 1 */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 hover:border-purple-500/50 transition space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 font-bold text-sm text-amber-300">
                <Volume2 className="w-4 h-4 text-amber-400" />
                語音合成 API (GPT-SoVITS / Edge-TTS)
              </div>
              <span className="text-[10px] font-mono bg-purple-950 text-purple-300 px-2 py-0.5 rounded border border-purple-500/30">POST</span>
            </div>
            <p className="text-xs text-slate-400">接收對話文字、音色模型 ID 與音高設定，動態生成高畫質 MP3/WAV 語音。</p>
            <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 text-[11px] font-mono text-emerald-400">
              http://localhost:9880/api/v1/tts_synthesize
            </div>
          </div>

          {/* Tool 2 */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 hover:border-purple-500/50 transition space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 font-bold text-sm text-amber-300">
                <Subtitles className="w-4 h-4 text-amber-400" />
                AutoSubs 自動字幕 API
              </div>
              <span className="text-[10px] font-mono bg-purple-950 text-purple-300 px-2 py-0.5 rounded border border-purple-500/30">POST</span>
            </div>
            <p className="text-xs text-slate-400">接收音訊或劇本，自動進行毫秒級時間軸對齊並輸出標準 .srt 字幕。</p>
            <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 text-[11px] font-mono text-emerald-400">
              http://localhost:9880/api/v1/autosubs
            </div>
          </div>

          {/* Tool 3 */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 hover:border-purple-500/50 transition space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 font-bold text-sm text-amber-300">
                <Video className="w-4 h-4 text-amber-400" />
                1080p MP4 影片壓製 API (Headless FFmpeg)
              </div>
              <span className="text-[10px] font-mono bg-purple-950 text-purple-300 px-2 py-0.5 rounded border border-purple-500/30">POST</span>
            </div>
            <p className="text-xs text-slate-400">接收完整故事 JSON 劇本，無介面自動合成語音、繪圖、字幕與 1080p 60fps MP4 影片。</p>
            <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 text-[11px] font-mono text-emerald-400">
              http://localhost:9880/api/v1/render_video
            </div>
          </div>

          {/* Tool 4 */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 hover:border-purple-500/50 transition space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 font-bold text-sm text-amber-300">
                <Server className="w-4 h-4 text-amber-400" />
                MCP 健康度檢查與工具清單 API
              </div>
              <span className="text-[10px] font-mono bg-emerald-950 text-emerald-300 px-2 py-0.5 rounded border border-emerald-500/30">GET</span>
            </div>
            <p className="text-xs text-slate-400">查詢 MCP 服務狀態、當前可用的工具列表與 API 接口格式。</p>
            <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 text-[11px] font-mono text-emerald-400">
              http://localhost:9880/api/v1/health
            </div>
          </div>
        </div>

        {/* MCP Server Instruction Code Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-sm text-slate-200 flex items-center gap-2">
              <Code className="w-4 h-4 text-purple-400" />
              MCP Server 命令列啟動指令 (Stdio JSON-RPC)
            </h3>
            <span className="text-xs text-emerald-400 font-bold flex items-center gap-1">
              <CheckCircle className="w-3.5 h-3.5" />
              已就緒 (Ready)
            </span>
          </div>

          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-xs text-purple-300 overflow-x-auto leading-relaxed">
            python scripts/mcp_server.py
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;
