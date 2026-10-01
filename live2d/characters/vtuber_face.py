# -*- coding: utf-8 -*-
"""VTuber face for the Python-drawn puppets -- the same feel as 卡洛兒姐姐 v2 (user reference
https://www.youtube.com/shorts/6a38dFsTuPs):

  閉眼_R / 閉眼_L   the smiling closed eye: one thick arch (∩, like ^) with two lashes at the outer corner. The rig
                    cross-fades the open eye into it at the end of a blink (rig.py, RIG['vtuber']).
  嘴_啊             talking 'ah': a D-shaped open mouth, corners turned up, dark red inside, upper teeth with two
                    small fangs, a pink tongue at the bottom.
  嘴_喔             talking 'oh': a small round open mouth with a little tongue.
The old 'stretch the mouth cavity' opening (口腔 s.x 1.45 / s.y 3.0) slid off the face when the head turned
(user: 公主說話的時候嘴巴會飛出去); these mouths are drawn whole and only fade in / unfold from their top edge.

add(groups, eyes=..., mouth=...) appends the parts to the character's 頭 group: the closed eyes into 眼_R / 眼_L,
the mouths into 嘴. Coordinates are design units (girl_v4.R), like every part.
"""
import numpy as np

from girl import Part, hx
from girl_v4 import R, K

INK = hx('2a1712')
CAVITY, CAVITY_DK = hx('7a1f2b'), hx('4e1019')
TONGUE, TONGUE_HI = hx('ef8a96'), hx('ffb3bc')
TOOTH, TOOTH_LN = hx('fffdf8'), hx('b9aaa4')


def closed_eye(side, cx, cy, w, h, lw=3.0, col=INK):
    """∩ arch from corner to corner, thickest at the top; lashes flick out at the OUTER corner (R = screen left)"""
    p = Part(f'閉眼_{side}')
    xs = np.linspace(-1.0, 1.0, 11)
    pts = [(cx + x * w / 2, cy + h * 0.15 - h * (1 - x * x)) for x in xs]
    prof = [0.35, 0.7, 0.95, 1.1, 1.2, 1.2, 1.15, 1.05, 0.9, 0.7, 0.4]
    p.rib(R(pts), [lw * K * a for a in prof], col, hardness=0.7, flow=0.6)
    o = -1 if side == 'R' else 1                                  # outer corner direction
    ex, ey = cx + o * w / 2, cy + h * 0.15
    for k, (dx, dy) in enumerate(((0.16, -0.10), (0.20, 0.06))):
        tip = (ex + o * w * dx, ey + w * dy)
        mid = (ex + o * w * dx * 0.5, ey + w * dy * 0.4)
        p.rib(R([(ex - o * w * 0.04, ey), mid, tip]), [lw * K * 0.9, lw * K * 0.6, lw * K * 0.15], col,
              hardness=0.7, flow=0.6)
    return p


