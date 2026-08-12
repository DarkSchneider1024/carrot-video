"""
Sprite Sheet Processor — Carrot Studio
Cuts a NxN sprite sheet image into individual frames, removes white/light background, 
and generates a smooth, low-fatigue animated GIF.

Usage:
  python scripts/generate_sprite_animation.py \
    --sprite public/assets/north_wind_sprite_ai.png \
    --rows 3 --cols 3 \
    --fps 2.5 \
    --remove-bg \
    --ping-pong \
    --output public/assets/north_wind_anim.gif
"""

import os
import sys
import argparse
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image, ImageFilter

def remove_white_background(img: Image.Image, threshold: int = 235, soft_margin: int = 20) -> Image.Image:
    """
    Remove white/light background from character sprite and create smooth alpha transparency.
    """
    img = img.convert("RGBA")
    data = img.getdata()
    new_data = []
    
    for item in data:
        r, g, b, a = item
        # Check brightness / lightness
        min_c = min(r, g, b)
        max_c = max(r, g, b)
        diff = max_c - min_c
        
        # If pixel is near-white and low saturation (background)
        if r >= threshold and g >= threshold and b >= threshold and diff < 25:
            # Completely transparent
            new_data.append((255, 255, 255, 0))
        elif r >= (threshold - soft_margin) and g >= (threshold - soft_margin) and b >= (threshold - soft_margin) and diff < 30:
            # Soft alpha transition for clean anti-aliasing edges
            avg = (r + g + b) / 3.0
            alpha = int(255 * (1.0 - (avg - (threshold - soft_margin)) / float(soft_margin)))
            alpha = max(0, min(255, alpha))
            new_data.append((r, g, b, alpha))
        else:
            new_data.append((r, g, b, a))

    img.putdata(new_data)
    return img


def cut_sprite_sheet(sprite_path: str, rows: int, cols: int, output_dir: str, remove_bg: bool = True) -> list[str]:
    """Cut a sprite sheet into individual frame PNGs with background removal."""
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
            
            if remove_bg:
                frame = remove_white_background(frame)
                
            frame_path = os.path.join(output_dir, f"frame_{frame_idx:03d}.png")
            frame.save(frame_path, "PNG")
            frame_paths.append(frame_path)
            frame_idx += 1

    print(f"[OK] Cut {frame_idx} frames with background removal -> {output_dir}")
    return frame_paths


def make_animated_gif(frame_paths: list[str], output_gif: str, fps: float = 2.5,
                      target_size: tuple[int,int] | None = None, ping_pong: bool = True, loop: int = 0):
    """
    Combine frame PNGs into a smooth, low-fatigue animated GIF.
    - Low FPS (default 2.5 fps) prevents eye fatigue
    - Ping-pong loop provides smooth forward-and-backward breathing motion
    """
    raw_frames = []
    for p in frame_paths:
        img = Image.open(p).convert("RGBA")
        if target_size:
            img = img.resize(target_size, Image.LANCZOS)
        raw_frames.append(img)

    # Ping-pong sequence: 0 -> 1 -> ... -> N-1 -> N-2 -> ... -> 1
    if ping_pong and len(raw_frames) > 2:
        frames_seq = raw_frames + raw_frames[-2:0:-1]
    else:
        frames_seq = raw_frames

    duration_ms = int(1000.0 / fps)
    
    # Save as transparent animated GIF
    frames_seq[0].save(
        output_gif,
        save_all=True,
        append_images=frames_seq[1:],
        duration=duration_ms,
        loop=loop,
        disposal=2,
        transparency=0,
    )
    size_kb = os.path.getsize(output_gif) // 1024
    print(f"[OK] Low-Fatigue Transparent GIF done: {output_gif} ({len(frames_seq)} frames, {fps}fps, {size_kb} KB)")


def main():
    parser = argparse.ArgumentParser(description="Sprite Sheet → Transparent Low-Fatigue Animated GIF Processor")
    parser.add_argument("--sprite",    required=True, help="Path to sprite sheet image")
    parser.add_argument("--rows",      type=int, default=3, help="Number of rows in sprite sheet")
    parser.add_argument("--cols",      type=int, default=3, help="Number of columns in sprite sheet")
    parser.add_argument("--fps",       type=float, default=2.5, help="Animation frame rate (default 2.5 fps for comfortable pacing)")
    parser.add_argument("--output",    required=True, help="Output animated GIF path")
    parser.add_argument("--size",      type=int, default=480, help="Output GIF square size (px)")
    parser.add_argument("--no-bg-remove", action="store_true", help="Disable automatic white background removal")
    parser.add_argument("--no-ping-pong", action="store_true", help="Disable ping-pong smooth looping")
    parser.add_argument("--frames-dir", default=None, help="Directory to save individual frames (optional)")
    args = parser.parse_args()

    frames_dir = args.frames_dir or os.path.splitext(args.output)[0] + "_frames"
    remove_bg = not args.no_bg_remove
    ping_pong = not args.no_ping_pong

    frame_paths = cut_sprite_sheet(args.sprite, args.rows, args.cols, frames_dir, remove_bg=remove_bg)
    make_animated_gif(frame_paths, args.output, fps=args.fps, target_size=(args.size, args.size), ping_pong=ping_pong)
    
    print(f"\n[DONE] Transparent sprite animation complete!")
    print(f"  Frames : {frames_dir}/")
    print(f"  GIF    : {args.output}")


if __name__ == "__main__":
    main()
