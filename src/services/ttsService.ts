// Web Speech API, GPT-SoVITS, & Edge-TTS Voice Player Service

export interface RealisticVoiceOption {
  id: string;
  displayName: string;
  gender: 'female' | 'male';
  lang: string;
  defaultPitch: number;
  defaultRate: number;
  sampleText: string;
  audioSampleUrl?: string;
  gptSovitsUrl?: string;
}

export const ULTRA_REALISTIC_VOICES: RealisticVoiceOption[] = [
  {
    id: 'vits-custom-female-ownwts6r7hq',
    displayName: '🎤【GPT-SoVITS 100% 複製女聲】(YouTube OWnWts6r7HQ API)',
    gender: 'female',
    lang: 'zh-TW',
    defaultPitch: 1.35,
    defaultRate: 1.0,
    sampleText: '你好！我是 GPT-SoVITS 複製原聲女主角！',
    audioSampleUrl: '/assets/vits_female_real.mp3',
    gptSovitsUrl: 'http://localhost:9880/tts'
  },
  {
    id: 'zh-TW-HsiaoChenNeural',
    displayName: '👩 曉臻 (台灣溫柔女聲 - 故事朗讀推薦)',
    gender: 'female',
    lang: 'zh-TW',
    defaultPitch: 1.02,
    defaultRate: 0.92,
    sampleText: '你好！我是溫柔女聲曉臻！'
  },
  {
    id: 'zh-TW-YunJheNeural',
    displayName: '👨 雲哲 (台灣沉穩低音男聲 - 獵人與北風推薦)',
    gender: 'male',
    lang: 'zh-TW',
    defaultPitch: 0.50, // Ultra Deep Male
    defaultRate: 0.85,
    sampleText: '你好！我是沉穩低音男聲雲哲！'
  },
  {
    id: 'zh-TW-HsiaoYuNeural',
    displayName: '👧 曉雨 (台灣高音童聲 - 小紅帽推薦)',
    gender: 'female',
    lang: 'zh-TW',
    defaultPitch: 1.60, // Ultra High Cute Child
    defaultRate: 1.10,
    sampleText: '你好！我是高音童聲小紅帽！'
  },
  {
    id: 'zh-CN-XiaoxiaoNeural',
    displayName: '👩 曉曉 (溫暖童話大師女聲)',
    gender: 'female',
    lang: 'zh-CN',
    defaultPitch: 0.90,
    defaultRate: 0.90,
    sampleText: '你好！我是童話大師曉曉！'
  },
  {
    id: 'zh-CN-YunjianNeural',
    displayName: '👨 雲健 (熱血中音男聲)',
    gender: 'male',
    lang: 'zh-CN',
    defaultPitch: 0.70,
    defaultRate: 1.15,
    sampleText: '你好！我是熱血男聲雲健！'
  }
];

// Active Audio Element Tracker to prevent dual overlapping sound bug
let currentActiveAudio: HTMLAudioElement | null = null;

export const stopSpeaking = (): void => {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
  if (currentActiveAudio) {
    try {
      currentActiveAudio.pause();
      currentActiveAudio.currentTime = 0;
    } catch (e) {
      // Ignore audio pause errors
    }
    currentActiveAudio = null;
  }
};

export const generateEdgeTTSScript = (
  dialogs: { sceneNum?: number; voice?: string; text: string; filename?: string }[]
): string => {
  return `# Python Edge-TTS Generator Script
import asyncio
import edge_tts

async def generate_all():
${dialogs
  .map(
    (d, i) =>
      `    communicate = edge_tts.Communicate('''${d.text}''', "${d.voice || 'zh-TW-HsiaoChenNeural'}")\n    await communicate.save("${d.filename || `scene_${i+1}.mp3`}")`
  )
  .join('\n')}

asyncio.run(generate_all())
`;
};

export const getAvailableVoices = (): Promise<SpeechSynthesisVoice[]> => {
  return new Promise((resolve) => {
    if (!('speechSynthesis' in window)) {
      resolve([]);
      return;
    }
    let voices = window.speechSynthesis.getVoices();
    if (voices.length > 0) {
      resolve(voices);
      return;
    }
    window.speechSynthesis.onvoiceschanged = () => {
      voices = window.speechSynthesis.getVoices();
      resolve(voices);
    };
    setTimeout(() => {
      resolve(window.speechSynthesis.getVoices());
    }, 300);
  });
};

