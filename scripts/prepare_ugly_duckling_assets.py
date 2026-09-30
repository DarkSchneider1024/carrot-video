import os
import sys
import shutil
import math
from collections import deque
from PIL import Image, ImageDraw, ImageOps, ImageFilter

sys.stdout.reconfigure(encoding='utf-8')

def remove_outer_white_background(img_path: str, out_png_path: str, color_tol: int = 35):
    """
    Remove ONLY the outer white/near-white background starting from the corners (BFS Flood Fill),
    preserving any white color inside the character sticker contour.
    """
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size
    pixels = img.load()
    
    visited = [[False for _ in range(h)] for _ in range(w)]
    queue = deque()
    
    def is_near_white(x, y):
        r, g, b, a = pixels[x, y]
        # Distance from pure white (255, 255, 255)
        dist = math.sqrt((255 - r)**2 + (255 - g)**2 + (255 - b)**2)
        return dist <= color_tol
    
    # Push all 4 image borders to queue if near white
    for x in range(w):
        if is_near_white(x, 0):
            queue.append((x, 0))
            visited[x][0] = True
        if is_near_white(x, h - 1):
            queue.append((x, h - 1))
            visited[x][h - 1] = True
            
    for y in range(h):
        if is_near_white(0, y) and not visited[0][y]:
            queue.append((0, y))
            visited[0][y] = True
        if is_near_white(w - 1, y) and not visited[w - 1][y]:
            queue.append((w - 1, y))
            visited[w - 1][y] = True
            
    # BFS flood fill
    while queue:
        cx, cy = queue.popleft()
        # Set outer pixel to transparent
        r, g, b, _ = pixels[cx, cy]
        pixels[cx, cy] = (255, 255, 255, 0)
        
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < w and 0 <= ny < h and not visited[nx][ny]:
                if is_near_white(nx, ny):
                    visited[nx][ny] = True
                    queue.append((nx, ny))
                    
    # Crop to bounding box
    bbox = img.getbbox()
    if bbox:
        pad = 16
        w_crop = max(0, bbox[0] - pad)
        h_crop = max(0, bbox[1] - pad)
        w2_crop = min(img.width, bbox[2] + pad)
        h2_crop = min(img.height, bbox[3] + pad)
        img = img.crop((w_crop, h_crop, w2_crop, h2_crop))
        
    # Put onto square canvas
    max_dim = max(img.width, img.height)
    square_img = Image.new("RGBA", (max_dim, max_dim), (0, 0, 0, 0))
    offset = ((max_dim - img.width) // 2, (max_dim - img.height) // 2)
    square_img.paste(img, offset)
    
    os.makedirs(os.path.dirname(os.path.abspath(out_png_path)), exist_ok=True)
    res_img = square_img.resize((512, 512), Image.Resampling.LANCZOS)
    res_img.save(out_png_path, "PNG")
    print(f"  ✓ Transparent sticker saved: {out_png_path}")

def generate_graceful_swan_sticker(out_path):
    size = 1024
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2 + 50
    
    # Body ellipse / feather shapes
    draw.ellipse([cx - 300, cy - 100, cx + 320, cy + 260], fill=(255, 255, 255, 255), outline=(30, 30, 30, 255), width=16)
    
    # Tail feathers
    tail_pts = [(cx + 250, cy), (cx + 380, cy - 80), (cx + 340, cy + 50), (cx + 420, cy - 20), (cx + 300, cy + 150)]
    draw.polygon(tail_pts, fill=(255, 255, 255, 255), outline=(30, 30, 30, 255))
    draw.line(tail_pts + [tail_pts[0]], fill=(30, 30, 30, 255), width=16)
    
    # Wing detail
    draw.arc([cx - 200, cy - 60, cx + 220, cy + 200], start=180, end=360, fill=(40, 40, 40, 255), width=12)
    draw.arc([cx - 150, cy, cx + 180, cy + 220], start=180, end=360, fill=(40, 40, 40, 255), width=10)
    
    # S-curved Neck & Head
    neck_pts_left = [
        (cx - 150, cy + 50),
        (cx - 240, cy - 80),
        (cx - 260, cy - 240),
        (cx - 190, cy - 360),
        (cx - 70, cy - 380),
        (cx - 10, cy - 320),
        (cx - 70, cy - 240),
        (cx - 140, cy - 160),
        (cx - 110, cy + 60)
    ]
    draw.polygon(neck_pts_left, fill=(255, 255, 255, 255), outline=(30, 30, 30, 255))
    draw.line(neck_pts_left + [neck_pts_left[0]], fill=(30, 30, 30, 255), width=18)
    
    # Head & Beak
    head_cx, head_cy = cx - 50, cy - 330
    draw.ellipse([head_cx - 90, head_cy - 90, head_cx + 70, head_cy + 70], fill=(255, 255, 255, 255), outline=(30, 30, 30, 255), width=16)
    
    # Golden Orange Beak
    beak_pts = [(head_cx + 50, head_cy - 20), (head_cx + 170, head_cy + 30), (head_cx + 40, head_cy + 50)]
    draw.polygon(beak_pts, fill=(255, 170, 0, 255), outline=(30, 30, 30, 255))
    draw.line(beak_pts + [beak_pts[0]], fill=(30, 30, 30, 255), width=14)
    draw.ellipse([head_cx + 20, head_cy - 25, head_cx + 55, head_cy + 15], fill=(30, 30, 30, 255))
    
    # Eye
    draw.ellipse([head_cx - 10, head_cy - 40, head_cx + 25, head_cy - 5], fill=(30, 30, 30, 255))
    draw.ellipse([head_cx + 5, head_cy - 35, head_cx + 18, head_cy - 20], fill=(255, 255, 255, 255))
    
    # Blush cheek
    draw.ellipse([head_cx - 30, head_cy - 5, head_cx + 10, head_cy + 30], fill=(255, 180, 190, 160))
    
    # Golden Crown on Head
    crown_pts = [
        (head_cx - 60, head_cy - 80),
        (head_cx - 70, head_cy - 140),
        (head_cx - 20, head_cy - 105),
        (head_cx + 10, head_cy - 150),
        (head_cx + 35, head_cy - 100),
        (head_cx + 60, head_cy - 135),
        (head_cx + 50, head_cy - 75)
    ]
    draw.polygon(crown_pts, fill=(255, 215, 0, 255), outline=(30, 30, 30, 255))
    draw.line(crown_pts + [crown_pts[0]], fill=(30, 30, 30, 255), width=12)
    draw.ellipse([head_cx + 5, head_cy - 125, head_cx + 15, head_cy - 115], fill=(255, 50, 100, 255))
    
    # Water ripples at bottom
    draw.ellipse([cx - 360, cy + 220, cx + 390, cy + 290], fill=(180, 230, 255, 220), outline=(50, 150, 230, 255), width=12)
    
    img_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
    img_512.save(out_path, "PNG")
    print(f"  ✓ Created graceful swan sticker: {out_path}")

def generate_flying_swan_sticker(out_path):
    size = 1024
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size // 2, size // 2 + 50
    
    # Large spread wings (left and right)
    left_wing = [
        (cx - 60, cy - 50),
        (cx - 250, cy - 250),
        (cx - 430, cy - 380),
        (cx - 400, cy - 260),
        (cx - 440, cy - 220),
        (cx - 390, cy - 120),
        (cx - 420, cy - 60),
        (cx - 320, cy + 20),
        (cx - 100, cy + 20)
    ]
    draw.polygon(left_wing, fill=(255, 255, 255, 255), outline=(30, 30, 30, 255))
    draw.line(left_wing + [left_wing[0]], fill=(30, 30, 30, 255), width=18)
    
    right_wing = [
        (cx + 60, cy - 50),
        (cx + 250, cy - 250),
        (cx + 430, cy - 380),
        (cx + 400, cy - 260),
        (cx + 440, cy - 220),
        (cx + 390, cy - 120),
        (cx + 420, cy - 60),
        (cx + 320, cy + 20),
        (cx + 100, cy + 20)
    ]
    draw.polygon(right_wing, fill=(255, 255, 255, 255), outline=(30, 30, 30, 255))
    draw.line(right_wing + [right_wing[0]], fill=(30, 30, 30, 255), width=18)
    
    # Body & Tail
    body_pts = [
        (cx - 90, cy - 80),
        (cx + 90, cy - 80),
        (cx + 70, cy + 180),
        (cx, cy + 320),
        (cx - 70, cy + 180)
    ]
    draw.polygon(body_pts, fill=(255, 255, 255, 255), outline=(30, 30, 30, 255))
    draw.line(body_pts + [body_pts[0]], fill=(30, 30, 30, 255), width=18)
    
    # Forward reaching Neck & Head
    neck_pts = [
        (cx - 45, cy - 80),
        (cx - 35, cy - 280),
        (cx - 60, cy - 360),
        (cx, cy - 420),
        (cx + 60, cy - 360),
        (cx + 35, cy - 280),
        (cx + 45, cy - 80)
    ]
    draw.polygon(neck_pts, fill=(255, 255, 255, 255), outline=(30, 30, 30, 255))
    draw.line(neck_pts + [neck_pts[0]], fill=(30, 30, 30, 255), width=18)
    
    # Head & Beak
    head_cx, head_cy = cx, cy - 380
    draw.ellipse([head_cx - 50, head_cy - 50, head_cx + 50, head_cy + 50], fill=(255, 255, 255, 255), outline=(30, 30, 30, 255), width=16)
    
    beak_pts = [(head_cx - 25, head_cy - 35), (head_cx, head_cy - 120), (head_cx + 25, head_cy - 35)]
    draw.polygon(beak_pts, fill=(255, 170, 0, 255), outline=(30, 30, 30, 255))
    draw.line(beak_pts + [beak_pts[0]], fill=(30, 30, 30, 255), width=14)
    draw.ellipse([head_cx - 20, head_cy - 40, head_cx + 20, head_cy - 20], fill=(30, 30, 30, 255))
    
    # Eyes
    draw.ellipse([head_cx - 35, head_cy - 15, head_cx - 15, head_cy + 5], fill=(30, 30, 30, 255))
    draw.ellipse([head_cx + 15, head_cy - 15, head_cx + 35, head_cy + 5], fill=(30, 30, 30, 255))
    
    # Golden Crown
    crown_pts = [
        (head_cx - 40, head_cy - 50),
        (head_cx - 45, head_cy - 90),
        (head_cx - 15, head_cy - 70),
        (head_cx, head_cy - 105),
        (head_cx + 15, head_cy - 70),
        (head_cx + 45, head_cy - 90),
        (head_cx + 40, head_cy - 50)
    ]
    draw.polygon(crown_pts, fill=(255, 215, 0, 255), outline=(30, 30, 30, 255))
    draw.line(crown_pts + [crown_pts[0]], fill=(30, 30, 30, 255), width=10)
    
    img_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
    img_512.save(out_path, "PNG")
    print(f"  ✓ Created flying swan sticker: {out_path}")

if __name__ == "__main__":
    brain_dir = r"C:\Users\gueiw\.gemini\antigravity-ide\brain\ca6881a9-e145-4695-a6f4-c5cef51359bf"
    assets_dir = r"c:\GitRoot\CarrotStudio\carrot-video\public\assets"
    story_img_dir = r"c:\GitRoot\CarrotStudio\carrot-video\醜小鴨\image"
    os.makedirs(assets_dir, exist_ok=True)
    os.makedirs(story_img_dir, exist_ok=True)
    
    bg_maps = {
        "bg_duck_pond_1786945368560.jpg": "bg_duck_pond.png",
        "bg_duck_barn_1786945513517.jpg": "bg_duck_barn.png",
        "bg_winter_lake_1786945674722.jpg": "bg_winter_lake.png",
        "bg_spring_lake_1786945855751.jpg": "bg_spring_lake.png",
        "bg_swan_sky_1786945893739.jpg": "bg_swan_sky.png",
    }
    
    for src_name, dst_name in bg_maps.items():
        src_path = os.path.join(brain_dir, src_name)
        if os.path.exists(src_path):
            img = Image.open(src_path).convert("RGB")
            img_hd = img.resize((1920, 1080), Image.Resampling.LANCZOS)
            img_hd.save(os.path.join(assets_dir, dst_name))
            img_hd.save(os.path.join(story_img_dir, dst_name))
            print(f"  ✓ Saved 1080p background: {dst_name}")

    remove_outer_white_background(
        os.path.join(brain_dir, "ugly_duckling_grey_1786946873579.jpg"),
        os.path.join(assets_dir, "ugly_duckling_grey.png"),
        color_tol=45
    )
    shutil.copyfile(os.path.join(assets_dir, "ugly_duckling_grey.png"), os.path.join(story_img_dir, "ugly_duckling_grey.png"))

    remove_outer_white_background(
        os.path.join(brain_dir, "mocking_ducks_1786946891025.jpg"),
        os.path.join(assets_dir, "mocking_ducks.png"),
        color_tol=45
    )
    shutil.copyfile(os.path.join(assets_dir, "mocking_ducks.png"), os.path.join(story_img_dir, "mocking_ducks.png"))

    remove_outer_white_background(
        os.path.join(brain_dir, "ugly_duckling_winter_1786946910062.jpg"),
        os.path.join(assets_dir, "ugly_duckling_winter.png"),
        color_tol=45
    )
    shutil.copyfile(os.path.join(assets_dir, "ugly_duckling_winter.png"), os.path.join(story_img_dir, "ugly_duckling_winter.png"))

    generate_graceful_swan_sticker(os.path.join(assets_dir, "swan_beautiful.png"))
    shutil.copyfile(os.path.join(assets_dir, "swan_beautiful.png"), os.path.join(story_img_dir, "swan_beautiful.png"))

    generate_flying_swan_sticker(os.path.join(assets_dir, "swan_flying.png"))
    shutil.copyfile(os.path.join(assets_dir, "swan_flying.png"), os.path.join(story_img_dir, "swan_flying.png"))

    print("All image assets prepared successfully!")
