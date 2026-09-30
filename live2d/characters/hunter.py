# -*- coding: utf-8 -*-
"""獵人 (the Huntsman) — Live2D-ready front view for the classic 小紅帽.

Same reference-pixel grid and skeleton as wolf.py (shoulder 300, waist 470, crotch 610, knee 760, ankle 925,
sole 1003) so the rig / stage treat him like the wolf. A sturdy, kind-looking man: green Tyrolean hat with a
red feather, chestnut hair and full beard, rosy nose, cream shirt under an open loden-green hunting jacket,
leather belt with a pouch, brown trousers, tall boots, a rifle slung across his back (barrel over his right
shoulder, stock behind his left hip) with the strap across his chest.
"""
import numpy as np

from girl import Part, hx, M, smooth
from girl_v4 import R, Rell, CX, SIDES, ID, K, LW

SKIN, SKIN_SH, SKIN_HI, SKIN_LN = hx('f4cda9'), hx('dca47f'), hx('fde6cf'), hx('8f5b3e')
NOSE_RED = hx('e79a86')
HAIR, HAIR_SH, HAIR_HI, HAIR_LN = hx('8b5230'), hx('643619'), hx('b8784a'), hx('361c0c')
JACK, JACK_SH, JACK_HI, JACK_LN = hx('55703d'), hx('3c522a'), hx('7c9a5d'), hx('1d2a12')
SHIRT, SHIRT_SH, SHIRT_LN = hx('f1e6cf'), hx('d6c6a6'), hx('8a7a5c')
CHECK = hx('c9463f', 110)
PANTS, PANTS_SH, PANTS_LN = hx('7a5a3c'), hx('5a4029'), hx('2c1d10')
BOOT, BOOT_SH, BOOT_HI, BOOT_LN = hx('3e2b1f'), hx('2a1c13'), hx('6a4c38'), hx('120b06')
LEATHER, LEATHER_LN = hx('6b4527'), hx('2a180a')
BRASS = hx('d4b060')
HAT, HAT_SH, HAT_HI, HAT_LN = hx('4b6636'), hx('354a25'), hx('6f8c55'), hx('18220e')
FEATHER, FEATHER_SH = hx('d5423a'), hx('8e1f1c')
WOOD, WOOD_SH, WOOD_LN = hx('8a5a32'), hx('5e3a1c'), hx('2e1a0a')
STEEL, STEEL_HI, STEEL_LN = hx('4a4e57'), hx('8d939e'), hx('1a1c21')
EYE_W, IRIS, PUPIL = hx('fbf8f2'), hx('6b4a2e'), hx('23160c')
MOUTH, TONGUE = hx('6a2a2a'), hx('d9747a')

EYE_Y, EYE_DX, MOUTH_Y = 186, 33, 246


def mirror_list(pts):
    return [(2 * CX - p[0],) + tuple(p[1:]) for p in reversed(pts)]


def sym(right):
    return right + mirror_list(right[1:-1])


# =================================================================== head
def ears():
    out = []
    for side, f in SIDES:
        p = Part(f'耳朵_{side}')
        ear = [(210, 170), (198, 164), (192, 176), (194, 196), (202, 212), (212, 214)]
        p.fill(f(R(ear)), SKIN)
        p.cfill(f(R([(196, 172), (206, 172), (206, 206), (198, 206)])), SKIN_SH, blur=2)
        p.line(f(R(ear)), LW, SKIN_LN, closed=True)
        out.append(p)
    return out


def back_hair():
    p = Part('後髮')
    pts = R(sym([(CX, 92), (244, 96), (212, 112), (198, 140), (196, 176), (200, 200), (226, 206), (CX, 206)]))
    p.fill(pts, HAIR_SH)
    p.line(pts, LW, HAIR_LN, closed=True)
    return p


def face():
    p = Part('臉')
    pts = R(sym([(CX, 100), (250, 103), (222, 116), (207, 142), (203, 176), (205, 208), (211, 234), (224, 256),
                 (244, 272), (264, 281), (CX, 284)]))
    p.fill(pts, SKIN)
    p.air(R([(200, 100), (371, 100), (371, 128), (200, 128)]), SKIN_SH, blur=8)          # shade under the hat
    p.air(R([(198, 150), (218, 150), (218, 250), (198, 250)]), SKIN_SH, blur=8)
    p.air(M(R([(198, 150), (218, 150), (218, 250), (198, 250)])), SKIN_SH, blur=8)
    p.air(R([(230, 140), (260, 140), (260, 160), (230, 160)]), SKIN_HI, blur=8)
    p.line(pts, LW, SKIN_LN, closed=True)
    return p


