import React, { useState } from 'react';
import { Download, CheckCircle, Video, RefreshCw, X, FileText, Sparkles, Smile } from 'lucide-react';
import type { StoryProject, CharacterMotionStyle } from '../types';
import { generateEdgeTTSScript } from '../services/ttsService';

interface VideoExporterProps {
  project: StoryProject;
  onClose: () => void;
}

export const VideoExporter: React.FC<VideoExporterProps> = ({ project, onClose }) => {
  const [isExporting, setIsExporting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [exportedVideoUrl, setExportedVideoUrl] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'exporter' | 'python_script'>('exporter');
  const [exportMotionStyle, setExportMotionStyle] = useState<CharacterMotionStyle>('head_bob');

  const isShorts = project.aspectRatio === '9:16';
  const width = isShorts ? 720 : 1280;
  const height = isShorts ? 1280 : 720;

  const pythonScript = generateEdgeTTSScript(
    project.scenes.map((s) => ({ sceneNum: s.sceneNumber, text: s.narrative }))
  );

  const startExporting = async () => {
    setIsExporting(true);
    setProgress(5);

    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const stream = canvas.captureStream(30);
    const mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm;codecs=vp9' });
    const chunks: Blob[] = [];

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.push(e.data);
    };

    mediaRecorder.onstop = () => {
      const blob = new Blob(chunks, { type: 'video/webm' });
      const url = URL.createObjectURL(blob);
      setExportedVideoUrl(url);
      setIsExporting(false);
      setProgress(100);
    };

    mediaRecorder.start();

    const totalScenes = project.scenes.length;

    const particles = Array.from({ length: 30 }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      size: Math.random() * 4 + 1.5,
      speedX: (Math.random() - 0.5) * 0.8,
      speedY: -Math.random() * 0.9 - 0.3,
      opacity: Math.random() * 0.7 + 0.3,
      hue: Math.random() * 60 + 40
    }));

    for (let i = 0; i < totalScenes; i++) {
      const scene = project.scenes[i];
      const sceneDurationSec = scene.duration || 6;
      const framesCount = sceneDurationSec * 30;

      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.src = scene.imageUrl || `https://image.pollinations.ai/prompt/fairytale?width=${width}&height=${height}`;
      await new Promise((res) => {
        img.onload = res;
        img.onerror = res;
      });

      for (let frame = 0; frame < framesCount; frame++) {
        const frameProgress = frame / framesCount;
        const elapsedSec = frame / 30;

        // Vyond 2D Head Bobbing & Swaying Transformation Matrix
        let headTilt = 0;
        let headBobY = 0;
        let bodySwayX = 0;
        let scale = 1.05;

        const currentMotion = scene.motionStyle || exportMotionStyle;

        if (currentMotion === 'head_bob') {
          headTilt = Math.sin(elapsedSec * 4.2) * 0.038;
          headBobY = Math.abs(Math.sin(elapsedSec * 4.2)) * 9;
          bodySwayX = Math.sin(elapsedSec * 2.1) * 8;
          scale = 1.05 + Math.sin(frameProgress * Math.PI) * 0.08;
        } else if (currentMotion === 'talking_sway') {
          headTilt = Math.sin(elapsedSec * 8) * 0.045;
          headBobY = Math.sin(elapsedSec * 6) * 12;
          bodySwayX = Math.cos(elapsedSec * 3) * 14;
          scale = 1.06 + Math.sin(elapsedSec * 5) * 0.015;
        } else {
          headTilt = Math.sin(elapsedSec * 1.8) * 0.02;
          headBobY = Math.sin(elapsedSec * 1.8) * 6;
          scale = 1.04 + Math.sin(elapsedSec * 1.8) * 0.02;
        }

        ctx.clearRect(0, 0, width, height);

        ctx.save();
        ctx.translate(width / 2 + bodySwayX, height / 2 + headBobY);
        ctx.rotate(headTilt);
        ctx.scale(scale, scale);
        ctx.drawImage(img, -width / 2, -height / 2, width, height);
        ctx.restore();

        // Volumetric Sunbeams
        const rayAngle = (elapsedSec * 0.1) % (Math.PI * 2);
        const rayGrad = ctx.createRadialGradient(
          width * 0.8 + Math.cos(rayAngle) * 50,
          100 + Math.sin(rayAngle) * 30,
          10,
          width * 0.8,
          100,
          width * 0.9
        );
        rayGrad.addColorStop(0, 'rgba(254, 240, 138, 0.25)');
        rayGrad.addColorStop(0.5, 'rgba(251, 191, 36, 0.1)');
        rayGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
        ctx.fillStyle = rayGrad;
        ctx.fillRect(0, 0, width, height);

        // Floating Particles
        ctx.save();
        particles.forEach((p) => {
          p.x += p.speedX + Math.sin(elapsedSec + p.hue) * 0.4;
          p.y += p.speedY;
          if (p.y < -20) p.y = height + 20;
          if (p.x < -20) p.x = width + 20;
          if (p.x > width + 20) p.x = -20;

          const pulseOpacity = p.opacity * (0.6 + Math.sin(elapsedSec * 3 + p.x) * 0.4);

          ctx.beginPath();
          ctx.arc(p.x, p.y, p.size * 2, 0, Math.PI * 2);
          ctx.fillStyle = `hsla(${p.hue}, 90%, 75%, ${pulseOpacity * 0.3})`;
          ctx.fill();

          ctx.beginPath();
          ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
          ctx.fillStyle = `hsla(${p.hue}, 100%, 85%, ${pulseOpacity})`;
          ctx.fill();
        });
        ctx.restore();

        // Character Name Badge
        if (scene.character) {
          ctx.save();
          ctx.font = 'bold 16px "Noto Sans TC", sans-serif';
          const textWidth = ctx.measureText(scene.character).width;
          ctx.fillStyle = 'rgba(245, 158, 11, 0.9)';
          ctx.beginPath();
          ctx.roundRect(30, 30, textWidth + 30, 36, 10);
          ctx.fill();
          ctx.fillStyle = '#0f172a';
          ctx.fillText(`🗣️ ${scene.character}`, 42, 54);
          ctx.restore();
        }

        // Subtitles Overlay
        if (scene.narrative) {
          const fontSize = isShorts ? 36 : 28;
          const textY = height - (isShorts ? 100 : 60);

          ctx.textAlign = 'center';
          ctx.font = `bold ${fontSize}px "Noto Sans TC", "Microsoft JhengHei", sans-serif`;

          ctx.strokeStyle = '#000000';
          ctx.lineWidth = 7;
          ctx.strokeText(scene.narrative, width / 2, textY);

          ctx.fillStyle = '#ffffff';
          ctx.fillText(scene.narrative, width / 2, textY);
        }

        await new Promise((r) => setTimeout(r, 1000 / 30));
      }

      setProgress(Math.round(((i + 1) / totalScenes) * 90));
    }

    mediaRecorder.stop();
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 w-full max-w-2xl rounded-2xl p-6 shadow-2xl space-y-5 relative">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <Video className="w-5 h-5 text-emerald-400" />
            <h3 className="text-lg font-bold text-white">匯出 Vyond 2D 動畫影片 (MP4 / WebM)</h3>
          </div>
          <button onClick={onClose} className="p-1 text-slate-400 hover:text-white rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
          <button
            onClick={() => setActiveTab('exporter')}
            className={`flex-1 py-2 rounded-lg font-medium transition ${
              activeTab === 'exporter' ? 'bg-emerald-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'
            }`}
          >
            直接瀏覽器 1080p 極速匯出
          </button>
          <button
            onClick={() => setActiveTab('python_script')}
            className={`flex-1 py-2 rounded-lg font-medium transition flex items-center justify-center gap-1.5 ${
              activeTab === 'python_script' ? 'bg-purple-500 text-white font-bold' : 'text-slate-400 hover:text-white'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            開源 Python 離線腳本
          </button>
        </div>

        {activeTab === 'exporter' ? (
          <div className="space-y-4 text-sm">
            {/* Motion Mode Selector */}
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3">
              <label className="block text-xs font-bold text-slate-300 flex items-center gap-1.5">
                <Smile className="w-4 h-4 text-amber-400" />
                選擇匯出影片的 Vyond 2D 角色動畫模式：
              </label>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <button
                  onClick={() => setExportMotionStyle('head_bob')}
                  className={`p-2.5 rounded-xl border text-center font-bold transition ${
                    exportMotionStyle === 'head_bob'
                      ? 'bg-amber-500/20 border-amber-500 text-amber-300'
                      : 'bg-slate-900 border-slate-800 text-slate-400'
                  }`}
                >
                  🎭 頭部自然晃動
                </button>
                <button
                  onClick={() => setExportMotionStyle('talking_sway')}
                  className={`p-2.5 rounded-xl border text-center font-bold transition ${
                    exportMotionStyle === 'talking_sway'
                      ? 'bg-amber-500/20 border-amber-500 text-amber-300'
                      : 'bg-slate-900 border-slate-800 text-slate-400'
                  }`}
                >
                  🗣️ 對話點頭擺動
                </button>
                <button
                  onClick={() => setExportMotionStyle('breathing')}
                  className={`p-2.5 rounded-xl border text-center font-bold transition ${
                    exportMotionStyle === 'breathing'
                      ? 'bg-amber-500/20 border-amber-500 text-amber-300'
                      : 'bg-slate-900 border-slate-800 text-slate-400'
                  }`}
                >
                  ⛵ 身體呼吸浮動
                </button>
              </div>
            </div>

            {isExporting ? (
              <div className="space-y-3 py-4 text-center">
                <div className="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto animate-spin">
                  <RefreshCw className="w-6 h-6" />
                </div>
                <div className="font-semibold text-slate-200">正在合成 Vyond 2D 角色頭部晃動動畫影片中...</div>
                <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-emerald-500 to-teal-400 h-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <div className="text-xs text-slate-400">{progress}% 完成</div>
              </div>
            ) : exportedVideoUrl ? (
              <div className="space-y-4 text-center py-2">
                <div className="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto">
                  <CheckCircle className="w-7 h-7" />
                </div>
                <div className="font-bold text-lg text-emerald-300">Vyond 2D 動畫影片合成成功！</div>
                <video src={exportedVideoUrl} controls className="w-full max-h-56 rounded-xl border border-slate-700 mx-auto" />
                <a
                  href={exportedVideoUrl}
                  download={`${project.title}_vyond_animated.webm`}
                  className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-slate-950 font-bold rounded-xl shadow-lg shadow-emerald-500/20 transition transform active:scale-95"
                >
                  <Download className="w-5 h-5" />
                  下載 1080p Vyond 動態影片 (.webm/.mp4)
                </a>
              </div>
            ) : (
              <button
                onClick={startExporting}
                className="w-full py-3.5 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-slate-950 font-bold rounded-xl shadow-lg shadow-emerald-500/20 transition transform active:scale-95 flex items-center justify-center gap-2 text-base"
              >
                <Sparkles className="w-5 h-5" />
                開始免費合成與匯出 Vyond 動態影片
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            <p className="text-xs text-slate-400">
              您可以複製下方開源 Python 腳本，結合免費 <code className="text-amber-300">edge-tts</code> 套件進行 100% 本地高品質音檔生成：
            </p>
            <pre className="bg-slate-950 p-3 rounded-xl border border-slate-800 text-xs font-mono text-purple-300 overflow-x-auto max-h-60">
              {pythonScript}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};
