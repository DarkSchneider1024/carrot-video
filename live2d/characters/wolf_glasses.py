# -*- coding: utf-8 -*-
"""大野狼 with thick black-framed glasses (《半夜三點的牛肉麵》: the anxious, self-defending wolf)."""
import copy

import wolf as W
from girl import Part, hx, M
from girl_v4 import R, CX, K, LW

FRAME, FRAME_HI = hx('17181c'), hx('4a4d57')


def glasses():
    p = Part('眼鏡')
    for g in (lambda q: q, M):
        cx, cy = CX - 36, 189
        rim = [(cx - 23, cy - 12), (cx - 16, cy - 17), (cx + 16, cy - 17), (cx + 23, cy - 11), (cx + 22, cy + 10),
               (cx + 14, cy + 17), (cx - 14, cy + 17), (cx - 22, cy + 11)]
        p.fill(g(R(rim)), hx('ffffff', 38))                                         # lens: faint glass
        p.air(g(R([(cx - 18, cy - 14), (cx - 6, cy - 14), (cx - 14, cy + 4), (cx - 20, cy + 4)])), hx('ffffff', 110), blur=2)
        p.line(g(R(rim)), 3.4, FRAME, closed=True)
        p.line(g(R([(cx - 20, cy - 13), (cx - 14, cy - 16), (cx + 12, cy - 16)])), 1.0, FRAME_HI)
        p.line(g(R([(cx - 23, cy - 8), (cx - 40, cy - 9), (cx - 47, cy - 6)])), 3.0, FRAME)      # temple
    p.line(R([(CX - 13, 186), (CX - 6, 182), (CX, 181.5), (CX + 6, 182), (CX + 13, 186)]), 3.0, FRAME)   # bridge
    return p


def build():
    out = []
    for name, items in W.build():
        if name == '頭':
            items = list(items) + [glasses()]
        out.append((name, items))
    return out


landmarks, body_landmarks = W.landmarks, W.body_landmarks
RIG = copy.deepcopy(W.RIG)
RIG['head3d']['layers']['眼鏡'] = (1, 9)
