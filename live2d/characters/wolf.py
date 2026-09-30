# -*- coding: utf-8 -*-
"""大野狼 (the Big Bad Wolf) — Live2D-ready anthropomorphic wolf, front view.

Drawn on the same reference-pixel grid as girl_v4 / red_hood (R() -> 1000 x 1667 design space), so the
same rig tooling works. Split like a Live2D character: eyes (white / iris / lids / lashes / highlight),
mouth (cavity / tongue / teeth / lips) under the muzzle, ears, cheek fur, arms (upper / fore / paw /
claws), legs, vest, trousers, tail.
"""
import math
import numpy as np

from girl import Part, hx, M, smooth, ellipse, arc
from girl_v4 import R, RP, Rell, CX, SIDES, ID, K, LW

FUR, FUR_SH, FUR_DK, FUR_HI, FUR_LN = hx('8a93a3'), hx('6a7384'), hx('4d5565'), hx('b5bdca'), hx('2b3039')
LIGHT, LIGHT_SH = hx('e8e6e0'), hx('c7c4bd')
NOSE = hx('24262c')
EYE_Y_, EYE_W_ = hx('f2c53d'), hx('fff6d6')
VEST, VEST_SH, VEST_HI, VEST_LN = hx('8a5a36'), hx('653f23'), hx('b07b52'), hx('3a2312')
PANTS, PANTS_SH, PANTS_LN = hx('5f5b48'), hx('45412f'), hx('24221a')
PATCH = hx('8f7a55')
MOUTH, TONGUE = hx('5a1f28'), hx('d86a78')

WOLF = dict(
    head_c=(CX, 176), ear_tip=(214, 58),
    eye_y=190, eye_dx=36, nose=(CX, 214), mouth_y=240,
    shoulder_y=300, waist_y=470, crotch_y=610, knee_y=760, ankle_y=925, sole_y=1003,
)


def mirror_list(pts):
    return [(2 * CX - p[0],) + tuple(p[1:]) for p in reversed(pts)]


def sym(right):
    """right half outline (top centre -> ... -> bottom centre) -> full closed outline."""
    return right + mirror_list(right[1:-1])


def fur_strands(p, pts_list, col, w=1.4):
    for pts in pts_list:
        p.strand(R(pts), w, col)


# =================================================================== head
def head_parts():
    parts = []
    # ears (behind the head)
    for side, f in SIDES:
        p = Part(f'耳朵_{side}')
        ear = [(236, 132), (222, 96), (214, 58, 'c'), (238, 82), (262, 112)]
        p.fill(f(R(ear)), FUR)
        p.cfill(f(R([(224, 120), (218, 70), (236, 90), (250, 118)])), hx('c79aa0'), blur=2)      # inner ear
        p.cfill(f(R([(205, 50), (245, 50), (245, 80), (205, 80)])), FUR_DK, blur=5)              # dark tip
        p.line(f(R(ear)), LW, FUR_LN, closed=True)
        parts.append(p)

    # head base with cheek fur flaring out
    p = Part('臉')
    head = sym([(CX, 110), (250, 114), (222, 130), (206, 158), (200, 188), (190, 206, 'c'), (204, 212),
                (194, 226, 'c'), (210, 232), (206, 246, 'c'), (226, 248), (246, 262), (CX, 270)])
    p.fill(R(head), FUR)
    p.air(R([(220, 112), (351, 112), (351, 150), (220, 150)]), FUR_HI, blur=12)                   # forehead light
    p.air(R([(190, 215), (240, 215), (240, 255), (190, 255)]), FUR_SH, blur=8)
    p.air(M(R([(190, 215), (240, 215), (240, 255), (190, 255)])), FUR_SH, blur=8)
    fur_strands(p, [[(262, 118), (258, 135), (256, 150)], [(309, 118), (313, 135), (315, 150)],
                    [(285, 112), (285, 128), (286, 140)]], FUR_DK, 1.3)
    p.line(R(head), LW, FUR_LN, closed=True)
    parts.append(p)

    # light fur on the cheeks + muzzle base
    p = Part('臉毛')
    cheeks = sym([(CX, 196), (262, 200), (238, 214), (222, 234), (240, 250), (262, 262), (CX, 268)])
    p.fill(R(cheeks), LIGHT)
    p.air(R([(220, 240), (351, 240), (351, 270), (220, 270)]), LIGHT_SH, blur=6)
    p.line(R(cheeks), LW * 0.8, hx('8f8d86'), closed=True)
    parts.append(p)

    # brows: heavy, angled down toward the nose (sly look)
    for side, f in SIDES:
        p = Part(f'眉毛_{side}')
        p.rib(f(R([(222, 168), (238, 170), (256, 176), (268, 182)])), [0.8 * K, 4.2 * K, 4.6 * K, 1.5 * K], FUR_LN,
              hardness=0.6, flow=0.5)
        parts.append(p)
    return parts


