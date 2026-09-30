# -*- coding: utf-8 -*-
"""Backgrounds for 《小紅帽：半夜三點的牛肉麵》 (night interiors), same painted style as backgrounds.py.

    python live2d/backgrounds_noodle.py   -> 小紅帽/backgrounds/<scene>/*.png, merged into layers.json

Layers named 'front' are drawn IN FRONT of the actors (bed quilt the wolf hides under, the dining table).
"""
import json, math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from backgrounds import (H, OUT, rgba, layer, vgrad, blob, ellipse_pts, noise, forest)


def font(size):
    for f in ('C:/Windows/Fonts/consolab.ttf', 'C:/Windows/Fonts/consola.ttf', 'C:/Windows/Fonts/arialbd.ttf'):
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def grade(im, mul, add=(0, 0, 0)):
    """colour-grade a layer (daylight -> moonlight), alpha untouched"""
    a = np.asarray(im).astype(np.float32)
    a[..., :3] = np.clip(a[..., :3] * np.array(mul, np.float32) + np.array(add, np.float32), 0, 255)
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def moon_window(im, x, y, w, h, frame='#4a3a44', sky=('#101a3a', '#27335e'), moon=True, curtain='#6b4a7a'):
    blob(im, [(x - 14, y - 14), (x + w + 14, y - 14), (x + w + 14, y + h + 14), (x - 14, y + h + 14)], rgba(frame))
    g = vgrad(w, sky[0], sky[1], 0, h).crop((0, 0, w, h))
    im.alpha_composite(g, (x, y))
    rng = random.Random(x)
    d = ImageDraw.Draw(im)
    for _ in range(26):
        sx, sy = rng.uniform(x, x + w), rng.uniform(y, y + h * 0.8)
        d.ellipse([sx - 1.5, sy - 1.5, sx + 1.5, sy + 1.5], fill=rgba('#fdf6d8', 220))
    if moon:
        blob(im, ellipse_pts(x + w * 0.68, y + h * 0.3, 70, 70), rgba('#fff6c8', 90), blur=30)
        blob(im, ellipse_pts(x + w * 0.68, y + h * 0.3, 38, 38), rgba('#fff4c2'))
        blob(im, ellipse_pts(x + w * 0.68 + 16, y + h * 0.3 - 8, 34, 34), rgba(sky[0]))       # crescent
    blob(im, [(x + w / 2 - 5, y), (x + w / 2 + 5, y), (x + w / 2 + 5, y + h), (x + w / 2 - 5, y + h)], rgba(frame))
    blob(im, [(x, y + h / 2 - 5), (x + w, y + h / 2 - 5), (x + w, y + h / 2 + 5), (x, y + h / 2 + 5)], rgba(frame))
    for side in (0, 1):                                                                   # curtains
        cx = x - 40 if side == 0 else x + w + 40
        sk = 20 if side else -20
        blob(im, [(cx - 50, y - 40), (cx + 50, y - 40), (cx + 30 + sk, y + h + 60), (cx - 30 + sk, y + h + 60)], rgba(curtain))
        for k in range(3):
            blob(im, [(cx - 30 + k * 25, y - 40), (cx - 22 + k * 25, y - 40), (cx - 24 + k * 25, y + h + 60),
                      (cx - 32 + k * 25, y + h + 60)], rgba('#000000', 40), blur=4)


def room_base(W, wall_top, wall_bot, floor_col, floor_dk, floor_y=760):
    wall = vgrad(W, wall_top, wall_bot, 0, floor_y)
    blob(wall, [(0, floor_y - 30), (W, floor_y - 30), (W, floor_y), (0, floor_y)], rgba('#000000', 60))   # skirting
    floor = layer(W)
    blob(floor, [(0, floor_y), (W, floor_y), (W, H), (0, H)], rgba(floor_col))
    d = ImageDraw.Draw(floor)
    for k, y in enumerate(range(floor_y + 30, H, 46)):                                     # boards
        d.line([(0, y), (W, y)], fill=rgba(floor_dk, 150), width=2)
        for x in range((k % 2) * 120, W, 240):
            d.line([(x, y), (x, y + 46)], fill=rgba(floor_dk, 110), width=2)
    return noise(wall, 3, 1), noise(floor, 4, 2)


