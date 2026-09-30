# -*- coding: utf-8 -*-
"""小紅帽 (Little Red Riding Hood) — Live2D-ready character.

Built on girl_v4 (same face construction, proportions, arms and legs, all checked by the
anime-girl-face / anime-girl-body rules): we take girl_v4's parts, recolour hair / eyes / skirt /
socks in HSV, drop the sailor-uniform parts, and add the costume: hood (back + front rim),
capelet, neck bow, braids, white collar, laced bodice, apron and a basket in her right hand.

Coordinates: reference px of girl_v4 (R() maps them to the 1000 x 1667 design space).
"""
import colorsys, math
import numpy as np

import girl_v4 as G4
from girl import Part, hx, M, smooth, ellipse, arc
from girl_v4 import R, RP, Rell, CX, SIDES, ID, K, LW

# ------------------------------------------------------------------ palette
RED, RED_SH, RED_DK, RED_HI, RED_LN = hx('cf3040'), hx('9e1f2e'), hx('6a1420'), hx('ef6d74'), hx('571018')
HAIR, HAIR_SH, HAIR_HI, HAIR_LN = hx('9a623f'), hx('734629'), hx('d9a47a'), hx('45271a')
BODICE, BODICE_SH, BODICE_LN = hx('3e2c35'), hx('2a1d24'), hx('150d12')
LACE = hx('efe6d6')
APRON, APRON_SH, APRON_LN = hx('fbfaf6'), hx('e3dfd6'), hx('9d968b')
BASKET, BASKET_SH, BASKET_HI, BASKET_LN = hx('b98552'), hx('8a5d34'), hx('dcae7c'), hx('4f3219')
CLOTH_A, CLOTH_B = hx('d8404b'), hx('fbf6ef')


# ------------------------------------------------------------------ recolouring helpers
def _is_col(v):
    return isinstance(v, tuple) and len(v) == 4 and all(isinstance(c, (int, np.integer)) for c in v)


def recolor(part, fn):
    part.ops = [tuple(fn(v) if _is_col(v) else v for v in op) for op in part.ops]


def drop_ops(part, pred):
    part.ops = [op for op in part.ops if not any(_is_col(v) and pred(v) for v in op)]


def hsv(c):
    return colorsys.rgb_to_hsv(c[0] / 255, c[1] / 255, c[2] / 255)


def from_hsv(h, s, v, a):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, max(0, min(1, s)), max(0, min(1, v)))
    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)), a)


def to_chestnut(c):
    """lavender hair -> chestnut brown (keeps the light/dark structure, adds warmth to highlights)."""
    h, s, v = hsv(c)
    if s < 0.02 and v > 0.97:
        return c
    s2 = 0.33 + 0.58 * s
    v2 = 0.62 * v ** 3 + 0.33 * (1 - s) ** 4 * v
    return from_hsv(0.075, s2, v2, c[3])


def to_amber(c):
    """teal iris -> warm amber brown."""
    h, s, v = hsv(c)
    if s < 0.05:
        return c
    return from_hsv(0.085, min(1, s * 1.05), v * (0.92 if v < 0.5 else 0.97), c[3])


def to_skirt_blue(c):
    """navy skirt -> muted cornflower blue."""
    h, s, v = hsv(c)
    return from_hsv(0.60, s * 0.8, min(1, v * 1.35 + 0.05), c[3])


def to_cream(c):
    """dark stockings -> cream white stockings (skin tones untouched)."""
    h, s, v = hsv(c)
    if v > 0.55:
        return c
    return from_hsv(0.09, 0.06 + 0.05 * (1 - v), 0.78 + 0.4 * v, c[3])


def mirror_list(pts):
    """mirror a right-half outline (keeps 'c' corner flags), reversed so it continues the outline."""
    return [(2 * CX - p[0],) + tuple(p[1:]) for p in reversed(pts)]


# ------------------------------------------------------------------ new parts (reference px)
def hood_back():
    p = Part('兜帽_後')
    shape = [(CX, 50), (243, 55), (208, 76), (190, 114), (183, 165), (184, 222), (188, 268), (181, 300),
             (205, 312), (CX, 316)]
    pts = R(shape + mirror_list(shape[:-1]))
    p.fill(pts, RED_DK)
    p.air(R([(200, 60), (371, 60), (371, 130), (200, 130)]), hx('8a1c29', 200), blur=18)     # lining catches light at the top
    p.air(R([(190, 240), (381, 240), (381, 320), (190, 320)]), hx('4a0e16', 200), blur=14)   # deeper inside
    p.line(pts, LW, RED_LN, closed=True)
    return p


