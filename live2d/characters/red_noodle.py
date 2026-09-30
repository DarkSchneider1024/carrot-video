# -*- coding: utf-8 -*-
"""小紅帽 (《半夜三點的牛肉麵》 version): same as red_hood, but instead of the basket she carries a clear plastic
take-out bag with a round microwave container of beef noodles inside. The layer keeps the name 籃子 so the rig
(arm field, Basket:: Swing) works unchanged.
"""
import numpy as np

import red_hood as RH
from girl import Part, hx
from girl_v4 import R, Rell, CX, K, LW

BAG, BAG_SH, BAG_LN = hx('f4f6fa', 170), hx('c9d0dc', 150), hx('8d97a8')
LID, LID_SH = hx('eef3f7', 220), hx('b9c6d2', 200)
SOUP, SOUP_DK, NOODLE, BEEF, GREEN = hx('a8552a'), hx('6e3217'), hx('f1d7a0'), hx('7a3d22'), hx('5f9a3c')


def noodle_bag(cx, grip_y, name='籃子', Rf=R):
    """clear take-out bag hanging from the grip point: handle loop, bag body, container inside (reference px)"""
    p = Part(name)
    x = lambda d: cx + d
    # container inside (drawn first, seen through the bag)
    body = [(x(-26), grip_y + 52), (x(26), grip_y + 52), (x(23), grip_y + 88), (x(-23), grip_y + 88)]
    p.fill(Rf(body), hx('e9eef3', 230))
    p.cfill(Rf([(x(-24), grip_y + 58), (x(24), grip_y + 58), (x(22), grip_y + 86), (x(-22), grip_y + 86)]), SOUP, blur=1)
    p.cfill(Rf([(x(-24), grip_y + 74), (x(24), grip_y + 74), (x(22), grip_y + 86), (x(-22), grip_y + 86)]), SOUP_DK, blur=3)
    for i, dx in enumerate(np.linspace(-18, 16, 7)):                      # noodles swirling in the soup
        p.line(Rf([(x(dx), grip_y + 62), (x(dx + 4), grip_y + 70), (x(dx - 2), grip_y + 80)]), 1.4, NOODLE, clipped=True)
    for dx, dy in [(-12, 64), (8, 66), (-2, 76)]:                          # beef chunks
        p.cfill(Rell(x(dx), grip_y + dy, 5, 3.4), BEEF, raw=True, blur=0.5)
    p.cfill(Rell(x(14), grip_y + 60, 3, 1.6), GREEN, raw=True, blur=0.3)   # scallion
    lid = [(x(-28), grip_y + 49), (x(28), grip_y + 49), (x(28), grip_y + 55), (x(-28), grip_y + 55)]
    p.fill(Rf(lid), LID, line=hx('9aa7b4'), lw=LW * 0.8)
    p.line(Rf(body), LW * 0.8, hx('9aa7b4'), closed=True)
    # bag handle (two loops meeting in the hand)
    for s_ in (-1, 1):
        loop = Rf([(x(0), grip_y), (x(10 * s_), grip_y + 6), (x(22 * s_), grip_y + 26), (x(28 * s_), grip_y + 40)])
        p.rib(loop, [3.2 * K] * 4, BAG_LN, hardness=0.6, flow=0.7)
        p.rib(loop, [2.0 * K] * 4, hx('f7f9fc', 230), hardness=0.7, flow=0.8)
    # bag body: translucent, crinkled
    bag = [(x(-30), grip_y + 36), (x(30), grip_y + 36), (x(35), grip_y + 70), (x(33), grip_y + 96, 'c'),
           (x(-33), grip_y + 96, 'c'), (x(-35), grip_y + 70)]
    p.fill(Rf(bag), BAG)
    for a, b in [((-18, 40), (-24, 90)), ((6, 40), (12, 92)), ((22, 44), (26, 88))]:
        p.line(Rf([(x(a[0]), grip_y + a[1]), (x((a[0] + b[0]) / 2 - 2), grip_y + (a[1] + b[1]) / 2), (x(b[0]), grip_y + b[1])]),
               0.9, BAG_SH, clipped=True)
    p.air(Rf([(x(-34), grip_y + 36), (x(-20), grip_y + 36), (x(-20), grip_y + 96), (x(-34), grip_y + 96)]), hx('ffffff', 120), blur=4)
    p.line(Rf(bag), LW * 0.8, BAG_LN, closed=True)
    return p


def phone(cx, cy, name='手機', Rf=R, tilt=0.0):
    """phone held in the free hand; the flashlight shines from its top end (the stage finds this layer)"""
    import math
    p = Part(name)
    c, s_ = math.cos(tilt), math.sin(tilt)
    Q = lambda pts: Rf([(cx + x * c - y * s_, cy + x * s_ + y * c) for x, y in pts])
    body = [(-8, -15), (8, -15), (8, 15), (-8, 15)]
    p.fill(Q(body), hx('23252c'), line=hx('0e0f13'), lw=LW * 0.8)
    p.cfill(Q([(-6, -12), (6, -12), (6, 12), (-6, 12)]), hx('3a4a66'), blur=0.3)
    p.cfill(Q([(-3, -14), (3, -14), (3, -11), (-3, -11)]), hx('fffbe0'), blur=0.3)        # the LED
    return p


def build():
    groups = RH.build()
    out = []
    for name, items in groups:
        new = []
        for it in items:
            if not isinstance(it, tuple) and it.name == '籃子':
                it = noodle_bag(176, 556)
            new.append(it)
            if not isinstance(it, tuple) and it.name == '手掌_L':
                new.append(phone(2 * CX - 178, 578))                   # in her free (left) hand
        out.append((name, new))
    return out


landmarks = RH.landmarks
body_landmarks = RH.body_landmarks
RIG = dict(RH.RIG)
RIG['arm_parts'] = {'R': RH.RIG['arm_parts']['R'], 'L': RH.RIG['arm_parts']['L'] + ['手機']}
RIG['extras'] = [{'param': 'Basket:: Swing', 'parts': ['籃子'], 'pivot': (176, 556), 'angle': 0.18, 'ramp': None},
                 # raise the free forearm to hold the phone up at chest height (flashlight in the night forest)
                 {'param': 'Arm:: Left:: Raise', 'parts': ['下臂_L', '手掌_L', '手指_L', '手機'],
                  'pivot': (2 * CX - 193, 472), 'angle': 2.55, 'ramp': (464, 488)}]