def headboard(im, x, y, w, col='#7a5238'):
    """headboard + pillow; y = mattress top"""
    blob(im, [(x - 14, y - 250), (x + w + 14, y - 250), (x + w + 14, y + 40), (x - 14, y + 40)], rgba(col))
    blob(im, ellipse_pts(x + w / 2, y - 250, w / 2 + 14, 50), rgba(col))
    blob(im, [(x + 12, y - 226), (x + w - 12, y - 226), (x + w - 12, y - 30), (x + 12, y - 30)], rgba('#000000', 50), blur=4)
    blob(im, ellipse_pts(x + w / 2, y - 60, w * 0.36, 44), rgba('#f6f1ea'))
    blob(im, ellipse_pts(x + w / 2, y - 48, w * 0.34, 20), rgba('#d8d0c4'), blur=6)


def bedroom_night():
    """小紅帽's bedroom at 02:39: moonlit window, her bed, nightstand with a red LED alarm clock"""
    W = 2400
    L = {}
    wall, floor = room_base(W, '#2c2a4a', '#3a3558', '#5a4a52', '#43363d')
    moon_window(wall, 1480, 170, 420, 330)
    for x in range(0, W, 90):
        blob(wall, [(x, 0), (x + 30, 0), (x + 30, 730), (x, 730)], rgba('#ffffff', 8))
    blob(wall, [(1400, 520), (2000, 520), (2350, 1080), (1250, 1080)], rgba('#9db4ff', 30), blur=40)     # moonbeam
    blob(wall, [(330, 180), (560, 180), (560, 460), (330, 460)], rgba('#b75b6a'))                          # poster
    blob(wall, [(350, 200), (540, 200), (540, 440), (350, 440)], rgba('#e8c6a8'))
    blob(wall, ellipse_pts(445, 300, 60, 60), rgba('#b75b6a'))
    L['wall'] = (wall, 0.9)
    room = layer(W)
    headboard(room, 250, 800, 620, '#6b4a36')
    blob(room, [(240, 780), (880, 780), (900, 900), (230, 900)], rgba('#c0394a'))                          # red quilt
    blob(room, [(240, 870), (900, 870), (900, 930), (230, 930)], rgba('#8e2433'))
    blob(room, [(240, 930), (900, 930), (900, 990), (240, 990)], rgba('#6b4a36'))
    blob(room, [(1020, 690), (1260, 690), (1260, 960), (1020, 960)], rgba('#6b4a36'))                      # nightstand
    blob(room, [(1010, 676), (1270, 676), (1270, 700), (1010, 700)], rgba('#83603f'))
    blob(room, [(1060, 600), (1230, 600), (1238, 680), (1052, 680)], rgba('#1c1c22'))                      # alarm clock
    blob(room, ellipse_pts(1145, 640, 110, 60), rgba('#ff3b3b', 40), blur=20)
    ImageDraw.Draw(room).text((1145, 640), '02:39', font=font(58), fill=rgba('#ff3b3b'), anchor='mm')
    L['floor'] = (floor, 1.0)                 # floor BELOW the furniture
    L['room'] = (room, 1.0)
    return W, L


def forest_night():
    W, L = forest()
    out = {}
    sky = vgrad(W, '#0b1230', '#23305a', 0, 800)
    d = ImageDraw.Draw(sky)
    rng = random.Random(3)
    for _ in range(260):
        x, y, r = rng.uniform(0, W), rng.uniform(0, 600), rng.uniform(0.8, 2.2)
        d.ellipse([x - r, y - r, x + r, y + r], fill=rgba('#fdf6d8', int(rng.uniform(120, 255))))
    blob(sky, ellipse_pts(2300, 190, 140, 140), rgba('#fff6c8', 70), blur=50)
    blob(sky, ellipse_pts(2300, 190, 70, 70), rgba('#fff4c2'))
    out['sky'] = (sky, 0.1)
    out['far'] = (grade(L['far'][0], (0.30, 0.36, 0.62)), 0.25)
    out['mid'] = (grade(L['mid'][0], (0.26, 0.30, 0.52)), 0.6)
    g = grade(L['ground'][0], (0.30, 0.34, 0.55))
    rng = random.Random(9)
    for _ in range(40):                                                                   # fireflies
        x, y = rng.uniform(0, W), rng.uniform(760, 980)
        blob(g, ellipse_pts(x, y, 10, 10), rgba('#f5ff9a', 60), blur=6)
        blob(g, ellipse_pts(x, y, 2.5, 2.5), rgba('#faffc8'))
    out['ground'] = (g, 1.0)
    out['fg'] = (grade(L['fg'][0], (0.22, 0.26, 0.42)), 1.25)
    return W, out


BED_X, BED_W, BED_Y = 1480, 460, 900       # grandma's bed (actors sit here); BED_Y = mattress top