def back_hair_short():
    p = Part('後髮_短')
    shape = [(CX, 70), (238, 78), (212, 100), (199, 140), (196, 200), (199, 250), (206, 290), (228, 300),
             (CX, 302)]
    pts = R(shape + mirror_list(shape[:-1]))
    p.fill(pts, HAIR_SH)
    p.air(R([(205, 200), (366, 200), (366, 305), (205, 305)]), hx('5a3620', 200), blur=12)
    rng = np.random.default_rng(5)
    for i in range(16):
        x0 = 204 + i * 10 + rng.normal(0, 2)
        p.strand(R([(x0 + (CX - x0) * 0.2, 90), (x0, 180), (x0 + rng.normal(0, 2), 290)]), 1.4, hx('5e3822', 150))
    p.line(pts, LW, HAIR_LN, closed=True)
    return p


def hood_rim():
    """Front edge of the hood framing the face: a thick red band over the crown and down both sides."""
    p = Part('兜帽_前')
    outer = [(181, 300), (188, 262), (185, 215), (186, 160), (193, 112), (212, 76), (245, 55), (CX, 49)]
    inner = [(CX, 67), (250, 72), (222, 92), (206, 125), (201, 170), (202, 218), (205, 262), (199, 302)]
    right = outer + inner
    band_R = R(right)
    band_L = M(R(right))
    # join both halves into one ribbon (outer R -> top -> outer L, then inner L -> inner R)
    full = R(outer) + M(R(outer))[::-1] + M(R(inner))[::-1] + R(inner)
    p.fill(full, RED, raw=True)
    p.air(R([(200, 48), (371, 48), (371, 80), (200, 80)]), RED_HI, blur=10)          # light on the crown
    p.air(R([(176, 200), (200, 200), (200, 305), (176, 305)]), RED_SH, blur=10)
    p.air(M(R([(176, 200), (200, 200), (200, 305), (176, 305)])), RED_SH, blur=10)
    p.line(smooth(R(outer), closed=False) + smooth(M(R(outer))[::-1], closed=False), LW, RED_LN, raw=True)
    p.line(smooth(M(R(inner))[::-1], closed=False) + smooth(R(inner), closed=False), LW, RED_LN, raw=True)
    return p


def braid(side):
    """Chunky three-strand braid hanging from under the hood in front of the capelet."""
    f = ID if side == 'R' else M
    p = Part(f'麻花辮_{side}')
    path = [(224, 236), (221, 272), (221, 306), (224, 340), (229, 372), (234, 398)]
    c = np.array(smooth(path, closed=False, n=12))
    lobes = 9
    for i in range(lobes):
        t = (i + 0.5) / lobes
        k = int(t * (len(c) - 1))
        x, y = c[k]
        w = 11.5 - 3.5 * t
        off = (1 if i % 2 else -1) * 2.2
        lobe = [(x + off - w, y - 6), (x + off, y - 12), (x + off + w, y - 4), (x + off + w * 0.6, y + 9),
                (x + off - w * 0.3, y + 11), (x + off - w, y + 3)]
        q = f(R(lobe))
        p.fill(q, HAIR)
        p.cfill(f(R([(x - 20, y + 2), (x + 20, y + 2), (x + 20, y + 14), (x - 20, y + 14)])), HAIR_SH, blur=2)
        p.strand(f(R([(x + off - w * 0.6, y - 5), (x + off, y - 1), (x + off + w * 0.5, y + 5)])), 1.3, HAIR_HI)
        p.line(q, LW * 0.9, HAIR_LN, closed=True)
    # ribbon tie + tuft
    tuft = [(226, 398), (242, 398), (246, 416), (240, 432, 'c'), (235, 420), (230, 434, 'c'), (225, 418)]
    p.fill(f(R(tuft)), HAIR, line=HAIR_LN, lw=LW * 0.9)
    p.cfill(f(R([(222, 415), (250, 415), (250, 440), (222, 440)])), HAIR_SH, blur=2)
    bow = [(234, 392), (224, 386), (222, 398), (234, 400), (246, 398), (245, 386)]
    p.fill(f(R(bow)), RED, line=RED_LN, lw=LW * 0.9)
    return p