def cheeks():
    p = Part('腮紅')
    for g in (ID, M):
        p.soft(g(Rell(236, 212, 15, 8)), hx('ef9a8a', 130), 6)
    return p


def beard():
    p = Part('鬍子')
    right = [(CX, 252), (270, 250), (252, 241), (236, 226), (220, 204), (211, 176), (204, 176), (202, 206),
             (207, 238), (219, 268), (238, 292), (262, 306), (CX, 311)]
    pts = R(sym(right))
    p.fill(pts, HAIR)
    p.air(R([(200, 270), (371, 270), (371, 312), (200, 312)]), HAIR_SH, blur=8)
    p.air(R([(250, 256), (321, 256), (321, 272), (250, 272)]), HAIR_SH, blur=5)          # under the lip
    rng = np.random.default_rng(11)
    for i in range(22):                                                                  # curly strands
        x = 212 + i * 7 + rng.normal(0, 2)
        y = 240 + abs(x - CX) * -0.2 + 40
        p.strand(R([(x, y - 18), (x + rng.normal(0, 3), y), (x + rng.normal(0, 3), y + 16)]), 1.2,
                 HAIR_HI if i % 3 == 0 else HAIR_SH)
    for g in (ID, M):                                                                    # sideburn texture
        p.strand(g(R([(207, 184), (206, 210), (211, 236)])), 1.2, HAIR_SH)
    p.line(pts, LW, HAIR_LN, closed=True)
    return p


def mouth_parts():
    my = MOUTH_Y
    out = []
    p = Part('口腔')
    p.fill(R([(CX - 12, my - 2), (CX, my + 1), (CX + 12, my - 2), (CX + 10, my), (CX, my + 2.5), (CX - 10, my)]),
           MOUTH)
    out.append(p)
    p = Part('舌頭')
    p.fill(R([(CX - 6, my), (CX, my - 0.5), (CX + 6, my), (CX + 3, my + 1.5), (CX - 3, my + 1.5)]), TONGUE)
    out.append(p)
    p = Part('下排牙齒')
    p.fill(R([(CX - 7, my + 0.5), (CX + 7, my + 0.5), (CX + 6, my + 1.5), (CX - 6, my + 1.5)]), hx('f4f1e8'), raw=True)
    out.append(p)
    p = Part('上排牙齒')
    p.fill(R([(CX - 9, my - 2), (CX + 9, my - 2), (CX + 8, my - 0.5), (CX - 8, my - 0.5)]), hx('fbf9f2'), raw=True)
    out.append(p)
    p = Part('下唇')
    p.rib(R([(CX - 7, my + 5), (CX, my + 6.5), (CX + 7, my + 5)]), [0.6 * K, 1.3 * K, 0.6 * K], hx('9c5a4a'),
          hardness=0.6, flow=0.5)
    out.append(p)
    return out


def mustache():
    p = Part('八字鬍')
    right = [(CX, 232), (272, 229), (258, 232), (246, 240), (238, 252, 'c'), (250, 248), (264, 244), (276, 242),
             (CX, 244)]
    pts = R(sym(right))
    p.fill(pts, HAIR)
    p.air(R([(236, 240), (335, 240), (335, 254), (236, 254)]), HAIR_SH, blur=4)
    for g in (ID, M):
        for k in range(4):
            p.strand(g(R([(282 - k * 8, 233), (272 - k * 9, 238), (262 - k * 8, 246)])), 1.0, HAIR_HI if k % 2 else HAIR_SH)
    p.line(pts, LW, HAIR_LN, closed=True)
    return p


def nose():
    p = Part('鼻子')
    nx, ny = CX, 214
    pts = [(nx - 12, ny + 4), (nx - 9, ny - 8), (nx - 4, ny - 26), (nx + 4, ny - 26), (nx + 9, ny - 8), (nx + 12, ny + 4),
           (nx + 6, ny + 11), (nx - 6, ny + 11)]
    p.fill(R(pts), SKIN)
    p.cfill(R([(nx - 11, ny - 6), (nx + 11, ny - 6), (nx + 13, ny + 12), (nx - 13, ny + 12)]), NOSE_RED, blur=5)
    p.air(R([(nx - 5, ny - 22), (nx + 1, ny - 22), (nx + 1, ny - 2), (nx - 5, ny - 2)]), SKIN_HI, blur=3)
    p.fill(Rell(nx - 5, ny + 7, 2.4, 1.6), hx('8a4a3a'), raw=True)
    p.fill(Rell(nx + 5, ny + 7, 2.4, 1.6), hx('8a4a3a'), raw=True)
    p.line(R([(nx - 12, ny + 4), (nx - 6, ny + 11), (nx + 6, ny + 11), (nx + 12, ny + 4)]), 1.1, SKIN_LN)
    p.line(R([(nx + 4, ny - 26), (nx + 9, ny - 8), (nx + 12, ny + 4)]), 0.9, SKIN_LN)
    return p


