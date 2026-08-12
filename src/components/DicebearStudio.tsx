import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { Play, Pause, Download, Sparkles, RefreshCw, Volume2, Video, Shuffle, Sparkle, BookOpen, Monitor, FileText, Subtitles } from 'lucide-react';
import { speakText, stopSpeaking, testVoiceInstant, ULTRA_REALISTIC_VOICES } from '../services/ttsService';
import { drawCanvasSubtitles, downloadSRTFile } from '../services/subtitleService';

export interface DicebearScene {
  id: string;
  title: string;
  characterName: string;
  seed: string;
  style: 'lorelei' | 'avataaars' | 'personas' | 'bottts' | 'fun-emoji';
  dialog: string;
  bgImageUrl: string;
  displacementScale: number;
}

const CLASSICAL_DICEBEAR_SCENES: DicebearScene[] = [
  {
    id: 'dicebear-scene-1',
    title: '第一幕：叮嚀與出發 (Dicebear 小紅帽)',
    characterName: '小紅帽',
    seed: 'LittleRedHood_Girl',
    style: 'lorelei',
    dialog: '在寧靜的小鎮裡，小紅帽準備穿過森林去探望生病的外婆。媽媽遞給她一籃糕點與葡萄酒，溫柔叮嚀：『親愛的孩子，路上千萬別離開小徑，也不要和陌生人說話喔！』',
    bgImageUrl: '/assets/bg_forest.png',
    displacementScale: 0.2
  },
  {
    id: 'dicebear-scene-2',
    title: '第二幕：森林巧遇大灰狼 (Dicebear 狼影)',
    characterName: '大灰狼',
    seed: 'BigBadWolf_Monster',
    style: 'bottts',
    dialog: '小紅帽提著籃子走在陽光灑落的森林小徑上，狡猾的大灰狼悄悄靠近，露出親切的笑容問：『可愛的小紅帽，你要去哪裡呀？要不要採一些美麗的花朵送給外婆呢？』',
    bgImageUrl: '/assets/bg_forest.png',
    displacementScale: 0.2
  },
  {
    id: 'dicebear-scene-3',
    title: '第三幕：外婆家小木屋 (Dicebear 外婆)',
    characterName: '外婆',
    seed: 'Grandma_Lady',
    style: 'personas',
    dialog: '大灰狼騙小紅帽去採花後，便急忙跑到外婆的小木屋，推開門吞下了可憐的外婆，並戴上外婆的睡帽與眼鏡，偷偷躺在床上假扮成外婆！',
    bgImageUrl: '/assets/bg_cabin.png',
    displacementScale: 0.2
  },
  {
    id: 'dicebear-scene-4',
    title: '第四幕：臥室問答 (Dicebear 假外婆)',
    characterName: '假外婆 (大灰狼)',
    seed: 'BigBadWolf_InBed',
    style: 'bottts',
    dialog: '小紅帽走進臥室來到床邊，疑惑地問：『外婆，你的耳朵怎麼這麼大呀？』大灰狼壓低聲音說：『這樣才能聽清楚你的聲音呀！』，說完大灰狼便猛地撲了過來！',
    bgImageUrl: '/assets/bg_cabin.png',
    displacementScale: 0.2
  },
  {
    id: 'dicebear-scene-5',
    title: '第五幕：獵人救援 (Dicebear 獵人)',
    characterName: '勇敢的獵人',
    seed: 'BraveHunter_Man',
    style: 'avataaars',
    dialog: '正當危急時刻，路過木屋的勇敢獵人衝進房內制服了大灰狼，成功救出了外婆與小紅帽！大家圍在桌旁品嚐糕點，故事有了平安快樂的結局！',
    bgImageUrl: '/assets/bg_cabin.png',
    displacementScale: 0.2
  }
];