def capelet(side):
    f = ID if side == 'R' else M
    p = Part(f'斗篷_{side}')
    shape = [(CX, 302), (266, 300), (244, 302), (214, 306), (190, 316), (176, 338), (170, 380), (168, 425),
             (170, 466, 'c'), (192, 480), (218, 484), (240, 478), (252, 468, 'c'), (256, 440), (264, 398),
             (274, 356), (281, 324)]
    pts = f(R(shape))
    p.fill(pts, RED)
    p.air(f(R([(190, 300), (262, 300), (262, 330), (190, 330)])), RED_HI, blur=10)            # shoulder top
    p.air(f(R([(160, 330), (192, 330), (192, 490), (160, 490)])), RED_SH, blur=10)            # outer side
    p.air(f(R([(200, 455), (262, 455), (262, 492), (200, 492)])), RED_SH, blur=6)             # toward the hem
    p.air(f(R([(214, 360), (226, 360), (222, 478), (210, 478)])), hx('b12838', 150), blur=7)  # soft fold (no line)
    p.line(pts, LW, RED_LN, closed=True)
    return p


def neck_bow():
    p = Part('斗篷結')
    loop_R = [(CX - 2, 303), (272, 293), (260, 292), (256, 302), (262, 312), (274, 311)]
    tail_R = [(CX - 3, 309), (277, 322), (271, 342, 'c'), (279, 336), (284, 344, 'c'), (CX, 314)]
    for g in (ID, M):
        p.fill(g(R(tail_R)), RED, line=RED_LN, lw=LW * 0.9)
        p.fill(g(R(loop_R)), RED)
        p.cfill(g(R([(254, 304), (CX, 304), (CX, 314), (254, 314)])), RED_SH, blur=2)
        p.line(g(R(loop_R)), LW * 0.9, RED_LN, closed=True)
    knot = [(CX - 5, 298), (CX + 5, 298), (CX + 6, 306), (CX + 5, 313), (CX - 5, 313), (CX - 6, 306)]
    p.fill(R(knot), RED, line=RED_LN, lw=LW * 0.9)
    p.air(R([(CX - 4, 298), (CX + 2, 298), (CX + 2, 304), (CX - 4, 304)]), RED_HI, blur=2)
    return p


def blouse_collar():
    p = Part('襯衫領')
    for g in (ID, M):
        q = g(R([(CX, 300), (268, 298), (258, 292), (254, 299), (259, 308), (272, 311), (CX, 309)]))
        p.fill(q, APRON)
        p.air(g(R([(252, 305), (CX, 305), (CX, 313), (252, 313)])), APRON_SH, blur=3)
        p.line(q, LW * 0.9, APRON_LN, closed=True)
    return p


def bodice():
    p = Part('馬甲')
    G4.WARP = G4.shoulder_warp
    try:
        shape = [(CX, 392), (262, 386), (242, 392), (226, 402), (222, 430), (226, 462), (228, 476),
                 (CX, 478)]
        pts = R(shape + mirror_list(shape[:-1]))
        p.fill(pts, BODICE)
        p.air(R([(214, 390), (238, 390), (238, 480), (214, 480)]), BODICE_SH, blur=6)
        p.air(M(R([(214, 390), (238, 390), (238, 480), (214, 480)])), BODICE_SH, blur=6)
        p.air(R([(262, 400), (309, 400), (309, 420), (262, 420)]), hx('5a4450', 150), blur=6)
        # lacing: criss-cross cord through small eyelets
        ys = np.linspace(398, 468, 6)
        for i in range(len(ys) - 1):
            p.line(R([(CX - 6, ys[i]), (CX + 6, ys[i + 1])]), 2.0, LACE, clipped=True)
            p.line(R([(CX + 6, ys[i]), (CX - 6, ys[i + 1])]), 2.0, LACE, clipped=True)
        for y in ys:
            for x in (CX - 7, CX + 7):
                p.fill(Rell(x, y, 1.6, 1.6), hx('c9b98f'), raw=True)
        p.line(pts, LW, BODICE_LN, closed=True)
    finally:
        G4.WARP = None
    return p


