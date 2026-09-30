# -*- coding: utf-8 -*-
"""紫髮小公主 (Princess) — built directly on 紫髮少女 (girl_dress / girl_v4).

Adds royal princess elements to the existing anime girl:
1. Pure gold princess crown (金冠) on top of the head
2. Glowing golden ball (金球) held near her hand
3. Gothic gown (哥德式禮服, v2): black-plum satin with white lace, crimson ribbons, long sleeves with lace cuffs,
   closed high lace yoke, floor-length tiered bell skirt (replaces the short skirt and stockings)
Face, eyes, hair, arms, chest physics and the nine-axis head are unchanged.
"""
import copy, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.abspath(os.path.join(HERE, '..', 'engine'))
if ENGINE not in sys.path:
    sys.path.insert(0, ENGINE)

import girl_dress as GD
import girl_v4 as G4
import red_hood as RH
from girl import Part, hx, M
from girl_v4 import R, Rell, CX, LW, K

# kid-friendly: high rounded lace yoke instead of the strapless neckline (the lace band now starts at the collar)
G4.BUST_HW, G4.BUST_TOP, G4.BUST_BOT = 30.0, 22.0, 24.0
GD.NECK_R = [(CX, 304, 'c'), (274, 303), (258, 306), (236, 316), (214, 330), (206, 338)]

GOLD, GOLD_SH, GOLD_HI, GOLD_LN = hx('f7ca39'), hx('c29719'), hx('fff28a'), hx('695009')
RUBY = hx('d42838')
WHITE = hx('ffffff')


def princess_crown():
    """Elegant gold princess crown placed above bangs / head."""
    p = Part('髮飾_王冠')
    base = [(256, 75), (252, 45), (268, 56), (CX, 34), (302, 56), (318, 45), (314, 75)]
    pts = R(base)
    p.fill(pts, GOLD)
    p.air(R([(250, 60), (320, 60), (320, 76), (250, 76)]), GOLD_SH, blur=4)
    p.air(R([(270, 36), (300, 36), (300, 50), (270, 50)]), GOLD_HI, blur=3)
    p.line(pts, LW * 1.1, GOLD_LN, closed=True)
    # Royal red jewel in centre
    p.fill(Rell(CX, 54, 4.0, 4.0), RUBY, line=GOLD_LN, lw=0.8)
    for x, y in [(252, 45), (CX, 34), (318, 45)]:
        p.fill(Rell(x, y, 2.8, 2.8), GOLD_HI, line=GOLD_LN, lw=0.8)
    return p


def golden_ball():
    """The key golden ball of the fairytale held near right hand."""
    p = Part('道具_金球')
    ball = Rell(180, 530, 24, 24)
    p.fill(ball, GOLD)
    p.air(Rell(180, 530, 32, 32), hx('ffd700', 120), blur=10)
    p.fill(Rell(175, 524, 6.0, 6.0), WHITE)
    p.line(ball, 1.2, GOLD_LN, closed=True)
    return p


GOWN, GOWN_SH, GOWN_HI, GOWN_LN = hx('2e1a3a'), hx('1a0e22'), hx('5a3a70'), hx('07030a')
CRIMSON, CRIMSON_SH, CRIMSON_HI, CRIMSON_LN = hx('9c1f35'), hx('6a1022'), hx('c8485c'), hx('30060e')
LACE, LACE_SH, LACE_LN = hx('fbf8fc'), hx('d8cfe0'), hx('8a8096')


def cmap(d):
    t = {k[:3]: v for k, v in d.items()}
    return lambda c: (t[c[:3]][:3] + (c[3],)) if c[:3] in t else c


DRESS_MAP = cmap({GD.DRESS: GOWN, GD.DRESS_SH: GOWN_SH, GD.DRESS_DK: GOWN_SH, GD.DRESS_HI: GOWN_HI, GD.DRESS_LN: GOWN_LN,
                  hx('6f82c8'): GOWN_SH, hx('8f9bcf'): GOWN_SH, hx('c9cee8'): LACE_SH, hx('aab3da'): LACE_SH,
                  hx('b4bde2'): LACE_SH})
