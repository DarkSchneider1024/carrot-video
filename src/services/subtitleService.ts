// AutoSubs Automatic Subtitle Generator & SRT File Service

export interface SubtitleScene {
  title: string;
  dialog: string;
  duration?: number;
}

export const formatSRTTime = (seconds: number): string => {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  const millis = Math.floor((seconds % 1) * 1000);

  const pad = (num: number, size: number = 2) => String(num).padStart(size, '0');
  return `${pad(hrs)}:${pad(mins)}:${pad(secs)},${pad(millis, 3)}`;
};

export const generateSRTContent = (scenes: SubtitleScene[], sceneDurationSec: number = 6): string => {
  let srtText = '';
  let currentTime = 0;

  scenes.forEach((scene, index) => {
    const duration = scene.duration || sceneDurationSec;
    const startTime = currentTime;
    const endTime = currentTime + duration;

    srtText += `${index + 1}\n`;
    srtText += `${formatSRTTime(startTime)} --> ${formatSRTTime(endTime)}\n`;
    srtText += `${scene.dialog.trim()}\n\n`;

    currentTime = endTime;
  });

  return srtText;
};

export const downloadSRTFile = (scenes: SubtitleScene[], filename: string = 'fairytale_subtitles.srt'): void => {
  const srtContent = generateSRTContent(scenes);
  const blob = new Blob([srtContent], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);

  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => {
    if (document.body.contains(a)) document.body.removeChild(a);
  }, 1000);
};

export const drawCanvasSubtitles = (
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  text: string
): void => {
  if (!text) return;

  ctx.save();

  const fontSize = Math.max(16, Math.round(width * 0.032));
  ctx.font = `bold ${fontSize}px "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", sans-serif`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';

  // Word wrap dialog text for high readability
  const maxTextWidth = width * 0.82;
  const words = text.split('');
  let line = '';
  const lines: string[] = [];

  for (let n = 0; n < words.length; n++) {
    const testLine = line + words[n];
    const metrics = ctx.measureText(testLine);
    if (metrics.width > maxTextWidth && n > 0) {
      lines.push(line);
      line = words[n];
    } else {
      line = testLine;
    }
  }
  lines.push(line);

  const lineHeight = fontSize * 1.35;
  const totalBoxHeight = lines.length * lineHeight + 18;
  const boxY = height - totalBoxHeight - 24;

  // Draw Dark Rounded Subtitle Pill Container
  const boxWidth = maxTextWidth + 32;
  const boxX = (width - boxWidth) / 2;

  ctx.fillStyle = 'rgba(10, 15, 29, 0.88)';
  ctx.strokeStyle = 'rgba(251, 191, 36, 0.4)';
  ctx.lineWidth = 2;

  // Draw Rounded Rectangle
  const radius = 12;
  ctx.beginPath();
  ctx.moveTo(boxX + radius, boxY);
  ctx.lineTo(boxX + boxWidth - radius, boxY);
  ctx.quadraticCurveTo(boxX + boxWidth, boxY, boxX + boxWidth, boxY + radius);
  ctx.lineTo(boxX + boxWidth, boxY + totalBoxHeight - radius);
  ctx.quadraticCurveTo(boxX + boxWidth, boxY + totalBoxHeight, boxX + boxWidth - radius, boxY + totalBoxHeight);
  ctx.lineTo(boxX + radius, boxY + totalBoxHeight);
  ctx.quadraticCurveTo(boxX, boxY + totalBoxHeight, boxX, boxY + totalBoxHeight - radius);
  ctx.lineTo(boxX, boxY + radius);
  ctx.quadraticCurveTo(boxX, boxY, boxX + radius, boxY);
  ctx.closePath();
  ctx.fill();
  ctx.stroke();

  // Render Subtitle Text with Outline
  lines.forEach((l, i) => {
    const textY = boxY + 12 + i * lineHeight + fontSize / 2;

    // Black Thick Stroke
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 4;
    ctx.lineJoin = 'round';
    ctx.strokeText(l, width / 2, textY);

    // Vibrant Yellow/White Text
    ctx.fillStyle = '#fef08a';
    ctx.fillText(l, width / 2, textY);
  });

  ctx.restore();
};