def apron():
    p = Part('圍裙')
    shape = [(CX, 478), (256, 479), (248, 520), (242, 565, 'c'), (246, 594), (262, 601), (CX, 602)]
    pts = R(shape + mirror_list(shape[:-1]))
    p.fill(pts, APRON)
    p.air(R([(240, 478), (331, 478), (331, 492), (240, 492)]), APRON_SH, blur=4)
    p.air(R([(236, 490), (256, 490), (252, 600), (236, 600)]), APRON_SH, blur=6)
    p.air(M(R([(236, 490), (256, 490), (252, 600), (236, 600)])), APRON_SH, blur=6)
    p.line(R([(246, 585), (266, 591), (CX, 593), (305, 591), (325, 585)]), 1.1, hx('d6d0c5'), clipped=True)
    p.line(pts, LW, APRON_LN, closed=True)
    return p


def basket():
    """Wicker basket hanging from the right hand (handle passes behind the fingers)."""
    p = Part('籃子')
    hx0, hy0 = 176.0, 590.0                         # where the hand grips the handle
    body = [(138, 626), (214, 626), (208, 668), (196, 684), (156, 684), (144, 668)]
    rim = [(134, 622), (218, 622), (218, 632), (134, 632)]
    # handle
    handle = R([(142, 628), (147, 606), (160, 592), (hx0, 589), (192, 592), (205, 606), (210, 628)])
    p.rib(handle, [5.5 * K] * 7, BASKET_LN, hardness=0.7, flow=0.8)
    p.rib(handle, [3.4 * K] * 7, BASKET, hardness=0.8, flow=0.9)
    # checkered cloth peeking out
    cloth = [(146, 624), (160, 610), (178, 616), (196, 606), (208, 622), (178, 628)]
    p.fill(R(cloth), CLOTH_B)
    for i in range(5):
        x = 150 + i * 12
        p.cfill(R([(x, 604), (x + 6, 604), (x + 6, 630), (x, 630)]), CLOTH_A, blur=0.3)
    p.line(R(cloth), LW * 0.8, hx('7d2a2f'), closed=True)
    # body with a weave pattern
    p.fill(R(body), BASKET)
    for y in np.arange(634, 684, 7):
        p.line(R([(140, y), (176, y + 1.5), (212, y)]), 1.0, BASKET_SH, clipped=True)
    for x in np.arange(146, 210, 9):
        p.line(R([(x, 630), (x + (176 - x) * 0.12, 684)]), 0.8, BASKET_HI, clipped=True)
    p.air(R([(190, 626), (216, 626), (206, 686), (186, 686)]), BASKET_SH, blur=6)
    p.line(R(body), LW, BASKET_LN, closed=True)
    p.fill(R(rim), BASKET, line=BASKET_LN, lw=LW)
    p.air(R([(134, 621), (218, 621), (218, 625), (134, 625)]), BASKET_HI, blur=2)
    return p


# ------------------------------------------------------------------ assemble
DROP = {'背景色', '後髮_R', '後髮_L', '後髮內層_R', '後髮內層_L', '鬢角_R', '鬢角_L', '呆毛', '髮飾',
        '領子_後', '領子_R', '領子_L', '領巾_R', '領巾_L', '領巾尾_R', '領巾尾_L', '領巾結', '耳朵_R', '耳朵_L'}
HAIRLIKE = ('瀏海', '碎髮', '眉毛')


