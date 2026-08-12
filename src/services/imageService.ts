import type { ArtStyle } from '../types';

const STYLE_PROMPTS: Record<ArtStyle, { prefix: string; suffix: string }> = {
  watercolor: {
    prefix: 'Children fairy tale storybook illustration, whimsical soft watercolor painting, dreamlike atmosphere,',
    suffix: 'hand painted texture, pastel color palette, gentle lighting, masterpiece, high quality'
  },
  '3d_pixar': {
    prefix: '3D animated movie style, cute character design, Pixar Disney aesthetic, vibrant storytelling scene,',
    suffix: 'octane render, soft warm lighting, expressive faces, 8k resolution, highly detailed'
  },
  ghibli_anime: {
    prefix: 'Studio Ghibli style anime illustration, cozy fairy tale landscape, vibrant colors, Hand-drawn anime artwork,',
    suffix: 'Hayao Miyazaki aesthetic, lush detailed background, magical glowing light, stunning masterpiece'
  },
  vintage_storybook: {
    prefix: 'Vintage 19th-century classic storybook illustration, gold leaf details, intricate line art watercolor,',
    suffix: 'Arthur Rackham and Beatrix Potter style, nostalgic nostalgic fairytale book page, elegant'
  },
  paper_cutout: {
    prefix: 'Intricate paper cut craft art style, layered colored paper fairy tale illustration, shadow box depth,',
    suffix: 'handcrafted paper art, vibrant textures, dramatic backlighting, clean paper craft design'
  },
  oil_painting: {
    prefix: 'Classic fairy tale oil painting on canvas, rich impasto textures, dramatic dramatic lighting,',
    suffix: 'master painter artwork, magical luminescent glow, storybook realism, detailed brushwork'
  }
};

/**
 * Free open-source Image Generator via Pollinations AI (100% Free, Keyless API)
 */
export async function generateFairyTaleImage(
  visualPrompt: string,
  style: ArtStyle = 'watercolor',
  aspectRatio: '16:9' | '9:16' = '16:9',
  seed?: number
): Promise<string> {
  const width = aspectRatio === '16:9' ? 1280 : 720;
  const height = aspectRatio === '16:9' ? 720 : 1280;
  
  const styleConfig = STYLE_PROMPTS[style] || STYLE_PROMPTS.watercolor;
  const fullPrompt = `${styleConfig.prefix} ${visualPrompt}, ${styleConfig.suffix}`;
  
  const randomSeed = seed !== undefined ? seed : Math.floor(Math.random() * 1000000);
  const encodedPrompt = encodeURIComponent(fullPrompt);
  
  const imageUrl = `https://image.pollinations.ai/prompt/${encodedPrompt}?width=${width}&height=${height}&seed=${randomSeed}&nologo=true&model=flux`;
  
  return new Promise((resolve) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.src = imageUrl;
    img.onload = () => resolve(imageUrl);
    img.onerror = () => {
      const fallbackUrl = `https://image.pollinations.ai/prompt/${encodedPrompt}?width=${width}&height=${height}&seed=${randomSeed}&nologo=true&model=turbo`;
      resolve(fallbackUrl);
    };
  });
}

/**
 * Generate 2D Cutout Character Avatar (Vyond style 2D cutout character)
 */
export async function generate2DCutoutAvatar(characterName: string): Promise<string> {
  const prompt = `2D Vyond cartoon style cute cutout character avatar of ${characterName}, standing full body, clean plain white background, vibrant flat vector illustration, isolated`;
  const encoded = encodeURIComponent(prompt);
  return `https://image.pollinations.ai/prompt/${encoded}?width=512&height=512&seed=888&nologo=true&model=flux`;
}

export function getStyleDisplayName(style: ArtStyle): string {
  const names: Record<ArtStyle, string> = {
    watercolor: '柔和水彩繪本 (Watercolor)',
    '3d_pixar': '3D 皮克斯動畫 (3D Pixar)',
    ghibli_anime: '吉卜力風格動漫 (Studio Ghibli)',
    vintage_storybook: '復古經典繪本 (Vintage Classic)',
    paper_cutout: '立體剪紙工藝 (Paper Cutout)',
    oil_painting: '奇幻古典油畫 (Fantasy Oil)'
  };
  return names[style] || style;
}
