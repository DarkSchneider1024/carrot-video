# -*- coding: utf-8 -*-
"""王子 (the Prince, after the frog's spell breaks) — built on hunter.py (same skeleton / rig).

Changes: clean-shaven young face (no beard / mustache, smaller nose blush), golden-blond hair with bangs,
small gold circlet crown, royal-blue coat with gold trim, white shirt and trousers, black boots, gold belt.
"""
import copy
import numpy as np

import hunter as H
import red_hood as RH
from girl import Part, hx, M
from girl_v4 import R, Rell, CX, K, LW, SIDES, ID

GOLD, GOLD_SH, GOLD_HI, GOLD_LN = hx('f5c63a'), hx('c2951a'), hx('fff08a'), hx('6a4f08')
HAIR, HAIR_SH, HAIR_HI, HAIR_LN = hx('f1c655'), hx('cf9a2c'), hx('fde89a'), hx('6e4a0c')


def cmap(d):
    t = {k[:3]: v for k, v in d.items()}
    return lambda c: (t[c[:3]][:3] + (c[3],)) if c[:3] in t else c


HAIR_MAP = cmap({H.HAIR: HAIR, H.HAIR_SH: HAIR_SH, H.HAIR_HI: HAIR_HI, H.HAIR_LN: HAIR_LN})
COAT_MAP = cmap({H.JACK: hx('2f5fb8'), H.JACK_SH: hx('1f4188'), H.JACK_HI: hx('5b88dc'), H.JACK_LN: hx('0c1c44')})
SHIRT_MAP = cmap({H.SHIRT: hx('fbfbfb'), H.SHIRT_SH: hx('dcdde6'), H.SHIRT_LN: hx('8a8c9a'), H.CHECK: hx('ffffff', 0)})
PANTS_MAP = cmap({H.PANTS: hx('f4f1ea'), H.PANTS_SH: hx('d6d2c6'), H.PANTS_LN: hx('7c786c')})
BOOT_MAP = cmap({H.BOOT: hx('2a2424'), H.BOOT_SH: hx('1a1414'), H.BOOT_HI: hx('4a4040'), H.BOOT_LN: hx('0a0606')})
BELT_MAP = cmap({H.LEATHER: GOLD_SH, H.LEATHER_LN: GOLD_LN, H.BRASS: GOLD_HI})
NOSE_MAP = cmap({H.NOSE_RED: hx('f0bba0')})

DROP = {'獵槍', '背帶', '帽子', '羽毛', '鬍子', '八字鬍', '腮紅'}


def top_hair():
    """full head of blond hair with side-swept bangs (the hunter's hat used to cover the crown)"""
    p = Part('頭頂髮')
    right = [(CX, 78), (258, 80), (230, 90), (208, 110), (198, 140), (197, 176), (204, 180), (210, 150), (222, 128),
             (240, 120)]
    left = [(300, 132), (318, 120), (340, 126), (356, 146), (366, 176), (374, 176), (373, 140), (363, 110),
            (341, 90), (313, 80)]
    bangs = right + [(262, 130), (274, 142, 'c'), (282, 128), (296, 146, 'c')] + left
    pts = R(bangs)
    p.fill(pts, HAIR)
    p.air(R([(230, 84), (300, 84), (300, 104), (230, 104)]), HAIR_HI, blur=8)
    p.air(R([(196, 130), (215, 130), (215, 180), (196, 180)]), HAIR_SH, blur=6)
    p.air(M(R([(196, 130), (215, 130), (215, 180), (196, 180)])), HAIR_SH, blur=6)
    for x0 in (236, 256, 280, 306, 330):
        p.strand(R([(x0, 88), (x0 + 6, 110), (x0 + 4, 126)]), 1.2, HAIR_SH)
    p.line(pts, LW, HAIR_LN, closed=True)
    return p


