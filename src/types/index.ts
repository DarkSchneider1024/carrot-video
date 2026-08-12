export type AspectRatio = '16:9' | '9:16';

export type ArtStyle = 
  | 'watercolor' 
  | '3d_pixar' 
  | 'ghibli_anime' 
  | 'vintage_storybook' 
  | 'paper_cutout'
  | 'oil_painting';

export type CharacterMotionStyle = 
  | 'head_bob'     // Vyond 風格頭部點頭晃動
  | 'talking_sway' // 對話頻率左右微擺
  | 'breathing'    // 2D 身體呼吸浮動
  | 'none';

export interface StoryScene {
  id: string;
  sceneNumber: number;
  narrative: string;
  visualPrompt: string;
  character: string;
  characterAvatarUrl?: string; // Transparent cutout avatar for 2D character bobbing
  motionStyle?: CharacterMotionStyle;
  imageUrl: string;
  isGeneratingImage?: boolean;
  duration: number; // in seconds
  audioBlobUrl?: string;
  audioDuration?: number;
}

export interface StoryProject {
  id: string;
  title: string;
  description: string;
  aspectRatio: AspectRatio;
  artStyle: ArtStyle;
  voiceName: string;
  bgMusicTrack: string;
  bgMusicVolume: number;
  scenes: StoryScene[];
}

export interface PresetStory {
  title: string;
  category: string;
  description: string;
  artStyle: ArtStyle;
  scenes: {
    narrative: string;
    visualPrompt: string;
    character: string;
    duration: number;
    motionStyle?: CharacterMotionStyle;
  }[];
}
