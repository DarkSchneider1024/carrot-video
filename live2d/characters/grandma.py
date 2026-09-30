# -*- coding: utf-8 -*-
"""外婆 (《半夜三點的牛肉麵》): sits in bed scrolling her phone, blanket over her lap.

Built on girl_v4's face construction (anime-girl-face rules), aged: grey hair swept back from a side parting into a
bob with a bun, soft wrinkles (smile lines, crow's feet, under-eye), round gold reading glasses, cream blouse
under a mauve knit cardigan. Her lower body is under a quilted blanket that is part of the puppet (so she always
"sits in bed" correctly); both hands hold a phone just above the blanket.
"""
import colorsys, copy
import numpy as np

import girl_v4 as G4
import red_hood as RH
from girl import Part, hx, M, smooth
from girl_v4 import R, Rell, CX, K, LW, SIDES, ID

HAIR, HAIR_SH, HAIR_HI, HAIR_LN = hx('d9d7df'), hx('aeabb8'), hx('f6f5fa'), hx('6f6b7c')
CARD, CARD_SH, CARD_HI, CARD_LN = hx('9c6f8e'), hx('744f69'), hx('c095b3'), hx('3f2638')
BLOUSE, BLOUSE_SH = hx('f5efe3'), hx('dcd2c0')
GOLD = hx('c9a24a')
QUILT, QUILT_SH, QUILT_HI, QUILT_LN = hx('f1e3c6'), hx('d4bf98'), hx('fff6e4'), hx('8a744f')
PHONE, SCREEN = hx('2a2c33'), hx('bfe3ff')


def to_grey(c):
    h, s, v = colorsys.rgb_to_hsv(c[0] / 255, c[1] / 255, c[2] / 255)
    v2 = 0.55 + 0.42 * v
    r, g, b = colorsys.hsv_to_rgb(0.72, 0.06, min(1, v2))
    return (int(r * 255), int(g * 255), int(b * 255), c[3])


def cmap(table):
    t = {k[:3]: v for k, v in table.items()}
    return lambda c: (t[c[:3]][:3] + (c[3],)) if c[:3] in t else c


BLOUSE_FROM_WHITE = cmap({G4.WHITE: BLOUSE, G4.WHITE_SH: BLOUSE_SH, G4.WHITE_LN: hx('9d927c'),
                          hx('c7cbe3'): hx('e7ddcb'), hx('cfd2e8'): hx('ece3d2'), hx('c9cde4'): hx('e3d8c4'),
                          hx('d0d4e8'): hx('e2d7c3'), hx('d8dcec'): hx('ebe2d1'), hx('c3c7db'): hx('b9ad96')})
CARD_FROM_SLEEVE = cmap({G4.WHITE: CARD, G4.WHITE_SH: CARD_SH, G4.WHITE_LN: CARD_LN})


def back_hair():
    p = Part('後髮_短')
    shape = [(CX, 64), (240, 70), (206, 96), (196, 140), (194, 190), (198, 232), (212, 252), (240, 258), (CX, 258)]
    pts = R(shape + RH.mirror_list(shape[:-1]))
    p.fill(pts, HAIR_SH)
    p.air(R([(190, 180), (381, 180), (381, 262), (190, 262)]), hx('8f8b9a', 200), blur=12)
    p.line(pts, LW, HAIR_LN, closed=True)
    return p


def bun():
    p = Part('髮髻')
    pts = Rell(CX + 6, 62, 30, 24)
    p.fill(pts, HAIR, raw=True)
    for a in np.linspace(0.3, 2.8, 5):
        p.strand(R([(CX + 6 - 26 * np.cos(a), 62 - 18 * np.sin(a)), (CX + 6, 50), (CX + 6 + 26 * np.cos(a + 0.4), 62 + 10)]), 1.2, HAIR_SH)
    p.air(R([(CX - 20, 40), (CX + 30, 40), (CX + 30, 56), (CX - 20, 56)]), HAIR_HI, blur=5)
    p.line(pts, LW, HAIR_LN, closed=True, raw=True)
    p.fill(R([(CX + 30, 58), (CX + 44, 52), (CX + 46, 60), (CX + 32, 64)]), hx('7b5b3a'), line=hx('3c2a1a'), lw=0.8)  # hairpin
    return p


