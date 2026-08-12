import type { PresetStory } from '../types';

export const PRESET_STORIES: PresetStory[] = [
  {
    title: '小紅帽與森林魔法派對 (Gemini 訂閱特製版)',
    category: '溫馨冒險童話',
    description: 'Gemini AI 特別改編：小紅帽穿過魔法森林探望外婆，發現大灰狼其實是在籌備外婆的驚喜生日派對！',
    artStyle: 'watercolor',
    scenes: [
      {
        character: '小紅帽',
        narrative: '在一個和煦的清晨，小紅帽提著滿滿一籃新鮮草莓與香甜的蛋糕，穿上奶奶縫製的紅斗篷，快樂地出發去探望外婆。',
        visualPrompt: 'Children fairy tale storybook illustration, soft whimsical watercolor style. A cute little girl wearing a bright red hooded cloak and dress, holding a woven basket with cakes and strawberries, walking along a sunlit magical forest path with colorful wildflowers and cute little birds, bright warm lighting, masterpiece',
        duration: 6
      },
      {
        character: '大灰狼',
        narrative: '微風拂過彩虹般的花田，發光的蝴蝶在周圍翩翩起舞。突然，大樹後面探出一隻毛茸茸的大灰狼，好奇地打量著小紅帽。',
        visualPrompt: 'Children fairy tale storybook illustration, soft whimsical watercolor style. A fluffy friendly big grey wolf with big curious eyes peeking out from behind a mossy ancient oak tree, looking at cute Little Red Riding Hood, glowing magical butterflies floating in the air, colorful forest background, warm dreamlike pastel palette',
        duration: 6
      },
      {
        character: '小紅帽',
        narrative: '大灰狼親切地建議：『森林深處開滿了許願花，外婆收到一定會很開心！』小紅帽開心地決定先為外婆採摘一束美麗的花朵。',
        visualPrompt: 'Children fairytale storybook illustration, soft watercolor texture. Little Red Riding Hood kneeling in a sunlit meadow of blooming colorful wildflowers, carefully picking a beautiful flower bouquet, magical golden sunbeams filtering through tall trees, enchanting peaceful atmosphere',
        duration: 6
      },
      {
        character: '外婆與大灰狼',
        narrative: '當小紅帽來到木屋前推開門時，驚喜地發現外婆與大灰狼正一起在餐桌前佈置彩帶與氣球！原來今天是外婆的秘密生日派對！',
        visualPrompt: 'Children fairytale storybook illustration, warm watercolor style. Inside a cozy rustic wooden cabin, kind smiling grandma sitting in a rocking chair next to a friendly wolf in a colorful party hat, hanging colorful party balloons and birthday banners around a strawberry cake on the table, cozy warm firelight',
        duration: 7
      },
      {
        character: '所有人',
        narrative: '小紅帽、外婆和大灰狼圍坐在蛋糕旁歡歌笑語，魔法森林裡傳遍了最溫暖的歡笑聲，大家過了一個無比難忘的節日。',
        visualPrompt: 'Children fairytale storybook illustration, happy watercolor style. Little Red Riding Hood, kind grandma, and friendly fluffy grey wolf celebrating together around a festive birthday table with a cake with candles, smiling happily, party hats, confetti floating, warm joyful ending',
        duration: 7
      }
    ]
  },
  {
    title: '三隻小豬的奇幻冒險',
    category: '伊索與經典童話',
    description: '經典童話新編：三隻小豬在彩虹森林建造溫馨小屋，同心協力應對大灰狼的考驗。',
    artStyle: 'watercolor',
    scenes: [
      {
        character: '旁白',
        narrative: '在遙遠的彩虹森林裡，住著三隻可愛的小豬兄弟：豬老大、豬老二和豬老三。',
        visualPrompt: 'Three cute fluffy little pigs wearing colorful overalls standing in a magical sunlit green forest with mushrooms',
        duration: 6
      },
      {
        character: '豬老大',
        narrative: '豬老大最喜歡偷懶，他在陽光下用輕盈的稻草搭建了一座黃金般的草屋。',
        visualPrompt: 'Cute little pig building a house made of straw in a sunny meadow, whimsical fairytale style',
        duration: 6
      },
      {
        character: '豬老二',
        narrative: '豬老二喜歡漂亮的木頭，他跑進森林裡，用帶有芳香的鬆木搭出了一間精緻的木屋。',
        visualPrompt: 'Little pig crafting a cozy wooden log cabin in the woods, colorful wooden beams, magical lighting',
        duration: 6
      },
      {
        character: '豬老三',
        narrative: '最勤勞的豬老三則搬來一塊塊沉穩的紅磚，細心地堆砌出一座無比堅固的磚石城堡。',
        visualPrompt: 'Hardworking pig laying red bricks with a trowel, building a sturdy fairytale brick house with chimney',
        duration: 6
      },
      {
        character: '大灰狼',
        narrative: '這天，森林深處走來一隻大灰狼！吹倒了草屋與木屋，三兄弟趕忙跑進堅固的磚屋裡。',
        visualPrompt: 'Funny goofy big bad wolf blowing air at a brick house, cute little pigs peeking from the window safely',
        duration: 7
      },
      {
        character: '旁白',
        narrative: '大灰狼怎麼也吹不動磚屋，最後三隻小豬在城堡裡快樂地唱著歌，過著平安幸福的生活。',
        visualPrompt: 'Three little pigs singing and celebrating around a cozy fireplace in their warm brick house, fairytale ending',
        duration: 7
      }
    ]
  },
  {
    title: '星空小熊與魔法糖果雨',
    category: '睡前治癒童話',
    description: '小熊奇奇在夜空中划著小船，將亮晶晶的星星收集起來，為森林裡的小動物降下糖果雨。',
    artStyle: 'ghibli_anime',
    scenes: [
      {
        character: '小熊奇奇',
        narrative: '夜幕低垂，小熊奇奇坐上一艘能飛的月亮小船，航行在湛藍如海的夜空中。',
        visualPrompt: 'Studio Ghibli style, adorable teddy bear sailing in a crescent moon boat in starry night sky with glowing clouds',
        duration: 7
      },
      {
        character: '旁白',
        narrative: '他伸出小網子，採集一顆顆像金幣般眨眼睛的小星星，裝進許願瓶裡。',
        visualPrompt: 'Little bear catching glowing magical yellow stars into a glass jar, breathtaking celestial background, anime style',
        duration: 7
      },
      {
        character: '小熊奇奇',
        narrative: '當許願瓶被裝滿時，神奇的事情發生了！夜空中輕飄飄地下起五彩繽紛的棉花糖與硬糖雨。',
        visualPrompt: 'Magical bedtime scene with colorful candies falling from night sky like stars, fantasy whimsical artwork',
        duration: 7
      },
      {
        character: '旁白',
        narrative: '森林裡的小動物們吃著甜甜的糖果，聽著溫柔的星光搖籃曲，甜甜地進入夢鄉。',
        visualPrompt: 'Cute sleeping woodland animals wrapped in soft blankets under starry sky, peaceful cozy bedtime atmosphere',
        duration: 7
      }
    ]
  }
];

export function getRandomPromptIdea(): string {
  const ideas = [
    '勇敢的小騎士與會吐七彩泡泡的友好巨龍',
    '深海里的珍珠小美人魚與尋寶機器人',
    '會說話的魔法橡木樹與森林精靈的果實祭典',
    '時空小貓咪穿越到糕點國度成爲大廚師'
  ];
  return ideas[Math.floor(Math.random() * ideas.length)];
}