def build():
    groups = G4.build()
    by = {}

    def walk(items, fn):
        out = []
        for it in items:
            if isinstance(it, tuple):
                out.append((it[0], walk(it[1], fn)))
            elif it.name not in DROP:
                fn(it)
                out.append(it)
        return out

    def fix(p):
        by[p.name] = p
        if p.name.startswith(HAIRLIKE):
            recolor(p, to_chestnut)
        elif p.name.startswith('眼球'):
            recolor(p, to_amber)
        elif p.name.startswith('裙') or p.name == '腰':
            drop_ops(p, lambda c: c[:3] == G4.STRIPE[:3])
            recolor(p, to_skirt_blue if p.name != '腰' else (lambda c: BODICE if c[:3] == G4.NAVY[:3] else c))
        elif p.name.startswith(('小腿', '大腿')):
            recolor(p, to_cream)
        elif p.name == '胸腔':
            drop_ops(p, lambda c: c[:3] == G4.NAVY[:3])          # sailor dickey lines
        elif p.name.startswith('上臂'):
            recolor(p, lambda c: G4.WHITE if c[:3] in (G4.NAVY[:3],) else c)
            drop_ops(p, lambda c: c[:3] == G4.STRIPE[:3])

    new = []
    for name, items in groups:
        if name == '背景':
            new.append((name, walk(items, fix)))
        elif name == '後髮':
            new.append((name, [hood_back(), back_hair_short()]))
        elif name == '身體':
            body = walk(items, fix)
            out = []
            for p in body:
                if p.name == '手掌_R':
                    out.append(basket())                      # above the skirt, below the hand
                out.append(p)
                if p.name == '腰':
                    pass
                if p.name == '裙_中':
                    out.append(apron())
                if p.name == '胸_L':
                    out.append(bodice())
                    out.append(blouse_collar())
            # capelet over the torso and the upper arms, bow on top
            i_forearm = next(i for i, p in enumerate(out) if p.name == '下臂_R')
            out[i_forearm:i_forearm] = [capelet('R'), capelet('L'), neck_bow()]
            new.append((name, out))
        elif name == '頭':
            head = walk(items, fix)
            # hood rim over the bangs; braids come out from under it
            head.append(braid('R'))
            head.append(braid('L'))
            head.append(hood_rim())
            new.append((name, head))
        else:
            new.append((name, walk(items, fix)))
    return new


landmarks = G4.landmarks
body_landmarks = G4.body_landmarks


# ------------------------------------------------------------------ rig (live2d/engine/rig.py)
RIG = dict(
    neck=(CX, 262), waist=(CX, G4.WAIST_Y),
    eyes={'R': (G4.EYE_CX_R, G4.EYE_Y), 'L': (G4.EYE_CX_L, G4.EYE_Y)}, lower_lid_dy=15, blink_drop=24,
    mouth_y=G4.MOUTH_Y,
    mouth_open=[('口腔', 'transform.s.y', 3.0), ('口腔', 'transform.s.x', 1.45), ('舌頭', 'transform.s.y', 2.2),
                ('舌頭', 'transform.t.y', 1.4), ('下排牙齒', 'transform.t.y', 2.6), ('下唇陰影', 'transform.t.y', 2.2)],   # wider & shallower (s.y 6 read as a box dropping below the lips)
    head3d=dict(center=(CX, 160), radii=(66, 108, 62), layers={
        '瀏海': (1, 14), '碎髮': (1, 12), '髮陰影': (1, 1), '眉毛': (1, 3), '鼻子': (1, 5), '高光': (1, 1.5),
        '眼': (1, 1), '上': (1, 1), '下': (1, 1), '口腔': (1, 1), '舌頭': (1, 1), '腮紅': (1, 0.5),
        '兜帽_前': (1, 8), '麻花辮': (1, 6), '兜帽_後': (-1, 6), '後髮': (-1, 2)}),
    hair_deform=['麻花辮_R', '麻花辮_L', '碎髮'],
    arm_parts={'R': ['上臂_R', '下臂_R', '手掌_R', '手指_R', '籃子'], 'L': ['上臂_L', '下臂_L', '手掌_L', '手指_L']},
    arm_pivots=((205, 318), (193, 472), (176, 556)), arm_warp=G4.shoulder_warp,
    breath_scale=['胸腔', '胸_R', '胸_L', '馬甲'],
    breath_lift=['斗篷_R', '斗篷_L', '斗篷結', '襯衫領', '上臂_R', '上臂_L'],
    extras=[{'param': 'Basket:: Swing', 'parts': ['籃子'], 'pivot': (176, 589), 'angle': 0.18, 'ramp': None}],
    lifts=[{'param': 'Leg:: Right:: Step', 'parts': ['大腿_R', '小腿_R', '鞋_R'], 'dy': -14},
           {'param': 'Leg:: Left:: Step', 'parts': ['大腿_L', '小腿_L', '鞋_L'], 'dy': -14}],
)
