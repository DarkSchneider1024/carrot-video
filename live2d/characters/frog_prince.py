# -*- coding: utf-8 -*-
"""青蛙王子 (The Frog Prince, under the spell) — Live2D / Inochi2D front view. v2 (v1 had a lid that covered
the whole eye so he always looked asleep, a floating crown, detached limbs and one arm missing).

A cute chibi frog standing upright on the shared reference grid (sole at y 1003 like the other puppets):
big round head with two bulging eyes on top, a small gold crown sitting between them, wide smile, pear-shaped
body with a cream belly, a little red royal cape-collar with a gold clasp, stubby arms with 3-finger webbed
hands, bent frog legs with big webbed feet.

Layers follow the rig conventions: 眼_R/眼_L groups hold 眼窩 (socket, stays), 眼白/眼球/高光 (squashed by
the blink), 上眼線 (lid line that drops); 嘴 group holds 口腔/舌頭/上唇.
"""
import numpy as np

from girl import Part, hx, M
from girl_v4 import R, Rell, CX, SIDES, ID, K, LW
import vtuber_face as VF

GRN, GRN_SH, GRN_HI, GRN_LN = hx('5cb84e'), hx('3f8a36'), hx('8ad872'), hx('1d4a18')
BELLY, BELLY_SH, BELLY_LN = hx('eef5c0'), hx('cfdc92'), hx('7f9148')
GOLD, GOLD_SH, GOLD_HI, GOLD_LN = hx('f7ca39'), hx('c29719'), hx('fff28a'), hx('695009')
RUBY, SAPPHIRE = hx('d42838'), hx('226ecf')
CAPE, CAPE_SH, CAPE_LN = hx('c8323c'), hx('8e1c24'), hx('4a0a10')
WHITE = hx('ffffff')
EYE_W, IRIS, PUPIL = hx('fffdf0'), hx('7a4a1c'), hx('1a120a')
MOUTH, TONGUE = hx('5a1a22'), hx('ef7c8c')

HEAD_C = (CX, 470)
EYE_DX, EYE_Y, EYE_R = 62, 392, 40
MOUTH_Y = 512


def mirror_list(pts):
    return [(2 * CX - p[0],) + tuple(p[1:]) for p in reversed(pts)]


def sym(right):
    return right + mirror_list(right[1:-1])


# =================================================================== head
def head():
    p = Part('臉')
    pts = Rell(HEAD_C[0], HEAD_C[1], 128, 92)
    p.fill(pts, GRN)
    p.air(Rell(CX - 30, 420, 80, 34), GRN_HI, blur=14)
    p.air(R([(150, 520), (420, 520), (420, 570), (150, 570)]), GRN_SH, blur=14)
    for x, y in [(CX - 40, 440), (CX + 52, 452), (CX - 88, 478), (CX + 92, 488)]:           # spots
        p.air(Rell(x, y, 8, 6), GRN_SH, blur=3)
    p.line(pts, LW * 1.2, GRN_LN, closed=True)
    return p


def cheeks():
    p = Part('腮紅')
    for g in (ID, M):
        p.soft(g(Rell(CX - 84, 506, 20, 11)), hx('f48a9a', 150), 7)
    return p


