# -*- coding: utf-8 -*-
"""Backgrounds for 青蛙王子 (The Frog Prince), same painted style as backgrounds.py.

    python live2d/backgrounds_frog.py   -> 青蛙王子/backgrounds/<scene>/*.png + layers.json

castle_garden   sunny castle garden: castle on the hill, a big linden tree, the old stone well, flowers
garden_sunset   the same garden at golden hour (ending)
palace_hall     the king's dining hall: stone walls, arched windows, red curtains, banners, throne, long table
"""
import json, os, random, math
from PIL import Image

from backgrounds import H, rgba, layer, vgrad, blob, ellipse_pts, noise, cloud, tree_round, strokes, flowers

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT = os.path.join(ROOT, '青蛙王子', 'backgrounds')


def tower(im, x, base, w, h, wall, wall_dk, roof, roof_dk, flag=None):
    blob(im, [(x - w / 2, base), (x - w / 2, base - h), (x + w / 2, base - h), (x + w / 2, base)], rgba(wall))
    blob(im, [(x + w * 0.15, base), (x + w * 0.15, base - h), (x + w / 2, base - h), (x + w / 2, base)], rgba(wall_dk, 120))
    for k in range(3):                                                        # crenellation-free cone roof
        pass
    blob(im, [(x - w * 0.62, base - h), (x, base - h - w * 1.3), (x + w * 0.62, base - h)], rgba(roof))
    blob(im, [(x, base - h - w * 1.3), (x + w * 0.62, base - h), (x + w * 0.1, base - h)], rgba(roof_dk, 150))
    for k in range(2):                                                        # windows
        wy = base - h * (0.35 + 0.3 * k)
        blob(im, [(x - w * 0.1, wy), (x - w * 0.1, wy - w * 0.28), (x, wy - w * 0.38), (x + w * 0.1, wy - w * 0.28),
                  (x + w * 0.1, wy)], rgba('#3a3a5a'))
    if flag:
        top = base - h - w * 1.3
        blob(im, [(x - 1.5, top), (x + 1.5, top), (x + 1.5, top - 40), (x - 1.5, top - 40)], rgba('#5a4a3a'))
        blob(im, [(x + 1.5, top - 40), (x + 36, top - 32), (x + 1.5, top - 22)], rgba(flag))


def castle(im, cx, base, s=1.0, tint=None):
    wall, wall_dk = ('#efe6f2', '#b7a9c6') if not tint else tint
    roof, roof_dk = '#5a7fd6', '#2f4f9e'
    blob(im, [(cx - 260 * s, base), (cx - 260 * s, base - 200 * s), (cx + 260 * s, base - 200 * s), (cx + 260 * s, base)],
         rgba(wall))
    for i in range(13):                                                       # battlements
        x = cx - 260 * s + i * 40 * s
        blob(im, [(x, base - 200 * s), (x, base - 222 * s), (x + 22 * s, base - 222 * s), (x + 22 * s, base - 200 * s)],
             rgba(wall))
    blob(im, [(cx - 50 * s, base), (cx - 50 * s, base - 90 * s)] +
         [(cx + 50 * s * math.cos(a), base - 90 * s - 50 * s * math.sin(a)) for a in [i * math.pi / 12 for i in range(13)]][::-1] +
         [(cx + 50 * s, base)], rgba('#6a4a3a'))                              # gate
    for x, w, h, fl in [(-260, 90, 330, '#e85a6a'), (260, 90, 330, '#f6c84a'), (-120, 70, 380, None),
                        (120, 70, 380, None), (0, 110, 470, '#e85a6a')]:
        tower(im, cx + x * s, base, w * s, h * s, wall, wall_dk, roof, roof_dk, fl)


