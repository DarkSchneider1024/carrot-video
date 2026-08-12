import React, { useState } from 'react';
import { RefreshCw, Volume2, Clock, Trash2, Image as ImageIcon, Sparkles, User } from 'lucide-react';
import type { StoryScene, ArtStyle, AspectRatio } from '../types';
import { generateFairyTaleImage } from '../services/imageService';
import { speakText, stopSpeaking } from '../services/ttsService';

interface SceneCardProps {
  scene: StoryScene;
  artStyle: ArtStyle;
  aspectRatio: AspectRatio;
  voiceName: string;
  isCurrentActive: boolean;
  onSelectScene: () => void;
  onUpdateScene: (updated: StoryScene) => void;
  onDeleteScene: () => void;
}

export const SceneCard: React.FC<SceneCardProps> = ({
  scene,
  artStyle,
  aspectRatio,
  voiceName,
  isCurrentActive,
  onSelectScene,
  onUpdateScene,
  onDeleteScene
}) => {
  const [isSpeaking, setIsSpeaking] = useState(false);

  const handleRegenerateImage = async (e: React.MouseEvent) => {
    e.stopPropagation();
    onUpdateScene({ ...scene, isGeneratingImage: true });

    try {
      const newSeed = Math.floor(Math.random() * 1000000);
      const url = await generateFairyTaleImage(
        scene.visualPrompt,
        artStyle,
        aspectRatio,
        newSeed
      );
      onUpdateScene({
        ...scene,
        imageUrl: url,
        isGeneratingImage: false
      });
    } catch (err) {
      console.error(err);
      onUpdateScene({ ...scene, isGeneratingImage: false });
    }
  };

  const handleSpeak = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (isSpeaking) {
      stopSpeaking();
      setIsSpeaking(false);
      return;
    }

    setIsSpeaking(true);
    await speakText(scene.narrative, voiceName);
    setIsSpeaking(false);
  };

  return (
    <div
      onClick={onSelectScene}
      className={`relative rounded-2xl border transition-all duration-200 overflow-hidden cursor-pointer ${
        isCurrentActive
          ? 'bg-slate-800/90 border-amber-500 shadow-lg shadow-amber-500/10 ring-2 ring-amber-500/50'
          : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-800/50'
      }`}
    >
      {/* Top Header Badge */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-slate-950/40 border-b border-slate-800/60 text-xs">
        <div className="flex items-center gap-2">
          <span className="w-5 h-5 rounded-full bg-amber-500 text-slate-950 font-bold flex items-center justify-center text-xs">
            {scene.sceneNumber}
          </span>
          <span className="font-semibold text-slate-300">分鏡 {scene.sceneNumber}</span>
          <span className="flex items-center gap-1 text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded-full">
            <User className="w-3 h-3 text-amber-400" />
            {scene.character || '旁白'}
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* Duration Pill */}
          <div className="flex items-center gap-1 text-slate-400 bg-slate-800 px-2 py-0.5 rounded-md">
            <Clock className="w-3 h-3 text-slate-400" />
            <input
              type="number"
              min={2}
              max={20}
              value={scene.duration}
              onChange={(e) =>
                onUpdateScene({ ...scene, duration: Math.max(2, parseInt(e.target.value) || 5) })
              }
              onClick={(e) => e.stopPropagation()}
              className="w-8 bg-transparent text-center font-bold text-amber-300 text-xs focus:outline-none"
            />
            <span>秒</span>
          </div>

          <button
            onClick={(e) => {
              e.stopPropagation();
              onDeleteScene();
            }}
            className="p-1 text-slate-500 hover:text-rose-400 rounded transition"
            title="刪除此分鏡"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="p-4 grid grid-cols-1 md:grid-cols-3 gap-4 items-start">
        {/* Image Preview Box */}
        <div className="relative aspect-video rounded-xl bg-slate-950 border border-slate-800 overflow-hidden group">
          {scene.isGeneratingImage ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 bg-slate-900/90 text-amber-400 text-xs font-medium">
              <RefreshCw className="w-6 h-6 animate-spin" />
              <span>開源 AI 繪圖中...</span>
            </div>
          ) : scene.imageUrl ? (
            <>
              <img
                src={scene.imageUrl}
                alt={`Scene ${scene.sceneNumber}`}
                className="w-full h-full object-cover transition transform group-hover:scale-105"
              />
              <button
                onClick={handleRegenerateImage}
                className="absolute top-2 right-2 p-2 bg-slate-950/80 hover:bg-amber-500 hover:text-slate-950 text-white rounded-lg backdrop-blur-md opacity-0 group-hover:opacity-100 transition shadow-lg flex items-center gap-1 text-xs"
                title="重新生成開源插畫"
              >
                <Sparkles className="w-3.5 h-3.5" />
                重繪
              </button>
            </>
          ) : (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-1 text-slate-500 text-xs">
              <ImageIcon className="w-8 h-8 stroke-1" />
              <span>尚未生成繪圖</span>
            </div>
          )}
        </div>

        {/* Story Text & Prompts Editor */}
        <div className="md:col-span-2 space-y-3">
          {/* Narrative Story Line */}
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1 flex items-center justify-between">
              <span>語音旁白 / 對話劇本 (中文)</span>
              <button
                onClick={handleSpeak}
                className={`flex items-center gap-1 text-xs px-2 py-0.5 rounded-md font-medium transition ${
                  isSpeaking
                    ? 'bg-rose-500 text-white animate-pulse'
                    : 'bg-amber-500/20 text-amber-300 hover:bg-amber-500/30'
                }`}
              >
                <Volume2 className="w-3 h-3" />
                {isSpeaking ? '停止試聽' : '試聽語音'}
              </button>
            </label>
            <textarea
              value={scene.narrative}
              onChange={(e) => onUpdateScene({ ...scene, narrative: e.target.value })}
              onClick={(e) => e.stopPropagation()}
              rows={2}
              className="w-full bg-slate-950/60 border border-slate-700/70 rounded-lg p-2.5 text-slate-100 text-sm focus:border-amber-500 focus:outline-none transition resize-none"
              placeholder="輸入發音旁白或對話..."
            />
          </div>

          {/* AI Visual Prompt */}
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">
              繪本畫面 Prompt (英文 AI 提示詞)
            </label>
            <input
              type="text"
              value={scene.visualPrompt}
              onChange={(e) => onUpdateScene({ ...scene, visualPrompt: e.target.value })}
              onClick={(e) => e.stopPropagation()}
              className="w-full bg-slate-950/60 border border-slate-700/70 rounded-lg px-2.5 py-1.5 text-slate-300 text-xs focus:border-amber-500 focus:outline-none transition"
              placeholder="Visual description for AI image generation..."
            />
          </div>
        </div>
      </div>
    </div>
  );
};