def eye(side):
    f = -1 if side == 'R' else 1
    cx, cy = CX + f * EYE_DX, EYE_Y
    parts = []
    p = Part(f'眼窩_{side}')
    bump = Rell(cx, cy, EYE_R + 6, EYE_R + 4)
    p.fill(bump, GRN)
    p.air(Rell(cx, cy - 20, EYE_R, 18), GRN_HI, blur=8)
    p.line(bump, LW * 1.2, GRN_LN, closed=True)
    parts.append(p)
    p = Part(f'眼白_{side}')
    ew = Rell(cx, cy + 2, EYE_R - 6, EYE_R - 5)
    p.fill(ew, EYE_W)
    p.air(Rell(cx, cy - 22, EYE_R - 8, 10), hx('d8d4bc'), blur=4)
    p.line(ew, 1.0, hx('6a6a50'), closed=True)
    parts.append(p)
    p = Part(f'眼球_{side}')
    p.fill(Rell(cx - f * 3, cy + 5, 20, 22), IRIS, raw=True)
    p.air(Rell(cx - f * 3, cy - 8, 20, 8), hx('3a220c'), blur=2, raw=True)
    p.fill(Rell(cx - f * 3, cy + 6, 11, 13), PUPIL, raw=True)
    parts.append(p)
    p = Part(f'高光_{side}')
    p.fill(Rell(cx - f * 3 - 7, cy - 3, 6.5, 7), WHITE, raw=True)
    p.fill(Rell(cx - f * 3 + 7, cy + 14, 3, 3), WHITE, raw=True)
    parts.append(p)
    p = Part(f'上眼線_{side}')
    arc = [(cx - 36, cy - 4), (cx - 24, cy - 26), (cx, cy - 35), (cx + 24, cy - 26), (cx + 36, cy - 4)]
    p.rib(R(arc), [1.2 * K, 3.0 * K, 3.6 * K, 3.0 * K, 1.2 * K], GRN_LN, hardness=0.7, flow=0.6)
    parts.append(p)
    return parts


def mouth_parts():
    out = []
    p = Part('口腔')
    cav = sym([(CX, MOUTH_Y + 2), (CX - 30, MOUTH_Y + 2), (CX - 46, MOUTH_Y - 4), (CX - 36, MOUTH_Y + 12),
               (CX - 16, MOUTH_Y + 20), (CX, MOUTH_Y + 22)])
    p.fill(R(cav), MOUTH)
    out.append(p)
    p = Part('舌頭')
    p.fill(Rell(CX, MOUTH_Y + 15, 16, 6), TONGUE)
    out.append(p)
    p = Part('上唇')
    lip = [(CX - 70, MOUTH_Y - 16), (CX - 48, MOUTH_Y - 2), (CX - 20, MOUTH_Y + 3), (CX, MOUTH_Y + 3),
           (CX + 20, MOUTH_Y + 3), (CX + 48, MOUTH_Y - 2), (CX + 70, MOUTH_Y - 16)]
    p.rib(R(lip), [1.0 * K, 2.4 * K, 2.6 * K, 2.6 * K, 2.6 * K, 2.4 * K, 1.0 * K], GRN_LN, hardness=0.7, flow=0.6)
    out.append(p)
    return out


def nostrils():
    p = Part('鼻子')
    for g in (ID, M):
        p.fill(g(Rell(CX - 12, 470, 3.2, 2.2)), GRN_LN, raw=True)
    return p


def crown():
    p = Part('王冠')
    y0 = 372
    base = [(CX - 30, y0), (CX - 34, y0 - 34), (CX - 17, y0 - 18), (CX, y0 - 42), (CX + 17, y0 - 18),
            (CX + 34, y0 - 34), (CX + 30, y0)]
    pts = R(base)
    p.fill(pts, GOLD)
    p.air(R([(CX - 34, y0 - 10), (CX + 34, y0 - 10), (CX + 34, y0), (CX - 34, y0)]), GOLD_SH, blur=3)
    p.air(R([(CX - 20, y0 - 38), (CX, y0 - 38), (CX, y0 - 20), (CX - 20, y0 - 20)]), GOLD_HI, blur=3)
    p.line(pts, LW * 1.1, GOLD_LN, closed=True)
    p.fill(Rell(CX, y0 - 12, 5, 5), RUBY, line=GOLD_LN, lw=0.8)
    p.fill(Rell(CX - 20, y0 - 9, 3.5, 3.5), SAPPHIRE, line=GOLD_LN, lw=0.8)
    p.fill(Rell(CX + 20, y0 - 9, 3.5, 3.5), SAPPHIRE, line=GOLD_LN, lw=0.8)
    for x, y in [(CX - 34, y0 - 34), (CX, y0 - 42), (CX + 34, y0 - 34)]:
        p.fill(Rell(x, y, 3.5, 3.5), GOLD_HI, line=GOLD_LN, lw=0.8)
    return p


# =================================================================== body
ARM_SH, ARM_EL, ARM_WR = (CX - 78, 600), (CX - 112, 690), (CX - 110, 770)