def wolf_eye(side):
    f = 1 if side == 'R' else -1
    cx = CX - f * WOLF['eye_dx']
    cy = WOLF['eye_y']

    def E(pts):
        return R([(cx - f * q[0], cy + q[1]) + tuple(q[2:]) for q in pts])     # +q[0] = toward the nose

    parts = []
    p = Part(f'下眼皮_{side}')
    p.fill(E([(-16, 3), (-6, 8), (8, 8), (15, 2), (16, 12), (0, 16), (-17, 12)]), FUR)
    parts.append(p)
    white = [(-17, 0), (-10, -8), (2, -11), (13, -6), (16, 2), (8, 7), (-6, 7)]
    p = Part(f'眼白_{side}')
    p.fill(E(white), EYE_W_)
    p.cfill(E([(-22, -14), (22, -14), (22, -3), (-22, -5)]), hx('d7c795'), blur=2)
    parts.append(p)
    p = Part(f'眼球_{side}')
    p.fill(Rell(cx + f * 1.5, cy - 0.5, 8.5, 9.5), EYE_Y_, raw=True)
    p.air(Rell(cx + f * 1.5, cy - 6, 10, 5), hx('c98a1f'), blur=2, raw=True)
    p.fill(Rell(cx + f * 1.5, cy - 0.5, 2.0, 7.5), hx('1c1408'), raw=True)                          # slit pupil
    p.line(Rell(cx + f * 1.5, cy - 0.5, 8.5, 9.5), 0.9, hx('6b4a10'), closed=True, raw=True)
    parts.append(p)
    p = Part(f'上眼線_{side}')
    p.rib(E([(-18, 1), (-11, -8), (0, -11.5), (10, -9), (17, -3)]), [2.0 * K, 3.4 * K, 3.8 * K, 3.2 * K, 1.2 * K],
          hx('1d1f25'), hardness=0.65, flow=0.55)
    parts.append(p)
    p = Part(f'上眼皮_{side}')
    p.fill(E([(-19, 1), (-11, -9), (0, -13), (11, -10), (18, -3), (20, -14), (0, -21), (-21, -12)]), FUR)
    parts.append(p)
    p = Part(f'高光_{side}')
    p.fill(Rell(cx - f * 2.5, cy - 4, 2.2, 2.4), hx('ffffff'), raw=True)
    parts.append(p)
    return parts


def mouth_parts():
    my = WOLF['mouth_y']
    out = []
    p = Part('口腔')                  # a dark sliver inside the lip line; Mouth:: Open scales it down
    p.fill(R([(CX - 20, my - 3), (CX, my + 1), (CX + 20, my - 3), (CX + 17, my - 1), (CX, my + 2.5), (CX - 17, my - 1)]),
           MOUTH)
    out.append(p)
    p = Part('舌頭')
    p.fill(R([(CX - 7, my), (CX, my - 0.5), (CX + 7, my), (CX + 4, my + 1.5), (CX - 4, my + 1.5)]), TONGUE)
    out.append(p)
    p = Part('下排牙齒')
    p.fill(R([(CX - 10, my + 0.5), (CX + 10, my + 0.5), (CX + 9, my + 1.5), (CX - 9, my + 1.5)]), hx('f4f1e8'), raw=True)
    out.append(p)
    p = Part('上排牙齒')              # includes one fang showing at the corner of the grin
    p.fill(R([(CX - 14, my - 2), (CX + 14, my - 2), (CX + 12, my - 0.5), (CX - 12, my - 0.5)]), hx('fbf9f2'), raw=True)
    fang = [(CX + 10, my - 2.5), (CX + 15, my - 2.5), (CX + 12.5, my + 6, 'c')]
    p.fill(R(fang), hx('fbf9f2'), line=hx('6a6a66'), lw=0.9)
    out.append(p)
    p = Part('上唇')                  # sly grin: corners pulled up and out
    p.rib(R([(CX - 24, my - 9), (CX - 14, my - 2.5), (CX, my + 0.5), (CX + 14, my - 2.5), (CX + 25, my - 10)]),
          [0.4 * K, 1.8 * K, 2.0 * K, 1.8 * K, 0.4 * K], FUR_LN, hardness=0.6, flow=0.55)
    p.rib(R([(CX, 224), (CX, my + 0.5)]), [1.5 * K, 1.2 * K], FUR_LN, hardness=0.6, flow=0.5)   # philtrum line
    out.append(p)
    return out