RIB_MAP = cmap({GD.RIB: CRIMSON, GD.RIB_SH: CRIMSON_SH, GD.RIB_HI: CRIMSON_HI, GD.RIB_LN: CRIMSON_LN})
SLEEVE_MAP = cmap({G4.SKIN: GOWN, G4.SKIN_SH: GOWN_SH, G4.SKIN_SH2: GOWN_SH, G4.SKIN_LN: GOWN_LN})
YOKE_MAP = cmap({G4.SKIN: GOWN, G4.SKIN_SH: GOWN_SH, G4.SKIN_SH2: GOWN_SH, G4.SKIN_LN: GOWN_LN})
DROP = {'裙_後', '裙_R', '裙_L', '裙_中'}

HEM_Y = 972.0


def skirt_hw(y):
    """half-width of the bell skirt at height y (reference px)"""
    return float(np.interp(y, [468, 520, 600, 760, 900, HEM_Y], [42, 74, 102, 128, 146, 156]))


def long_skirt():
    p = Part('長裙')
    ys = np.linspace(468, HEM_Y, 40)
    right = [(CX - skirt_hw(y), y) for y in ys]
    xs = np.linspace(CX - skirt_hw(HEM_Y), CX + skirt_hw(HEM_Y), 25)
    hem = [(x, HEM_Y + (6 if i % 2 else 0)) for i, x in enumerate(xs)]
    pts = R(right + hem + [(CX + skirt_hw(y), y) for y in ys[::-1]])
    p.fill(pts, GOWN)
    for k in range(-5, 6):                                                           # soft folds
        x0 = CX + k * 11
        p.air(R([(x0 - 2, 520), (x0 + 2, 520), (CX + k * 28 + 3, HEM_Y), (CX + k * 28 - 3, HEM_Y)]),
              GOWN_HI if k % 2 else GOWN_SH, blur=6)
    p.air(R([(CX - 170, 468), (CX - 110, 468), (CX - 120, HEM_Y), (CX - 180, HEM_Y)]), GOWN_SH, blur=14)
    p.air(M(R([(CX - 170, 468), (CX - 110, 468), (CX - 120, HEM_Y), (CX - 180, HEM_Y)])), GOWN_SH, blur=14)
    for y0, h in ((700, 22), (850, 22)):                                             # tier ruffles: lace + ribbon
        band = [(CX - skirt_hw(y0), y0, 'c'), (CX + skirt_hw(y0), y0, 'c'),
                (CX + skirt_hw(y0 + h), y0 + h, 'c'), (CX - skirt_hw(y0 + h), y0 + h, 'c')]
        p.fill(R(band), LACE, line=LACE_LN, lw=LW * 0.7)
        xs2 = np.linspace(CX - skirt_hw(y0 + h), CX + skirt_hw(y0 + h), 31)
        for x in np.linspace(CX - skirt_hw(y0), CX + skirt_hw(y0), 18)[1:-1]:
            p.line(R([(x, y0 + 3), (x, y0 + h - 3)]), 0.6, LACE_SH)
        rib = [(CX - skirt_hw(y0 - 7), y0 - 7, 'c'), (CX + skirt_hw(y0 - 7), y0 - 7, 'c'), (CX + skirt_hw(y0), y0, 'c'),
               (CX - skirt_hw(y0), y0, 'c')]
        p.fill(R(rib), CRIMSON)
    hb = [(x, HEM_Y - 16) + (('c',) if i in (0, len(xs) - 1) else ()) for i, x in enumerate(xs)] + [(x, HEM_Y + (8 if i % 2 else 3)) for i, x in enumerate(xs)][::-1]
    p.fill(R(hb), LACE, line=LACE_LN, lw=LW * 0.7)                                    # lace hem
    p.line(pts, LW, GOWN_LN, closed=True)
    return p