def grandma_room(candle=False):
    """grandma's bedroom: door (left), wardrobe, window, bed with headboard (right), nightstand + lamp / candle"""
    W = 2400
    L = {}
    top, bot = ('#5a4638', '#6e5645') if not candle else ('#2e2230', '#3a2c34')
    wall, floor = room_base(W, top, bot, '#7a5a40', '#5c4230')
    for x in range(0, W, 60):
        blob(wall, [(x, 0), (x + 3, 0), (x + 3, 730), (x, 730)], rgba('#000000', 30))
    moon_window(wall, 1080, 160, 300, 280, frame='#3e2e24', curtain='#8a5a5a')
    blob(wall, [(1880, 170), (2060, 170), (2060, 330), (1880, 330)], rgba('#c9a24a'))                     # photo frame
    blob(wall, [(1895, 185), (2045, 185), (2045, 315), (1895, 315)], rgba('#e9ddc6'))
    L['wall'] = (wall, 0.9)
    room = layer(W)
    blob(room, [(120, 200), (400, 200), (400, 770), (120, 770)], rgba('#6b4a36'))                          # door
    blob(room, [(140, 220), (380, 220), (380, 770), (140, 770)], rgba('#83603f'))
    blob(room, ellipse_pts(355, 500, 10, 10), rgba('#d8b060'))
    blob(room, [(560, 150), (960, 150), (960, 800), (560, 800)], rgba('#5e3f2c'))                          # wardrobe
    blob(room, [(575, 170), (755, 170), (755, 780), (575, 780)], rgba('#7a5238'))
    blob(room, [(765, 170), (945, 170), (945, 780), (765, 780)], rgba('#7a5238'))
    for x in (745, 775):
        blob(room, [(x - 4, 440), (x + 4, 440), (x + 4, 500), (x - 4, 500)], rgba('#d8b060'))
    headboard(room, BED_X, BED_Y - 180, BED_W)
    blob(room, [(BED_X - 10, BED_Y - 20), (BED_X + BED_W + 10, BED_Y - 20), (BED_X + BED_W + 10, BED_Y + 90),
                (BED_X - 10, BED_Y + 90)], rgba('#6b4a36'))                                                  # bed frame
    blob(room, [(1990, 690), (2190, 690), (2190, 960), (1990, 960)], rgba('#6b4a36'))                      # nightstand
    blob(room, [(1980, 676), (2200, 676), (2200, 700), (1980, 700)], rgba('#83603f'))
    if not candle:
        blob(room, [(2060, 560), (2120, 560), (2140, 676), (2040, 676)], rgba('#caa56a'))                  # lamp
        blob(room, [(2020, 470), (2160, 470), (2130, 565), (2050, 565)], rgba('#f7e2b0'))
        blob(room, ellipse_pts(2090, 520, 260, 200), rgba('#ffd98a', 50), blur=60)
    else:
        blob(room, [(2080, 600), (2100, 600), (2100, 676), (2080, 676)], rgba('#f2ead8'))                  # candle
        blob(room, ellipse_pts(2090, 588, 8, 14), rgba('#ffcf5a'))
        blob(room, ellipse_pts(2090, 588, 240, 220), rgba('#ffb04a', 70), blur=70)
    L['floor'] = (floor, 1.0)                 # floor BELOW the furniture
    L['room'] = (room, 1.0)
    if candle:
        # the quilt the disguised wolf hides under -- in FRONT of the actors
        front = layer(W)
        top_edge = [(BED_X - 25, 720), (BED_X + 80, 706), (BED_X + 230, 712), (BED_X + 380, 704), (BED_X + 485, 720)]
        blob(front, top_edge + [(BED_X + 510, 1000), (BED_X - 40, 1000)], rgba('#e9d8b4'))
        for x in range(BED_X, BED_X + 480, 60):
            blob(front, [(x, 715), (x + 3, 715), (x + 8, 1000), (x + 5, 1000)], rgba('#c8b288'))
        blob(front, [(BED_X - 40, 700), (BED_X + 510, 700), (BED_X + 510, 740), (BED_X - 40, 740)], rgba('#fff6e4', 110), blur=10)
        blob(front, [(BED_X - 50, 990), (BED_X + 520, 990), (BED_X + 520, H), (BED_X - 50, H)], rgba('#6b4a36'))
        L['front'] = (front, 1.0)
    return W, L


TABLE_Y = 740                               # dining table top (actors sit behind it)