def nose_part():
    p = Part('鼻子')
    nx, ny = WOLF['nose']
    nose = [(nx - 13, ny - 6), (nx, ny - 9), (nx + 13, ny - 6), (nx + 8, ny + 5), (nx, ny + 9, 'c'), (nx - 8, ny + 5)]
    p.fill(R(nose), NOSE)
    p.air(R([(nx - 8, ny - 8), (nx + 2, ny - 8), (nx + 2, ny - 3), (nx - 8, ny - 3)]), hx('7a7f8c'), blur=2)
    # muzzle bridge line
    p.line(R([(nx - 15, 184), (nx - 13, 200)]), 1.0, FUR_SH)
    p.line(R([(nx + 15, 184), (nx + 13, 200)]), 1.0, FUR_SH)
    return p


def head_tuft():
    p = Part('頭毛')
    tuft = [(250, 116), (262, 96), (270, 110), (282, 88), (292, 108), (305, 92), (310, 112), (322, 114),
            (CX, 126)]
    p.fill(R(tuft), FUR, line=FUR_LN, lw=LW * 0.9)
    p.air(R([(250, 88), (322, 88), (322, 110), (250, 110)]), FUR_HI, blur=5)
    return p


# =================================================================== body
def build():
    G = []

    bg = []
    p = Part('影子')
    p.soft(Rell(CX, 1003, 105, 13), hx('7d6b6b', 150), 10)
    bg.append(p)
    G.append(('背景', bg))

    back = []
    p = Part('尾巴')
    tail = [(318, 560), (352, 548), (392, 566), (428, 606), (444, 652), (440, 700, 'c'), (420, 676),
            (402, 690, 'c'), (392, 660), (370, 640), (344, 612), (322, 596)]
    p.fill(R(tail), FUR)
    p.cfill(R([(400, 640), (460, 640), (460, 720), (400, 720)]), LIGHT, blur=6)                 # light tip
    p.air(R([(318, 560), (380, 560), (380, 620), (318, 620)]), FUR_SH, blur=8)
    fur_strands(p, [[(340, 566), (380, 590), (412, 630)], [(336, 590), (372, 612), (400, 650)]], FUR_DK, 1.3)
    p.line(R(tail), LW, FUR_LN, closed=True)
    back.append(p)
    G.append(('尾', back))

    body = []
    # legs in trousers + paws
    for side, f in SIDES:
        p = Part(f'腿_{side}')
        leg = f(R([(226, 600), (283, 600), (282, 700), (278, 800), (274, 900), (272, 930), (236, 932),
                   (232, 900), (228, 800), (226, 700)]))
        p.fill(leg, PANTS)
        p.cfill(f(R([(266, 600), (290, 600), (290, 935), (262, 935)])), PANTS_SH, blur=4)
        p.cfill(f(R([(236, 760), (262, 758), (264, 790), (238, 792)])), PATCH, blur=0.3)          # patch on the knee
        for x in (240, 248, 256):
            p.line(f(R([(x, 758), (x + 2, 791)])), 0.8, hx('5b4a30'), clipped=True)
        p.line(f(R([(236, 918), (254, 922), (272, 918)])), 1.0, PANTS_LN)                        # frayed hem
        p.line(leg, LW, PANTS_LN, closed=True)
        body.append(p)
    for side, f in SIDES:
        p = Part(f'腳_{side}')
        paw = f(R([(232, 922), (272, 922), (284, 960), (286, 994), (270, 1004), (234, 1004), (220, 992),
                   (222, 958)]))
        p.fill(paw, FUR)
        p.cfill(f(R([(210, 986), (296, 986), (296, 1010), (210, 1010)])), FUR_SH, blur=2)
        for x in (232, 247, 262, 276):
            p.fill(f(R([(x - 3, 1000), (x + 3, 1000), (x, 1010, 'c')])), hx('e9e4d8'), line=FUR_LN, lw=0.8)
        for x in (240, 255, 269):
            p.line(f(R([(x, 978), (x, 1000)])), 0.9, FUR_LN)
        p.line(paw, LW, FUR_LN, closed=True)
        body.append(p)

    # torso: fur, light chest fur, vest
    p = Part('脖子')
    neck = R([(262, 250), (309, 250), (312, 300), (259, 300)])
    p.fill(neck, FUR)
    p.air(R([(255, 250), (316, 250), (316, 280), (255, 280)]), FUR_DK, blur=6)
    body.append(p)

    p = Part('胸腔')
    torso = sym([(CX, 284), (250, 288), (212, 298), (192, 316), (194, 360), (204, 410), (214, 450), (220, 480),
                 (222, 520), (226, 606), (CX, 610)])
    p.fill(R(torso), FUR)
    chest = sym([(CX, 286), (258, 292), (242, 330), (244, 380), (256, 430), (270, 470), (CX, 482)])
    p.cfill(R(chest), LIGHT, blur=1.2)
    fur_strands(p, [[(262, 300), (258, 330), (262, 352)], [(309, 300), (313, 330), (309, 352)],
                    [(CX, 330), (285, 360), (286, 382)]], LIGHT_SH, 1.5)
    p.line(R(torso), LW, FUR_LN, closed=True)
    body.append(p)

    # arms: upper / fore / paw / claws (same field-deform rig as the girls)
    ARM_O = [(192, 312), (183, 360), (175, 410), (168, 460), (162, 500), (156, 540), (152, 566)]
    ARM_I = [(228, 316), (220, 360), (211, 410), (202, 460), (194, 500), (188, 540), (186, 566)]

    def arm_piece(side, y0, y1, name):
        f = ID if side == 'R' else M
        o = [q for q in ARM_O if y0 <= q[1] <= y1]
        i = [q for q in ARM_I if y0 <= q[1] <= y1]
        p = Part(f'{name}_{side}')
        poly = f(R(o + i[::-1]))
        p.fill(poly, FUR)
        p.cfill(f(R([(206, 300), (232, 300), (200, 580), (180, 580)])), FUR_SH, blur=4)
        p.line(f(R(o)), LW, FUR_LN)
        p.line(f(R(i)), LW, FUR_LN)
        return p

    for side in ('R', 'L'):
        body.append(arm_piece(side, 300, 480, '上臂'))
    for side in ('R', 'L'):
        body.append(arm_piece(side, 450, 570, '下臂'))
    for side, f in SIDES:
        p = Part(f'手掌_{side}')
        paw = f(R([(150, 558), (188, 560), (200, 580), (198, 608), (182, 620), (156, 618), (142, 600), (144, 574)]))
        p.fill(paw, FUR)
        p.cfill(f(R([(182, 558), (206, 558), (202, 622), (180, 622)])), FUR_SH, blur=3)
        p.line(paw, LW, FUR_LN, closed=True)
        body.append(p)
    for side, f in SIDES:
        p = Part(f'手指_{side}')
        for (x, y, l) in [(149, 608, 14), (159, 613, 16), (169, 614, 16), (179, 611, 14), (188, 606, 12)]:
            c = f(R([(x, y), (x - 0.5, y + l * 0.6), (x + 0.5, y + l)]))
            p.rib(c, [5.8 * K, 5.6 * K, 4.4 * K], FUR_LN, hardness=0.7, flow=0.8)
            p.rib(c, [4.4 * K, 4.2 * K, 3.1 * K], FUR, hardness=0.8, flow=0.9)
            p.fill(f(R([(x - 2, y + l - 1), (x + 2, y + l - 1), (x + 0.5, y + l + 6, 'c')])), hx('efeae0'),
                   line=FUR_LN, lw=0.7)                                                           # claw
        body.append(p)
    for side, f in SIDES:
        p = Part(f'背心_{side}')
        vest = f(R([(262, 290), (236, 292), (206, 304), (196, 324), (200, 380), (210, 430), (218, 480),
                    (224, 530), (250, 540), (262, 520), (256, 470), (246, 420), (244, 370), (248, 330)]))
        p.fill(vest, VEST)
        p.air(f(R([(190, 300), (240, 300), (240, 340), (190, 340)])), VEST_HI, blur=8)
        p.air(f(R([(190, 420), (226, 420), (226, 545), (190, 545)])), VEST_SH, blur=8)
        for y in (400, 450, 500):                                                                   # buttons
            p.fill(Rell(252 if side == 'R' else 2 * CX - 252, y, 3.2, 3.2), hx('d9c28a'), raw=True)
        p.line(f(R([(214, 520), (232, 528)])), 1.0, VEST_LN)                                       # torn edge
        p.line(vest, LW, VEST_LN, closed=True)
        body.append(p)
    p = Part('腰帶')
    belt = R([(218, 560), (353, 560), (355, 580), (216, 580)])
    p.fill(belt, hx('3a2a1c'), line=hx('14100a'), lw=LW)
    p.fill(R([(CX - 10, 558), (CX + 10, 558), (CX + 10, 582), (CX - 10, 582)]), hx('c8b27a'), line=hx('5a4a26'), lw=1.0)
    body.append(p)

    G.append(('身體', body))

    # head (drawn last; eyes/mouth grouped like the girls)
    head = []
    hp = head_parts()
    head += hp[:2]                     # ears behind the head
    head.append(hp[2])                 # face base
    head.append(hp[3])                 # light cheek / muzzle fur
    head.append(('嘴', mouth_parts()))
    head.append(nose_part())
    head.append(('眼_R', wolf_eye('R')))
    head.append(('眼_L', wolf_eye('L')))
    head += hp[4:]                     # brows
    head.append(head_tuft())
    G.append(('頭', head))
    return G


