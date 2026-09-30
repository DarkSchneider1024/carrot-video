# -*- coding: utf-8 -*-
"""Daytime backgrounds for the classic 小紅帽 (with the huntsman), same painted style as backgrounds_noodle.py.

    python live2d/backgrounds_classic.py   -> 小紅帽/backgrounds/<scene>/*.png, merged into layers.json

grandma_room_day      grandma's bedroom in daylight (sunny window, warm wall); grandma's puppet brings her own quilt
grandma_room_day_bed  same room + the quilt in FRONT of the actors (the disguised / sleeping wolf lies under it)
"""
import json, os, random, math
from PIL import Image, ImageDraw

from backgrounds import H, OUT, rgba, layer, vgrad, blob, ellipse_pts, noise, cloud, pine, strokes, flowers, tree_round
import math
from backgrounds_noodle import room_base, headboard, BED_X, BED_W, BED_Y


def sun_window(im, x, y, w, h, frame='#5a4030', curtain='#b0604e'):
    blob(im, [(x - 14, y - 14), (x + w + 14, y - 14), (x + w + 14, y + h + 14), (x - 14, y + h + 14)], rgba(frame))
    g = vgrad(w, '#8fc8f0', '#d6eefa', 0, h).crop((0, 0, w, h))
    im.alpha_composite(g, (x, y))
    rng = random.Random(x)
    for _ in range(3):                                                                    # clouds
        cx, cy = rng.uniform(x + 40, x + w - 40), rng.uniform(y + 30, y + h * 0.5)
        for k in range(4):
            blob(im, ellipse_pts(cx + (k - 1.5) * 22, cy + (k % 2) * 6, 26, 18), rgba('#ffffff', 230), blur=2)
    blob(im, [(x, y + h * 0.78), (x + w, y + h * 0.7), (x + w, y + h), (x, y + h)], rgba('#7fae5a'))   # hill
    for k in range(4):                                                                    # distant trees
        tx = x + 30 + k * (w - 60) / 3
        blob(im, ellipse_pts(tx, y + h * 0.72, 22, 30), rgba('#4f7f3c'))
    blob(im, [(x + w / 2 - 5, y), (x + w / 2 + 5, y), (x + w / 2 + 5, y + h), (x + w / 2 - 5, y + h)], rgba(frame))
    blob(im, [(x, y + h / 2 - 5), (x + w, y + h / 2 - 5), (x + w, y + h / 2 + 5), (x, y + h / 2 + 5)], rgba(frame))
    for side in (0, 1):                                                                   # curtains (tied back)
        cx = x - 40 if side == 0 else x + w + 40
        sk = 20 if side else -20
        blob(im, [(cx - 50, y - 40), (cx + 50, y - 40), (cx + 30 + sk, y + h + 60), (cx - 30 + sk, y + h + 60)], rgba(curtain))
        for k in range(3):
            blob(im, [(cx - 30 + k * 25, y - 40), (cx - 22 + k * 25, y - 40), (cx - 24 + k * 25, y + h + 60),
                      (cx - 32 + k * 25, y + h + 60)], rgba('#000000', 35), blur=4)
        blob(im, [(cx - 40 + sk * 0.5, y + h * 0.55), (cx + 40 + sk * 0.5, y + h * 0.55), (cx + 40 + sk * 0.5, y + h * 0.6),
                  (cx - 40 + sk * 0.5, y + h * 0.6)], rgba('#e0b050'))                     # tie-back