def front_hair():
    """swept back from a side parting (her left), forehead visible, bob down to the jaw at the sides"""
    p = Part('前髮')
    right = [(302, 76), (272, 78), (240, 88), (214, 108), (201, 140), (196, 182), (200, 222), (212, 246, 'c'),
             (222, 226), (219, 190), (221, 152), (234, 132), (256, 120), (286, 116), (306, 113)]
    left = [(306, 113), (326, 117), (344, 126), (356, 146), (357, 182), (352, 222), (360, 246, 'c'),
            (372, 222), (376, 180), (370, 138), (354, 104), (330, 82)]
    pts = R(right + left)
    p.fill(pts, HAIR)
    p.air(R([(200, 70), (380, 70), (380, 100), (200, 100)]), HAIR_HI, blur=10)
    p.air(R([(190, 170), (226, 170), (226, 250), (190, 250)]), HAIR_SH, blur=8)
    p.air(M(R([(190, 170), (226, 170), (226, 250), (190, 250)])), HAIR_SH, blur=8)
    rng = np.random.default_rng(4)
    for i in range(14):                                      # strands sweeping back from the parting
        x0 = 300 - i * 7 + rng.normal(0, 1.5)
        p.strand(R([(306, 108), (x0 - 14, 92 + i * 0.6), (x0 - 40, 104 + i * 3), (x0 - 60, 150 + i * 4)]), 1.1,
                 HAIR_SH if i % 2 else HAIR_HI)
    for i in range(8):
        x0 = 312 + i * 7
        p.strand(R([(306, 108), (x0 + 12, 94), (x0 + 30, 110 + i * 3), (x0 + 38, 150 + i * 5)]), 1.1,
                 HAIR_SH if i % 2 else HAIR_HI)
    p.line(pts, LW, HAIR_LN, closed=True)
    p.line(R([(306, 113), (304, 94), (302, 76)]), 1.0, HAIR_LN)                      # the parting
    return p


def wrinkles():
    p = Part('皺紋')
    c = hx('c79386', 190)
    for g in (ID, M):
        p.line(g(R([(248, 219), (250, 229), (255, 238)])), 0.9, c)          # smile line
        p.line(g(R([(229, 196), (236, 200), (244, 200)])), 0.8, c)          # under the eye
        for dy in (-3, 2):                                                    # crow's feet
            p.line(g(R([(211, 184 + dy), (205, 182 + dy * 1.6)])), 0.7, c)
    p.line(R([(274, 124), (285.5, 122), (297, 124)]), 0.8, hx('d9a89a', 170))    # forehead line
    return p


def reading_glasses():
    p = Part('老花眼鏡')
    for g, cx in ((ID, G4.EYE_CX_R), (M, G4.EYE_CX_R)):
        rim = Rell(cx, G4.EYE_Y + 2, 23, 19)
        p.fill(g(rim), hx('ffffff', 30), raw=True)
        p.line(g(rim), 1.6, GOLD, closed=True, raw=True)
        p.air(g(R([(cx - 16, G4.EYE_Y - 12), (cx - 6, G4.EYE_Y - 12), (cx - 12, G4.EYE_Y + 6), (cx - 18, G4.EYE_Y + 6)])),
              hx('ffffff', 90), blur=2)
        p.line(g(R([(cx - 23, G4.EYE_Y - 2), (cx - 34, G4.EYE_Y - 4)])), 1.5, GOLD)            # temple
    p.line(R([(G4.EYE_CX_R + 23, G4.EYE_Y - 2), (CX, G4.EYE_Y - 6), (2 * CX - G4.EYE_CX_R - 23, G4.EYE_Y - 2)]), 1.5, GOLD)
    for g in (ID, M):                                                           # chain
        p.line(g(R([(G4.EYE_CX_R - 34, G4.EYE_Y - 4), (G4.EYE_CX_R - 40, G4.EYE_Y + 40), (G4.EYE_CX_R - 30, 262)])), 0.8, GOLD)
    return p