const NORTH_WIND_DICEBEAR_SCENES: DicebearScene[] = [
  {
    id: 'dicebear-wind-1',
    title: '第一幕：北風與太陽的爭論 (Dicebear 故事)',
    characterName: '北風與太陽',
    seed: 'NorthWind_Gust',
    style: 'bottts',
    dialog: '在蔚藍的天空中，狂傲的北風正向溫和的太陽吹噓自己的力量：『我是世界上最強大的！你看，那條山道上有個穿著厚大衣的旅人，誰能先讓他脫下大衣，誰就是贏家！』',
    bgImageUrl: '/assets/bg_mountain.png',
    displacementScale: 0.2
  },
  {
    id: 'dicebear-wind-2',
    title: '第二幕：北風發威狂風呼嘯',
    characterName: '呼嘯的北風',
    seed: 'FreezingWind_Cold',
    style: 'bottts',
    dialog: '北風吸足了一口氣，使勁向旅人吹去！狂風呼呼作響、寒風刺骨。然而，北風越吹得兇猛，旅人就把厚大衣裹得越緊，死死不肯鬆手！',
    bgImageUrl: '/assets/bg_mountain.png',
    displacementScale: 0.2
  },
  {
    id: 'dicebear-wind-3',
    title: '第三幕：太陽發出溫暖光芒',
    characterName: '溫暖的太陽',
    seed: 'WarmSun_Smile',
    style: 'fun-emoji',
    dialog: '北風吹得筋疲力竭只能放棄。此時，太陽從雲端露出了燦爛的微笑，向大地散發出溫和耀眼的陽光與暖意。',
    bgImageUrl: '/assets/bg_mountain.png',
    displacementScale: 0.2
  },
  {
    id: 'dicebear-wind-4',
    title: '第四幕：旅人熱得脫下大衣',
    characterName: '擦汗的旅人',
    seed: 'HotTraveler_Man',
    style: 'lorelei',
    dialog: '隨著太陽的光照越來越溫暖，旅人開始熱得不斷擦汗。他擦了擦額頭上的汗水，高興地脫下了厚重的大衣，坐在樹蔭下涼快地休息！',
    bgImageUrl: '/assets/bg_mountain.png',
    displacementScale: 0.2
  },
  {
    id: 'dicebear-wind-5',
    title: '第五幕：寓言啟示 - 溫柔勝過強迫',
    characterName: '太陽與北風大團圓',
    seed: 'SunAndWind_Friends',
    style: 'lorelei',
    dialog: '勝負揭曉！太陽溫柔地對北風說：『看到了吧？溫和與關懷的力量，往往比暴力與強迫更能打動人心。』這就是經典伊索寓言「北風與太陽」教導我們的智慧。',
    bgImageUrl: '/assets/bg_mountain.png',
    displacementScale: 0.2
  }
];