def circlet():
    p = Part('王冠')
    base = [(246, 92), (250, 70), (262, 82), (274, 62), (CX, 76), (297, 62), (309, 82), (321, 70), (325, 92),
            (CX, 88)]
    pts = R(base)
    p.fill(pts, GOLD)
    p.air(R([(246, 82), (325, 82), (325, 94), (246, 94)]), GOLD_SH, blur=3)
    p.line(pts, LW, GOLD_LN, closed=True)
    p.fill(Rell(CX, 82, 4, 4), hx('2a6ed0'), line=GOLD_LN, lw=0.8)
    for x, y in [(250, 70), (274, 62), (297, 62), (321, 70)]:
        p.fill(Rell(x, y, 2.8, 2.8), GOLD_HI, line=GOLD_LN, lw=0.7)
    return p


def gold_trim(p, side):
    f = ID if side == 'R' else M
    p.line(f(R([(262, 318), (254, 350), (254, 400), (258, 470), (266, 540), (270, 600), (268, 646)])), 2.2, GOLD)
    for y in (420, 470, 520):
        p.fill(f(Rell(250, y, 3.6, 3.6)), GOLD, line=GOLD_LN, lw=0.6)


SKIN, SKIN_SH, SKIN_HI, SKIN_LN = H.SKIN, H.SKIN_SH, H.SKIN_HI, H.SKIN_LN
IRIS, IRIS_DK, IRIS_HI = hx('3a7fd0'), hx('1c3f7a'), hx('8fc8ff')
EYE_Y, EYE_DX, S = 186, 36, 1.35


def face():
    """slimmer, younger face with a pointed (V) chin"""
    p = Part('臉')
    pts = R(H.sym([(CX, 100), (250, 103), (222, 116), (207, 142), (204, 176), (207, 204), (214, 226), (228, 248),
                   (248, 266), (268, 278), (CX, 282)]))
    p.fill(pts, SKIN)
    p.air(R([(200, 100), (371, 100), (371, 124), (200, 124)]), SKIN_SH, blur=8)
    p.air(R([(198, 150), (216, 150), (216, 240), (198, 240)]), SKIN_SH, blur=8)
    p.air(M(R([(198, 150), (216, 150), (216, 240), (198, 240)])), SKIN_SH, blur=8)
    p.line(pts, LW, SKIN_LN, closed=True)
    return p


def nose():
    p = Part('鼻子')
    p.line(R([(CX + 2, 200), (CX + 4, 216), (CX, 220)]), 1.3, SKIN_LN)
    p.air(R([(CX - 4, 196), (CX + 1, 196), (CX + 1, 214), (CX - 4, 214)]), SKIN_HI, blur=2)
    return p


def eye(side):
    """big anime eye: blue iris with gradient, pupil, two highlights, thick lash line"""
    f = 1 if side == 'R' else -1
    cx, cy = CX - f * EYE_DX, EYE_Y

    def E(pts):
        return R([(cx - f * q[0] * S, cy + q[1] * S) + tuple(q[2:]) for q in pts])

    parts = []
    p = Part(f'下眼皮_{side}')
    p.fill(E([(-17, 6), (-6, 12), (8, 12), (16, 5), (18, 16), (0, 20), (-18, 16)]), SKIN)
    parts.append(p)
    p = Part(f'眼白_{side}')
    p.fill(E([(-16, 4), (-11, -9), (0, -14), (12, -11), (17, -2), (10, 10), (-6, 11)]), hx('fdfdff'))
    p.cfill(E([(-20, -16), (20, -16), (20, -6), (-20, -7)]), hx('d8def0'), blur=2)
    parts.append(p)
    p = Part(f'眼球_{side}')
    p.fill(Rell(cx + f * 0.5, cy, 10.5 * S, 12.5 * S), IRIS, raw=True)
    p.air(Rell(cx + f * 0.5, cy - 6 * S, 11 * S, 6 * S), IRIS_DK, blur=2, raw=True)
    p.air(Rell(cx + f * 0.5, cy + 7 * S, 8 * S, 4 * S), IRIS_HI, blur=2, raw=True)
    p.fill(Rell(cx + f * 0.5, cy + 0.5, 4.6 * S, 5.8 * S), hx('0c1a33'), raw=True)
    p.line(Rell(cx + f * 0.5, cy, 10.5 * S, 12.5 * S), 0.9, IRIS_DK)
    parts.append(p)
    p = Part(f'上眼線_{side}')
    p.rib(E([(-18, 3), (-12, -8), (0, -14), (12, -12), (19, -4), (22, -1)]),
          [1.4 * K, 3.2 * K, 3.8 * K, 3.8 * K, 3.0 * K, 1.0 * K], hx('1e140e'), hardness=0.7, flow=0.6)
    parts.append(p)
    p = Part(f'上眼皮_{side}')
    p.fill(E([(-19, 2), (-12, -9), (0, -15), (12, -13), (20, -4), (22, -18), (0, -25), (-21, -14)]), SKIN)
    parts.append(p)
    p = Part(f'高光_{side}')
    p.fill(Rell(cx - f * 3.5 * S, cy - 5 * S, 3.4 * S, 3.8 * S), hx('ffffff'), raw=True)
    p.fill(Rell(cx + f * 4 * S, cy + 6 * S, 1.8 * S, 1.8 * S), hx('ffffff'), raw=True)
    parts.append(p)
    return parts


