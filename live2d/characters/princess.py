# -*- coding: utf-8 -*-
"""紫髮小公主 (Princess) — built directly on 紫髮少女 (girl_dress / girl_v4).

Adds royal princess elements to the existing anime girl:
1. Pure gold princess crown (金冠) on top of the head
2. Glowing golden ball (金球) held near her hand
All original face, eyes, hair, dress, arms, chest physics, and nine-axis head are preserved.
"""
import copy, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.abspath(os.path.join(HERE, '..', 'engine'))
if ENGINE not in sys.path:
    sys.path.insert(0, ENGINE)

import girl_dress as GD
import girl_v4 as G4
from girl import Part, hx, M
from girl_v4 import R, Rell, CX, LW

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


def build():
    groups = GD.build()
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