def eye(side):
    f = 1 if side == 'R' else -1
    cx = CX - f * EYE_DX
    cy = EYE_Y

    def E(pts):
        return R([(cx - f * q[0], cy + q[1]) + tuple(q[2:]) for q in pts])

    parts = []
    p = Part(f'下眼皮_{side}')
    p.fill(E([(-14, 3), (-5, 8), (7, 8), (13, 2), (14, 11), (0, 15), (-15, 11)]), SKIN)
    parts.append(p)
    p = Part(f'眼白_{side}')
    p.fill(E([(-13, 1), (-7, -6), (2, -8), (11, -5), (13, 1), (6, 6), (-5, 6)]), EYE_W)
    p.cfill(E([(-18, -12), (18, -12), (18, -3), (-18, -4)]), hx('e2d6c6'), blur=2)
    parts.append(p)
    p = Part(f'眼球_{side}')
    p.fill(Rell(cx + f * 1.0, cy - 0.5, 6.4, 7.0), IRIS, raw=True)
    p.air(Rell(cx + f * 1.0, cy - 4.5, 7, 3.5), hx('3d2714'), blur=1.5, raw=True)
    p.fill(Rell(cx + f * 1.0, cy - 0.3, 3.2, 3.6), PUPIL, raw=True)
    parts.append(p)
    p = Part(f'上眼線_{side}')
    p.rib(E([(-15, 1), (-9, -6), (0, -9), (9, -7), (14, -2)]), [1.6 * K, 2.8 * K, 3.0 * K, 2.6 * K, 1.0 * K],
          hx('2a1a12'), hardness=0.65, flow=0.55)
    parts.append(p)
    p = Part(f'上眼皮_{side}')
    p.fill(E([(-16, 1), (-9, -7), (0, -11), (10, -8), (16, -2), (18, -14), (0, -21), (-18, -12)]), SKIN)
    parts.append(p)
    p = Part(f'高光_{side}')
    p.fill(Rell(cx - f * 2.0, cy - 3.5, 1.9, 2.1), hx('ffffff'), raw=True)
    parts.append(p)
    return parts


def brows():
    out = []
    for side, f in SIDES:
        p = Part(f'眉毛_{side}')
        p.rib(f(R([(236, 166), (248, 161), (262, 160), (272, 164)])), [1.5 * K, 4.6 * K, 4.4 * K, 2.2 * K], HAIR_LN,
              hardness=0.6, flow=0.55)
        out.append(p)
    return out


def front_hair():
    """short locks peeking out under the hat brim at the temples"""
    p = Part('前髮')
    for g in (ID, M):
        lock = [(204, 112), (230, 110), (224, 124), (214, 142), (210, 168, 'c'), (205, 150), (202, 128)]
        p.fill(g(R(lock)), HAIR)
        p.strand(g(R([(222, 114), (213, 132), (209, 160)])), 1.2, HAIR_HI)
        p.line(g(R(lock)), LW, HAIR_LN, closed=True)
    return p


def hat():
    p = Part('帽子')
    crown = [(236, 104), (240, 70), (252, 46), (272, 38, 'c'), (285, 46), (300, 38, 'c'), (320, 46), (332, 70),
             (336, 104)]
    p.fill(R(crown), HAT)
    p.air(R([(236, 40), (270, 40), (266, 104), (236, 104)]), HAT_HI, blur=8)
    p.air(R([(312, 40), (340, 40), (340, 104), (312, 104)]), HAT_SH, blur=8)
    p.line(R(crown), LW, HAT_LN, closed=True)
    band = [(237, 90), (335, 90), (336, 104), (236, 104)]
    p.fill(R(band), LEATHER, line=LEATHER_LN, lw=LW * 0.9)
    brim = [(186, 110), (206, 98), (240, 96), (CX, 97), (331, 96), (365, 98), (385, 110), (360, 118), (CX, 114),
            (211, 118)]
    p.fill(R(brim), HAT)
    p.air(R([(186, 108), (385, 108), (385, 120), (186, 120)]), HAT_SH, blur=4)
    p.line(R(brim), LW, HAT_LN, closed=True)
    return p


