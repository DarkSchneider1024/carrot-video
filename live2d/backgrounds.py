# -*- coding: utf-8 -*-
"""Painted, layered backgrounds for the Live2D fairy-tale videos (pure Python: PIL + numpy).

    python live2d/backgrounds.py            -> 小紅帽/backgrounds/<scene>/<layer>.png + layers.json

Every scene is split into parallax layers (sky / far / mid / ground / fg). The stage renderer moves them at
different speeds when the camera pans, like Vyond. Widths are larger than 1920 so the camera can travel.
Style: soft painted look -- gradients, blurred shapes, light noise, a few crisp accent strokes.
"""
import json, math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT = os.path.join(ROOT, '小紅帽', 'backgrounds')
H = 1080


def rgba(h, a=255):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def layer(w):
    return Image.new('RGBA', (w, H), (0, 0, 0, 0))


def vgrad(w, top, bot, y0=0, y1=H):
    a = np.zeros((H, w, 4), np.float32)
    t = np.clip((np.arange(H) - y0) / max(1, y1 - y0), 0, 1)[:, None, None]
    a[:] = np.array(rgba(top), np.float32) * (1 - t) + np.array(rgba(bot), np.float32) * t
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def blob(im, pts, col, blur=0, ss=2):
    """soft polygon painted onto im (supersampled, optional blur)."""
    w, h = im.size
    m = Image.new('L', (w * ss, h * ss), 0)
    ImageDraw.Draw(m).polygon([(x * ss, y * ss) for x, y in pts], fill=255)
    m = m.resize((w, h), Image.LANCZOS)
    if blur:
        m = m.filter(ImageFilter.GaussianBlur(blur))
    c = Image.new('RGBA', (w, h), col[:3] + (0,))
    c.putalpha(m.point(lambda v: v * col[3] // 255))
    im.alpha_composite(c)


def ellipse_pts(cx, cy, rx, ry, n=48, wobble=0.0, rng=None):
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + (wobble * (rng.random() - 0.5) if rng else 0)
        out.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    return out


def noise(im, amount=6, seed=1):
    rng = np.random.default_rng(seed)
    a = np.asarray(im).astype(np.int16)
    n = rng.normal(0, amount, a.shape[:2])[..., None]
    a[..., :3] = np.clip(a[..., :3] + n, 0, 255)
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def strokes(im, n, box, cols, length=(10, 26), width=(2, 4), angle=(-100, -80), seed=0, alpha=200):
    """grass-like crisp strokes."""
    rng = random.Random(seed)
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = box
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        L = rng.uniform(*length) * (0.6 + 0.8 * (y - y0) / max(1, y1 - y0))
        a = math.radians(rng.uniform(*angle))
        c = rgba(rng.choice(cols), alpha)
        d.line([(x, y), (x + L * math.cos(a), y + L * math.sin(a))], fill=c, width=int(rng.uniform(*width)))


def cloud(im, cx, cy, s, col='#ffffff', a=210, seed=0):
    rng = random.Random(seed)
    for i in range(7):
        blob(im, ellipse_pts(cx + rng.uniform(-1.4, 1.4) * s, cy + rng.uniform(-0.3, 0.2) * s,
                             s * rng.uniform(0.6, 1.0), s * rng.uniform(0.35, 0.55)), rgba(col, a), blur=6)


def tree_round(im, x, base, h, trunk_w, crown, cols, seed=0, blur=0):
    rng = random.Random(seed)
    blob(im, [(x - trunk_w / 2, base), (x - trunk_w * 0.35, base - h * 0.55), (x + trunk_w * 0.35, base - h * 0.55),
              (x + trunk_w / 2, base)], rgba(cols['trunk']), blur=blur)
    for i in range(9):
        cx = x + rng.uniform(-0.55, 0.55) * crown
        cy = base - h * 0.62 - rng.uniform(-0.25, 0.35) * crown
        r = crown * rng.uniform(0.45, 0.7)
        col = cols['leaf_dk'] if cy > base - h * 0.6 else cols['leaf']
        blob(im, ellipse_pts(cx, cy, r, r * 0.85, wobble=0.18, rng=rng), rgba(col), blur=blur)
    for i in range(5):                                              # light on the upper-left
        cx = x - crown * rng.uniform(0.1, 0.5)
        cy = base - h * 0.62 - crown * rng.uniform(0.2, 0.55)
        blob(im, ellipse_pts(cx, cy, crown * 0.28, crown * 0.22, wobble=0.2, rng=rng), rgba(cols['leaf_hi'], 170),
             blur=blur + 2)


def pine(im, x, base, h, w, col, col_dk, blur=0):
    for k in range(4):
        y_top = base - h + k * h * 0.2
        y_bot = y_top + h * 0.38
        ww = w * (0.45 + 0.2 * k)
        blob(im, [(x, y_top), (x + ww, y_bot), (x - ww, y_bot)], rgba(col if k % 2 == 0 else col_dk), blur=blur)
    blob(im, [(x - w * 0.06, base - h * 0.12), (x + w * 0.06, base - h * 0.12), (x + w * 0.06, base),
              (x - w * 0.06, base)], rgba('#5a4032'), blur=blur)


def flowers(im, n, box, cols, r=(3, 7), seed=0):
    rng = random.Random(seed)
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = box
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        rr = rng.uniform(*r) * (0.5 + (y - y0) / max(1, y1 - y0))
        c = rgba(rng.choice(cols))
        for k in range(5):
            a = k * 2 * math.pi / 5
            d.ellipse([x + rr * math.cos(a) - rr * 0.6, y + rr * math.sin(a) - rr * 0.6,
                       x + rr * math.cos(a) + rr * 0.6, y + rr * math.sin(a) + rr * 0.6], fill=c)
        d.ellipse([x - rr * 0.45, y - rr * 0.45, x + rr * 0.45, y + rr * 0.45], fill=rgba('#ffd35a'))


# =================================================================== scenes
def cottage():
    W = 2400
    L = {}
    sky = vgrad(W, '#9fd0f0', '#f6efe0', 0, 700)
    for i, (x, y, s) in enumerate([(320, 170, 70), (980, 120, 90), (1650, 190, 70), (2150, 110, 80)]):
        cloud(sky, x, y, s, seed=i)
    L['sky'] = (noise(sky, 3, 1), 0.1)

    far = layer(W)
    blob(far, [(0, 640)] + [(x, 560 + 50 * math.sin(x / 260) + 20 * math.sin(x / 90)) for x in range(0, W + 1, 40)]
         + [(W, 1080), (0, 1080)], rgba('#a8c9a0'), blur=2)
    blob(far, [(0, 700)] + [(x, 640 + 40 * math.sin(x / 330 + 1)) for x in range(0, W + 1, 40)] + [(W, 1080), (0, 1080)],
         rgba('#8db784'), blur=1)
    rng = random.Random(3)
    for x in range(40, W, 120):
        pine(far, x + rng.uniform(-30, 30), 660 + rng.uniform(-10, 20), rng.uniform(120, 190), 60, '#6f9e78', '#5d8b68', blur=1)
    L['far'] = (far, 0.3)

    mid = layer(W)
    # cottage
    cx, base = 760, 760
    blob(mid, [(cx - 250, base), (cx - 250, base - 230), (cx + 250, base - 230), (cx + 250, base)], rgba('#f3e2c4'))
    for yy in range(base - 225, base, 26):                                        # timber lines
        ImageDraw.Draw(mid).line([(cx - 250, yy), (cx + 250, yy)], fill=rgba('#e2cda8'), width=3)
    blob(mid, [(cx - 290, base - 225), (cx, base - 420), (cx + 290, base - 225), (cx + 270, base - 205),
               (cx - 270, base - 205)], rgba('#c2493f'))                            # roof
    blob(mid, [(cx - 290, base - 225), (cx, base - 420), (cx + 20, base - 405), (cx - 260, base - 215)],
         rgba('#d9665a'))
    blob(mid, [(cx + 140, base - 330), (cx + 190, base - 330), (cx + 190, base - 260), (cx + 140, base - 290)],
         rgba('#8a6a5a'))                                                           # chimney
    blob(mid, [(cx - 50, base), (cx - 50, base - 140), (cx, base - 170), (cx + 50, base - 140), (cx + 50, base)],
         rgba('#7a4a2e'))                                                           # door
    ImageDraw.Draw(mid).ellipse([cx + 25, base - 75, cx + 37, base - 63], fill=rgba('#e8c46a'))
    for wx in (cx - 170, cx + 110):                                                 # windows
        blob(mid, [(wx, base - 170), (wx + 70, base - 170), (wx + 70, base - 95), (wx, base - 95)], rgba('#6a4a36'))
        blob(mid, [(wx + 6, base - 164), (wx + 64, base - 164), (wx + 64, base - 101), (wx + 6, base - 101)],
             rgba('#bfe0f0'))
        ImageDraw.Draw(mid).line([(wx + 35, base - 164), (wx + 35, base - 101)], fill=rgba('#6a4a36'), width=5)
        ImageDraw.Draw(mid).line([(wx + 6, base - 132), (wx + 64, base - 132)], fill=rgba('#6a4a36'), width=5)
        blob(mid, [(wx - 6, base - 95), (wx + 76, base - 95), (wx + 70, base - 80), (wx, base - 80)], rgba('#9b6a44'))
        flowers(mid, 7, (wx, base - 95, wx + 70, base - 86), ['#ff8fa3', '#fff1a8', '#ffffff'], (3, 5), seed=wx)
    tree_round(mid, 1500, 780, 420, 60, 170, dict(trunk='#7a5a44', leaf='#7fb069', leaf_dk='#5f9152',
                                                  leaf_hi='#b9dc8c'), seed=4)
    tree_round(mid, 250, 790, 380, 54, 150, dict(trunk='#7a5a44', leaf='#86b870', leaf_dk='#63965a',
                                                 leaf_hi='#c2e39a'), seed=5)
    # fence
    for fx in range(1050, 2350, 70):
        blob(mid, [(fx, 800), (fx, 720), (fx + 12, 708), (fx + 24, 720), (fx + 24, 800)], rgba('#e8d8bd'))
    for fy in (738, 772):
        blob(mid, [(1040, fy), (2360, fy), (2360, fy + 12), (1040, fy + 12)], rgba('#d8c6a6'))
    L['mid'] = (mid, 0.7)

    ground = layer(W)
    blob(ground, [(0, 760), (W, 740), (W, H), (0, H)], rgba('#9ccc7a'))
    blob(ground, [(0, 900), (W, 860), (W, H), (0, H)], rgba('#8cc06c'), blur=30)
    blob(ground, [(640, 760), (880, 760), (1180, H), (380, H)], rgba('#e6cf9e'), blur=3)       # path to the door
    strokes(ground, 2600, (0, 770, W, H), ['#7fb35f', '#a9d882', '#6ea553'], seed=7, alpha=180)
    flowers(ground, 120, (0, 800, W, H), ['#ff8fa3', '#ffffff', '#fff1a8', '#c9a7ff'], seed=8)
    L['ground'] = (noise(ground, 4, 2), 1.0)
    return W, L


def forest():
    W = 3400
    L = {}
    sky = vgrad(W, '#d7ecd9', '#f5f0d8', 0, 800)
    L['sky'] = (sky, 0.1)

    far = layer(W)
    rng = random.Random(11)
    for x in range(-40, W + 60, 70):
        pine(far, x + rng.uniform(-20, 20), 700 + rng.uniform(-20, 20), rng.uniform(380, 520), 110,
             '#9dbfa4', '#8bb094', blur=3)
    blob(far, [(0, 690), (W, 690), (W, H), (0, H)], rgba('#a9c79f'), blur=8)
    L['far'] = (far, 0.25)

    mid = layer(W)
    rng = random.Random(12)
    for i, x in enumerate(range(120, W, 330)):
        x += rng.uniform(-80, 80)
        tw = rng.uniform(60, 90)
        blob(mid, [(x - tw / 2, 820), (x - tw * 0.4, 0), (x + tw * 0.4, 0), (x + tw / 2, 820)], rgba('#6b5444'))
        blob(mid, [(x - tw * 0.1, 820), (x - tw * 0.05, 0), (x + tw * 0.38, 0), (x + tw / 2, 820)], rgba('#57443a'))
        for k in range(8):
            cy = rng.uniform(-40, 260)
            blob(mid, ellipse_pts(x + rng.uniform(-180, 180), cy, rng.uniform(120, 200), rng.uniform(80, 130),
                                  wobble=0.2, rng=rng), rgba(rng.choice(['#4f8a55', '#5d9a60', '#467c4d'])))
        for k in range(3):
            blob(mid, ellipse_pts(x + rng.uniform(-150, 60), rng.uniform(-20, 180), 90, 60, wobble=0.25, rng=rng),
                 rgba('#8cc27a', 170), blur=4)
    for x in range(0, W, 260):                                                    # sun rays
        blob(mid, [(x + 60, 0), (x + 130, 0), (x + 420, 900), (x + 300, 900)], rgba('#fff7d0', 55), blur=30)
    L['mid'] = (mid, 0.6)

    ground = layer(W)
    blob(ground, [(0, 780), (W, 780), (W, H), (0, H)], rgba('#7fae62'))
    blob(ground, [(0, 860)] + [(x, 880 + 25 * math.sin(x / 300)) for x in range(0, W + 1, 50)] + [(W, 1000)]
         + [(x, 990 + 20 * math.sin(x / 260 + 2)) for x in range(W, -1, -50)], rgba('#dcc48f'), blur=4)  # dirt path
    strokes(ground, 3400, (0, 790, W, H), ['#6d9d52', '#94c476', '#5c8c45'], seed=13, alpha=170)
    flowers(ground, 80, (0, 800, W, H), ['#ffffff', '#fff1a8', '#ffb3c1'], (2, 5), seed=14)
    L['ground'] = (noise(ground, 4, 3), 1.0)

    fg = layer(W)
    rng = random.Random(15)
    for x in range(-60, W + 100, 420):
        x += rng.uniform(-100, 100)
        for k in range(6):
            blob(fg, ellipse_pts(x + rng.uniform(-110, 110), H - rng.uniform(10, 90), rng.uniform(90, 150),
                                 rng.uniform(60, 90), wobble=0.25, rng=rng), rgba(rng.choice(['#3f7040', '#4a7f45'])))
    L['fg'] = (fg, 1.25)
    return W, L


def meadow():
    W = 2600
    L = {}
    sky = vgrad(W, '#8cc8f0', '#fbf1dc', 0, 720)
    for i, (x, y, s) in enumerate([(400, 150, 80), (1200, 100, 100), (2000, 180, 80)]):
        cloud(sky, x, y, s, seed=20 + i)
    L['sky'] = (sky, 0.1)

    far = layer(W)
    blob(far, [(0, 620)] + [(x, 560 + 60 * math.sin(x / 400) + 15 * math.sin(x / 120)) for x in range(0, W + 1, 40)]
         + [(W, H), (0, H)], rgba('#a6cf8f'), blur=2)
    rng = random.Random(21)
    for x in (120, 380, 2250, 2480):
        tree_round(far, x, 640, 300, 40, 120, dict(trunk='#7a6050', leaf='#7cad68', leaf_dk='#5f9152',
                                                   leaf_hi='#b3d98c'), seed=x)
    L['far'] = (far, 0.3)

    ground = layer(W)
    blob(ground, [(0, 700), (W, 690), (W, H), (0, H)], rgba('#9fd07a'))
    blob(ground, [(0, 860), (W, 830), (W, H), (0, H)], rgba('#8cc46a'), blur=30)
    strokes(ground, 3000, (0, 700, W, H), ['#7fb35f', '#abd985', '#6ea553'], seed=22, alpha=170)
    flowers(ground, 600, (0, 710, W, H), ['#ff8fa3', '#ffffff', '#fff1a8', '#c9a7ff', '#ffb46b'], (3, 9), seed=23)
    L['ground'] = (noise(ground, 4, 4), 1.0)

    fg = layer(W)
    flowers(fg, 60, (0, 1000, W, H + 30), ['#ff6f8f', '#ffffff', '#ffe066'], (10, 18), seed=24)
    strokes(fg, 500, (0, 990, W, H), ['#5f9a48', '#77b35a'], length=(30, 60), width=(4, 7), seed=25, alpha=230)
    L['fg'] = (fg, 1.2)
    return W, L


SCENES = {'cottage': cottage, 'forest': forest, 'meadow': meadow}


def main():
    manifest = {}
    for name, fn in SCENES.items():
        W, L = fn()
        d = os.path.join(OUT, name)
        os.makedirs(d, exist_ok=True)
        manifest[name] = {'width': W, 'height': H, 'layers': []}
        for lname, (im, par) in L.items():
            im.save(os.path.join(d, f'{lname}.png'), optimize=True)
            manifest[name]['layers'].append({'name': lname, 'file': f'{name}/{lname}.png', 'parallax': par})
        # flat preview
        flat = Image.new('RGBA', (W, H))
        for lname, (im, par) in L.items():
            flat.alpha_composite(im)
        flat.convert('RGB').save(os.path.join(d, '_preview.jpg'), quality=88)
        print(name, W, list(L))
    with open(os.path.join(OUT, 'layers.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