def body():
    out = []
    for side, f in SIDES:                                           # back legs (folded frog legs + big feet)
        p = Part(f'腿_{side}')
        thigh = [(CX - 60, 760), (CX - 108, 770), (CX - 146, 820), (CX - 150, 880), (CX - 128, 930), (CX - 96, 950),
                 (CX - 70, 930), (CX - 52, 870)]
        p.fill(f(R(thigh)), GRN)
        p.air(f(R([(CX - 150, 860), (CX - 100, 860), (CX - 100, 950), (CX - 150, 950)])), GRN_SH, blur=8)
        p.air(f(R([(CX - 130, 790), (CX - 100, 790), (CX - 100, 830), (CX - 130, 830)])), GRN_HI, blur=8)
        p.line(f(R(thigh)), LW * 1.1, GRN_LN, closed=True)
        out.append(p)
    for side, f in SIDES:
        p = Part(f'腳_{side}')
        foot = [(CX - 70, 930), (CX - 110, 942), (CX - 150, 968), (CX - 172, 990), (CX - 168, 1004), (CX - 140, 1002),
                (CX - 118, 1006), (CX - 94, 1002), (CX - 70, 1005), (CX - 50, 996), (CX - 48, 960)]
        p.fill(f(R(foot)), GRN)
        p.air(f(R([(CX - 175, 985), (CX - 45, 985), (CX - 45, 1008), (CX - 175, 1008)])), GRN_SH, blur=5)
        for tx in (CX - 160, CX - 118, CX - 72):                                          # toe pads
            p.fill(f(Rell(tx, 1000, 8, 6)), GRN_HI, line=GRN_LN, lw=0.8)
        p.line(f(R(foot)), LW * 1.1, GRN_LN, closed=True)
        out.append(p)

    p = Part('胸腔')
    torso = sym([(CX, 540), (CX - 60, 546), (CX - 88, 580), (CX - 100, 650), (CX - 104, 730), (CX - 96, 800),
                 (CX - 70, 860), (CX - 36, 890), (CX, 896)])
    p.fill(R(torso), GRN)
    p.air(R([(CX - 110, 560), (CX - 70, 560), (CX - 70, 890), (CX - 110, 890)]), GRN_SH, blur=10)
    p.air(M(R([(CX - 110, 560), (CX - 70, 560), (CX - 70, 890), (CX - 110, 890)])), GRN_SH, blur=10)
    p.line(R(torso), LW * 1.2, GRN_LN, closed=True)
    out.append(p)

    p = Part('肚皮')
    belly = sym([(CX, 600), (CX - 44, 606), (CX - 66, 650), (CX - 72, 730), (CX - 62, 810), (CX - 36, 860),
                 (CX, 872)])
    p.fill(R(belly), BELLY)
    p.air(R([(CX - 72, 800), (CX + 72, 800), (CX + 72, 875), (CX - 72, 875)]), BELLY_SH, blur=10)
    for y in (660, 710, 760, 810):                                                        # belly lines
        w = 58 - abs(y - 730) * 0.25
        p.line(R([(CX - w, y), (CX, y + 6), (CX + w, y)]), 0.9, BELLY_SH, clipped=True)
    p.line(R(belly), LW * 0.9, BELLY_LN, closed=True)
    out.append(p)

    p = Part('披風領')
    cape = sym([(CX, 560), (CX - 40, 548), (CX - 84, 556), (CX - 100, 580), (CX - 78, 606), (CX - 40, 598),
                (CX, 612)])
    p.fill(R(cape), CAPE)
    p.air(R([(CX - 100, 590), (CX + 100, 590), (CX + 100, 612), (CX - 100, 612)]), CAPE_SH, blur=5)
    p.line(R(cape), LW, CAPE_LN, closed=True)
    p.fill(Rell(CX, 594, 9, 9), GOLD, line=GOLD_LN, lw=0.9)
    p.fill(Rell(CX, 594, 4, 4), RUBY, raw=True)
    out.append(p)

    for side, f in SIDES:                                           # arms: shoulder -> elbow -> wrist
        p = Part(f'上臂_{side}')
        up = [(CX - 66, 586), (CX - 94, 590), (CX - 126, 686), (CX - 98, 700), (CX - 76, 620)]
        p.fill(f(R(up)), GRN)
        p.air(f(R([(CX - 130, 640), (CX - 110, 640), (CX - 110, 700), (CX - 130, 700)])), GRN_SH, blur=6)
        p.line(f(R(up)), LW * 1.1, GRN_LN, closed=True)
        out.append(p)
    for side, f in SIDES:
        p = Part(f'下臂_{side}')
        low = [(CX - 126, 676), (CX - 98, 690), (CX - 96, 770), (CX - 124, 772)]
        p.fill(f(R(low)), GRN)
        p.air(f(R([(CX - 128, 700), (CX - 114, 700), (CX - 114, 772), (CX - 128, 772)])), GRN_SH, blur=5)
        p.line(f(R([(CX - 126, 676), (CX - 124, 772)])), LW * 1.1, GRN_LN)
        p.line(f(R([(CX - 98, 690), (CX - 96, 770)])), LW * 1.1, GRN_LN)
        out.append(p)
    for side, f in SIDES:
        p = Part(f'手掌_{side}')
        p.fill(f(Rell(CX - 110, 776, 18, 14)), GRN, line=GRN_LN, lw=LW)
        for dx, dy in [(-16, 12), (0, 18), (16, 12)]:                                     # 3 webbed fingers
            p.fill(f(Rell(CX - 110 + dx, 776 + dy, 7, 7)), GRN_HI, line=GRN_LN, lw=0.9)
        out.append(p)
    return out