def feather():
    p = Part('羽毛')
    stem = R([(328, 98), (346, 70), (366, 44), (378, 30)])
    vane = [(330, 96), (338, 72), (352, 50), (376, 28, 'c'), (370, 52), (356, 74), (340, 94)]
    p.fill(R(vane), FEATHER)
    p.air(R([(350, 60), (380, 60), (380, 100), (350, 100)]), FEATHER_SH, blur=6)
    p.line(stem, 1.0, FEATHER_SH)
    p.line(R(vane), LW * 0.9, hx('5c1210'), closed=True)
    return p


# =================================================================== body
ARM_O = [(192, 312), (183, 360), (175, 410), (168, 460), (162, 500), (156, 540), (152, 566)]
ARM_I = [(228, 316), (220, 360), (211, 410), (202, 460), (194, 500), (188, 540), (186, 566)]


def rifle():
    """slung across the back: barrel up over his right shoulder, stock out behind his left hip"""
    p = Part('獵槍')
    a = np.array([178.0, 190.0])            # muzzle
    b = np.array([418.0, 700.0])            # butt
    d = (b - a) / np.linalg.norm(b - a)
    n = np.array([-d[1], d[0]])
    pt = lambda t, w: tuple(a + d * t + n * w)
    L = np.linalg.norm(b - a)
    barrel = [pt(0, -3.2), pt(0, 3.2), pt(L * 0.62, 4.2), pt(L * 0.62, -4.2)]
    p.fill(R(barrel), STEEL, line=STEEL_LN, lw=LW * 0.8)
    p.line(R([pt(4, -1.2), pt(L * 0.6, -1.6)]), 1.0, STEEL_HI)
    stock = [pt(L * 0.55, -6), pt(L * 0.55, 7), pt(L * 0.8, 9), pt(L * 0.86, 16), pt(L, 18), pt(L, -12),
             pt(L * 0.86, -8), pt(L * 0.8, -7)]
    p.fill(R(stock), WOOD)
    p.air(R([pt(L * 0.7, 6), pt(L, 6), pt(L, 20), pt(L * 0.7, 20)]), WOOD_SH, blur=4)
    p.line(R(stock), LW * 0.9, WOOD_LN, closed=True)
    p.fill(R([pt(L - 2, -12), pt(L, -12), pt(L, 18), pt(L - 2, 18)]), hx('2a1a0e'))              # butt plate
    return p


