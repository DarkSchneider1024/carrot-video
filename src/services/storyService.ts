import type { StoryScene, ArtStyle, AspectRatio, StoryProject } from '../types';
import { PRESET_STORIES } from './storyTemplates';
import { generateFairyTaleImage } from './imageService';

/**
 * Generate a full Story Project with multi-scene script & prompts
 */
export async function createStoryFromPreset(
  presetIndex: number = 0,
  artStyle?: ArtStyle,
  aspectRatio: AspectRatio = '16:9'
): Promise<StoryProject> {
  const preset = PRESET_STORIES[presetIndex] || PRESET_STORIES[0];
  const style = artStyle || preset.artStyle;

  const scenes: StoryScene[] = preset.scenes.map((s, idx) => ({
    id: `scene-${Date.now()}-${idx}`,
    sceneNumber: idx + 1,
    narrative: s.narrative,
    visualPrompt: s.visualPrompt,
    character: s.character,
    duration: s.duration,
    imageUrl: '',
    isGeneratingImage: true
  }));

  const project: StoryProject = {
    id: `project-${Date.now()}`,
    title: preset.title,
    description: preset.description,
    aspectRatio,
    artStyle: style,
    voiceName: 'zh-TW-HsiaoChenNeural',
    bgMusicTrack: 'lullaby_magic',
    bgMusicVolume: 0.25,
    scenes
  };

  return project;
}

/**
 * Generate AI fairytale scenes from custom user prompt
 */
export async function generateCustomStory(
  topic: string,
  artStyle: ArtStyle = 'watercolor',
  aspectRatio: AspectRatio = '16:9'
): Promise<StoryProject> {
  const generatedScenes: Omit<StoryScene, 'id' | 'imageUrl'>[] = [
    {
      sceneNumber: 1,
      narrative: `很久很久以前，在一個充滿神奇力量的王國裡，關於『${topic}』的故事就這樣開始了。`,
      visualPrompt: `Fairytale entrance scene of ${topic}, beautiful sunlit fairytale Kingdom with rainbow castle and magical flowers`,
      character: '旁白',
      duration: 6
    },
    {
      sceneNumber: 2,
      narrative: `主角滿懷著勇氣與好奇心，踏上了充滿驚喜的探索旅程。`,
      visualPrompt: `Cute fairytale hero exploring a magical glowing forest path, mysterious whimsical environment`,
      character: '小勇士',
      duration: 6
    },
    {
      sceneNumber: 3,
      narrative: `在旅途中，他們遇到了好心的森林伙伴，並一起解開了古老的魔法謎題。`,
      visualPrompt: `Fairytale characters sharing glowing magical fruits under a giant glowing oak tree, friendly atmosphere`,
      character: '森林精靈',
      duration: 7
    },
    {
      sceneNumber: 4,
      narrative: `最終，大家都學會了分享與愛的力量，歡喜地圍繞在魔法森林裡舉行盛大的慶典！`,
      visualPrompt: `Grand fairytale celebration in a festive town square with fairy lights, fireworks, joyful characters celebrating`,
      character: '旁白',
      duration: 7
    }
  ];

  const scenes: StoryScene[] = generatedScenes.map((s, idx) => ({
    ...s,
    id: `custom-scene-${Date.now()}-${idx}`,
    imageUrl: '',
    isGeneratingImage: true
  }));

  return {
    id: `project-custom-${Date.now()}`,
    title: `${topic} - 奇幻故事`,
    description: `專為 YouTube 童話故事頻道打造的客製化影音劇本`,
    aspectRatio,
    artStyle,
    voiceName: 'zh-TW-HsiaoChenNeural',
    bgMusicTrack: 'lullaby_magic',
    bgMusicVolume: 0.25,
    scenes
  };
}

/**
 * Load images for all scenes in parallel
 */
export async function populateSceneImages(
  project: StoryProject,
  onSceneUpdate: (sceneId: string, imageUrl: string) => void
): Promise<void> {
  const promises = project.scenes.map(async (scene) => {
    try {
      const url = await generateFairyTaleImage(
        scene.visualPrompt,
        project.artStyle,
        project.aspectRatio,
        scene.sceneNumber * 777
      );
      onSceneUpdate(scene.id, url);
    } catch (err) {
      console.error(`Failed image gen for scene ${scene.id}`, err);
    }
  });

  await Promise.all(promises);
}