def cardigan(side):
    f = ID if side == 'R' else M
    p = Part(f'開襟衫_{side}')

    def draw():
        pts = f(R([(262, 286), (240, 292), (213, 301), (205, 318), (208, 350), (213, 385), (220, 420), (226, 450),
                   (228, 474), (268, 474), (266, 430), (262, 380), (262, 330), (270, 296)]))
        p.fill(pts, CARD)
        p.air(f(R([(198, 300), (226, 300), (230, 476), (206, 476)])), CARD_SH, blur=8)
        p.air(f(R([(236, 300), (266, 300), (262, 340), (236, 340)])), CARD_HI, blur=8)
        for y in np.arange(310, 470, 7):                                      # knit ribs
            p.line(f(R([(214, y), (240, y + 1.5), (262, y)])), 0.7, CARD_SH, clipped=True)
        for y in (360, 410, 455):
            p.fill(Rell(263 if side == 'R' else 2 * CX - 263, y, 3.2, 3.2), hx('e8d9b8'), raw=True)
        p.line(pts, LW, CARD_LN, closed=True)
    G4.WARP = G4.shoulder_warp
    try:
        draw()
    finally:
        G4.WARP = None
    return p


def blanket():
    p = Part('棉被')
    top = [(120, 452), (180, 444), (240, 450), (CX, 446), (330, 450), (390, 444), (452, 452)]
    pts = R(top + [(470, 640), (100, 640)])
    p.fill(pts, QUILT)
    for x in np.arange(130, 460, 42):                                          # quilting
        p.line(R([(x, 452), (x + 6, 640)]), 1.0, QUILT_SH, clipped=True)
    for y in (500, 560):
        p.line(R([(100, y), (470, y + 4)]), 1.0, QUILT_SH, clipped=True)
    p.air(R([(100, 446), (470, 446), (470, 470), (100, 470)]), QUILT_HI, blur=8)
    p.air(R([(100, 600), (470, 600), (470, 640), (100, 640)]), QUILT_SH, blur=12)
    p.line(smooth(R(top), closed=False), LW, QUILT_LN, raw=True)
    return p


def phone_hands():
    p = Part('手機')
    ph = [(268, 392), (304, 388), (308, 446), (272, 450)]
    p.fill(R(ph), PHONE)
    p.cfill(R([(272, 396), (301, 393), (304, 440), (275, 443)]), SCREEN, blur=0.3)
    for i, y in enumerate((402, 412, 422)):                                    # chat bubbles on the screen
        x0 = 276 if i % 2 == 0 else 286
        p.cfill(R([(x0, y), (x0 + 14, y - 0.5), (x0 + 14, y + 6), (x0, y + 6.5)]), hx('f3c6b2') if i % 2 == 0 else hx('ffffff'), blur=0.3)
    p.line(R(ph), LW * 0.8, hx('111216'), closed=True)
    for g, (hx0, hy0) in ((ID, (270, 442)), (ID, (308, 438))):          # one hand on each side of the phone
        hand = [(hx0 - 12, hy0 - 6), (hx0 + 4, hy0 - 12), (hx0 + 10, hy0 + 2), (hx0 + 6, hy0 + 14), (hx0 - 10, hy0 + 14)]
        p.fill(R(hand), G4.SKIN, line=G4.SKIN_LN, lw=LW * 0.9)
        p.cfill(R([(hx0 - 14, hy0 + 6), (hx0 + 12, hy0 + 6), (hx0 + 12, hy0 + 16), (hx0 - 14, hy0 + 16)]), G4.SKIN_SH, blur=2)
        cuff = [(hx0 - 16, hy0 + 8), (hx0 + 10, hy0 + 8), (hx0 + 12, hy0 + 20), (hx0 - 18, hy0 + 20)]
        p.fill(R(cuff), CARD, line=CARD_LN, lw=LW * 0.8)
    return p


