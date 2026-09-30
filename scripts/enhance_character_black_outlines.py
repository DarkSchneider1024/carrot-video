import os
import sys
import shutil
from PIL import Image, ImageFilter, ImageOps

sys.stdout.reconfigure(encoding='utf-8')

def add_bold_black_outline(img_path: str, out_path: str, outline_px: int = 6):
    """
    Adds a solid, clean, bold black contour outline around the entire character sprite,
    guaranteeing crisp edges that never get accidentally cropped or clipped.
    """
    img = Image.open(img_path).convert("RGBA")
    
    # Extract alpha channel
    alpha = img.split()[3]
    
    # Create outline by expanding the binary alpha mask
    # Threshold alpha to 0 or 255
    binary_alpha = alpha.point(lambda p: 255 if p > 50 else 0)
    
    # Expand the mask by outline_px using MaxFilter
    expanded_alpha = binary_alpha.filter(ImageFilter.MaxFilter(outline_px * 2 + 1))
    
    # Create solid black image for the outline
    black_canvas = Image.new("RGBA", img.size, (20, 20, 20, 255))
    
    # Composite: Black outline behind original character
    outlined_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
    outlined_img.paste(black_canvas, (0, 0), mask=expanded_alpha)
    outlined_img.paste(img, (0, 0), mask=alpha)
    
    # Auto-crop with comfortable padding
    bbox = outlined_img.getbbox()
    if bbox:
        pad = 20
        w_crop = max(0, bbox[0] - pad)
        h_crop = max(0, bbox[1] - pad)
        w2_crop = min(outlined_img.width, bbox[2] + pad)
        h2_crop = min(outlined_img.height, bbox[3] + pad)
        outlined_img = outlined_img.crop((w_crop, h_crop, w2_crop, h2_crop))
        
    # Resize onto square 512x512 canvas
    max_dim = max(outlined_img.width, outlined_img.height)
    square_img = Image.new("RGBA", (max_dim, max_dim), (0, 0, 0, 0))
    offset = ((max_dim - outlined_img.width) // 2, (max_dim - outlined_img.height) // 2)
    square_img.paste(outlined_img, offset)
    
    final_512 = square_img.resize((512, 512), Image.Resampling.LANCZOS)
    
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    final_512.save(out_path, "PNG")
    print(f"  ✓ Added bold black outline (width {outline_px}px): {out_path}")

if __name__ == "__main__":
    assets_dir = r"c:\GitRoot\CarrotStudio\carrot-video\public\assets"
    story_img_dir = r"c:\GitRoot\CarrotStudio\carrot-video\醜小鴨\image"
    
    characters = [
        "ugly_duckling_grey.png",
        "mocking_ducks.png",
        "ugly_duckling_winter.png",
        "swan_beautiful.png",
        "swan_flying.png"
    ]
    
    print("🎨 Enhancing bold black outlines for all 醜小鴨 characters...")
    for char in characters:
        src = os.path.join(assets_dir, char)
        if os.path.exists(src):
            add_bold_black_outline(src, src, outline_px=7)
            shutil.copyfile(src, os.path.join(story_img_dir, char))
            
    print("✅ All character outlines updated successfully!")