def build():
    G = []
    p = Part('影子')
    p.soft(Rell(CX, 1003, 110, 13), hx('7d6b6b', 150), 10)
    G.append(('背景', [p]))
    G.append(('尾', [rifle()]))

    body = []
    for side, f in SIDES:
        p = Part(f'腿_{side}')
        leg = f(R([(224, 600), (284, 600), (283, 700), (280, 800), (276, 860), (234, 862), (230, 800), (226, 700)]))
        p.fill(leg, PANTS)
        p.cfill(f(R([(266, 600), (292, 600), (290, 865), (262, 865)])), PANTS_SH, blur=4)
        p.line(f(R([(262, 612), (258, 760)])), 0.9, PANTS_SH)                                  # crease
        p.line(leg, LW, PANTS_LN, closed=True)
        body.append(p)
    for side, f in SIDES:
        p = Part(f'腳_{side}')
        boot = f(R([(230, 830), (280, 830), (282, 900), (286, 960), (292, 986), (290, 1004), (224, 1004), (220, 990),
                    (226, 950), (228, 900)]))
        p.fill(boot, BOOT)
        p.cfill(f(R([(268, 830), (296, 830), (296, 1006), (270, 1006)])), BOOT_SH, blur=4)
        p.air(f(R([(234, 840), (246, 840), (246, 960), (234, 960)])), BOOT_HI, blur=4)
        cuff = f(R([(226, 826), (284, 826), (286, 850), (224, 850)]))                              # folded top
        p.fill(cuff, BOOT_HI, line=BOOT_LN, lw=LW * 0.9)
        p.fill(f(R([(218, 996), (294, 996), (294, 1006), (218, 1006)])), hx('1c120b'))          # sole
        p.line(boot, LW, BOOT_LN, closed=True)
        body.append(p)

    p = Part('脖子')
    neck = R([(262, 262), (309, 262), (312, 304), (259, 304)])
    p.fill(neck, SKIN)
    p.air(R([(255, 262), (316, 262), (316, 290), (255, 290)]), SKIN_SH, blur=6)
    body.append(p)

    p = Part('胸腔')
    torso = sym([(CX, 290), (250, 292), (212, 300), (192, 318), (194, 360), (204, 410), (212, 450), (218, 490),
                 (220, 540), (224, 606), (CX, 610)])
    p.fill(R(torso), SHIRT)
    for x in np.arange(212, 362, 16):                                                            # faint checks
        p.line(R([(x, 290), (x, 610)]), 1.4, CHECK, clipped=True)
    for y in np.arange(300, 610, 16):
        p.line(R([(190, y), (381, y)]), 1.4, CHECK, clipped=True)
    p.air(R([(250, 300), (321, 300), (321, 330), (250, 330)]), SHIRT_SH, blur=8)
    p.line(R([(CX, 312), (CX, 606)]), 1.0, SHIRT_LN)                                              # placket
    for y in (340, 380, 420):
        p.fill(Rell(CX + 5, y, 2.4, 2.4), hx('b9a98a'), raw=True)
    p.line(R(torso), LW, SHIRT_LN, closed=True)
    body.append(p)

    def arm_piece(side, y0, y1, name):
        f = ID if side == 'R' else M
        o = [q for q in ARM_O if y0 <= q[1] <= y1]
        i = [q for q in ARM_I if y0 <= q[1] <= y1]
        p = Part(f'{name}_{side}')
        poly = f(R(o + i[::-1]))
        p.fill(poly, JACK)
        p.cfill(f(R([(206, 300), (232, 300), (200, 580), (180, 580)])), JACK_SH, blur=4)
        if name == '下臂':
            p.cfill(f(R([(150, 538), (192, 538), (190, 570), (148, 570)])), JACK_SH, blur=0.5)     # cuff
            p.line(f(R([(155, 540), (190, 541)])), 1.0, JACK_LN)
        p.line(f(R(o)), LW, JACK_LN)
        p.line(f(R(i)), LW, JACK_LN)
        return p

    for side in ('R', 'L'):
        body.append(arm_piece(side, 300, 480, '上臂'))
    for side in ('R', 'L'):
        body.append(arm_piece(side, 450, 570, '下臂'))
    for side, f in SIDES:
        p = Part(f'手掌_{side}')
        hand = f(R([(152, 560), (188, 562), (198, 580), (196, 604), (182, 614), (158, 612), (146, 598), (147, 574)]))
        p.fill(hand, SKIN)
        p.cfill(f(R([(182, 560), (204, 560), (200, 616), (180, 616)])), SKIN_SH, blur=3)
        p.line(hand, LW, SKIN_LN, closed=True)
        body.append(p)
    for side, f in SIDES:
        p = Part(f'手指_{side}')
        for (x, y, l) in [(152, 604, 11), (161, 608, 13), (170, 609, 13), (179, 607, 12), (187, 602, 10)]:
            c = f(R([(x, y), (x - 0.4, y + l * 0.6), (x + 0.3, y + l)]))
            p.rib(c, [6.2 * K, 6.0 * K, 5.0 * K], SKIN_LN, hardness=0.7, flow=0.8)
            p.rib(c, [4.8 * K, 4.6 * K, 3.7 * K], SKIN, hardness=0.8, flow=0.9)
        body.append(p)

    for side, f in SIDES:
        p = Part(f'外套_{side}')
        jac = f(R([(260, 292), (236, 293), (206, 304), (195, 324), (198, 380), (204, 440), (209, 500), (211, 560),
                   (205, 640), (240, 648), (268, 646), (270, 600), (266, 540), (258, 470), (254, 400), (254, 350),
                   (262, 318)]))
        p.fill(jac, JACK)
        p.air(f(R([(190, 300), (240, 300), (240, 340), (190, 340)])), JACK_HI, blur=8)
        p.air(f(R([(190, 440), (222, 440), (222, 650), (190, 650)])), JACK_SH, blur=8)
        lapel = [(262, 318), (254, 350), (254, 392), (240, 360), (236, 320), (248, 300)]              # lapel
        p.fill(f(R(lapel)), JACK_SH, line=JACK_LN, lw=LW * 0.8)
        pocket = [(216, 590), (258, 590), (260, 628), (218, 630)]
        p.fill(f(R(pocket)), JACK_SH, line=JACK_LN, lw=LW * 0.8)
        flap = [(214, 584), (260, 584), (258, 600), (237, 606), (216, 600)]
        p.fill(f(R(flap)), JACK, line=JACK_LN, lw=LW * 0.8)
        for y in (420, 470):
            p.fill(Rell(250 if side == 'R' else 2 * CX - 250, y, 3.4, 3.4), hx('3a2a1a'), raw=True)
        p.line(jac, LW, JACK_LN, closed=True)
        body.append(p)

    p = Part('領子')
    for g in (ID, M):
        q = g(R([(CX, 300), (266, 292), (252, 294), (254, 310), (268, 318), (CX, 312)]))
        p.fill(q, SHIRT, line=SHIRT_LN, lw=LW * 0.9)
    body.append(p)

    p = Part('腰帶')
    belt = R([(210, 548), (361, 548), (363, 570), (208, 570)])
    p.fill(belt, LEATHER, line=LEATHER_LN, lw=LW)
    p.fill(R([(CX - 11, 545), (CX + 11, 545), (CX + 11, 573), (CX - 11, 573)]), BRASS, line=hx('6a5020'), lw=1.0)
    p.fill(R([(CX - 6, 551), (CX + 6, 551), (CX + 6, 567), (CX - 6, 567)]), LEATHER)
    pouch = [(318, 566), (350, 566), (352, 602), (334, 610), (316, 602)]
    p.fill(R(pouch), LEATHER, line=LEATHER_LN, lw=LW * 0.9)
    p.line(R([(318, 578), (334, 584), (350, 578)]), 1.0, LEATHER_LN)
    body.append(p)

    p = Part('背帶')
    strap = R([(206, 300), (222, 296), (362, 560), (348, 566)])
    p.fill(strap, LEATHER, line=LEATHER_LN, lw=LW * 0.9)
    p.fill(R([(270, 408), (284, 402), (290, 414), (276, 420)]), BRASS, line=hx('6a5020'), lw=0.8)
    body.append(p)
    G.append(('身體', body))

    head = []
    head += ears()
    head.append(back_hair())
    head.append(face())
    head.append(cheeks())
    head.append(beard())
    head.append(('嘴', mouth_parts()))
    head.append(mustache())
    head.append(nose())
    head.append(('眼_R', eye('R')))
    head.append(('眼_L', eye('L')))
    head += brows()
    head.append(front_hair())
    head.append(hat())
    head.append(feather())
    G.append(('頭', head))
    return G