def landmarks():
    return {}


def body_landmarks():
    return {}


# ------------------------------------------------------------------ rig (live2d/engine/rig.py)
RIG = dict(
    neck=(CX, 265), waist=(CX, 470),
    eyes={'R': (CX - WOLF['eye_dx'], WOLF['eye_y']), 'L': (CX + WOLF['eye_dx'], WOLF['eye_y'])},
    lower_lid_dy=7, blink_drop=16, mouth_y=WOLF['mouth_y'],
    mouth_open=[('口腔', 'transform.s.y', 5.0), ('口腔', 'transform.s.x', 1.05), ('舌頭', 'transform.s.y', 3.0),
                ('舌頭', 'transform.t.y', 4.0), ('下排牙齒', 'transform.t.y', 8.0)],
    head3d=dict(center=(CX, 176), radii=(70, 92, 62), layers={
        '鼻子': (1, 30), '上唇': (1, 20), '口腔': (1, 18), '舌頭': (1, 18), '上排牙齒': (1, 19), '下排牙齒': (1, 18),
        '臉毛': (1, 6), '眼': (1, 2), '上': (1, 2), '下': (1, 2), '高光': (1, 2.5), '眉毛': (1, 4), '頭毛': (1, 6),
        '耳朵': (1, -2)}),
    head_groups=('頭',),
    hair_deform=[],
    arm_parts={'R': ['上臂_R', '下臂_R', '手掌_R', '手指_R'], 'L': ['上臂_L', '下臂_L', '手掌_L', '手指_L']},
    arm_pivots=((210, 316), (186, 470), (169, 562)), arm_warp=None,
    breath_scale=['胸腔'], breath_lift=['背心_R', '背心_L', '上臂_R', '上臂_L'],
    extras=[{'param': 'Tail:: Sway', 'parts': ['尾巴'], 'pivot': (322, 575), 'angle': 0.22, 'ramp': (570, 690)}],
    lifts=[{'param': 'Leg:: Right:: Step', 'parts': ['腿_R', '腳_R'], 'dy': -14},
           {'param': 'Leg:: Left:: Step', 'parts': ['腿_L', '腳_L'], 'dy': -14}],
)