def mouth_ah(mx, my, w, lw=1.6):
    """D shape: the top edge smiles (corners up), the bottom is a deep round arc"""
    p = Part('嘴_啊')
    d = 0.62 * w
    top = [(mx - w / 2, my - 0.14 * w, 'c'), (mx - w * 0.25, my - 0.02 * w), (mx, my), (mx + w * 0.25, my - 0.02 * w),
           (mx + w / 2, my - 0.14 * w, 'c')]
    arc = [(mx + w / 2 * np.cos(t), my - 0.14 * w * abs(np.cos(t)) ** 3 + d * np.sin(t))
           for t in np.linspace(0.12, np.pi - 0.12, 15)]
    pts = R(top + arc)
    p.fill(pts, CAVITY)
    p.cfill(R([(mx - w, my - w), (mx + w, my - w), (mx + w, my + d * 0.35), (mx - w, my + d * 0.35)]), CAVITY_DK, blur=3)
    # tongue
    p.cfill(R([(mx + 0.36 * w * np.cos(t), my + d * 0.98 - 0.30 * d * np.sin(t)) for t in np.linspace(0, np.pi, 16)]),
            TONGUE, blur=0.8)
    p.cfill(R([(mx - 0.12 * w, my + d * 0.78), (mx + 0.12 * w, my + d * 0.78), (mx + 0.08 * w, my + d * 0.86),
               (mx - 0.08 * w, my + d * 0.86)]), TONGUE_HI, blur=2)
    # upper teeth along the top edge + two small fangs
    band = top[:1] + [q[:2] for q in top[1:-1]] + top[-1:] + \
        [(mx + w * 0.42, my - 0.06 * w + 0.13 * w), (mx, my + 0.12 * w), (mx - w * 0.42, my - 0.06 * w + 0.13 * w)]
    p.cfill(R(band), TOOTH, blur=0.6)
    for s in (-1, 1):
        fx = mx + s * 0.27 * w
        p.cfill(R([(fx - 0.05 * w, my + 0.07 * w), (fx + 0.05 * w, my + 0.07 * w), (fx + 0.005 * w * s, my + 0.22 * w)]),
                TOOTH, blur=0.4)
        p.line(R([(fx - 0.05 * w * s, my + 0.08 * w), (fx + 0.005 * w * s, my + 0.22 * w)]), 0.7, TOOTH_LN)
    p.line(pts, lw, INK, closed=True)
    return p


def mouth_oh(mx, my, w, lw=1.6):
    """small round 'oh', a little taller than wide"""
    p = Part('嘴_喔')
    rx, ry = 0.24 * w, 0.30 * w
    cy = my + ry * 0.75
    pts = R([(mx + rx * np.cos(t), cy + ry * np.sin(t)) for t in np.linspace(0, 2 * np.pi, 28, endpoint=False)])
    p.fill(pts, CAVITY)
    p.cfill(R([(mx - w, cy - w), (mx + w, cy - w), (mx + w, cy - ry * 0.3), (mx - w, cy - ry * 0.3)]), CAVITY_DK, blur=2)
    p.cfill(R([(mx + 0.7 * rx * np.cos(t), cy + ry - 0.45 * ry * np.sin(t)) for t in np.linspace(0, np.pi, 12)]),
            TONGUE, blur=0.8)
    p.cfill(R([(mx - rx, cy - ry), (mx + rx, cy - ry), (mx + rx, cy - ry * 0.72), (mx - rx, cy - ry * 0.72)]),
            TOOTH, blur=0.6)
    p.line(pts, lw, INK, closed=True)
    return p


def add(groups, eyes, mouth, eye_lw=3.0, mouth_lw=1.6, wrap=None):
    """eyes = {'R': (cx, cy, w, h), 'L': (...)}, mouth = (mx, my, w), all design units. wrap: optional decorator
    that draws the parts in the character's own warp (e.g. hunter_head.scaled)."""
    call = (lambda f, *a, **k: wrap(f)(*a, **k)) if wrap else (lambda f, *a, **k: f(*a, **k))
    out = []
    for name, items in groups:
        if name == '頭':
            new = []
            for it in items:
                if isinstance(it, tuple) and it[0] in ('眼_R', '眼_L'):
                    s = it[0][-1]
                    new.append((it[0], list(it[1]) + [call(closed_eye, s, *eyes[s], lw=eye_lw)]))
                elif isinstance(it, tuple) and it[0] == '嘴':
                    new.append(('嘴', list(it[1]) + [call(mouth_ah, *mouth, lw=mouth_lw),
                                                     call(mouth_oh, *mouth, lw=mouth_lw)]))
                else:
                    new.append(it)
            items = new
        out.append((name, items))
    return out


def rig(RIG):
    """turn on the VTuber blink / mouth in engine/rig.py and give the new layers a depth on the nine-axis head"""
    RIG['vtuber'] = True
    RIG['head3d']['layers'].update({'閉眼': (1, 2.0), '嘴_': (1, 1.5)})
