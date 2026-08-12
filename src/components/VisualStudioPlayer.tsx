import React, { useRef, useEffect, useState } from 'react';
import { Play, Pause, SkipBack, SkipForward, Smile } from 'lucide-react';
import type { StoryProject, CharacterMotionStyle } from '../types';
import { speakText, stopSpeaking } from '../services/ttsService';

interface VisualStudioPlayerProps {
  project: StoryProject;
  activeSceneIndex: number;
  onSceneChange: (index: number) => void;
}

interface Particle {
  x: number;
  y: number;
  size: number;
  speedX: number;
  speedY: number;
  opacity: number;
  hue: number;
}

export const VisualStudioPlayer: React.FC<VisualStudioPlayerProps> = ({
  project,
  activeSceneIndex,
  onSceneChange
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [motionMode, setMotionMode] = useState<CharacterMotionStyle>('head_bob');
  const animationFrameRef = useRef<number | null>(null);
  const imagesCacheRef = useRef<Map<string, HTMLImageElement>>(new Map());
  const particlesRef = useRef<Particle[]>([]);

  const currentScene = project.scenes[activeSceneIndex];
  const isShorts = project.aspectRatio === '9:16';

  // Initialize fairytale floating magic particles
  useEffect(() => {
    const particles: Particle[] = [];
    const count = 35;
    for (let i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * 1280,
        y: Math.random() * 1280,
        size: Math.random() * 4 + 1.5,
        speedX: (Math.random() - 0.5) * 0.8,
        speedY: -Math.random() * 0.9 - 0.3,
        opacity: Math.random() * 0.7 + 0.3,
        hue: Math.random() * 60 + 40
      });
    }
    particlesRef.current = particles;
  }, []);

  // Preload scene images into cache
  useEffect(() => {
    project.scenes.forEach((scene) => {
      if (scene.imageUrl && !imagesCacheRef.current.has(scene.imageUrl)) {
        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.src = scene.imageUrl;
        img.onload = () => {
          imagesCacheRef.current.set(scene.imageUrl, img);
        };
      }
    });
  }, [project.scenes]);

  // Main Render Loop with Vyond 2D Character Head Bobbing & Talking Sway
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const targetWidth = isShorts ? 720 : 1280;
    const targetHeight = isShorts ? 1280 : 720;

    canvas.width = targetWidth;
    canvas.height = targetHeight;

    let startTime = performance.now();

    const render = (now: number) => {
      const elapsed = (now - startTime) / 1000;
      setCurrentTime(elapsed);

      ctx.clearRect(0, 0, targetWidth, targetHeight);

      if (currentScene) {
        const cachedImg = imagesCacheRef.current.get(currentScene.imageUrl);
        const duration = currentScene.duration || 6;
        const progress = Math.min(1, elapsed / duration);

        if (cachedImg && cachedImg.complete) {
          // --- Vyond 2D Cutout & Head Bobbing Transformation Matrix ---
          let headTilt = 0;
          let headBobY = 0;
          let bodySwayX = 0;
          let scale = 1.05;

          const currentMotion = currentScene.motionStyle || motionMode;

          if (currentMotion === 'head_bob') {
            headTilt = Math.sin(elapsed * 4.2) * 0.038;
            headBobY = Math.abs(Math.sin(elapsed * 4.2)) * 9;
            bodySwayX = Math.sin(elapsed * 2.1) * 8;
            scale = 1.05 + Math.sin(progress * Math.PI) * 0.08;
          } else if (currentMotion === 'talking_sway') {
            const talkSpeed = isPlaying ? 10 : 3;
            headTilt = Math.sin(elapsed * talkSpeed) * 0.045;
            headBobY = Math.sin(elapsed * (talkSpeed * 0.7)) * 12;
            bodySwayX = Math.cos(elapsed * 3) * 14;
            scale = 1.06 + Math.sin(elapsed * 5) * 0.015;
          } else if (currentMotion === 'breathing') {
            headTilt = Math.sin(elapsed * 1.8) * 0.02;
            headBobY = Math.sin(elapsed * 1.8) * 6;
            scale = 1.04 + Math.sin(elapsed * 1.8) * 0.02;
          } else {
            scale = 1.05 + Math.sin(progress * Math.PI) * 0.12;
            bodySwayX = Math.sin(progress * Math.PI) * 15;
          }

          ctx.save();
          ctx.translate(targetWidth / 2 + bodySwayX, targetHeight / 2 + headBobY);
          ctx.rotate(headTilt);
          ctx.scale(scale, scale);

          ctx.drawImage(
            cachedImg,
            -targetWidth / 2,
            -targetHeight / 2,
            targetWidth,
            targetHeight
          );
          ctx.restore();

          // Volumetric Light Beam Overlay
          const rayAngle = (elapsed * 0.1) % (Math.PI * 2);
          const rayGrad = ctx.createRadialGradient(
            targetWidth * 0.8 + Math.cos(rayAngle) * 50,
            100 + Math.sin(rayAngle) * 30,
            10,
            targetWidth * 0.8,
            100,
            targetWidth * 0.9
          );
          rayGrad.addColorStop(0, 'rgba(254, 240, 138, 0.2)');
          rayGrad.addColorStop(0.5, 'rgba(251, 191, 36, 0.08)');
          rayGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
          ctx.fillStyle = rayGrad;
          ctx.fillRect(0, 0, targetWidth, targetHeight);

          // Floating Firefly Particles
          ctx.save();
          particlesRef.current.forEach((p) => {
            p.x += p.speedX + Math.sin(elapsed + p.hue) * 0.4;
            p.y += p.speedY;
            if (p.y < -20) p.y = targetHeight + 20;
            if (p.x < -20) p.x = targetWidth + 20;
            if (p.x > targetWidth + 20) p.x = -20;

            const pulseOpacity = p.opacity * (0.6 + Math.sin(elapsed * 3 + p.x) * 0.4);

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

          // Draw Character Name Badge when speaking
          if (currentScene.character) {
            ctx.save();
            ctx.font = 'bold 16px "Noto Sans TC", sans-serif';
            const textWidth = ctx.measureText(currentScene.character).width;
            
            ctx.fillStyle = 'rgba(245, 158, 11, 0.9)';
            ctx.beginPath();
            ctx.roundRect(30, 30, textWidth + 30, 36, 10);
            ctx.fill();

            ctx.fillStyle = '#0f172a';
            ctx.fillText(`🗣️ ${currentScene.character}`, 42, 54);
            ctx.restore();
          }
        } else {
          const grad = ctx.createLinearGradient(0, 0, targetWidth, targetHeight);
          grad.addColorStop(0, '#1e1b4b');
          grad.addColorStop(1, '#311042');
          ctx.fillStyle = grad;
          ctx.fillRect(0, 0, targetWidth, targetHeight);

          ctx.fillStyle = '#f59e0b';
          ctx.font = 'bold 28px sans-serif';
          ctx.textAlign = 'center';
          ctx.fillText(`✨ 正在載入分鏡 #${currentScene.sceneNumber} 繪圖...`, targetWidth / 2, targetHeight / 2);
        }

        // Subtitle Overlay
        if (currentScene.narrative) {
          const captionBoxHeight = isShorts ? 200 : 130;
          const fontSize = isShorts ? 32 : 28;

          const bottomGrad = ctx.createLinearGradient(0, targetHeight - captionBoxHeight - 60, 0, targetHeight);
          bottomGrad.addColorStop(0, 'rgba(0, 0, 0, 0)');
          bottomGrad.addColorStop(0.4, 'rgba(0, 0, 0, 0.7)');
          bottomGrad.addColorStop(1, 'rgba(0, 0, 0, 0.9)');
          ctx.fillStyle = bottomGrad;
          ctx.fillRect(0, targetHeight - captionBoxHeight - 60, targetWidth, captionBoxHeight + 60);

          const textY = targetHeight - (isShorts ? 90 : 50);

          ctx.textAlign = 'center';
          ctx.font = `bold ${fontSize}px "Noto Sans TC", "Microsoft JhengHei", sans-serif`;

          ctx.strokeStyle = '#000000';
          ctx.lineWidth = 7;
          ctx.strokeText(currentScene.narrative, targetWidth / 2, textY);

          ctx.fillStyle = '#ffffff';
          ctx.fillText(currentScene.narrative, targetWidth / 2, textY);
        }
      }

      if (isPlaying) {
        const sceneDuration = currentScene?.duration || 6;
        if (elapsed >= sceneDuration) {
          if (activeSceneIndex < project.scenes.length - 1) {
            onSceneChange(activeSceneIndex + 1);
            startTime = performance.now();
          } else {
            setIsPlaying(false);
          }
        } else {
          animationFrameRef.current = requestAnimationFrame(render);
        }
      } else {
        animationFrameRef.current = requestAnimationFrame(render);
      }
    };

    animationFrameRef.current = requestAnimationFrame(render);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [currentScene, isPlaying, activeSceneIndex, project.scenes, isShorts, motionMode]);

  const togglePlay = async () => {
    if (isPlaying) {
      setIsPlaying(false);
      stopSpeaking();
    } else {
      setIsPlaying(true);
      if (currentScene?.narrative) {
        speakText(currentScene.narrative, project.voiceName);
      }
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-2xl flex flex-col items-center gap-4">
      {/* Player Header */}
      <div className="w-full flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse" />
          <span className="font-bold text-slate-200 flex items-center gap-1">
            <Smile className="w-4 h-4 text-amber-400" />
            Vyond 2D 角色動畫與頭部晃動引擎
          </span>
        </div>
        
        {/* Vyond Animation Mode Switcher */}
        <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setMotionMode('head_bob')}
            className={`px-2.5 py-1 rounded-lg font-semibold transition ${
              motionMode === 'head_bob'
                ? 'bg-amber-500 text-slate-950 shadow'
                : 'text-slate-400 hover:text-white'
            }`}
            title="頭部自然點頭晃動 (Vyond 2D Head Bobbing)"
          >
            🎭 頭部晃動
          </button>

          <button
            onClick={() => setMotionMode('talking_sway')}
            className={`px-2.5 py-1 rounded-lg font-semibold transition ${
              motionMode === 'talking_sway'
                ? 'bg-amber-500 text-slate-950 shadow'
                : 'text-slate-400 hover:text-white'
            }`}
            title="對話擺動 (Talking Sway)"
          >
            🗣️ 對話擺動
          </button>

          <button
            onClick={() => setMotionMode('breathing')}
            className={`px-2.5 py-1 rounded-lg font-semibold transition ${
              motionMode === 'breathing'
                ? 'bg-amber-500 text-slate-950 shadow'
                : 'text-slate-400 hover:text-white'
            }`}
            title="身體呼吸浮動 (Breathing Sway)"
          >
            ⛵ 呼吸浮動
          </button>
        </div>
      </div>

      {/* Canvas Viewport Box */}
      <div className="relative rounded-xl overflow-hidden shadow-2xl bg-black border border-slate-800 flex items-center justify-center max-w-full group">
        <canvas
          ref={canvasRef}
          className={`object-contain max-h-[480px] w-auto ${isShorts ? 'aspect-[9/16]' : 'aspect-[16/9]'}`}
        />

        {!isPlaying && (
          <button
            onClick={togglePlay}
            className="absolute p-4 rounded-full bg-amber-500/90 hover:bg-amber-400 text-slate-950 shadow-2xl backdrop-blur-md transition transform hover:scale-110"
          >
            <Play className="w-8 h-8 fill-slate-950" />
          </button>
        )}
      </div>

      {/* Timeline Controls Bar */}
      <div className="w-full space-y-2">
        <div className="flex items-center justify-between text-xs text-slate-400 px-1">
          <span>分鏡 {activeSceneIndex + 1} / {project.scenes.length}</span>
          <span>{currentTime.toFixed(1)}s / {(currentScene?.duration || 6).toFixed(1)}s</span>
        </div>

        <div className="flex items-center justify-center gap-3">
          <button
            onClick={() => {
              if (activeSceneIndex > 0) onSceneChange(activeSceneIndex - 1);
            }}
            disabled={activeSceneIndex === 0}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-200 transition"
          >
            <SkipBack className="w-4 h-4" />
          </button>

          <button
            onClick={togglePlay}
            className="px-5 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold flex items-center gap-2 shadow-lg shadow-amber-500/20 transition transform active:scale-95 text-sm"
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 fill-slate-950" />}
            <span>{isPlaying ? '暫停播放' : '播放 Vyond 2D 動畫分鏡'}</span>
          </button>

          <button
            onClick={() => {
              if (activeSceneIndex < project.scenes.length - 1) onSceneChange(activeSceneIndex + 1);
            }}
            disabled={activeSceneIndex === project.scenes.length - 1}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-200 transition"
          >
            <SkipForward className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
