import React from 'react';
import { Video, Sparkles, Image as ImageIcon } from 'lucide-react';

interface NavbarProps {
  activeTab: 'img2threejs' | 'dicebear';
  setActiveTab: (tab: 'img2threejs' | 'dicebear') => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  return (
    <header className="bg-slate-900/90 backdrop-blur-md border-b border-slate-800 text-white sticky top-0 z-40 px-4 py-3 shadow-lg">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-500 via-pink-500 to-amber-500 flex items-center justify-center shadow-md shadow-purple-500/20">
            <Video className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-bold text-lg tracking-wide bg-gradient-to-r from-purple-200 via-pink-200 to-amber-200 bg-clip-text text-transparent">
                Carrot Studio 3D
              </h1>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30 font-bold">
                100% 免費開源正統童話
              </span>
            </div>
            <p className="text-xs text-slate-400">專為 YouTube 童話故事頻道打造的開源 3D 影片與人物生成軟體</p>
          </div>
        </div>

        {/* Studio Navigation Tabs */}
        <div className="flex items-center gap-2 bg-slate-950 p-1.5 rounded-2xl border border-slate-800">
          <button
            onClick={() => setActiveTab('dicebear')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition ${
              activeTab === 'dicebear'
                ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg shadow-purple-500/25 ring-1 ring-purple-400/40'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Sparkles className="w-4 h-4 text-amber-400" />
            <span>🐻 Dicebear 開源人物分頁 (小紅帽)</span>
          </button>

          <button
            onClick={() => setActiveTab('img2threejs')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition ${
              activeTab === 'img2threejs'
                ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg shadow-purple-500/25 ring-1 ring-purple-400/40'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <ImageIcon className="w-4 h-4 text-emerald-400" />
            <span>🎨 Img2ThreeJS 真實圖片分頁</span>
          </button>
        </div>
      </div>
    </header>
  );
};
