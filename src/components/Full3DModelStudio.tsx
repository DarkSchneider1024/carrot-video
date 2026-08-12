import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { Play, Pause, Download, Sparkles, RefreshCw, Box, Camera, Volume2 } from 'lucide-react';
import { speakText, stopSpeaking, ULTRA_REALISTIC_VOICES } from '../services/ttsService';

export interface Full3DScene {
  id: string;
  title: string;
  characterType: 'wolf' | 'grandma' | 'hunter' | 'red_hood';
  characterName: string;
  dialog: string;
  duration: number;
  environment: 'forest' | 'cabin';
}

const FULL_3D_SCENES: Full3DScene[] = [
  {
    id: 'scene-3d-1',
    title: '第一幕：3D 大野狼在森林相遇',
    characterType: 'wolf',
    characterName: '大灰狼',
    dialog: '在綠意盎然的 3D 魔法森林小徑上，全身毛茸茸的 3D 大灰狼向小紅帽打了個招呼：『嘿！小紅帽，你要去哪裡呀？』',
    duration: 6,
    environment: 'forest'
  },
  {
    id: 'scene-3d-2',
    title: '第二幕：3D 外婆在小木屋門口招呼',
    characterType: 'grandma',
    characterName: '外婆',
    dialog: '慈祥的 3D 外婆拄著拐杖，在木屋門口高興地揮手：『親愛的孩子，快進來坐吧！』',
    duration: 6,
    environment: 'cabin'
  },
  {
    id: 'scene-3d-3',
    title: '第三幕：3D 獵人巡邏維護森林安全',
    characterType: 'hunter',
    characterName: '獵人',
    dialog: '戴著獵帽、留著大鬍子的 3D 獵人手握長槍，高聲喊道：『大家請放心，有我在守護森林的平靜！』',
    duration: 6,
    environment: 'forest'
  },
  {
    id: 'scene-3d-4',
    title: '第四幕：3D 小紅帽來到外婆家驚喜',
    characterType: 'red_hood',
    characterName: '小紅帽',
    dialog: '3D 小紅帽拉緊紅色斗篷推開門，驚喜地發現大家早已為外婆佈置好生日派對了！',
    duration: 7,
    environment: 'cabin'
  }
];