def lace_front():
    """flat white lace chest panel from the collar to under the bust (covers the bust cups: no bulging shading)"""
    p = Part('蕾絲胸衣')
    xs = np.linspace(205, 2 * CX - 205, 50)
    band = R([(x, GD.neck_y(x) - 1) for x in xs] + [(x, GD.lace_bottom(x)) for x in xs[::-1]])
    p.fill(band, LACE)
    GD.lace_rings(p, 205, 2 * CX - 205, GD.neck_y, GD.lace_bottom, R)
    for g in ((lambda q: q), M):
        p.air(g(R([(200, 300), (226, 300), (230, 412), (204, 412)])), LACE_SH, blur=6)
    p.line(R([(x, GD.lace_bottom(x)) for x in xs]), 0.9, LACE_LN)
    for y in (330, 356, 382):                                                        # little crimson bows
        p.fill(R([(CX - 9, y - 5), (CX, y), (CX - 9, y + 5)]), CRIMSON, line=CRIMSON_LN, lw=0.6)
        p.fill(R([(CX + 9, y - 5), (CX, y), (CX + 9, y + 5)]), CRIMSON, line=CRIMSON_LN, lw=0.6)
        p.fill(Rell(CX, y, 2.2, 2.2), CRIMSON_HI, raw=True)
    return p


def corset_lacing():
    p = Part('束腰綁帶')
    for y in np.arange(424, 468, 9):
        p.line(R([(CX - 7, y), (CX + 7, y + 6)]), 1.1, CRIMSON)
        p.line(R([(CX + 7, y), (CX - 7, y + 6)]), 1.1, CRIMSON)
        for x in (CX - 7, CX + 7):
            p.fill(Rell(x, y, 1.3, 1.3), GOLD, raw=True)
    return p


def lace_cuff(p, side):
    f = (lambda q: q) if side == 'R' else M
    GD.with_warp(lambda: p.fill(f(R([(152, 536), (194, 540), (198, 556), (150, 552)])), LACE, line=LACE_LN, lw=LW * 0.7))


def gothic(p):
    n = p.name
    if n.startswith(('洋裝', '腰')) or n == '頸飾':
        RH.recolor(p, DRESS_MAP)
        RH.recolor(p, RIB_MAP)
    elif n.startswith(('上臂', '下臂')):
        RH.recolor(p, SLEEVE_MAP)
        if n.startswith('下臂'):
            lace_cuff(p, n[-1])
    elif n in ('胸腔', '胸_R', '胸_L'):
        RH.recolor(p, YOKE_MAP)


def build():
    groups = GD.build()
    out = []
    for name, items in groups:
        if name == '身體':
            body = []
            for it in items:
                if it.name in DROP:
                    continue
                if it.name == '腰':
                    body.append(long_skirt())
                gothic(it)
                body.append(it)
                if it.name == '洋裝_上身':
                    body.append(corset_lacing())
                if it.name == '洋裝_荷葉邊':
                    body.insert(len(body) - 1, lace_front())
            items = body
        out.append((name, items))
    groups = out
    new = []
    for name, items in groups:
        if name == '頭':
            # Add crown to head group so it tracks head 9-axis movement
            head_items = list(items)
            head_items.append(princess_crown())
            new.append((name, head_items))
        elif name == '身體':
            body_items = list(items)
            body_items.append(golden_ball())
            new.append((name, body_items))
        else:
            new.append((name, items))
    return new


landmarks = GD.landmarks
body_landmarks = GD.body_landmarks

# Inherit and adapt RIG configuration
RIG = copy.deepcopy(GD.RIG)
RIG['head3d']['layers']['髮飾_王冠'] = (1, 16)
RIG['arm_parts']['R'].append('道具_金球')
RIG['breath_scale'] = RIG['breath_scale'] + ['蕾絲胸衣']
# kid-friendly: no chest bounce (the flat lace front stays put; nothing underneath can peek out)
RIG['chest'] = dict(RIG['chest'], sway=0.0, bounce=0.0, squash=0.0)
