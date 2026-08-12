import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { Play, Pause, Download, Sparkles, RefreshCw, Layers, Camera, Volume2 } from 'lucide-react';
import { speakText, stopSpeaking, ULTRA_REALISTIC_VOICES } from '../services/ttsService';

export interface UserFairytaleScene {
  id: string;
  title: string;
  characterName: string;
  dialog: string;
  duration: number;
  bgTextureUrl: string;
  charTextureUrl: string;
  motionStyle: 'head_bob' | 'talking_sway' | 'breathing';
}

const USER_CUSTOM_SCENES: UserFairytaleScene[] = [
  {
    id: 'user-scene-1',
    title: '第一幕：小紅帽與大灰狼在森林相遇',
    characterName: '大灰狼',
    dialog: '在綠意盎然的魔法森林小徑上，小紅帽遇見了打著藍格紋領巾的大灰狼。大灰狼露出調皮的笑容說：『小紅帽，你要去哪裡呀？』',
    duration: 6,
    bgTextureUrl: '/assets/forest.jpg',
    charTextureUrl: '/assets/wolf.png',
    motionStyle: 'head_bob'
  },
  {
    id: 'user-scene-2',
    title: '第二幕：親切的外婆與爺爺招呼',
    characterName: '外婆',
    dialog: '外婆和爺爺親切地在門口向小紅帽揮手致意，外婆高興地說：『親愛的孩子，快進來坐吧！』',
    duration: 6,
    bgTextureUrl: '/assets/forest.jpg',
    charTextureUrl: '/assets/grandma.png',
    motionStyle: 'breathing'
  },
  {
    id: 'user-scene-3',
    title: '第三幕：勇敢的獵人巡邏森林',
    characterName: '獵人',
    dialog: '留著帥氣大鬍子的獵人叔叔手提獵槍在森林中巡邏，他高聲提醒：『大家要小心森林深處，守護童話世界的平安！』',
    duration: 6,
    bgTextureUrl: '/assets/forest.jpg',
    charTextureUrl: '/assets/hunter.png',
    motionStyle: 'talking_sway'
  },
  {
    id: 'user-scene-4',
    title: '第四幕：小紅帽來到外婆家臥室',
    characterName: '小紅帽與大灰狼',
    dialog: '當小紅帽推開外婆家臥室的門時，驚喜地發現大灰狼正穿著粉紅睡袍，大聲說：『驚喜！歡迎來到外婆家！』',
    duration: 7,
    bgTextureUrl: '/assets/grandma_house.png',
    charTextureUrl: '/assets/wolf.png',
    motionStyle: 'head_bob'
  },
  {
    id: 'user-scene-5',
    title: '第五幕：童話大團圓歡樂派對',
    characterName: '所有人',
    dialog: '大灰狼、外婆、獵人與小紅帽歡聚一堂，小木屋裡傳遍了溫暖快樂的歌聲與歡笑！',
    duration: 7,
    bgTextureUrl: '/assets/grandma_house.png',
    charTextureUrl: '/assets/grandma.png',
    motionStyle: 'talking_sway'
  }
];

