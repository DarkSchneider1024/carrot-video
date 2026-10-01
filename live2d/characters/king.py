# -*- coding: utf-8 -*-
"""國王 (the King, 青蛙王子) — built on hunter.py (same skeleton / rig).

Changes: no rifle / strap / hat / feather; silver-white hair and full beard; gold crown with jewels;
royal red coat with ermine-white trim, gold waistcoat, gold belt, dark red trousers, black boots.
"""
import copy
import numpy as np

import hunter as H
import hunter_head as HH
import vtuber_face as VF
import red_hood as RH
from girl import Part, hx, M
from girl_v4 import R, Rell, CX, K, LW, SIDES, ID

GOLD, GOLD_SH, GOLD_HI, GOLD_LN = hx('f5c63a'), hx('c2951a'), hx('fff08a'), hx('6a4f08')
RUBY, SAPPHIRE, EMERALD = hx('d42838'), hx('2a6ed0'), hx('2fa05a')
ERMINE, ERMINE_SH = hx('fbfaf6'), hx('d9d6cc')


HH.patch(H)


def cmap(d):
    t = {k[:3]: v for k, v in d.items()}
    return lambda c: (t[c[:3]][:3] + (c[3],)) if c[:3] in t else c


HAIR_MAP = cmap({H.HAIR: hx('e9e6e0'), H.HAIR_SH: hx('bdb8ae'), H.HAIR_HI: hx('ffffff'), H.HAIR_LN: hx('6f6a62')})
COAT_MAP = cmap({H.JACK: hx('b32a33'), H.JACK_SH: hx('82161f'), H.JACK_HI: hx('d8505a'), H.JACK_LN: hx('3f070c')})
SHIRT_MAP = cmap({H.SHIRT: hx('f3d77a'), H.SHIRT_SH: hx('d2b04c'), H.SHIRT_LN: hx('7a5e14'), H.CHECK: hx('e8c55a', 0)})
PANTS_MAP = cmap({H.PANTS: hx('6e1a22'), H.PANTS_SH: hx('4f1017'), H.PANTS_LN: hx('26060a')})
BOOT_MAP = cmap({H.BOOT: hx('2a2222'), H.BOOT_SH: hx('1a1414'), H.BOOT_HI: hx('4a3e3e'), H.BOOT_LN: hx('0a0606')})
BELT_MAP = cmap({H.LEATHER: GOLD_SH, H.LEATHER_LN: GOLD_LN, H.BRASS: RUBY})

DROP = {'獵槍', '背帶', '帽子', '羽毛'}


@HH.scaled
def crown():
    p = Part('王冠')
    base = [(236, 104), (234, 58), (252, 80), (262, 44), (274, 76), (CX, 34), (297, 76), (309, 44), (319, 80),
            (337, 58), (335, 104)]
    pts = R(base)
    p.fill(pts, GOLD)
    p.air(R([(234, 84), (337, 84), (337, 104), (234, 104)]), GOLD_SH, blur=4)
    p.air(R([(250, 50), (280, 50), (280, 80), (250, 80)]), GOLD_HI, blur=5)
    p.line(pts, LW * 1.1, GOLD_LN, closed=True)
    band = [(234, 92), (337, 92), (338, 108), (233, 108)]
    p.fill(R(band), ERMINE, line=hx('9a968c'), lw=LW * 0.8)
    for x in np.arange(240, 334, 12):
        p.fill(Rell(x, 100, 1.6, 2.4), hx('222222'), raw=True)                   # ermine spots
    p.fill(Rell(CX, 72, 6, 7), RUBY, line=GOLD_LN, lw=0.9)
    p.fill(Rell(256, 80, 4.5, 5), SAPPHIRE, line=GOLD_LN, lw=0.9)
    p.fill(Rell(315, 80, 4.5, 5), EMERALD, line=GOLD_LN, lw=0.9)
    for x, y in [(234, 58), (262, 44), (CX, 34), (309, 44), (337, 58)]:
        p.fill(Rell(x, y, 4, 4), GOLD_HI, line=GOLD_LN, lw=0.8)
    return p


@HH.scaled
def top_hair():
    """silver hair on the crown of the head (the hunter's hat used to cover it)"""
    p = Part('頭頂髮')
    pts = R(H.sym([(CX, 94), (256, 96), (230, 104), (212, 118), (204, 140), (212, 128), (236, 114), (CX, 110)]))
    p.fill(pts, hx('e9e6e0'))
    p.line(pts, LW, hx('6f6a62'), closed=True)
    return p


@HH.slim
def ermine_collar():
    p = Part('披肩毛領')
    for g in (ID, M):
        q = g(R([(CX, 300), (262, 292), (226, 294), (198, 304), (188, 322), (206, 334), (240, 326), (266, 318),
                 (CX, 316)]))
        p.fill(q, ERMINE, line=hx('9a968c'), lw=LW * 0.9)
        for x, y in [(206, 314), (228, 312), (250, 306)]:
            p.fill(g(Rell(x, y, 1.8, 2.6)), hx('222222'), raw=True)
    p.fill(Rell(CX, 318, 7, 7), GOLD, line=GOLD_LN, lw=0.9)                     # clasp
    p.fill(Rell(CX, 318, 3.5, 3.5), RUBY, raw=True)
    return p


def fix(p):
    n = p.name
    if n in ('後髮', '鬍子', '八字鬍', '前髮') or n.startswith('眉毛'):
        RH.recolor(p, HAIR_MAP)
    elif n.startswith(('外套', '上臂', '下臂')):
        RH.recolor(p, COAT_MAP)
    elif n in ('胸腔', '領子'):
        RH.recolor(p, SHIRT_MAP)
    elif n.startswith('腿'):
        RH.recolor(p, PANTS_MAP)
    elif n.startswith('腳'):
        RH.recolor(p, BOOT_MAP)
    elif n == '腰帶':
        RH.recolor(p, BELT_MAP)


def build():
    out = []
    for name, items in HH.build_slim(H):
        new = []
        for it in items:
            if isinstance(it, tuple):
                for q in it[1]:
                    fix(q)
                new.append(it)
                continue
            if it.name in DROP:
                continue
            fix(it)
            new.append(it)
            if it.name == '領子':
                new.append(ermine_collar())
            if it.name == '後髮':
                new.append(top_hair())
        if name == '頭':
            new.append(crown())
        if new:
            out.append((name, new))
    return VF.add(out, eyes={s: (*RIG['eyes'][s], 24, 5) for s in 'RL'}, mouth=(CX, RIG['mouth_y'] - 1, 17),
                  eye_lw=2.2, mouth_lw=1.1)


landmarks, body_landmarks = H.landmarks, H.body_landmarks
RIG = copy.deepcopy(H.RIG)
RIG['head3d']['layers'].pop('帽子', None)
RIG['head3d']['layers'].pop('羽毛', None)
RIG['head3d']['layers']['王冠'] = (1, 10)
RIG['head3d']['layers']['頭頂髮'] = (1, 4)
RIG['breath_lift'] = ['外套_R', '外套_L', '領子', '披肩毛領', '上臂_R', '上臂_L']
HH.rig(RIG)
HH.rig_body(RIG)
VF.rig(RIG)          # VTuber blink (smiling ^) + D-shaped talking mouth (卡洛兒 v2 style)