def build():
    G = []
    p = Part('影子')
    p.soft(Rell(CX, 1004, 150, 14), hx('5d6b5d', 150), 10)
    G.append(('背景', [p]))
    G.append(('身體', body()))
    h = [head(), cheeks(), nostrils(), ('嘴', mouth_parts())]
    h.append(('眼_R', eye('R')))
    h.append(('眼_L', eye('L')))
    h.append(crown())
    G.append(('頭', h))
    return VF.add(G, eyes={'R': (CX - EYE_DX, EYE_Y + 6, 62, 14), 'L': (CX + EYE_DX, EYE_Y + 6, 62, 14)},
                  mouth=(CX, MOUTH_Y, 78), eye_lw=4.2, mouth_lw=2.2)


def landmarks():
    return {}


def body_landmarks():
    return {}


RIG = dict(
    neck=(CX, 548), waist=(CX, 720),
    eyes={'R': (CX - EYE_DX, EYE_Y), 'L': (CX + EYE_DX, EYE_Y)},
    lower_lid_dy=22, blink_drop=30, mouth_y=MOUTH_Y,
    mouth_open=[('口腔', 'transform.s.y', 2.6), ('口腔', 'transform.s.x', 1.15), ('舌頭', 'transform.s.y', 1.8),
                ('舌頭', 'transform.t.y', 4.0)],
    head3d=dict(center=HEAD_C, radii=(130, 120, 90), layers={
        '王冠': (1, 30), '眼窩': (1, 10), '眼白': (1, 14), '眼球': (1, 16), '高光': (1, 17), '上眼線': (1, 15),
        '上唇': (1, 12), '口腔': (1, 11), '舌頭': (1, 11), '鼻子': (1, 14), '腮紅': (1, 8), '臉': (1, 2)}),
    head_groups=('頭',),
    hair_deform=[],
    arm_parts={'R': ['上臂_R', '下臂_R', '手掌_R'], 'L': ['上臂_L', '下臂_L', '手掌_L']},
    arm_pivots=(ARM_SH, ARM_EL, ARM_WR), arm_warp=None,
    breath_scale=['胸腔', '肚皮'], breath_lift=['披風領', '上臂_R', '上臂_L'],
    extras=[],
    lifts=[{'param': 'Leg:: Right:: Step', 'parts': ['腿_R', '腳_R'], 'dy': -18},
           {'param': 'Leg:: Left:: Step', 'parts': ['腿_L', '腳_L'], 'dy': -18}],
)
VF.rig(RIG)          # VTuber blink (smiling ^) + D-shaped talking mouth (卡洛兒 v2 style)
