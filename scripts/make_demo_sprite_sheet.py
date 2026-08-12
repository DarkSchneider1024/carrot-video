"""
Sprite Sheet Generator from Single Image (Demo / Fallback)
Generates a 3x3 sprite sheet by applying per-frame transformations
(offset, scale, hue shift, brightness) to simulate different animation poses.

Usage:
  python scripts/make_demo_sprite_sheet.py \
    --input public/assets/north_wind.png \
    --output public/assets/north_wind_sprite.png \
    --rows 3 --cols 3
"""

import os
import sys
import argparse
sys.stdout.reconfigure(encoding='utf-8')
import math
from PIL import Image, ImageEnhance, ImageFilter, ImageChops

def apply_frame_transform(img: Image.Image, frame_idx: int, total: int) -> Image.Image:
    """
    Apply a unique per-frame transform to simulate animation poses.
    Transformations: rotation, horizontal flip, brightness, scale offset
    """
    img = img.copy().convert("RGBA")
    w, h = img.size

    # Per-frame transform table (rotation_deg, scale, brightness, offset_x, offset_y, flip)
    transforms = [
        # Row 0: 北風 吹氣 pose
        (-5,  1.00, 1.05,   0,   0, False),   # 0: neutral lean left
        ( 0,  1.02, 1.10,   0, -10, False),   # 1: center, slightly up (puff start)
        ( 5,  1.00, 1.05,   0,   0, False),   # 2: lean right
        # Row 1: 用力吹 hard blow
        (-8,  1.04, 1.15, -15,   5, False),   # 3: lunge left
        ( 0,  1.05, 1.20,   0,  10, False),   # 4: forward power
        ( 8,  1.04, 1.15,  15,   5, False),   # 5: lunge right
        # Row 2: 回歸 / 挫敗 return
        (-4,  0.98, 0.95,  -5, -5, True),    # 6: flip + slight shrink
        ( 0,  0.96, 0.90,   0,  5, False),   # 7: tired, slightly smaller
        ( 4,  0.98, 0.95,   5, -5, True),    # 8: flip lean
    ]

    if frame_idx >= len(transforms):
        return img

    rot, scale, brightness, off_x, off_y, flip = transforms[frame_idx]

    # Flip
    if flip:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)

    # Rotate
    if rot != 0:
        img = img.rotate(rot, expand=False, resample=Image.BICUBIC)

    # Scale
    if scale != 1.0:
        new_w = int(w * scale)
        new_h = int(h * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        # Crop or pad back to original size
        canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        paste_x = (w - new_w) // 2 + off_x
        paste_y = (h - new_h) // 2 + off_y
        canvas.paste(img, (paste_x, paste_y), img)
        img = canvas
    elif off_x != 0 or off_y != 0:
        canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        canvas.paste(img, (off_x, off_y), img)
        img = canvas

    # Brightness
    if brightness != 1.0:
        r, g, b, a = img.split()
        rgb = Image.merge("RGB", (r, g, b))
        rgb = ImageEnhance.Brightness(rgb).enhance(brightness)
        r2, g2, b2 = rgb.split()
        img = Image.merge("RGBA", (r2, g2, b2, a))

    return img


def main():
    parser = argparse.ArgumentParser(description="Generate demo sprite sheet from single image")
    parser.add_argument("--input",  required=True, help="Input character PNG")
    parser.add_argument("--output", required=True, help="Output sprite sheet PNG")
    parser.add_argument("--rows",   type=int, default=3)
    parser.add_argument("--cols",   type=int, default=3)
    parser.add_argument("--frame-size", type=int, default=512, help="Each frame size (px)")
    args = parser.parse_args()

    n_frames = args.rows * args.cols
    fs = args.frame_size

    src = Image.open(args.input).convert("RGBA")
    # Resize to frame_size for uniformity
    src = src.resize((fs, fs), Image.LANCZOS)

    sheet_w = fs * args.cols
    sheet_h = fs * args.rows
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (255, 255, 255, 255))

    for i in range(n_frames):
        row = i // args.cols
        col = i  % args.cols
        frame = apply_frame_transform(src, i, n_frames)
        sheet.paste(frame, (col * fs, row * fs), frame)
        print(f"  [OK] Frame {i+1}/{n_frames} done")

    os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)
    sheet.save(args.output)
    print(f"\n[DONE] Sprite sheet saved: {args.output}  ({sheet_w}x{sheet_h}px, {n_frames} frames)")


if __name__ == "__main__":
    main()