def grandma_room_day(bed_front=False):
    W = 2400
    L = {}
    wall, floor = room_base(W, '#b89a78', '#a88a68', '#9a7552', '#7a5a3e')
    for x in range(0, W, 60):
        blob(wall, [(x, 0), (x + 3, 0), (x + 3, 730), (x, 730)], rgba('#000000', 22))
    sun_window(wall, 1080, 160, 300, 280)
    blob(wall, [(1000, 520), (1480, 520), (1700, 1080), (820, 1080)], rgba('#fff2c0', 45), blur=40)     # sunbeam
    blob(wall, [(1880, 170), (2060, 170), (2060, 330), (1880, 330)], rgba('#c9a24a'))                     # photo frame
    blob(wall, [(1895, 185), (2045, 185), (2045, 315), (1895, 315)], rgba('#e9ddc6'))
    blob(wall, ellipse_pts(1970, 250, 34, 40), rgba('#d7a0a0'))                                           # a little portrait
    L['wall'] = (wall, 0.9)
    room = layer(W)
    blob(room, [(120, 200), (400, 200), (400, 770), (120, 770)], rgba('#7a5238'))                          # door
    blob(room, [(140, 220), (380, 220), (380, 770), (140, 770)], rgba('#9a7148'))
    blob(room, ellipse_pts(355, 500, 10, 10), rgba('#d8b060'))
    blob(room, [(560, 150), (960, 150), (960, 800), (560, 800)], rgba('#6e4a33'))                          # wardrobe
    blob(room, [(575, 170), (755, 170), (755, 780), (575, 780)], rgba('#8a5f40'))
    blob(room, [(765, 170), (945, 170), (945, 780), (765, 780)], rgba('#8a5f40'))
    for x in (745, 775):
        blob(room, [(x - 4, 440), (x + 4, 440), (x + 4, 500), (x - 4, 500)], rgba('#d8b060'))
    headboard(room, BED_X, BED_Y - 180, BED_W, col='#8a5c3e')
    blob(room, [(BED_X - 10, BED_Y - 20), (BED_X + BED_W + 10, BED_Y - 20), (BED_X + BED_W + 10, BED_Y + 90),
                (BED_X - 10, BED_Y + 90)], rgba('#7a5238'))                                                  # bed frame
    blob(room, [(1990, 690), (2190, 690), (2190, 960), (1990, 960)], rgba('#7a5238'))                      # nightstand
    blob(room, [(1980, 676), (2200, 676), (2200, 700), (1980, 700)], rgba('#9a7148'))
    blob(room, [(2050, 600), (2130, 600), (2140, 676), (2040, 676)], rgba('#e8e0d0'))                      # vase
    for k, c in enumerate(('#e85a6a', '#f6c84a', '#ffffff', '#e85a6a')):                                    # flowers
        blob(room, ellipse_pts(2060 + k * 20, 585 - (k % 2) * 14, 14, 14), rgba(c))
    blob(room, [(700, 900), (1300, 900), (1340, 1000), (660, 1000)], rgba('#b04a3a', 170))                # rug
    L['floor'] = (floor, 1.0)
    L['room'] = (room, 1.0)
    if bed_front:
        front = layer(W)
        top_edge = [(BED_X - 25, 720), (BED_X + 80, 706), (BED_X + 230, 712), (BED_X + 380, 704), (BED_X + 485, 720)]
        blob(front, top_edge + [(BED_X + 510, 1000), (BED_X - 40, 1000)], rgba('#f1e3c6'))
        for x in range(BED_X, BED_X + 480, 60):
            blob(front, [(x, 715), (x + 3, 715), (x + 8, 1000), (x + 5, 1000)], rgba('#d4bf98'))
        blob(front, [(BED_X - 40, 700), (BED_X + 510, 700), (BED_X + 510, 740), (BED_X - 40, 740)], rgba('#fff6e4', 120), blur=10)
        blob(front, [(BED_X - 50, 990), (BED_X + 520, 990), (BED_X + 520, H), (BED_X - 50, H)], rgba('#7a5238'))
        L['front'] = (front, 1.0)
    return W, L