export const DicebearStudio: React.FC = () => {
  const mountRef = useRef<HTMLDivElement | null>(null);
  const overlayCanvasRef = useRef<HTMLCanvasElement | null>(null);

  const [selectedStory, setSelectedStory] = useState<'wind_and_sun' | 'red_riding_hood'>('wind_and_sun');
  const [scenes, setScenes] = useState<DicebearScene[]>(NORTH_WIND_DICEBEAR_SCENES);
  const [activeSceneIndex, setActiveSceneIndex] = useState(0);
  const [selectedVoiceId, setSelectedVoiceId] = useState('vits-custom-female-ownwts6r7hq');
  const [isPlaying, setIsPlaying] = useState(false);
  const [isTestingVoice, setIsTestingVoice] = useState(false);
  const [enableSubtitles, setEnableSubtitles] = useState(true);
  const [depthScale] = useState(0.15);
  const [cameraMode, setCameraMode] = useState<'flat_static' | 'flat_pan' | 'flat_zoom' | 'orbit_360'>('flat_static');
  const [isExporting, setIsExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);
  const [exportedUrl, setExportedUrl] = useState<string | null>(null);
  const [exportFilename, setExportFilename] = useState<string>('dicebear_story.mp4');

  const currentScene = scenes[activeSceneIndex];
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);

  const handleStoryChange = (story: 'wind_and_sun' | 'red_riding_hood') => {
    setSelectedStory(story);
    if (story === 'red_riding_hood') {
      setScenes(CLASSICAL_DICEBEAR_SCENES);
    } else {
      setScenes(NORTH_WIND_DICEBEAR_SCENES);
    }
    setActiveSceneIndex(0);
  };

  const handleInstantVoiceTest = async () => {
    setIsTestingVoice(true);
    await testVoiceInstant(selectedVoiceId);
    setIsTestingVoice(false);
  };

  const getDicebearPngUrl = (style: string, seed: string): string => {
    return `https://api.dicebear.com/7.x/${style}/png?seed=${encodeURIComponent(seed)}&size=512&scale=90`;
  };

  const randomizeCurrentSeed = () => {
    const updated = [...scenes];
    updated[activeSceneIndex].seed = `seed_${Math.floor(Math.random() * 1000000)}`;
    setScenes(updated);
  };

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth;
    const height = container.clientHeight;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0f1d);

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 1.05, 3.6);
    camera.lookAt(0, 1.05, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    rendererRef.current = renderer;

    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    // Create 2D Canvas for AutoSubs Subtitle Overlay
    const overlayCanvas = document.createElement('canvas');
    overlayCanvas.width = width;
    overlayCanvas.height = height;
    overlayCanvas.style.position = 'absolute';
    overlayCanvas.style.top = '0';
    overlayCanvas.style.left = '0';
    overlayCanvas.style.pointerEvents = 'none';
    container.appendChild(overlayCanvas);
    overlayCanvasRef.current = overlayCanvas;

    const ambient = new THREE.AmbientLight(0xffffff, 1.0);
    scene.add(ambient);

    const sun = new THREE.DirectionalLight(0xfef08a, 1.5);
    sun.position.set(2, 5, 4);
    scene.add(sun);

    const textureLoader = new THREE.TextureLoader();
    textureLoader.setCrossOrigin('anonymous');

    const bgTexture = textureLoader.load(currentScene.bgImageUrl);
    const bgGeo = new THREE.PlaneGeometry(8.5, 5.0);
    const bgMat = new THREE.MeshBasicMaterial({ map: bgTexture });
    const bgMesh = new THREE.Mesh(bgGeo, bgMat);
    bgMesh.position.z = -1.8;
    scene.add(bgMesh);

    const characterGroup = new THREE.Group();
    characterGroup.position.y = 1.05;
    scene.add(characterGroup);

    const dicebearPngUrl = getDicebearPngUrl(currentScene.style, currentScene.seed);

    textureLoader.load(
      dicebearPngUrl,
      (charTex) => {
        const planeWidth = 2.4;
        const planeHeight = 2.4;
        const charGeo = new THREE.PlaneGeometry(planeWidth, planeHeight, 32, 32);

        const charMat = new THREE.MeshStandardMaterial({
          map: charTex,
          displacementMap: charTex,
          displacementScale: depthScale,
          displacementBias: -0.02,
          transparent: true,
          alphaTest: 0.1,
          roughness: 0.4,
          metalness: 0.0,
          side: THREE.DoubleSide
        });

        const charMesh = new THREE.Mesh(charGeo, charMat);
        charMesh.castShadow = true;
        charMesh.receiveShadow = true;
        characterGroup.add(charMesh);
      }
    );

    let clock = new THREE.Clock();
    let animationId: number;

    const renderLoop = () => {
      animationId = requestAnimationFrame(renderLoop);
      const time = clock.getElapsedTime();

      if (isPlaying || isTestingVoice) {
        characterGroup.position.y = 1.05 + Math.sin(time * 5) * 0.04;
        characterGroup.rotation.z = Math.sin(time * 3) * 0.03;
      } else {
        characterGroup.position.y = 1.05 + Math.sin(time * 1.5) * 0.015;
        characterGroup.rotation.z = 0;
      }

      if (cameraMode === 'flat_static') {
        camera.position.set(0, 1.05, 3.6);
        camera.rotation.set(0, 0, 0);
        camera.lookAt(0, 1.05, 0);
      } else if (cameraMode === 'flat_pan') {
        camera.position.x = Math.sin(time * 0.4) * 0.2;
        camera.position.y = 1.05;
        camera.position.z = 3.6;
        camera.lookAt(0, 1.05, 0);
      } else if (cameraMode === 'flat_zoom') {
        const zoom = Math.sin(time * 0.4) * 0.15;
        camera.position.set(0, 1.05, 3.6 - zoom);
        camera.lookAt(0, 1.05, 0);
      } else {
        const radius = 3.6;
        const angle = time * 0.6;
        camera.position.x = Math.sin(angle) * radius;
        camera.position.z = Math.cos(angle) * radius;
        camera.lookAt(0, 1.05, 0);
      }

      renderer.render(scene, camera);

      // Render AutoSubs Subtitles onto Overlay Canvas & Burn into Video
      const ctx = overlayCanvas.getContext('2d');
      if (ctx) {
        ctx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
        if (enableSubtitles) {
          drawCanvasSubtitles(ctx, overlayCanvas.width, overlayCanvas.height, currentScene.dialog);
        }
      }
    };

    renderLoop();

    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
      overlayCanvas.width = w;
      overlayCanvas.height = h;
    };

    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener('resize', handleResize);
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
      if (container.contains(overlayCanvas)) {
        container.removeChild(overlayCanvas);
      }
    };
  }, [currentScene, isPlaying, isTestingVoice, depthScale, cameraMode, enableSubtitles]);

  const togglePlay = async () => {
    if (isPlaying) {
      setIsPlaying(false);
      stopSpeaking();
    } else {
      setIsPlaying(true);
      await speakText(currentScene.dialog, selectedVoiceId);
      setIsPlaying(false);
    }
  };

  const handleExportSampleVideo = async () => {
    const renderer = rendererRef.current;
    const overlayCanvas = overlayCanvasRef.current;
    if (!renderer || !overlayCanvas) return;

    setIsExporting(true);
    setExportProgress(5);

    const width = renderer.domElement.width;
    const height = renderer.domElement.height;
    const compositeCanvas = document.createElement('canvas');
    compositeCanvas.width = width;
    compositeCanvas.height = height;
    const compCtx = compositeCanvas.getContext('2d')!;

    const compStream = compositeCanvas.captureStream(30);
    const mediaRecorder = new MediaRecorder(compStream, { mimeType: 'video/webm;codecs=vp9' });
    const chunks: Blob[] = [];

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      const webmBlob = new Blob(chunks, { type: 'video/webm' });

      // Attempt FFmpeg MP4 Server Conversion for 100% Standard H.264 MP4
      try {
        const res = await fetch('http://localhost:9880/convert_mp4', {
          method: 'POST',
          body: webmBlob
        });

        if (res.ok) {
          const mp4Blob = await res.blob();
          const url = URL.createObjectURL(mp4Blob);
          const name = `${selectedStory}_dicebear.mp4`;
          setExportedUrl(url);
          setExportFilename(name);
          setIsExporting(false);
          setExportProgress(100);

          const a = document.createElement('a');
          a.href = url;
          a.download = name;
          document.body.appendChild(a);
          a.click();
          setTimeout(() => {
            if (document.body.contains(a)) document.body.removeChild(a);
          }, 1000);
          return;
        }
      } catch (err) {
        console.log('FFmpeg MP4 converter server offline, saving as WebM container...');
      }

      const url = URL.createObjectURL(webmBlob);
      const name = `${selectedStory}_dicebear.webm`;
      setExportedUrl(url);
      setExportFilename(name);
      setIsExporting(false);
      setExportProgress(100);

      const a = document.createElement('a');
      a.href = url;
      a.download = name;
      document.body.appendChild(a);
      a.click();
      setTimeout(() => {
        if (document.body.contains(a)) document.body.removeChild(a);
      }, 1000);
    };

    mediaRecorder.start();

    for (let sIdx = 0; sIdx < scenes.length; sIdx++) {
      setActiveSceneIndex(sIdx);
      const scene = scenes[sIdx];
      
      speakText(scene.dialog, selectedVoiceId);

      for (let f = 0; f < 180; f++) {
        compCtx.drawImage(renderer.domElement, 0, 0);
        compCtx.drawImage(overlayCanvas, 0, 0);

        setExportProgress(Math.round(((sIdx * 180 + f) / (scenes.length * 180)) * 95));
        await new Promise((r) => setTimeout(r, 1000 / 30));
      }
    }

    mediaRecorder.stop();
  };

  return (
    <div className="max-w-7xl mx-auto p-4 md:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      {/* Left Column */}
      <section className="lg:col-span-7 space-y-5">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-2xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-500 via-pink-500 to-amber-500 flex items-center justify-center text-white shadow-lg shadow-purple-500/20">
                <BookOpen className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  Dicebear 開源向量童話故事生成器
                  <span className="text-xs bg-emerald-500/20 text-emerald-300 px-2.5 py-0.5 rounded-full border border-emerald-500/30 font-bold flex items-center gap-1">
                    <Subtitles className="w-3.5 h-3.5" />
                    AutoSubs 自動字幕
                  </span>
                </h2>
                <p className="text-xs text-slate-400">已調整為全平面靜態定鏡（零旋轉暈眩）與 AI 生成高畫質童話背景！</p>
              </div>
            </div>

            {/* Story Switcher Dropdown */}
            <div className="flex items-center gap-2">
              <label className="text-xs font-bold text-slate-300">選擇童話故事:</label>
              <select
                value={selectedStory}
                onChange={(e) => handleStoryChange(e.target.value as any)}
                className="bg-purple-950 border border-purple-500 text-purple-200 font-bold text-xs rounded-xl p-2 focus:outline-none"
              >
                <option value="wind_and_sun">🌬️ ☀️ 北風與太陽 (The North Wind and Sun)</option>
                <option value="red_riding_hood">👧 🐺 正統小紅帽 (Little Red Riding Hood)</option>
              </select>
            </div>
          </div>

          {/* Dicebear Preview & Controls */}
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-bold text-amber-300 flex items-center gap-1.5">
                <Sparkle className="w-4 h-4 text-amber-400" />
                Dicebear 即時 2D 圖片預覽 (種子: {currentScene.seed})
              </span>
              <button
                onClick={randomizeCurrentSeed}
                className="flex items-center gap-1 px-3 py-1.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold rounded-xl shadow-md transition transform active:scale-95"
              >
                <Shuffle className="w-3.5 h-3.5" />
                一鍵隨機換造型
              </button>
            </div>

            <div className="flex items-center gap-4 bg-slate-900/80 p-3 rounded-xl border border-slate-800">
              <div className="w-20 h-20 bg-slate-950 rounded-xl border border-purple-500/40 p-1 flex items-center justify-center shrink-0 shadow-inner">
                <img
                  src={getDicebearPngUrl(currentScene.style, currentScene.seed)}
                  alt={currentScene.characterName}
                  className="w-full h-full object-contain"
                />
              </div>

              <div className="flex-1 space-y-2">
                <div>
                  <label className="block text-slate-400 mb-1 font-semibold">角色種子 (Seed 名稱):</label>
                  <input
                    type="text"
                    value={currentScene.seed}
                    onChange={(e) => {
                      const updated = [...scenes];
                      updated[activeSceneIndex].seed = e.target.value;
                      setScenes(updated);
                    }}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-white focus:outline-none focus:border-purple-500 text-xs font-mono"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1 font-semibold">Dicebear 開源風格 Style:</label>
                  <select
                    value={currentScene.style}
                    onChange={(e) => {
                      const updated = [...scenes];
                      updated[activeSceneIndex].style = e.target.value as any;
                      setScenes(updated);
                    }}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-white focus:outline-none focus:border-purple-500 text-xs"
                  >
                    <option value="lorelei">Lorelei (Q版可愛童話向量角色)</option>
                    <option value="avataaars">Avataaars (美式向量角色)</option>
                    <option value="personas">Personas (扁平簡約風)</option>
                    <option value="bottts">Bottts (北風與怪獸角色)</option>
                    <option value="fun-emoji">Fun-Emoji (太陽表情風)</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Voice Selector with Instant Test Button */}
          <div className="space-y-1.5 text-xs">
            <label className="block text-slate-300 font-bold flex items-center gap-1">
              <Volume2 className="w-4 h-4 text-amber-400" />
              發音語音選單 (可切換不同音色):
            </label>
            <div className="flex items-center gap-2">
              <select
                value={selectedVoiceId}
                onChange={(e) => setSelectedVoiceId(e.target.value)}
                className="flex-1 bg-slate-950 border border-slate-700/80 rounded-xl p-2.5 text-slate-100 focus:border-amber-500 focus:outline-none font-bold"
              >
                {ULTRA_REALISTIC_VOICES.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.displayName}
                  </option>
                ))}
              </select>

              {/* Instant Test Button (Only speaks "你好") */}
              <button
                onClick={handleInstantVoiceTest}
                disabled={isTestingVoice}
                className="px-4 py-2.5 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-slate-950 font-bold rounded-xl shadow-lg shadow-amber-500/20 transition flex items-center gap-1.5 shrink-0 active:scale-95"
              >
                <Volume2 className="w-4 h-4" />
                <span>{isTestingVoice ? '發音中...' : '🔊 試聽音色 (你好)'}</span>
              </button>
            </div>
          </div>

          {/* Current Dialog Editor */}
          <div className="space-y-2">
            <label className="block text-xs font-bold text-slate-300 flex items-center justify-between">
              <span>童話劇本與發音對話 (可自由編輯)</span>
              <span className="text-purple-400 font-bold">登場角色：{currentScene.characterName}</span>
            </label>
            <textarea
              value={currentScene.dialog}
              onChange={(e) => {
                const updated = [...scenes];
                updated[activeSceneIndex].dialog = e.target.value;
                setScenes(updated);
              }}
              rows={3}
              className="w-full bg-slate-950 border border-slate-700/80 rounded-xl p-3 text-slate-100 text-sm focus:border-purple-500 focus:outline-none transition resize-none"
            />
          </div>
        </div>

        {/* Scene List */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-sm text-slate-200 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-purple-400" />
              【{selectedStory === 'wind_and_sun' ? '北風與太陽' : '正統小紅帽'}】2D 全平面分鏡列表 ({scenes.length})
            </h3>

            {/* SRT Download Button */}
            <button
              onClick={() => downloadSRTFile(scenes, `${selectedStory}_subtitles.srt`)}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-amber-300 font-bold text-xs rounded-xl border border-amber-500/30 transition shadow-md"
            >
              <FileText className="w-3.5 h-3.5" />
              下載 SRT 字幕檔 (.srt)
            </button>
          </div>

          <div className="space-y-2.5">
            {scenes.map((scene, idx) => (
              <div
                key={scene.id}
                onClick={() => setActiveSceneIndex(idx)}
                className={`p-4 rounded-2xl border transition cursor-pointer flex items-center justify-between gap-4 ${
                  idx === activeSceneIndex
                    ? 'bg-purple-950/40 border-purple-500 ring-2 ring-purple-500/40 shadow-lg'
                    : 'bg-slate-900/60 border-slate-800 hover:bg-slate-800/50'
                }`}
              >
                <div className="flex items-center gap-3">
                  <img src={getDicebearPngUrl(scene.style, scene.seed)} alt={scene.characterName} className="w-10 h-10 object-contain rounded-lg bg-slate-950 border border-slate-800" />
                  <div>
                    <h4 className="font-bold text-sm text-white">{scene.title}</h4>
                    <p className="text-xs text-slate-400 line-clamp-1 mt-0.5">{scene.dialog}</p>
                  </div>
                </div>

                <div className="text-xs font-semibold text-purple-400 bg-purple-500/10 px-3 py-1 rounded-full border border-purple-500/20 shrink-0">
                  {scene.characterName}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Right Column */}
      <section className="lg:col-span-5 lg:sticky lg:top-20 space-y-4">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-2xl space-y-4">
          <div className="flex flex-col gap-2 text-xs text-slate-400">
            <div className="flex items-center justify-between">
              <span className="font-bold text-slate-200 flex items-center gap-1.5">
                <Monitor className="w-4 h-4 text-purple-400" />
                全平面 2D 定鏡視窗 (零暈眩)
              </span>

              <button
                onClick={() => setEnableSubtitles(!enableSubtitles)}
                className={`flex items-center gap-1 px-2.5 py-1 rounded-lg font-bold transition ${
                  enableSubtitles
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                    : 'bg-slate-800 text-slate-400'
                }`}
              >
                <Subtitles className="w-3.5 h-3.5" />
                AutoSubs 字幕: {enableSubtitles ? '開啟' : '關閉'}
              </button>
            </div>

            {/* Camera View Mode Controls: Flat Static Default */}
            <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 space-y-2">
              <label className="block text-[11px] font-bold text-slate-300">選擇視角鏡頭模式 (防暈眩)：</label>
              <div className="grid grid-cols-2 gap-1.5 text-[11px]">
                <button
                  onClick={() => setCameraMode('flat_static')}
                  className={`p-2 rounded-lg font-bold transition text-left ${
                    cameraMode === 'flat_static' ? 'bg-emerald-600 text-white' : 'bg-slate-900 text-slate-400'
                  }`}
                >
                  📺 全平面 2D 定鏡 (預設推薦)
                </button>

                <button
                  onClick={() => setCameraMode('flat_pan')}
                  className={`p-2 rounded-lg font-bold transition text-left ${
                    cameraMode === 'flat_pan' ? 'bg-emerald-600 text-white' : 'bg-slate-900 text-slate-400'
                  }`}
                >
                  ↔️ 2D 橫向微速平移
                </button>

                <button
                  onClick={() => setCameraMode('flat_zoom')}
                  className={`p-2 rounded-lg font-bold transition text-left ${
                    cameraMode === 'flat_zoom' ? 'bg-emerald-600 text-white' : 'bg-slate-900 text-slate-400'
                  }`}
                >
                  🔍 2D 靜態特寫
                </button>

                <button
                  onClick={() => setCameraMode('orbit_360')}
                  className={`p-2 rounded-lg font-bold transition text-left ${
                    cameraMode === 'orbit_360' ? 'bg-purple-600 text-white' : 'bg-slate-900 text-slate-400'
                  }`}
                >
                  🔄 360° 環繞 (舊版)
                </button>
              </div>
            </div>
          </div>

          <div ref={mountRef} className="w-full aspect-[4/3] bg-black rounded-xl overflow-hidden border border-slate-800 relative shadow-2xl" />

          <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 text-center">
            <p className="text-xs text-amber-300 font-bold tracking-wide leading-relaxed">
              「{currentScene.dialog}」
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={togglePlay}
              className="flex-1 py-3 bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600 text-white font-bold rounded-xl shadow-lg shadow-purple-500/20 transition flex items-center justify-center gap-2 text-sm"
            >
              {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              <span>{isPlaying ? '暫停 2D 配音' : '朗讀當前分鏡對話'}</span>
            </button>

            <button
              onClick={handleExportSampleVideo}
              disabled={isExporting}
              className="flex-1 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-slate-950 font-bold rounded-xl shadow-lg shadow-emerald-500/20 transition flex items-center justify-center gap-2 text-sm"
            >
              {isExporting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Video className="w-4 h-4" />}
              <span>{isExporting ? `${exportProgress}% 合成 MP4 中` : '🎬 自動合成並下載 MP4'}</span>
            </button>
          </div>

          {exportedUrl && (
            <div className="text-center pt-2">
              <a
                href={exportedUrl}
                download={exportFilename}
                className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-slate-950 font-bold rounded-xl text-sm shadow-xl shadow-emerald-500/20 transition transform active:scale-95"
              >
                <Download className="w-5 h-5" />
                重新下載影片檔 ({exportFilename})
              </a>
            </div>
          )}
        </div>
      </section>
    </div>
  );
};