def landmarks():
    return {}


def body_landmarks():
    return {}


RIG = dict(
    neck=(CX, 265), waist=(CX, 470),
    eyes={'R': (CX - EYE_DX, EYE_Y), 'L': (CX + EYE_DX, EYE_Y)},
    lower_lid_dy=6, blink_drop=13, mouth_y=MOUTH_Y,
    mouth_open=[('口腔', 'transform.s.y', 4.5), ('口腔', 'transform.s.x', 1.1), ('舌頭', 'transform.s.y', 2.6),
                ('舌頭', 'transform.t.y', 3.0), ('下排牙齒', 'transform.t.y', 6.0), ('下唇', 'transform.t.y', 5.0)],
    head3d=dict(center=(CX, 190), radii=(72, 100, 62), layers={
        '鼻子': (1, 14), '八字鬍': (1, 10), '口腔': (1, 7), '舌頭': (1, 7), '上排牙齒': (1, 7), '下排牙齒': (1, 7),
        '下唇': (1, 7), '鬍子': (1, 4), '腮紅': (1, 1), '眼': (1, 2), '上': (1, 2), '下': (1, 2), '高光': (1, 2.5),
        '眉毛': (1, 4), '前髮': (1, 3), '帽子': (1, 10), '羽毛': (1, 12), '耳朵': (1, -4), '後髮': (-1, 2)}),
    head_groups=('頭',),
    hair_deform=[],
    arm_parts={'R': ['上臂_R', '下臂_R', '手掌_R', '手指_R'], 'L': ['上臂_L', '下臂_L', '手掌_L', '手指_L']},
    arm_pivots=((210, 316), (186, 470), (169, 562)), arm_warp=None,
    breath_scale=['胸腔'], breath_lift=['外套_R', '外套_L', '領子', '背帶', '上臂_R', '上臂_L'],
    extras=[],
    lifts=[{'param': 'Leg:: Right:: Step', 'parts': ['腿_R', '腳_R'], 'dy': -14},
           {'param': 'Leg:: Left:: Step', 'parts': ['腿_L', '腳_L'], 'dy': -14}],
)