def living_room():
    """living room / kitchen at night: dining table in front of the actors, bowl of beef noodles, microwave"""
    W = 2400
    L = {}
    wall, floor = room_base(W, '#4a4034', '#5a4e40', '#8a6a4c', '#6a4e38')
    moon_window(wall, 1700, 150, 320, 280, frame='#3e2e24', curtain='#7a6a4a')
    blob(wall, [(200, 420), (900, 420), (900, 450), (200, 450)], rgba('#3a2e24'))
    L['wall'] = (wall, 0.9)
    room = layer(W)
    blob(room, [(150, 520), (1000, 520), (1000, 790), (150, 790)], rgba('#e9e2d4'))                        # counter
    blob(room, [(140, 500), (1010, 500), (1010, 530), (140, 530)], rgba('#b9ad96'))
    blob(room, [(600, 380), (860, 380), (860, 500), (600, 500)], rgba('#dcdcdc'))                           # microwave
    blob(room, [(620, 400), (780, 400), (780, 480), (620, 480)], rgba('#2a2e36'))
    ImageDraw.Draw(room).text((820, 420), '0:00', font=font(22), fill=rgba('#6cff8a'), anchor='mm')
    blob(room, ellipse_pts(1400, 250, 300, 220), rgba('#ffd98a', 40), blur=60)
    blob(room, [(1380, 0), (1420, 0), (1420, 170), (1380, 170)], rgba('#3a2e24'))                          # pendant lamp
    blob(room, [(1320, 170), (1480, 170), (1440, 230), (1360, 230)], rgba('#e8c77a'))
    L['floor'] = (floor, 1.0)                 # floor BELOW the furniture
    L['room'] = (room, 1.0)
    front = layer(W)
    blob(front, [(1000, TABLE_Y), (1760, TABLE_Y), (1800, TABLE_Y + 50), (960, TABLE_Y + 50)], rgba('#a0744e'))
    blob(front, [(960, TABLE_Y + 50), (1800, TABLE_Y + 50), (1800, TABLE_Y + 80), (960, TABLE_Y + 80)], rgba('#7a5238'))
    for x in (1000, 1740):
        blob(front, [(x, TABLE_Y + 80), (x + 30, TABLE_Y + 80), (x + 30, H), (x, H)], rgba('#6b4a36'))
    blob(front, [(1060, TABLE_Y + 60), (1700, TABLE_Y + 60), (1700, H), (1060, H)], rgba('#000000', 40), blur=20)
    bx, by = 1300, TABLE_Y - 4                                                                              # noodle bowl
    blob(front, [(bx - 96, by), (bx + 96, by), (bx + 70, by + 58), (bx - 70, by + 58)], rgba('#f3efe6'))
    blob(front, [(bx - 90, by + 12), (bx + 90, by + 12), (bx + 86, by + 22), (bx - 86, by + 22)], rgba('#3a6ab0'))
    blob(front, ellipse_pts(bx, by, 96, 26), rgba('#f3efe6'))
    blob(front, ellipse_pts(bx, by, 84, 20), rgba('#a8552a'))
    for k in range(6):
        blob(front, ellipse_pts(bx - 50 + k * 20, by - 2 + (k % 2) * 4, 16, 6), rgba('#f1d7a0'))
    for dx in (-30, 18, 44):
        blob(front, ellipse_pts(bx + dx, by + 2, 16, 8), rgba('#7a3d22'))
    blob(front, ellipse_pts(bx + 60, by - 4, 6, 3), rgba('#5f9a3c'))
    blob(front, [(bx + 70, by - 30), (bx + 150, by - 90), (bx + 156, by - 84), (bx + 78, by - 24)], rgba('#caa56a'))
    L['front'] = (front, 1.0)
    return W, L


SCENES = {'bedroom_night': bedroom_night, 'forest_night': forest_night, 'grandma_room': grandma_room,
          'grandma_room_candle': lambda: grandma_room(candle=True), 'living_room': living_room}


def main():
    path = os.path.join(OUT, 'layers.json')
    manifest = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else {}
    for name, fn in SCENES.items():
        W, L = fn()
        d = os.path.join(OUT, name)
        os.makedirs(d, exist_ok=True)
        manifest[name] = {'width': W, 'height': H, 'layers': []}
        flat = Image.new('RGBA', (W, H))
        for lname, (im, par) in L.items():
            im.save(os.path.join(d, f'{lname}.png'), optimize=True)
            manifest[name]['layers'].append({'name': lname, 'file': f'{name}/{lname}.png', 'parallax': par,
                                             'front': lname == 'front'})
            flat.alpha_composite(im)
        flat.convert('RGB').save(os.path.join(d, '_preview.jpg'), quality=88)
        print(name, W, list(L))
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
