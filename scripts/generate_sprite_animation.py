"""
Sprite Sheet Processor — Carrot Studio
Cuts a NxN sprite sheet image into individual frames and generates an animated GIF.

Usage:
  python scripts/generate_sprite_animation.py \
    --sprite public/assets/north_wind_sprite.png \
    --rows 3 --cols 3 \
    --fps 8 \
    --output public/assets/north_wind_anim.gif
"""

import os
import sys
import argparse
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image

def cut_sprite_sheet(sprite_path: str, rows: int, cols: int, output_dir: str) -> list[str]:
    """Cut a sprite sheet into individual frame PNGs."""
    img = Image.open(sprite_path).convert("RGBA")
    width, height = img.size
    frame_w = width // cols
    frame_h = height // rows

    os.makedirs(output_dir, exist_ok=True)
    frame_paths = []

    frame_idx = 0
    for row in range(rows):
        for col in range(cols):
            left   = col * frame_w
            top    = row * frame_h
            right  = left + frame_w
            bottom = top + frame_h
            frame = img.crop((left, top, right, bottom))
            frame_path = os.path.join(output_dir, f"frame_{frame_idx:03d}.png")
            frame.save(frame_path)
            frame_paths.append(frame_path)
            frame_idx += 1

    print(f"[OK] Cut {frame_idx} frames -> {output_dir}")
    return frame_paths


def make_animated_gif(frame_paths: list[str], output_gif: str, fps: int = 8,
                      target_size: tuple[int,int] | None = None, loop: int = 0):
    """Combine frame PNGs into an animated GIF."""
    frames = []
    for p in frame_paths:
        img = Image.open(p).convert("RGBA")
        if target_size:
            img = img.resize(target_size, Image.LANCZOS)
        frames.append(img)

    duration_ms = int(1000 / fps)
    frames[0].save(
        output_gif,
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,
        loop=loop,
        disposal=2,
    )
    size_kb = os.path.getsize(output_gif) // 1024
    print(f"[OK] Animated GIF done: {output_gif}  ({len(frames)} frames, {fps}fps, {size_kb} KB)")


def main():
    parser = argparse.ArgumentParser(description="Sprite Sheet → Animated GIF Processor")
    parser.add_argument("--sprite",  required=True, help="Path to sprite sheet image")
    parser.add_argument("--rows",    type=int, default=3, help="Number of rows in sprite sheet")
    parser.add_argument("--cols",    type=int, default=3, help="Number of columns in sprite sheet")
    parser.add_argument("--fps",     type=int, default=8, help="Animation frame rate")
    parser.add_argument("--output",  required=True, help="Output animated GIF path")
    parser.add_argument("--size",    type=int, default=480, help="Output GIF square size (px)")
    parser.add_argument("--frames-dir", default=None, help="Directory to save individual frames (optional)")
    args = parser.parse_args()

    frames_dir = args.frames_dir or os.path.splitext(args.output)[0] + "_frames"
    frame_paths = cut_sprite_sheet(args.sprite, args.rows, args.cols, frames_dir)
    make_animated_gif(frame_paths, args.output, fps=args.fps, target_size=(args.size, args.size))
    print(f"\n[DONE] Sprite animation complete!")
    print(f"  Frames : {frames_dir}/")
    print(f"  GIF    : {args.output}")


if __name__ == "__main__":
    main()
