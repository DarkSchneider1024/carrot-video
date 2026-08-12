import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { Play, Pause, Box, Smile } from 'lucide-react';

export const ThreeDCharacterStudio: React.FC = () => {
  const mountRef = useRef<HTMLDivElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(true);
  const [actionName, setActionName] = useState<'nod' | 'talk' | 'wave'>('nod');

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    // 1. Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f172a);

    // 2. Camera setup
    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(0, 1.2, 3.5);

    // 3. Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    container.appendChild(renderer.domElement);

    // 4. Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xfef08a, 1.5);
    dirLight.position.set(5, 8, 5);
    dirLight.castShadow = true;
    scene.add(dirLight);

    const pointLight = new THREE.PointLight(0xf43f5e, 1.2, 10);
    pointLight.position.set(-2, 2, 2);
    scene.add(pointLight);

    // 5. Build Procedural 3D Fairytale Character (Little Red Riding Hood 3D Character Model)
    const characterGroup = new THREE.Group();

    // Body (Red Dress)
    const dressGeo = new THREE.ConeGeometry(0.5, 1.0, 32);
    const dressMat = new THREE.MeshStandardMaterial({ color: 0xe11d48, roughness: 0.3 });
    const dress = new THREE.Mesh(dressGeo, dressMat);
    dress.position.y = 0.5;
    characterGroup.add(dress);

    // Head
    const headGeo = new THREE.SphereGeometry(0.35, 32, 32);
    const headMat = new THREE.MeshStandardMaterial({ color: 0xffedd5, roughness: 0.4 });
    const head = new THREE.Mesh(headGeo, headMat);
    head.position.y = 1.2;
    characterGroup.add(head);

    // Red Hooded Cape
    const capeGeo = new THREE.SphereGeometry(0.39, 32, 16, 0, Math.PI * 2, 0, Math.PI * 0.6);
    const capeMat = new THREE.MeshStandardMaterial({ color: 0xbe123c, roughness: 0.2, side: THREE.DoubleSide });
    const cape = new THREE.Mesh(capeGeo, capeMat);
    cape.position.y = 1.22;
    characterGroup.add(cape);

    // Eyes
    const eyeGeo = new THREE.SphereGeometry(0.04, 16, 16);
    const eyeMat = new THREE.MeshBasicMaterial({ color: 0x0f172a });

    const leftEye = new THREE.Mesh(eyeGeo, eyeMat);
    leftEye.position.set(-0.12, 1.25, 0.31);
    characterGroup.add(leftEye);

    const rightEye = new THREE.Mesh(eyeGeo, eyeMat);
    rightEye.position.set(0.12, 1.25, 0.31);
    characterGroup.add(rightEye);

    // Cute Cheeks
    const cheekGeo = new THREE.SphereGeometry(0.05, 16, 16);
    const cheekMat = new THREE.MeshBasicMaterial({ color: 0xf43f5e });

    const leftCheek = new THREE.Mesh(cheekGeo, cheekMat);
    leftCheek.position.set(-0.18, 1.15, 0.29);
    characterGroup.add(leftCheek);

    const rightCheek = new THREE.Mesh(cheekGeo, cheekMat);
    rightCheek.position.set(0.18, 1.15, 0.29);
    characterGroup.add(rightCheek);

    // Arms
    const armGeo = new THREE.CylinderGeometry(0.06, 0.06, 0.5);
    const armMat = new THREE.MeshStandardMaterial({ color: 0xbe123c });

    const leftArm = new THREE.Mesh(armGeo, armMat);
    leftArm.position.set(-0.45, 0.7, 0);
    leftArm.rotation.z = Math.PI * 0.15;
    characterGroup.add(leftArm);

    const rightArm = new THREE.Mesh(armGeo, armMat);
    rightArm.position.set(0.45, 0.7, 0);
    rightArm.rotation.z = -Math.PI * 0.15;
    characterGroup.add(rightArm);

    scene.add(characterGroup);

    // Floor Platform
    const floorGeo = new THREE.CylinderGeometry(1.5, 1.5, 0.1, 32);
    const floorMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.8 });
    const floor = new THREE.Mesh(floorGeo, floorMat);
    floor.position.y = -0.05;
    scene.add(floor);

    // 6. Animation Loop
    let clock = new THREE.Clock();
    let reqId: number;

    const animate = () => {
      reqId = requestAnimationFrame(animate);
      const time = clock.getElapsedTime();

      if (isPlaying) {
        if (actionName === 'nod') {
          head.rotation.x = Math.sin(time * 4) * 0.15;
          head.rotation.y = Math.sin(time * 2) * 0.1;
          characterGroup.position.y = Math.abs(Math.sin(time * 4)) * 0.05;
          rightArm.rotation.x = Math.sin(time * 3) * 0.2;
        } else if (actionName === 'talk') {
          head.rotation.y = Math.sin(time * 6) * 0.2;
          head.rotation.z = Math.cos(time * 8) * 0.05;
          characterGroup.position.y = Math.sin(time * 6) * 0.04;
          leftArm.rotation.x = Math.sin(time * 5) * 0.4;
          rightArm.rotation.x = Math.cos(time * 5) * 0.4;
        } else if (actionName === 'wave') {
          rightArm.rotation.z = -Math.PI * 0.3 + Math.sin(time * 8) * 0.4;
          head.rotation.z = Math.sin(time * 3) * 0.1;
          characterGroup.position.y = Math.sin(time * 2) * 0.02;
        }
      }

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!container) return;
      camera.aspect = container.clientWidth / container.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(container.clientWidth, container.clientHeight);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(reqId);
      window.removeEventListener('resize', handleResize);
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
    };
  }, [isPlaying, actionName]);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-2xl space-y-4 text-slate-100">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-purple-500/20 text-purple-400 flex items-center justify-center">
            <Box className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              Three.js 程式 3D 角色引擎 + HyperFrames
              <span className="text-[10px] bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded-full border border-emerald-500/30 font-bold">
                0 繪影 API 額度消耗
              </span>
            </h3>
            <p className="text-xs text-slate-400">使用網頁程式碼直接渲染 3D 角色與 60FPS 骨骼動畫，徹底省去 Gemini 繪圖點數！</p>
          </div>
        </div>

        <button
          onClick={() => setIsPlaying(!isPlaying)}
          className="p-2 bg-slate-800 hover:bg-slate-700 text-amber-300 rounded-xl text-xs font-semibold border border-slate-700 transition flex items-center gap-1.5"
        >
          {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          <span>{isPlaying ? '暫停 3D 動態' : '播放 3D 動效'}</span>
        </button>
      </div>

      {/* 3D Viewport Box */}
      <div ref={mountRef} className="w-full h-80 bg-slate-950 rounded-xl overflow-hidden border border-slate-800 relative shadow-inner" />

      {/* Control Actions */}
      <div className="flex items-center justify-between bg-slate-950 p-3 rounded-xl border border-slate-800 text-xs">
        <span className="text-slate-400 font-semibold flex items-center gap-1">
          <Smile className="w-4 h-4 text-purple-400" />
          選擇 3D 骨骼動作模式：
        </span>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setActionName('nod')}
            className={`px-3 py-1.5 rounded-lg font-bold transition ${
              actionName === 'nod' ? 'bg-purple-500 text-white shadow' : 'bg-slate-800 text-slate-400 hover:text-white'
            }`}
          >
            🎭 頭部點頭晃動 (Nod)
          </button>
          <button
            onClick={() => setActionName('talk')}
            className={`px-3 py-1.5 rounded-lg font-bold transition ${
              actionName === 'talk' ? 'bg-purple-500 text-white shadow' : 'bg-slate-800 text-slate-400 hover:text-white'
            }`}
          >
            🗣️ 對話微擺動作 (Talk)
          </button>
          <button
            onClick={() => setActionName('wave')}
            className={`px-3 py-1.5 rounded-lg font-bold transition ${
              actionName === 'wave' ? 'bg-purple-500 text-white shadow' : 'bg-slate-800 text-slate-400 hover:text-white'
            }`}
          >
            👋 舉手揮手招呼 (Wave)
          </button>
        </div>
      </div>
    </div>
  );
};