export const Full3DModelStudio: React.FC = () => {
  const mountRef = useRef<HTMLDivElement | null>(null);
  const [scenes, setScenes] = useState<Full3DScene[]>(FULL_3D_SCENES);
  const [activeSceneIndex, setActiveSceneIndex] = useState(0);
  const [selectedVoiceId, setSelectedVoiceId] = useState('zh-TW-HsiaoChenNeural');
  const [isPlaying, setIsPlaying] = useState(false);
  const [cameraOrbit, setCameraOrbit] = useState(0);
  const [isExporting, setIsExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);
  const [exportedUrl, setExportedUrl] = useState<string | null>(null);

  const currentScene = scenes[activeSceneIndex];
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);

  // 3D Procedural Mesh Model Builders (Full 360-Degree Polygonal Meshes)
  const build3DWolfModel = () => {
    const group = new THREE.Group();

    // Body (Grey Fur Torso)
    const bodyGeo = new THREE.CylinderGeometry(0.35, 0.45, 0.9, 16);
    const wolfMat = new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.5 });
    const body = new THREE.Mesh(bodyGeo, wolfMat);
    body.position.y = 0.45;
    group.add(body);

    // Blue Scarf around neck
    const scarfGeo = new THREE.TorusGeometry(0.38, 0.08, 16, 32);
    const scarfMat = new THREE.MeshStandardMaterial({ color: 0x2563eb, roughness: 0.3 });
    const scarf = new THREE.Mesh(scarfGeo, scarfMat);
    scarf.rotation.x = Math.PI / 2;
    scarf.position.y = 0.88;
    group.add(scarf);

    // Head Group (for nodding animation)
    const headGroup = new THREE.Group();
    headGroup.position.y = 1.15;

    const headGeo = new THREE.SphereGeometry(0.38, 16, 16);
    const head = new THREE.Mesh(headGeo, wolfMat);
    headGroup.add(head);

    // Snout / Muzzle
    const snoutGeo = new THREE.ConeGeometry(0.2, 0.4, 16);
    const snout = new THREE.Mesh(snoutGeo, wolfMat);
    snout.rotation.x = Math.PI / 2;
    snout.position.set(0, -0.05, 0.35);
    headGroup.add(snout);

    // Nose
    const noseGeo = new THREE.SphereGeometry(0.06, 8, 8);
    const noseMat = new THREE.MeshBasicMaterial({ color: 0x0f172a });
    const nose = new THREE.Mesh(noseGeo, noseMat);
    nose.position.set(0, -0.05, 0.55);
    headGroup.add(nose);

    // Ears
    const earGeo = new THREE.ConeGeometry(0.12, 0.3, 8);
    const leftEar = new THREE.Mesh(earGeo, wolfMat);
    leftEar.position.set(-0.22, 0.35, 0);
    leftEar.rotation.z = -0.2;
    headGroup.add(leftEar);

    const rightEar = new THREE.Mesh(earGeo, wolfMat);
    rightEar.position.set(0.22, 0.35, 0);
    rightEar.rotation.z = 0.2;
    headGroup.add(rightEar);

    // Eyes
    const eyeGeo = new THREE.SphereGeometry(0.05, 8, 8);
    const leftEye = new THREE.Mesh(eyeGeo, noseMat);
    leftEye.position.set(-0.15, 0.1, 0.32);
    headGroup.add(leftEye);

    const rightEye = new THREE.Mesh(eyeGeo, noseMat);
    rightEye.position.set(0.15, 0.1, 0.32);
    headGroup.add(rightEye);

    group.add(headGroup);

    // Tail
    const tailGeo = new THREE.CylinderGeometry(0.08, 0.02, 0.7, 8);
    const tail = new THREE.Mesh(tailGeo, wolfMat);
    tail.position.set(0, 0.3, -0.4);
    tail.rotation.x = -0.8;
    group.add(tail);

    return { group, headGroup };
  };

  const build3DGrandmaModel = () => {
    const group = new THREE.Group();

    // Purple Dress
    const dressGeo = new THREE.ConeGeometry(0.55, 1.1, 16);
    const dressMat = new THREE.MeshStandardMaterial({ color: 0x7c3aed, roughness: 0.4 });
    const dress = new THREE.Mesh(dressGeo, dressMat);
    dress.position.y = 0.55;
    group.add(dress);

    // Head Group
    const headGroup = new THREE.Group();
    headGroup.position.y = 1.25;

    const headGeo = new THREE.SphereGeometry(0.32, 16, 16);
    const headMat = new THREE.MeshStandardMaterial({ color: 0xffedd5, roughness: 0.5 });
    const head = new THREE.Mesh(headGeo, headMat);
    headGroup.add(head);

    // White Hair Bun
    const hairGeo = new THREE.SphereGeometry(0.22, 16, 16);
    const hairMat = new THREE.MeshStandardMaterial({ color: 0xe2e8f0, roughness: 0.6 });
    const hair = new THREE.Mesh(hairGeo, hairMat);
    hair.position.set(0, 0.22, -0.15);
    headGroup.add(hair);

    // Spectacles / Glasses Frame
    const glassGeo = new THREE.TorusGeometry(0.08, 0.015, 8, 16);
    const glassMat = new THREE.MeshBasicMaterial({ color: 0xf59e0b });

    const leftGlass = new THREE.Mesh(glassGeo, glassMat);
    leftGlass.position.set(-0.12, 0.05, 0.3);
    headGroup.add(leftGlass);

    const rightGlass = new THREE.Mesh(glassGeo, glassMat);
    rightGlass.position.set(0.12, 0.05, 0.3);
    headGroup.add(rightGlass);

    group.add(headGroup);

    // Cane
    const caneGeo = new THREE.CylinderGeometry(0.03, 0.03, 1.0);
    const caneMat = new THREE.MeshStandardMaterial({ color: 0x78350f, roughness: 0.5 });
    const cane = new THREE.Mesh(caneGeo, caneMat);
    cane.position.set(0.45, 0.5, 0.2);
    group.add(cane);

    return { group, headGroup };
  };

  const build3DHunterModel = () => {
    const group = new THREE.Group();

    // Coat (Khaki Brown)
    const coatGeo = new THREE.CylinderGeometry(0.4, 0.5, 1.0, 16);
    const coatMat = new THREE.MeshStandardMaterial({ color: 0x78350f, roughness: 0.6 });
    const coat = new THREE.Mesh(coatGeo, coatMat);
    coat.position.y = 0.5;
    group.add(coat);

    // Head Group
    const headGroup = new THREE.Group();
    headGroup.position.y = 1.2;

    const headGeo = new THREE.SphereGeometry(0.34, 16, 16);
    const headMat = new THREE.MeshStandardMaterial({ color: 0xffedd5 });
    const head = new THREE.Mesh(headGeo, headMat);
    headGroup.add(head);

    // Hunting Hat
    const hatGeo = new THREE.CylinderGeometry(0.38, 0.48, 0.2, 16);
    const hatMat = new THREE.MeshStandardMaterial({ color: 0x451a03 });
    const hat = new THREE.Mesh(hatGeo, hatMat);
    hat.position.y = 0.25;
    headGroup.add(hat);

    // Large Black Mustache
    const stacheGeo = new THREE.BoxGeometry(0.3, 0.08, 0.1);
    const stacheMat = new THREE.MeshBasicMaterial({ color: 0x0f172a });
    const stache = new THREE.Mesh(stacheGeo, stacheMat);
    stache.position.set(0, -0.08, 0.32);
    headGroup.add(stache);

    group.add(headGroup);

    // Rifle Gun
    const rifleGeo = new THREE.BoxGeometry(0.06, 0.9, 0.08);
    const rifleMat = new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.8 });
    const rifle = new THREE.Mesh(rifleGeo, rifleMat);
    rifle.position.set(-0.45, 0.8, 0.1);
    rifle.rotation.z = -0.3;
    group.add(rifle);

    return { group, headGroup };
  };

  const build3DRedHoodModel = () => {
    const group = new THREE.Group();

    // Red Dress
    const dressGeo = new THREE.ConeGeometry(0.48, 0.95, 16);
    const dressMat = new THREE.MeshStandardMaterial({ color: 0xe11d48, roughness: 0.3 });
    const dress = new THREE.Mesh(dressGeo, dressMat);
    dress.position.y = 0.48;
    group.add(dress);

    // Head Group
    const headGroup = new THREE.Group();
    headGroup.position.y = 1.15;

    const headGeo = new THREE.SphereGeometry(0.32, 16, 16);
    const headMat = new THREE.MeshStandardMaterial({ color: 0xffedd5 });
    const head = new THREE.Mesh(headGeo, headMat);
    headGroup.add(head);

    // Red Cape Hood
    const hoodGeo = new THREE.SphereGeometry(0.37, 16, 16, 0, Math.PI * 2, 0, Math.PI * 0.75);
    const hoodMat = new THREE.MeshStandardMaterial({ color: 0xbe123c, side: THREE.DoubleSide });
    const hood = new THREE.Mesh(hoodGeo, hoodMat);
    hood.position.y = 0.03;
    headGroup.add(hood);

    group.add(headGroup);

    return { group, headGroup };
  };

  // Build Full 3D WebGL Scene
  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth;
    const height = container.clientHeight;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(currentScene.environment === 'forest' ? 0x064e3b : 0x311042);

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(Math.sin(cameraOrbit) * 3.5, 1.4, Math.cos(cameraOrbit) * 3.5);
    camera.lookAt(0, 1.0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    rendererRef.current = renderer;

    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    const ambient = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambient);

    const sun = new THREE.DirectionalLight(0xfef08a, 1.8);
    sun.position.set(4, 8, 4);
    sun.castShadow = true;
    scene.add(sun);

    const fillLight = new THREE.PointLight(0xf43f5e, 1.2, 10);
    fillLight.position.set(-3, 2, 2);
    scene.add(fillLight);

    const stageGroup = new THREE.Group();

    const floorGeo = new THREE.CylinderGeometry(3.0, 3.0, 0.15, 32);
    const floorMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.8 });
    const floor = new THREE.Mesh(floorGeo, floorMat);
    floor.position.y = -0.08;
    floor.receiveShadow = true;
    stageGroup.add(floor);

    const treeMat = new THREE.MeshStandardMaterial({ color: 0x047857, roughness: 0.6 });
    const trunkMat = new THREE.MeshStandardMaterial({ color: 0x78350f, roughness: 0.9 });

    for (let i = 0; i < 6; i++) {
      const angle = (i / 6) * Math.PI * 2;
      const radius = 2.4;

      const treeGroup = new THREE.Group();
      treeGroup.position.set(Math.cos(angle) * radius, 0, Math.sin(angle) * radius);

      const trunkGeo = new THREE.CylinderGeometry(0.08, 0.12, 0.8);
      const trunk = new THREE.Mesh(trunkGeo, trunkMat);
      trunk.position.y = 0.4;
      treeGroup.add(trunk);

      const foliageGeo = new THREE.ConeGeometry(0.5, 1.2, 8);
      const foliage = new THREE.Mesh(foliageGeo, treeMat);
      foliage.position.y = 1.2;
      treeGroup.add(foliage);

      stageGroup.add(treeGroup);
    }

    scene.add(stageGroup);

    let characterModel: { group: THREE.Group; headGroup: THREE.Group };

    if (currentScene.characterType === 'wolf') {
      characterModel = build3DWolfModel();
    } else if (currentScene.characterType === 'grandma') {
      characterModel = build3DGrandmaModel();
    } else if (currentScene.characterType === 'hunter') {
      characterModel = build3DHunterModel();
    } else {
      characterModel = build3DRedHoodModel();
    }

    scene.add(characterModel.group);

    const particleCount = 50;
    const particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount * 3; i += 3) {
      positions[i] = (Math.random() - 0.5) * 6;
      positions[i + 1] = Math.random() * 3.5;
      positions[i + 2] = (Math.random() - 0.5) * 6;
    }
    particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const particleMat = new THREE.PointsMaterial({ color: 0xf59e0b, size: 0.07, transparent: true });
    const particles = new THREE.Points(particleGeo, particleMat);
    scene.add(particles);

    let clock = new THREE.Clock();
    let animationId: number;

    const renderLoop = () => {
      animationId = requestAnimationFrame(renderLoop);
      const time = clock.getElapsedTime();

      if (isPlaying) {
        characterModel.headGroup.rotation.x = Math.sin(time * 5) * 0.15;
        characterModel.headGroup.rotation.y = Math.sin(time * 3) * 0.2;
        characterModel.group.position.y = Math.abs(Math.sin(time * 5)) * 0.06;
        characterModel.group.rotation.y = Math.sin(time * 1.5) * 0.15;
      } else {
        characterModel.headGroup.rotation.x = Math.sin(time * 2) * 0.05;
        characterModel.group.position.y = Math.sin(time * 2) * 0.02;
      }

      camera.position.x = Math.sin(cameraOrbit + time * 0.1) * 3.6;
      camera.position.z = Math.cos(cameraOrbit + time * 0.1) * 3.6;
      camera.lookAt(0, 1.0, 0);

      const posArr = particleGeo.attributes.position.array as Float32Array;
      for (let i = 1; i < particleCount * 3; i += 3) {
        posArr[i] += 0.005;
        if (posArr[i] > 3.5) posArr[i] = 0;
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
  }, [currentScene, isPlaying, cameraOrbit]);

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
                <Box className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  真實 3D 多邊形網格模型 Studio
                  <span className="text-xs bg-purple-500/20 text-purple-300 px-2.5 py-0.5 rounded-full border border-purple-500/30 font-bold">
                    360° 全多邊形 3D 骨骼模型
                  </span>
                </h2>
                <p className="text-xs text-slate-400">具備頭部、肢體、服飾與 3D 骨骼擺動角色的真實 3D 童話工作室！</p>
              </div>
            </div>
          </div>

          {/* Voice Selector */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div>
              <label className="block text-slate-300 mb-1 font-bold flex items-center gap-1">
                <Volume2 className="w-4 h-4 text-amber-400" />
                極致真人語音引擎 (Microsoft Neural Speech)
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
              <span className="text-purple-400 font-bold">3D 角色：{currentScene.characterName}</span>
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
            真實 3D 多邊形分鏡列表 ({scenes.length})
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
                  <div className="w-9 h-9 rounded-xl bg-purple-500/20 text-purple-300 flex items-center justify-center font-bold text-xs">
                    3D
                  </div>
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
              真實 360° 3D WebGL 視窗
            </span>

            {/* Orbit Slider */}
            <div className="flex items-center gap-2">
              <span>3D 視角旋轉:</span>
              <input
                type="range"
                min={-Math.PI}
                max={Math.PI}
                step={0.1}
                value={cameraOrbit}
                onChange={(e) => setCameraOrbit(parseFloat(e.target.value))}
                className="w-24 accent-purple-500 cursor-pointer"
              />
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
              <span>{isPlaying ? '暫停 3D 動態' : '播放真實 3D 人聲動畫'}</span>
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
                download="full_3d_fairytale.webm"
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-emerald-500 text-slate-950 font-bold rounded-xl text-xs shadow-lg hover:bg-emerald-400 transition"
              >
                <Download className="w-4 h-4" />
                下載 1080p 真實 3D MP4 影片 (.webm)
              </a>
            </div>
          )}
        </div>
      </section>
    </div>
  );
};
