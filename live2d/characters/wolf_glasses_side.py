# -*- coding: utf-8 -*-
"""大野狼 profile with black-framed glasses. The near lens rides with the head; the far lens rides with the far
eye (hidden at 90 deg, slides out at 70 deg with Head:: Turn)."""
import copy

import wolf_side as WS
from girl import Part, hx
from girl_v4 import R, CX, K, LW

X = lambda d: CX + d
FRAME = hx('17181c')


def glasses_near():
    p = Part('眼鏡')
    rim = [(X(27), 174), (X(56), 170), (X(59), 186), (X(55), 196), (X(31), 197), (X(27), 186)]
    p.fill(R(rim), hx('ffffff', 38))
    p.line(R(rim), 3.4, FRAME, closed=True)
    p.line(R([(X(27), 178), (X(4), 172), (X(-10), 170)]), 3.0, FRAME)                           # temple to the ear
    p.line(R([(X(59), 178), (X(64), 176)]), 3.0, FRAME)                                         # bridge stub
    return p


def glasses_far():
    p = Part('遠鏡片')           # same slide-out as the far eye (behind the head at rest)
    rim = [(X(44), 174), (X(56), 173), (X(58), 186), (X(55), 193), (X(45), 193)]
    p.line(R(rim), 3.0, FRAME, closed=True)
    return p


def build():
    out = []
    for name, items in WS.build():
        if name == '頭':
            new = []
            for it in items:
                new.append(it)
                if isinstance(it, tuple) and it[0] == '遠眼':
                    new[-1] = ('遠眼', list(it[1]) + [glasses_far()])
            new.append(glasses_near())
            items = new
        out.append((name, items))
    return out


SIDE_RIG = copy.deepcopy(WS.SIDE_RIG)
SIDE_RIG['turn']['far_eye']['parts'] = SIDE_RIG['turn']['far_eye']['parts'] + ['遠鏡片']