def well(im, x, base):
    """old round stone well with a little wooden roof (drawn at character scale: rim ~ knee-high of the princess)"""
    w, h = 300, 190
    blob(im, ellipse_pts(x, base, w / 2 + 20, 26), rgba('#000000', 60), blur=10)                      # shadow
    blob(im, [(x - w / 2, base - h), (x + w / 2, base - h), (x + w / 2, base), (x - w / 2, base)], rgba('#a39c94'))
    rng = random.Random(3)
    for row in range(5):                                                                             # stones
        y = base - h + row * (h / 5)
        off = 0 if row % 2 else 30
        for k in range(-3, 4):
            sx = x + k * 60 + off - 30
            if sx < x - w / 2 - 20 or sx > x + w / 2 - 20:
                continue
            c = rng.choice(['#b8b1a8', '#9d958c', '#c6bfb4', '#8f877e'])
            blob(im, [(max(sx + 3, x - w / 2), y + 3), (min(sx + 57, x + w / 2), y + 3), (min(sx + 57, x + w / 2), y + h / 5 - 3),
                      (max(sx + 3, x - w / 2), y + h / 5 - 3)], rgba(c))
    blob(im, [(x - w / 2 - 14, base - h - 18), (x + w / 2 + 14, base - h - 18), (x + w / 2 + 14, base - h + 8),
              (x - w / 2 - 14, base - h + 8)], rgba('#cfc8bd'))                                        # rim
    blob(im, ellipse_pts(x, base - h - 18, w / 2 + 14, 16), rgba('#dcd6cc'))
    blob(im, ellipse_pts(x, base - h - 18, w / 2 - 6, 10), rgba('#1d2a3a'))                           # dark water
    for sx in (x - w / 2 + 6, x + w / 2 - 20):                                                       # posts
        blob(im, [(sx, base - h - 18), (sx + 14, base - h - 18), (sx + 14, base - h - 250), (sx, base - h - 250)],
             rgba('#7a5238'))
    blob(im, [(x - w / 2 - 50, base - h - 240), (x, base - h - 330), (x + w / 2 + 50, base - h - 240),
              (x + w / 2 + 30, base - h - 225), (x, base - h - 305), (x - w / 2 - 30, base - h - 225)], rgba('#b04a3a'))
    blob(im, [(x, base - h - 330), (x + w / 2 + 50, base - h - 240), (x + w / 2 + 30, base - h - 225), (x, base - h - 305)],
         rgba('#7e2e24', 160))
    blob(im, [(x - w / 2 + 10, base - h - 150), (x + w / 2 - 10, base - h - 150), (x + w / 2 - 10, base - h - 140),
              (x - w / 2 + 10, base - h - 140)], rgba('#5a3a26'))                                      # crank bar
    blob(im, [(x - 2, base - h - 145), (x + 2, base - h - 145), (x + 2, base - h - 60), (x - 2, base - h - 60)],
         rgba('#8a7a6a'))                                                                            # rope
    blob(im, [(x - 22, base - h - 64), (x + 22, base - h - 64), (x + 18, base - h - 30), (x - 18, base - h - 30)],
         rgba('#8a5a34'))                                                                            # bucket


def garden(sunset=False):
    W = 2800
    L = {}
    if sunset:
        sky = vgrad(W, '#f59a6a', '#ffe2a8', 0, 720)
        blob(sky, ellipse_pts(2000, 520, 110, 110), rgba('#fff2c0', 230), blur=8)
        for i, (x, y, s) in enumerate([(500, 180, 80), (1400, 120, 90), (2300, 200, 70)]):
            cloud(sky, x, y, s, col='#ffd6c0', seed=40 + i)
    else:
        sky = vgrad(W, '#86c4f2', '#f6f1e0', 0, 720)
        for i, (x, y, s) in enumerate([(400, 150, 80), (1300, 100, 100), (2300, 170, 80)]):
            cloud(sky, x, y, s, seed=30 + i)
    L['sky'] = (noise(sky, 3, 1), 0.1)

    far = layer(W)
    hill = '#a6cf8f' if not sunset else '#c9b77f'
    blob(far, [(0, 640)] + [(x, 600 - 90 * math.exp(-((x - 1900) / 500) ** 2) + 20 * math.sin(x / 170))
                            for x in range(0, W + 1, 40)] + [(W, H), (0, H)], rgba(hill), blur=2)
    castle(far, 1900, 540, 0.8, tint=None if not sunset else ('#f7dccf', '#c9a08f'))
    for x in (200, 480, 900, 2500, 2700):
        tree_round(far, x, 660, 260, 36, 110, dict(trunk='#7a6050', leaf='#7cad68', leaf_dk='#5f9152',
                                                   leaf_hi='#b3d98c'), seed=x)
    if sunset:
        blob(far, [(0, 0), (W, 0), (W, H), (0, H)], rgba('#ff9a50', 40))
    L['far'] = (far, 0.3)

    mid = layer(W)
    tree_round(mid, 520, 760, 820, 110, 330, dict(trunk='#6e4f3a', leaf='#5f9e4c', leaf_dk='#4b8440',
                                                   leaf_hi='#9ccf78'), seed=11)             # the big linden tree
    for x in range(1100, W, 180):                                                            # rose hedge
        blob(mid, ellipse_pts(x, 720, 110, 60, wobble=0.2, rng=random.Random(x)), rgba('#4f8a42'))
        flowers(mid, 10, (x - 90, 680, x + 90, 740), ['#e84a6a', '#ffffff', '#ff9ab0'], (5, 8), seed=x)
    if sunset:
        blob(mid, [(0, 0), (W, 0), (W, H), (0, H)], rgba('#ff9a50', 30))
    L['mid'] = (mid, 0.6)

    ground = layer(W)
    g1, g2 = ('#9fd07a', '#8cc46a') if not sunset else ('#b9c47a', '#a6b064')
    blob(ground, [(0, 740), (W, 740), (W, H), (0, H)], rgba(g1))
    blob(ground, [(0, 900), (W, 870), (W, H), (0, H)], rgba(g2), blur=30)
    blob(ground, [(700, H), (900, 760), (1000, 760), (1300, H)], rgba('#e8d6ae'), blur=3)                # garden path
    strokes(ground, 2800, (0, 740, W, H), ['#7fb35f', '#abd985', '#6ea553'], seed=22, alpha=160)
    flowers(ground, 500, (0, 750, W, H), ['#ff8fa3', '#ffffff', '#fff1a8', '#c9a7ff', '#ffb46b'], (3, 8), seed=23)
    well(ground, 1720, 905)
    if sunset:
        blob(ground, [(0, 0), (W, 0), (W, H), (0, H)], rgba('#ff9a50', 35))
    L['ground'] = (noise(ground, 4, 4), 1.0)

    fg = layer(W)
    strokes(fg, 400, (0, 1030, W, H), ['#5f9a48', '#77b35a'], length=(30, 60), width=(4, 7), seed=25, alpha=230)
    flowers(fg, 40, (0, 1040, W, H + 30), ['#ff6f8f', '#ffffff', '#ffe066'], (10, 16), seed=24)
    L['fg'] = (fg, 1.2)
    return W, L