def cottage_door():
    """close-up of grandma's front door, drawn at the characters' scale (door ~870 px, wolf 900 px)"""
    W = 2400
    L = {}
    sky = vgrad(W, '#9fd0f0', '#f6efe0', 0, 700)
    for i, (x, y, s) in enumerate([(250, 150, 80), (700, 90, 70)]):
        cloud(sky, x, y, s, seed=i + 5)
    L['sky'] = (noise(sky, 3, 1), 0.1)
    far = layer(W)
    blob(far, [(0, 620)] + [(x, 560 + 40 * math.sin(x / 240)) for x in range(0, W + 1, 40)] + [(W, H), (0, H)],
         rgba('#a8c9a0'), blur=2)
    rng = random.Random(7)
    for x in range(40, 1400, 110):
        pine(far, x + rng.uniform(-20, 20), 660, rng.uniform(150, 220), 70, '#6f9e78', '#5d8b68', blur=1)
    L['far'] = (far, 0.3)
    ground = layer(W)
    blob(ground, [(0, 700), (W, 700), (W, H), (0, H)], rgba('#8cc46e'))
    blob(ground, [(0, 700), (W, 700), (W, 760), (0, 760)], rgba('#7ab35e'), blur=6)
    blob(ground, [(0, 900), (1150, 930), (1620, 930), (1620, H), (0, H)], rgba('#e6cf9e'), blur=3)   # path to the door
    strokes(ground, 2600, (0, 700, W, H), ['#5f9e48', '#76b65a', '#9ccf78'], seed=3)
    flowers(ground, 120, (0, 720, 1100, 890), ['#ffffff', '#f6c84a', '#e86a8a', '#b48ae0'], seed=4)
    L['ground'] = (noise(ground, 4, 2), 1.0)
    house = layer(W)
    WX0 = 930
    blob(house, [(WX0, 60), (W, 60), (W, 985), (WX0, 985)], rgba('#f3e2c4'))                     # wall
    for yy in range(90, 985, 34):                                                                # timber boards
        blob(house, [(WX0, yy), (W, yy), (W, yy + 3), (WX0, yy + 3)], rgba('#e2cda8'))
    blob(house, [(WX0, 60), (WX0 + 26, 60), (WX0 + 26, 985), (WX0, 985)], rgba('#d8bf98'))       # corner post
    blob(house, [(WX0 - 60, 0), (W, 0), (W, 70), (WX0 - 60, 100)], rgba('#c2493f'))             # roof eave
    blob(house, [(WX0 - 60, 80), (W, 52), (W, 76), (WX0 - 60, 106)], rgba('#8e2f28'))
    blob(house, [(WX0, 940), (W, 940), (W, 990), (WX0, 990)], rgba('#b89a78'))                  # stone footing
    # door (arched), frame, knob, knocker
    DX0, DX1, DT, DB = 1180, 1560, 110, 945
    arch = [(DX0 + (DX1 - DX0) / 2 + (DX1 - DX0) / 2 * math.cos(a), DT + 120 - 120 * math.sin(a))
            for a in [i * math.pi / 24 for i in range(25)]]
    frame = [(DX0 - 30, DB), (DX0 - 30, DT + 120)] + [(x + (x - (DX0 + DX1) / 2) * 0.16, y - 30) for x, y in arch[::-1]] + [(DX1 + 30, DT + 120), (DX1 + 30, DB)]
    blob(house, frame, rgba('#6a4028'))
    door = [(DX0, DB), (DX0, DT + 120)] + arch[::-1] + [(DX1, DT + 120), (DX1, DB)]
    blob(house, door, rgba('#8a5634'))
    for x in range(DX0 + 60, DX1, 70):                                                          # planks
        blob(house, [(x, DT + 20), (x + 5, DT + 20), (x + 5, DB), (x, DB)], rgba('#6e4228'))
    for y in (DT + 250, DB - 180):                                                              # iron straps
        blob(house, [(DX0, y), (DX1, y), (DX1, y + 18), (DX0, y + 18)], rgba('#3a3036'))
    blob(house, ellipse_pts(DX1 - 55, 560, 16, 16), rgba('#e8c46a'))                          # knob
    blob(house, ellipse_pts((DX0 + DX1) / 2, 380, 30, 30), rgba('#c9a24a'))                    # knocker ring
    blob(house, ellipse_pts((DX0 + DX1) / 2, 380, 20, 20), rgba('#8a5634'))
    blob(house, [(DX0 - 50, DB), (DX1 + 50, DB), (DX1 + 70, 1000), (DX0 - 70, 1000)], rgba('#a9a39a'))   # doorstep
    blob(house, [(DX0 - 70, 992), (DX1 + 70, 992), (DX1 + 70, 1004), (DX0 - 70, 1004)], rgba('#7f7a72'))
    # window with a flower box
    for wx in (1780,):
        blob(house, [(wx - 20, 300), (wx + 400, 300), (wx + 400, 700), (wx - 20, 700)], rgba('#6a4a36'))
        g = vgrad(380, '#bfe0f0', '#e6f4fa', 0, 380).crop((0, 0, 380, 380))
        house.alpha_composite(g, (wx, 310))
        blob(house, [(wx + 182, 310), (wx + 198, 310), (wx + 198, 690), (wx + 182, 690)], rgba('#6a4a36'))
        blob(house, [(wx, 490), (wx + 380, 490), (wx + 380, 506), (wx, 506)], rgba('#6a4a36'))
        blob(house, [(wx - 40, 700), (wx + 420, 700), (wx + 400, 780), (wx - 20, 780)], rgba('#9a6a40'))
        for k in range(9):
            blob(house, ellipse_pts(wx + k * 48, 690, 26, 20), rgba('#5f9e48'))
            blob(house, ellipse_pts(wx + k * 48 + 8, 676, 14, 14), rgba(['#e85a6a', '#f6c84a', '#ffffff'][k % 3]))
    blob(house, [(1650, 330), (1700, 330), (1690, 420), (1660, 420)], rgba('#3a3036'))           # lantern
    blob(house, [(1655, 360), (1695, 360), (1688, 412), (1662, 412)], rgba('#ffe7a0'))
    blob(house, [(WX0, 60), (W, 60), (W, 130), (WX0, 130)], rgba('#000000', 60), blur=14)       # eave shadow
    L['house'] = (house, 1.0)
    return W, L


SCENES = {'cottage_door': cottage_door, 'grandma_room_day': grandma_room_day, 'grandma_room_day_bed': lambda: grandma_room_day(bed_front=True)}


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