export const speakText = async (
  text: string,
  voiceId: string = 'vits-custom-female-ownwts6r7hq',
  overrideRate?: number,
  overridePitch?: number
): Promise<void> => {
  // CRITICAL FIX: Stop all existing speech synthesis AND active audio elements first to prevent dual voice overlap!
  stopSpeaking();

  const voicePreset = ULTRA_REALISTIC_VOICES.find((v) => v.id === voiceId) || ULTRA_REALISTIC_VOICES[0];

  // Attempt GPT-SoVITS local voice cloning API server first
  if (voicePreset.gptSovitsUrl) {
    try {
      const url = `${voicePreset.gptSovitsUrl}?text=${encodeURIComponent(text)}`;
      const res = await fetch(url, { method: 'GET' });
      if (res.ok) {
        const blob = await res.blob();
        const audioUrl = URL.createObjectURL(blob);
        return new Promise((resolve) => {
          const audio = new Audio(audioUrl);
          currentActiveAudio = audio;
          audio.onended = () => {
            currentActiveAudio = null;
            resolve();
          };
          audio.onerror = () => {
            currentActiveAudio = null;
            resolve();
          };
          audio.play().catch(() => {
            currentActiveAudio = null;
            resolve();
          });
        });
      }
    } catch (err) {
      console.log('GPT-SoVITS API server offline, falling back to speech synthesis...');
    }
  }

  if (!('speechSynthesis' in window)) {
    console.warn('Web Speech API is not supported in this browser.');
    return;
  }

  const voices = await getAvailableVoices();
  const pitch = overridePitch ?? voicePreset.defaultPitch;
  const rate = overrideRate ?? voicePreset.defaultRate;

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.pitch = pitch;
  utterance.rate = rate;

  const chineseVoices = voices.filter(
    (v) => v.lang.includes('zh') || v.lang.includes('ZH') || v.lang.includes('cmn')
  );

  let selectedVoice: SpeechSynthesisVoice | undefined;

  if (chineseVoices.length > 0) {
    if (voiceId.includes('YunJhe') || voiceId.includes('Yunjian')) {
      selectedVoice =
        chineseVoices.find((v) => v.name.toLowerCase().includes('male') || v.name.includes('Danny') || v.name.includes('Kangkang') || v.name.includes('雲哲') || v.name.includes('雲健')) ||
        chineseVoices[Math.min(1, chineseVoices.length - 1)];
    } else if (voiceId.includes('HsiaoYu')) {
      selectedVoice =
        chineseVoices.find((v) => v.name.includes('HsiaoYu') || v.name.includes('Yaoyao') || v.name.includes('曉雨')) ||
        chineseVoices[0];
    } else {
      selectedVoice =
        chineseVoices.find((v) => v.name.includes('HsiaoChen') || v.name.includes('Xiaoxiao') || v.name.includes('Hanhan') || v.name.includes('Yating') || v.name.includes('曉臻')) ||
        chineseVoices[0];
    }
  } else if (voices.length > 0) {
    selectedVoice = voices[0];
  }

  if (selectedVoice) {
    utterance.voice = selectedVoice;
  }

  return new Promise((resolve) => {
    utterance.onend = () => resolve();
    utterance.onerror = () => resolve();
    window.speechSynthesis.speak(utterance);
  });
};

export const testVoiceInstant = async (voiceId: string): Promise<void> => {
  stopSpeaking();
  const preset = ULTRA_REALISTIC_VOICES.find((v) => v.id === voiceId) || ULTRA_REALISTIC_VOICES[0];
  if (preset.audioSampleUrl) {
    return new Promise((resolve) => {
      const audio = new Audio(preset.audioSampleUrl);
      currentActiveAudio = audio;
      audio.onended = () => {
        currentActiveAudio = null;
        resolve();
      };
      audio.onerror = () => {
        currentActiveAudio = null;
        resolve();
      };
      audio.play().catch(() => {
        currentActiveAudio = null;
        resolve();
      });
    });
  }
  await speakText(preset.sampleText, voiceId);
};
