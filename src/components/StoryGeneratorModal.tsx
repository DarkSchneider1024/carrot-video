import React, { useState } from 'react';
import { Sparkles, BookOpen, Wand2, Palette, X } from 'lucide-react';
import type { ArtStyle, AspectRatio } from '../types';
import { PRESET_STORIES, getRandomPromptIdea } from '../services/storyTemplates';
import { getStyleDisplayName } from '../services/imageService';

interface StoryGeneratorModalProps {
  aspectRatio: AspectRatio;
  onSelectPreset: (presetIndex: number, style: ArtStyle) => void;
  onGenerateCustom: (topic: string, style: ArtStyle) => void;
  onClose: () => void;
}

export const StoryGeneratorModal: React.FC<StoryGeneratorModalProps> = ({
  onSelectPreset,
  onGenerateCustom,
  onClose
}) => {
  const [activeTab, setActiveTab] = useState<'preset' | 'custom'>('preset');
  const [customTopic, setCustomTopic] = useState('');
  const [selectedStyle, setSelectedStyle] = useState<ArtStyle>('watercolor');
  const [isGenerating, setIsGenerating] = useState(false);

  const styles: ArtStyle[] = [
    'watercolor',
    '3d_pixar',
    'ghibli_anime',
    'vintage_storybook',
    'paper_cutout',
    'oil_painting'
  ];

  const handleRandomIdea = () => {
    setCustomTopic(getRandomPromptIdea());
  };

  const handleCustomSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customTopic.trim()) return;

    setIsGenerating(true);
    onGenerateCustom(customTopic, selectedStyle);
    setIsGenerating(false);
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 w-full max-w-3xl rounded-2xl p-6 shadow-2xl space-y-5 relative max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">建立童話故事頻道劇本</h3>
              <p className="text-xs text-slate-400">選擇熱門童話範本或輸入文字由 AI 自動繪製分鏡</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 text-slate-400 hover:text-white rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Style Selector Header */}
        <div className="space-y-2">
          <label className="block text-xs font-semibold text-slate-300 flex items-center gap-1.5">
            <Palette className="w-3.5 h-3.5 text-amber-400" />
            選擇繪本美術風格 (Art Style)
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {styles.map((style) => (
              <button
                key={style}
                type="button"
                onClick={() => setSelectedStyle(style)}
                className={`p-2.5 rounded-xl border text-xs text-left font-medium transition ${
                  selectedStyle === style
                    ? 'bg-amber-500/10 border-amber-500 text-amber-300 font-bold ring-1 ring-amber-500/50'
                    : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                }`}
              >
                {getStyleDisplayName(style)}
              </button>
            ))}
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
          <button
            onClick={() => setActiveTab('preset')}
            className={`flex-1 py-2 rounded-lg font-medium transition flex items-center justify-center gap-1.5 ${
              activeTab === 'preset' ? 'bg-amber-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            精選經典童話範本
          </button>
          <button
            onClick={() => setActiveTab('custom')}
            className={`flex-1 py-2 rounded-lg font-medium transition flex items-center justify-center gap-1.5 ${
              activeTab === 'custom' ? 'bg-amber-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'
            }`}
          >
            <Wand2 className="w-3.5 h-3.5" />
            自訂童話主題 AI 生成
          </button>
        </div>

        {/* Tab 1: Presets */}
        {activeTab === 'preset' ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {PRESET_STORIES.map((preset, index) => (
              <div
                key={index}
                onClick={() => onSelectPreset(index, selectedStyle)}
                className="group bg-slate-950/80 border border-slate-800 hover:border-amber-500/80 p-4 rounded-xl space-y-3 cursor-pointer transition shadow-md hover:shadow-amber-500/10 flex flex-col justify-between"
              >
                <div>
                  <span className="text-[10px] uppercase font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full">
                    {preset.category}
                  </span>
                  <h4 className="font-bold text-sm text-slate-100 group-hover:text-amber-300 transition mt-2">
                    {preset.title}
                  </h4>
                  <p className="text-xs text-slate-400 mt-1 line-clamp-3 leading-relaxed">
                    {preset.description}
                  </p>
                </div>
                <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-xs text-slate-500">
                  <span>{preset.scenes.length} 個童話分鏡</span>
                  <span className="text-amber-400 font-semibold group-hover:translate-x-1 transition">使用此故事 →</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* Tab 2: Custom Topic Generator */
          <form onSubmit={handleCustomSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center justify-between">
                <span>輸入您的故事主題或主角</span>
                <button
                  type="button"
                  onClick={handleRandomIdea}
                  className="text-amber-400 hover:underline text-xs flex items-center gap-1"
                >
                  <Wand2 className="w-3 h-3" />
                  隨機靈感
                </button>
              </label>
              <input
                type="text"
                value={customTopic}
                onChange={(e) => setCustomTopic(e.target.value)}
                placeholder="例如：勇敢的小熊在彩虹糖果王國尋找魔法鑰匙..."
                className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-sm text-white focus:border-amber-500 focus:outline-none transition"
              />
            </div>

            <button
              type="submit"
              disabled={!customTopic.trim() || isGenerating}
              className="w-full py-3 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 disabled:opacity-50 text-slate-950 font-bold rounded-xl shadow-lg shadow-amber-500/20 transition transform active:scale-95 flex items-center justify-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              <span>一鍵生成童話劇本與分鏡畫面</span>
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