def brows():
    out = []
    for side, f in SIDES:
        p = Part(f'眉毛_{side}')
        p.rib(f(R([(228, 152), (240, 146), (256, 144), (270, 149)])), [1.2 * K, 3.4 * K, 3.2 * K, 1.4 * K], HAIR_LN,
              hardness=0.6, flow=0.55)
        out.append(p)
    return out


REPLACE = {'臉': face, '鼻子': nose}


def fix(p):
    n = p.name
    if n in ('後髮', '前髮') or n.startswith('眉毛'):
        RH.recolor(p, HAIR_MAP)
    elif n.startswith('外套'):
        RH.recolor(p, COAT_MAP)
        gold_trim(p, n[-1])
    elif n.startswith(('上臂', '下臂')):
        RH.recolor(p, COAT_MAP)
    elif n in ('胸腔', '領子'):
        RH.recolor(p, SHIRT_MAP)
    elif n.startswith('腿'):
        RH.recolor(p, PANTS_MAP)
    elif n.startswith('腳'):
        RH.recolor(p, BOOT_MAP)
    elif n == '腰帶':
        RH.recolor(p, BELT_MAP)
    elif n == '鼻子':
        RH.recolor(p, NOSE_MAP)


def build():
    out = []
    for name, items in H.build():
        new = []
        for it in items:
            if isinstance(it, tuple):
                if it[0] in ('眼_R', '眼_L'):
                    new.append((it[0], eye(it[0][-1])))
                    continue
                for q in it[1]:
                    fix(q)
                new.append(it)
                continue
            if it.name in DROP:
                continue
            if it.name in REPLACE:
                it = REPLACE[it.name]()
            elif it.name.startswith('眉毛'):
                if it.name.endswith('_R'):
                    new += brows()
                continue
            fix(it)
            new.append(it)
        if name == '頭':
            new.append(top_hair())
            new.append(circlet())
        if new:
            out.append((name, new))
    return out


landmarks, body_landmarks = H.landmarks, H.body_landmarks
RIG = copy.deepcopy(H.RIG)
for k in ('帽子', '羽毛', '鬍子', '八字鬍'):
    RIG['head3d']['layers'].pop(k, None)
RIG['head3d']['layers']['王冠'] = (1, 12)
RIG['head3d']['layers']['頭頂髮'] = (1, 6)
RIG['breath_lift'] = ['外套_R', '外套_L', '領子', '上臂_R', '上臂_L']
RIG['eyes'] = {'R': (CX - EYE_DX, EYE_Y), 'L': (CX + EYE_DX, EYE_Y)}
RIG['lower_lid_dy'], RIG['blink_drop'] = 12, 27