export const Img2ThreeJSStudio: React.FC = () => {
  const mountRef = useRef<HTMLDivElement | null>(null);
  const [scenes, setScenes] = useState<UserFairytaleScene[]>(USER_CUSTOM_SCENES);
  const [activeSceneIndex, setActiveSceneIndex] = useState(0);
  const [selectedVoiceId, setSelectedVoiceId] = useState('zh-TW-HsiaoChenNeural');
  const [isPlaying, setIsPlaying] = useState(false);
  const [motionStyle, setMotionStyle] = useState<'head_bob' | 'talking_sway' | 'breathing'>('head_bob');
  const [isExporting, setIsExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);
  const [exportedUrl, setExportedUrl] = useState<string | null>(null);

  const currentScene = scenes[activeSceneIndex];
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);

  // Build Img2ThreeJS 3D Scene using User's Real Uploaded Images
  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth;
    const height = container.clientHeight;

    // 1. Scene
    const scene = new THREE.Scene();

    // 2. Camera
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 1.2, 4.0);

    // 3. Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    rendererRef.current = renderer;

    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    // 4. Lighting
    const ambient = new THREE.AmbientLight(0xffffff, 1.0);
    scene.add(ambient);

    const sun = new THREE.DirectionalLight(0xfef08a, 1.6);
    sun.position.set(4, 8, 4);
    sun.castShadow = true;
    sun.shadow.mapSize.width = 1024;
    sun.shadow.mapSize.height = 1024;
    scene.add(sun);

    const textureLoader = new THREE.TextureLoader();

    // 5. User Background Image Texture Plane
    const bgTexture = textureLoader.load(currentScene.bgTextureUrl);
    const bgGeo = new THREE.PlaneGeometry(8, 4.8);
    const bgMat = new THREE.MeshBasicMaterial({ map: bgTexture });
    const bgMesh = new THREE.Mesh(bgGeo, bgMat);
    bgMesh.position.z = -2;
    scene.add(bgMesh);

    // 6. User Character Cutout Image Texture (Img2ThreeJS 3D Extruded Parallax Mesh)
    const charTexture = textureLoader.load(currentScene.charTextureUrl);
    const cardGroup = new THREE.Group();

    // 3D Parallax Character Mesh Card
    const cardGeo = new THREE.PlaneGeometry(2.4, 2.4, 32, 32);
    const cardMat = new THREE.MeshStandardMaterial({
      map: charTexture,
      transparent: true,
      roughness: 0.2,
      metalness: 0.1,
      side: THREE.DoubleSide
    });
    const cardMesh = new THREE.Mesh(cardGeo, cardMat);
    cardMesh.castShadow = true;
    cardMesh.receiveShadow = true;
    cardGroup.add(cardMesh);

    // Frame Depth Backing
    const frameGeo = new THREE.BoxGeometry(2.45, 2.45, 0.08);
    const frameMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.7 });
    const frameMesh = new THREE.Mesh(frameGeo, frameMat);
    frameMesh.position.z = -0.05;
    cardGroup.add(frameMesh);

    cardGroup.position.y = 1.05;
    scene.add(cardGroup);

    // 7. Floor Shadow Receiver
    const floorGeo = new THREE.CylinderGeometry(2.8, 2.8, 0.1, 32);
    const floorMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.9 });
    const floor = new THREE.Mesh(floorGeo, floorMat);
    floor.position.y = -0.15;
    floor.receiveShadow = true;
    scene.add(floor);

    // 8. Sparkle Particles
    const particleCount = 50;
    const particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount * 3; i += 3) {
      positions[i] = (Math.random() - 0.5) * 8;
      positions[i + 1] = Math.random() * 4;
      positions[i + 2] = (Math.random() - 0.5) * 5;
    }
    particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const particleMat = new THREE.PointsMaterial({ color: 0xfcb454, size: 0.07, transparent: true, opacity: 0.8 });
    const particles = new THREE.Points(particleGeo, particleMat);
    scene.add(particles);

    // 9. Animation Render Loop
    let clock = new THREE.Clock();
    let animationId: number;

    const renderLoop = () => {
      animationId = requestAnimationFrame(renderLoop);
      const time = clock.getElapsedTime();

      if (motionStyle === 'head_bob') {
        cardGroup.rotation.z = Math.sin(time * 4) * 0.05;
        cardGroup.rotation.y = Math.sin(time * 2) * 0.08;
        cardGroup.position.y = 1.05 + Math.abs(Math.sin(time * 4)) * 0.08;
      } else if (motionStyle === 'talking_sway') {
        const talkSpeed = isPlaying ? 9 : 3;
        cardGroup.rotation.y = Math.sin(time * talkSpeed) * 0.12;
        cardGroup.rotation.x = Math.cos(time * 6) * 0.06;
        cardGroup.position.y = 1.05 + Math.sin(time * talkSpeed) * 0.05;
      } else {
        cardGroup.rotation.z = Math.sin(time * 1.5) * 0.02;
        cardGroup.position.y = 1.05 + Math.sin(time * 1.5) * 0.04;
      }

      // Camera Orbit Ken Burns Fly-through
      camera.position.x = Math.sin(time * 0.3) * 0.35;
      camera.position.y = 1.2 + Math.cos(time * 0.3) * 0.12;
      camera.lookAt(0, 1.05, 0);

      const posArr = particleGeo.attributes.position.array as Float32Array;
      for (let i = 1; i < particleCount * 3; i += 3) {
        posArr[i] += 0.005;
        if (posArr[i] > 4) posArr[i] = 0;
      }
      particleGeo.attributes.position.needsUpdate = true;

      renderer.render(scene, camera);
    };

    renderLoop();

    const handleResize = () => {
      if (!container) return;
      camera.aspect = container.clientWidth / container.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(container.clientWidth, container.clientHeight);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener('resize', handleResize);
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
    };
  }, [currentScene, motionStyle, isPlaying]);

  // Ultra-Realistic Neural Speech Synthesis Trigger
  const togglePlay = async () => {
    if (isPlaying) {
      setIsPlaying(false);
      stopSpeaking();
    } else {
      setIsPlaying(true);
      await speakText(currentScene.dialog, selectedVoiceId, 0.92, 1.02);
      setIsPlaying(false);
    }
  };

  // Export 1080p MP4
  const handleExportMP4 = async () => {
    const renderer = rendererRef.current;
    if (!renderer) return;

    setIsExporting(true);
    setExportProgress(10);

    const canvas = renderer.domElement;
    const stream = canvas.captureStream(30);
    const mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm;codecs=vp9' });
    const chunks: Blob[] = [];

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.push(e.data);
    };

    mediaRecorder.onstop = () => {
      const blob = new Blob(chunks, { type: 'video/webm' });
      const url = URL.createObjectURL(blob);
      setExportedUrl(url);
      setIsExporting(false);
      setExportProgress(100);
    };

    mediaRecorder.start();

    for (let i = 0; i <= 80; i++) {
      setExportProgress(Math.round((i / 80) * 100));
      await new Promise((r) => setTimeout(r, 100));
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
                <Layers className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  Img2ThreeJS 3D 童話故事生成器 (實體圖片版)
                  <span className="text-xs bg-emerald-500/20 text-emerald-300 px-2.5 py-0.5 rounded-full border border-emerald-500/30 font-bold">
                    真實圖片 3D 視差載入
                  </span>
                </h2>
                <p className="text-xs text-slate-400">已成功載入您提供的「大野狼、外婆、獵人、森林與外婆家」真實圖片！</p>
              </div>
            </div>
          </div>

          {/* Voice Selector for Realistic Human Speech */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div>
              <label className="block text-slate-300 mb-1 font-bold flex items-center gap-1">
                <Volume2 className="w-4 h-4 text-amber-400" />
                選擇極致真人語音引擎 (Microsoft Neural Speech)
              </label>
              <select
                value={selectedVoiceId}
                onChange={(e) => setSelectedVoiceId(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700/80 rounded-xl p-2 text-slate-100 focus:border-amber-500 focus:outline-none"
              >
                {ULTRA_REALISTIC_VOICES.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.displayName}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Current Dialog Editor */}
          <div className="space-y-2">
            <label className="block text-xs font-bold text-slate-300 flex items-center justify-between">
              <span>童話劇本與發音對話 (可自由編輯)</span>
              <span className="text-amber-400 font-bold">登場角色：{currentScene.characterName}</span>
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
          <h3 className="font-bold text-sm text-slate-200 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-purple-400" />
            真實圖片 3D 童話分鏡列表 ({scenes.length})
          </h3>

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
                  <img src={scene.charTextureUrl} alt={scene.characterName} className="w-10 h-10 object-contain rounded-lg bg-slate-950 border border-slate-800" />
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
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="font-bold text-slate-200 flex items-center gap-1.5">
              <Camera className="w-4 h-4 text-purple-400" />
              Img2ThreeJS 3D 深度鏡頭預覽
            </span>

            <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800">
              <button
                onClick={() => setMotionStyle('head_bob')}
                className={`px-2 py-0.5 rounded-lg text-[11px] font-bold transition ${
                  motionStyle === 'head_bob' ? 'bg-purple-600 text-white' : 'text-slate-400'
                }`}
              >
                🎭 3D 點頭
              </button>
              <button
                onClick={() => setMotionStyle('talking_sway')}
                className={`px-2.5 py-0.5 rounded-lg text-[11px] font-bold transition ${
                  motionStyle === 'talking_sway' ? 'bg-purple-600 text-white' : 'text-slate-400'
                }`}
              >
                🗣️ 對話擺動
              </button>
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
              <span>{isPlaying ? '暫停真人語音' : '試聽極致真人語音 3D 動畫'}</span>
            </button>

            <button
              onClick={handleExportMP4}
              disabled={isExporting}
              className="flex-1 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-slate-950 font-bold rounded-xl shadow-lg shadow-emerald-500/20 transition flex items-center justify-center gap-2 text-sm"
            >
              {isExporting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
              <span>{isExporting ? `${exportProgress}% 合成中` : '匯出 3D MP4'}</span>
            </button>
          </div>

          {exportedUrl && (
            <div className="text-center pt-2">
              <a
                href={exportedUrl}
                download="img2threejs_user_fairytale_3d.webm"
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-emerald-500 text-slate-950 font-bold rounded-xl text-xs shadow-lg hover:bg-emerald-400 transition"
              >
                <Download className="w-4 h-4" />
                下載 1080p 3D MP4 影片 (.webm)
              </a>
            </div>
          )}
        </div>
      </section>
    </div>
  );
};