DROP = {'背景色', '影子', '後髮_R', '後髮_L', '後髮內層_R', '後髮內層_L', '呆毛', '髮飾', '瀏海_R', '瀏海_L', '瀏海_中',
        '碎髮', '鬢角_R', '鬢角_L', '髮陰影_R', '髮陰影_中', '髮陰影_L', '領子_後', '領子_R', '領子_L', '領巾_R', '領巾_L',
        '領巾尾_R', '領巾尾_L', '領巾結', '小腿_R', '小腿_L', '鞋_R', '鞋_L', '大腿_R', '大腿_L', '裙_後', '裙_R', '裙_L',
        '裙_中', '腰', '下臂_R', '下臂_L', '手掌_R', '手掌_L', '手指_R', '手指_L'}


def build():
    groups = G4.build()

    def fix(p):
        if p.name in ('胸腔', '胸_R', '胸_L'):
            RH.drop_ops(p, lambda c: c[:3] == G4.NAVY[:3])
            RH.recolor(p, BLOUSE_FROM_WHITE)
        elif p.name.startswith('上臂'):
            RH.drop_ops(p, lambda c: c[:3] in (G4.NAVY[:3], G4.STRIPE[:3]))
            RH.recolor(p, CARD_FROM_SLEEVE)
            RH.recolor(p, lambda c: CARD[:3] + (c[3],) if c[:3] == G4.SKIN[:3] else
                       (CARD_SH[:3] + (c[3],) if c[:3] == G4.SKIN_SH[:3] else (CARD_LN[:3] + (c[3],) if c[:3] == G4.SKIN_LN[:3] else c)))
        elif p.name.startswith('眉毛'):
            RH.recolor(p, to_grey)
        elif p.name.startswith('眼球'):
            RH.recolor(p, RH.to_amber)                    # warm brown eyes (teal read too young)

    def walk(items):
        out = []
        for it in items:
            if isinstance(it, tuple):
                out.append((it[0], walk(it[1])))
            elif it.name not in DROP:
                fix(it)
                out.append(it)
        return out

    new = []
    for name, items in groups:
        if name == '背景':
            continue
        items = walk(items)
        if name == '後髮':
            items = [bun(), back_hair()]
        elif name == '身體':
            items = items + [cardigan('R'), cardigan('L'), blanket(), phone_hands()]
        elif name == '頭':
            items = items + [wrinkles(), front_hair(), reading_glasses()]
        new.append((name, items))
    return new


landmarks, body_landmarks = G4.landmarks, G4.body_landmarks

RIG = dict(
    neck=(CX, 262), waist=(CX, G4.WAIST_Y),
    eyes={'R': (G4.EYE_CX_R, G4.EYE_Y), 'L': (G4.EYE_CX_L, G4.EYE_Y)}, lower_lid_dy=15, blink_drop=24,
    mouth_y=G4.MOUTH_Y,
    mouth_open=[('口腔', 'transform.s.y', 3.0), ('口腔', 'transform.s.x', 1.45), ('舌頭', 'transform.s.y', 2.2),
                ('舌頭', 'transform.t.y', 1.4), ('下排牙齒', 'transform.t.y', 2.6), ('下唇陰影', 'transform.t.y', 2.2)],   # wider & shallower (s.y 6 read as a box dropping below the lips)
    head3d=dict(center=(CX, 160), radii=(66, 108, 62), layers={
        '前髮': (1, 10), '眉毛': (1, 3), '鼻子': (1, 5), '高光': (1, 1.5), '眼': (1, 1), '上': (1, 1), '下': (1, 1),
        '口腔': (1, 1), '舌頭': (1, 1), '腮紅': (1, 0.5), '皺紋': (1, 0.5), '老花眼鏡': (1, 9), '耳朵': (1, -4),
        '後髮': (-1, 2), '髮髻': (-1, 6)}),
    hair_deform=[],
    breath_scale=['胸腔', '開襟衫_R', '開襟衫_L'],
    breath_lift=['手機', '上臂_R', '上臂_L'],
)
