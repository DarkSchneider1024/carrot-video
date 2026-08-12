"""
Character Background Alpha Transparent Processing Script
Removes white backgrounds from AI generated character PNGs
"""

import os
import sys
import math
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

def remove_white_background(input_path: str, output_path: str, threshold: int = 40):
    img = Image.open(input_path).convert("RGBA")
    datas = img.getdata()

    new_data = []
    for item in datas:
        r, g, b, a = item
        # Euclidean distance from pure white (255, 255, 255)
        dist = math.sqrt((255 - r)**2 + (255 - g)**2 + (255 - b)**2)
        if dist < threshold:
            new_data.append((255, 255, 255, 0)) # Make transparent
        elif dist < threshold + 20:
            # Smooth edge alpha transition
            alpha = int(((dist - threshold) / 20.0) * 255)
            new_data.append((r, g, b, alpha))
        else:
            new_data.append((r, g, b, a))

    img.putdata(new_data)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img.save(output_path, "PNG")
    print(f"✅ Transparent PNG processed: {output_path}")

if __name__ == "__main__":
    char_map = {
        r"C:\Users\gueiw\.gemini\antigravity-ide\brain\7448899a-daac-4d08-b1cc-fd53756f1439\north_wind_character_1786512701255.png": "public/assets/north_wind.png",
        r"C:\Users\gueiw\.gemini\antigravity-ide\brain\7448899a-daac-4d08-b1cc-fd53756f1439\warm_sun_character_1786513132500.png": "public/assets/warm_sun.png",
        r"C:\Users\gueiw\.gemini\antigravity-ide\brain\7448899a-daac-4d08-b1cc-fd53756f1439\traveler_coat_character_1786513150349.png": "public/assets/traveler_coat.png",
        r"C:\Users\gueiw\.gemini\antigravity-ide\brain\7448899a-daac-4d08-b1cc-fd53756f1439\traveler_rest_character_1786513165768.png": "public/assets/traveler_rest.png"
    }

    for src, dst in char_map.items():
        if os.path.exists(src):
            remove_white_background(src, dst)
        else:
            print(f"File not found: {src}")