def palace_hall():
    W = 2600
    L = {}
    wall = vgrad(W, '#e9dcc4', '#cdb896', 0, 760)
    for y in range(0, 760, 60):                                                              # stone courses
        off = 0 if (y // 60) % 2 else 60
        blob(wall, [(0, y), (W, y), (W, y + 3), (0, y + 3)], rgba('#b8a27e', 150))
        for x in range(off, W, 120):
            blob(wall, [(x, y), (x + 3, y), (x + 3, y + 60), (x, y + 60)], rgba('#b8a27e', 120))
    for wx in (300, 900, 1700, 2300):                                                        # arched windows
        blob(wall, [(wx - 110, 560), (wx - 110, 250)] + [(wx + 110 * math.cos(a), 250 - 110 * math.sin(a))
                                                          for a in [i * math.pi / 16 for i in range(17)]][::-1] +
             [(wx + 110, 560)], rgba('#6a5a4a'))
        g = vgrad(200, '#a8d8f8', '#fbeec8', 140, 560)
        m = layer(200)
        blob(m, [(0, 555), (0, 250)] + [(100 + 100 * math.cos(a), 250 - 100 * math.sin(a))
                                        for a in [i * math.pi / 16 for i in range(17)]][::-1] + [(200, 555)], rgba('#ffffff'))
        g.putalpha(m.split()[3])
        wall.alpha_composite(g, (wx - 100, 0))
        blob(wall, [(wx - 3, 150), (wx + 3, 150), (wx + 3, 555), (wx - 3, 555)], rgba('#6a5a4a'))
        blob(wall, [(wx - 100, 380), (wx + 100, 380), (wx + 100, 386), (wx - 100, 386)], rgba('#6a5a4a'))
        for side in (-1, 1):                                                                 # red curtains
            cx = wx + side * 140
            blob(wall, [(cx - 45, 110), (cx + 45, 110), (cx + 30 + side * 10, 700), (cx - 30 + side * 10, 700)],
                 rgba('#b52a36'))
            blob(wall, [(cx - 10, 110), (cx + 4, 110), (cx + 4 + side * 10, 700), (cx - 10 + side * 10, 700)],
                 rgba('#7e1a24', 150))
        blob(wall, [(wx - 190, 90), (wx + 190, 90), (wx + 190, 125), (wx - 190, 125)], rgba('#d4a640'))
    for bx in (600, 2000):                                                                   # royal banners
        blob(wall, [(bx - 60, 120), (bx + 60, 120), (bx + 60, 520), (bx, 580), (bx - 60, 520)], rgba('#3a5fb8'))
        blob(wall, ellipse_pts(bx, 300, 34, 34), rgba('#f5c63a'))
        blob(wall, [(bx - 24, 290), (bx - 26, 262), (bx - 12, 276), (bx, 256), (bx + 12, 276), (bx + 26, 262),
                    (bx + 24, 290)], rgba('#b32a33'))
    L['wall'] = (noise(wall, 3, 5), 0.85)

    room = layer(W)
    floor = vgrad(W, '#b99870', '#8a6a48', 740, H)
    fl = layer(W)
    fl.alpha_composite(floor)
    blob(fl, [(0, 0), (W, 0), (W, 740), (0, 740)], rgba('#000000', 0))
    room.alpha_composite(Image.composite(floor, layer(W), Image.new('L', (W, H), 0).point(lambda v: v)))
    blob(room, [(0, 740), (W, 740), (W, H), (0, H)], rgba('#a78660'))
    for k, y in enumerate(range(740, H, 50)):                                                # checker floor
        for x in range(-100 + (k % 2) * 100, W, 200):
            blob(room, [(x, y), (x + 100, y), (x + 100, y + 50), (x, y + 50)], rgba('#8e6e4c', 150))
    blob(room, [(900, 760), (1700, 760), (1800, H), (800, H)], rgba('#a82a34'))              # red carpet
    blob(room, [(900, 760), (930, 760), (830, H), (800, H)], rgba('#f5c63a'))
    blob(room, [(1670, 760), (1700, 760), (1800, H), (1770, H)], rgba('#f5c63a'))
    # throne at the back
    blob(room, [(1210, 760), (1210, 420), (1260, 380), (1300, 350), (1340, 380), (1390, 420), (1390, 760)],
         rgba('#c9982a'))
    blob(room, [(1235, 740), (1235, 440), (1300, 390), (1365, 440), (1365, 740)], rgba('#b52a36'))
    blob(room, [(1190, 640), (1410, 640), (1410, 680), (1190, 680)], rgba('#d4a640'))
    blob(room, ellipse_pts(1300, 360, 16, 16), rgba('#e84a5a'))
    # long dining table (left) with golden plates, cups and food
    TX0, TX1, TY = 60, 820, 700
    blob(room, [(TX0, TY), (TX1, TY), (TX1 + 20, TY + 30), (TX0 - 20, TY + 30)], rgba('#fbfbf6'))
    blob(room, [(TX0 - 20, TY + 30), (TX1 + 20, TY + 30), (TX1 + 20, TY + 150), (TX0 - 20, TY + 150)], rgba('#f1efe6'))
    for x in range(TX0, TX1, 60):
        blob(room, [(x, TY + 30), (x + 4, TY + 30), (x + 10, TY + 150), (x + 6, TY + 150)], rgba('#d9d6cc'))
    blob(room, [(TX0, TY + 150), (TX0 + 24, TY + 150), (TX0 + 24, 960), (TX0, 960)], rgba('#6e4a33'))
    blob(room, [(TX1 - 24, TY + 150), (TX1, TY + 150), (TX1, 960), (TX1 - 24, 960)], rgba('#6e4a33'))
    for x in range(TX0 + 60, TX1 - 20, 150):
        blob(room, ellipse_pts(x, TY + 12, 34, 9), rgba('#f5c63a'))
        blob(room, ellipse_pts(x, TY + 10, 24, 6), rgba('#fff3c0'))
        blob(room, [(x + 45, TY + 12), (x + 45, TY - 30), (x + 65, TY - 30), (x + 65, TY + 12)], rgba('#d4a640'))
    blob(room, ellipse_pts(440, TY - 20, 70, 36), rgba('#e8a050'))                          # roast
    blob(room, ellipse_pts(440, TY - 28, 50, 20), rgba('#f0c070'))
    for k, c in enumerate(['#e84a5a', '#f5c63a', '#8ac050', '#e84a5a', '#f59a40']):         # fruit bowl
        blob(room, ellipse_pts(700 + (k - 2) * 16, TY - 16 - (k % 2) * 12, 13, 13), rgba(c))
    # chandelier glow
    for cx in (700, 1900):
        blob(room, ellipse_pts(cx, 80, 150, 40), rgba('#ffe9a0', 60), blur=30)
    L['room'] = (noise(room, 3, 6), 1.0)
    return W, L


SCENES = {'castle_garden': lambda: garden(False), 'garden_sunset': lambda: garden(True), 'palace_hall': palace_hall}


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
            manifest[name]['layers'].append({'name': lname, 'file': f'{name}/{lname}.png', 'parallax': par})
            flat.alpha_composite(im)
        flat.convert('RGB').save(os.path.join(d, '_preview.jpg'), quality=88)
        print(name, W, list(L))
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
