# -*- coding: utf-8 -*-
"""獵人 side view (profile, facing right) for walking shots.

Same skeleton as wolf_side.py (hip 600, knee 760, ankle 925, sole 1003; shoulder 316, elbow 468, wrist 560) so the
stage's walk solver treats him like the wolf, and the same palette as hunter.py. Human profile head: skull circle,
forehead -> brow -> bridge -> round rosy nose -> upper lip under a bushy moustache; a full beard hides the jaw.
Tyrolean hat with the feather at the back; rifle slung on the back (behind everything).
Volume: light from the upper front (form() core shadow along back edges, light band along front edges).
"""
import numpy as np

from girl import Part, hx, smooth
from girl_v4 import R, Rell, CX, K, LW
from red_hood_side import band, form
from hunter import (SKIN, SKIN_SH, SKIN_HI, SKIN_LN, NOSE_RED, HAIR, HAIR_SH, HAIR_HI, HAIR_LN, JACK, JACK_SH,
                    JACK_HI, JACK_LN, SHIRT, SHIRT_SH, SHIRT_LN, PANTS, PANTS_SH, PANTS_LN, BOOT, BOOT_SH, BOOT_HI,
                    BOOT_LN, LEATHER, LEATHER_LN, BRASS, HAT, HAT_SH, HAT_HI, HAT_LN, FEATHER, FEATHER_SH, WOOD,
                    WOOD_SH, WOOD_LN, STEEL, STEEL_HI, STEEL_LN, EYE_W, IRIS, PUPIL, MOUTH)

X = lambda dx: CX + dx

HIP, KNEE, ANKLE = (X(-2), 600), (X(0), 760), (X(-2), 925)
SHOULDER, ELBOW, WRIST = (X(-4), 316), (X(-10), 468), (X(-4), 560)
NECK, WAIST = (X(4), 262), (X(0), 470)
EYE = (X(45), 184)
MOUTHP = (X(60), 241)


def far(c):
    return (int(c[0] * 0.78), int(c[1] * 0.78), int(c[2] * 0.84), c[3])


# ------------------------------------------------------------------ legs
def thigh(tag, f):
    p = Part(f'大腿_{tag}')
    front = [(X(30), 576), (X(36), 630), (X(33), 680), (X(26), 740), (X(22), 764)]
    back = [(X(-34), 576), (X(-36), 640), (X(-28), 700), (X(-22), 764)]
    pts = R(front + [(X(12), 778), (X(0), 782), (X(-12), 778)] + back[::-1])
    p.fill(pts, f(PANTS))
    form(p, front, back, f=f)
    p.line(R([(X(20), 610), (X(28), 660), (X(24), 700)]), 1.0, f(PANTS_LN), clipped=True)
    p.line(smooth(R(front), closed=False), LW, f(PANTS_LN), raw=True)
    p.line(smooth(R(back), closed=False), LW, f(PANTS_LN), raw=True)
    return p


def shin(tag, f):
    p = Part(f'小腿_{tag}')
    front = [(X(21), 760), (X(20), 820), (X(20), 880), (X(20), 934)]
    back = [(X(-23), 760), (X(-28), 810), (X(-27), 860), (X(-24), 936)]
    pts = R([(X(-14), 745), (X(0), 740), (X(14), 745)] + front + back[::-1])
    p.fill(pts, f(PANTS))
    p.clip(pts)
    p.cfill(R([(X(-40), 832), (X(40), 832), (X(40), 950), (X(-40), 950)]), f(BOOT), blur=0.3)          # boot shaft
    form(p, front, back, f=f)
    p.cfill(R([(X(-40), 826), (X(40), 826), (X(40), 848), (X(-40), 848)]), f(BOOT_HI), blur=0.3)       # folded top
    p.line(R([(X(-30), 848), (X(30), 848)]), 1.0, f(BOOT_LN), clipped=True)
    p.line(R([(X(-30), 826), (X(30), 826)]), 1.0, f(BOOT_LN), clipped=True)
    p.line(smooth(R(front), closed=False), LW, f(PANTS_LN), raw=True)
    p.line(smooth(R(back), closed=False), LW, f(PANTS_LN), raw=True)
    return p


def foot(tag, f):
    p = Part(f'腳_{tag}')
    pts = R([(X(-24), 910), (X(20), 910), (X(26), 950), (X(50), 966), (X(62), 984), (X(60), 1004, 'c'),
             (X(-28), 1004, 'c'), (X(-30), 960)])
    p.fill(pts, f(BOOT))
    band(p, [(X(-24), 910), (X(-30), 960), (X(-28), 1004)], 14, f(BOOT_SH), blur=3)
    p.air(R([(X(22), 948), (X(46), 962), (X(52), 976), (X(26), 972)]), f(BOOT_HI), blur=4)
    p.cfill(R([(X(-40), 994), (X(80), 994), (X(80), 1010), (X(-40), 1010)]), f(hx('1c120b')), blur=0.5)   # sole
    p.line(pts, LW, f(BOOT_LN), closed=True)
    return p


# ------------------------------------------------------------------ arms
def upper_arm(tag, f):
    p = Part(f'上臂_{tag}')
    front = [(X(14), 300), (X(12), 390), (X(2), 476)]
    back = [(X(-26), 300), (X(-30), 390), (X(-24), 478)]
    pts = R(front + back[::-1])
    p.fill(pts, f(JACK))
    form(p, front, back, w_sh=0.5, f=f)
    p.line(pts, LW, f(JACK_LN), closed=True)
    return p


def forearm(tag, f):
    p = Part(f'下臂_{tag}')
    front = [(X(2), 456), (X(6), 510), (X(6), 552)]
    back = [(X(-24), 456), (X(-20), 510), (X(-16), 552)]
    pts = R(front + back[::-1])
    p.fill(pts, f(JACK))
    form(p, front, back, f=f)
    p.cfill(R([(X(-30), 530), (X(14), 530), (X(14), 556), (X(-30), 556)]), f(JACK_SH), blur=0.4)      # cuff
    p.line(smooth(R(front), closed=False), LW, f(JACK_LN), raw=True)
    p.line(smooth(R(back), closed=False), LW, f(JACK_LN), raw=True)
    p.line(R([(X(-22), 532), (X(6), 532)]), 1.0, f(JACK_LN))
    hand = R([(X(-18), 550), (X(8), 550), (X(16), 572), (X(14), 598), (X(0), 608), (X(-14), 600), (X(-20), 574)])
    p.fill(hand, f(SKIN))
    p.cfill(R([(X(-30), 580), (X(-8), 580), (X(-8), 612), (X(-30), 612)]), f(SKIN_SH), blur=3)
    p.line(hand, LW, f(SKIN_LN), closed=True)
    p.line(R([(X(8), 584), (X(12), 596)]), 0.9, f(SKIN_LN))                                          # finger split
    return p


# ------------------------------------------------------------------ torso
def rifle():
    p = Part('獵槍')
    a = np.array([X(-52), 196.0])
    b = np.array([X(-92), 690.0])
    d = (b - a) / np.linalg.norm(b - a)
    n = np.array([-d[1], d[0]])
    pt = lambda t, w: tuple(a + d * t + n * w)
    L = float(np.linalg.norm(b - a))
    p.fill(R([pt(0, -3.2), pt(0, 3.2), pt(L * 0.62, 4.2), pt(L * 0.62, -4.2)]), STEEL, line=STEEL_LN, lw=LW * 0.8)
    p.line(R([pt(4, -1.2), pt(L * 0.6, -1.6)]), 1.0, STEEL_HI)
    stock = [pt(L * 0.55, -6), pt(L * 0.55, 7), pt(L * 0.8, 9), pt(L * 0.86, 16), pt(L, 18), pt(L, -12),
             pt(L * 0.86, -8), pt(L * 0.8, -7)]
    p.fill(R(stock), WOOD)
    p.line(R(stock), LW * 0.9, WOOD_LN, closed=True)
    return p


def neck():
    p = Part('脖子')
    pts = R([(X(-26), 232), (X(24), 238), (X(30), 270), (X(34), 304), (X(-30), 304), (X(-34), 270)])
    p.fill(pts, SKIN)
    p.cfill(R([(X(-40), 232), (X(40), 232), (X(40), 280), (X(-40), 280)]), SKIN_SH, blur=6)
    return p


def torso():
    p = Part('胸腔')
    front = [(X(24), 286), (X(40), 320), (X(47), 370), (X(45), 430), (X(40), 480), (X(38), 540), (X(40), 606)]
    back = [(X(-32), 282), (X(-46), 330), (X(-44), 390), (X(-38), 450), (X(-38), 520), (X(-44), 580), (X(-40), 606)]
    pts = R(front + back[::-1])
    p.fill(pts, SHIRT)
    band(p, front, -8, hx('ffffff', 90), blur=3)
    for y in (340, 380, 420):
        p.fill(Rell(X(40), y, 2.2, 2.2), hx('b9a98a'), raw=True)
    p.line(pts, LW, SHIRT_LN, closed=True)
    return p


def jacket():
    p = Part('外套')
    front = [(X(20), 288), (X(34), 330), (X(38), 390), (X(36), 450), (X(36), 520), (X(44), 642)]
    back = [(X(-40), 284), (X(-56), 340), (X(-54), 400), (X(-48), 470), (X(-50), 560), (X(-58), 648)]
    pts = R(front + back[::-1])
    p.fill(pts, JACK)
    form(p, front, back, w_sh=0.4)
    p.air(R([(X(-40), 286), (X(20), 286), (X(20), 326), (X(-40), 326)]), JACK_HI, blur=8)
    flap = [(X(-6), 586), (X(34), 586), (X(34), 602), (X(14), 608), (X(-6), 602)]
    p.fill(R([(X(-6), 590), (X(34), 590), (X(35), 630), (X(-5), 632)]), JACK_SH, line=JACK_LN, lw=LW * 0.8)
    p.fill(R(flap), JACK, line=JACK_LN, lw=LW * 0.8)
    for y in (420, 470):
        p.fill(Rell(X(30), y, 3.2, 3.2), hx('3a2a1a'), raw=True)
    p.line(pts, LW, JACK_LN, closed=True)
    return p


def belt():
    p = Part('腰帶')
    p.fill(R([(X(-50), 548), (X(38), 548), (X(40), 570), (X(-51), 570)]), LEATHER, line=LEATHER_LN, lw=LW)
    p.fill(R([(X(26), 545), (X(42), 545), (X(42), 573), (X(26), 573)]), BRASS, line=hx('6a5020'), lw=1.0)
    return p


def strap():
    p = Part('背帶')
    p.fill(R([(X(-18), 290), (X(-4), 292), (X(-44), 548), (X(-58), 544)]), LEATHER, line=LEATHER_LN, lw=LW * 0.9)
    return p


# ------------------------------------------------------------------ head
FACE = [(X(-10), 98), (X(28), 102), (X(48), 124), (X(54), 158), (X(52), 174), (X(56), 188), (X(62), 204),
        (X(60), 222), (X(58), 236), (X(56), 250), (X(46), 264), (X(24), 272), (X(0), 268), (X(-30), 252),
        (X(-52), 222), (X(-62), 182), (X(-58), 138), (X(-40), 110)]


def back_hair():
    p = Part('後髮')
    pts = R([(X(-20), 100), (X(-46), 108), (X(-64), 140), (X(-68), 184), (X(-60), 226), (X(-44), 246),
             (X(-26), 236), (X(-20), 180)])
    p.fill(pts, HAIR_SH)
    p.air(R([(X(-70), 100), (X(-40), 100), (X(-40), 250), (X(-70), 250)]), HAIR_LN, blur=10)
    p.line(pts, LW, HAIR_LN, closed=True)
    return p


def far_eye():
    shape = [(X(49), 181), (X(53), 179), (X(55), 184), (X(53), 189), (X(49), 188)]
    p1 = Part('遠眼白')
    p1.fill(R(shape), EYE_W)
    p2 = Part('遠眼球')
    p2.clip(R(shape))
    p2.cfill(Rell(X(52), 184, 2.6, 4.4), IRIS, raw=True, blur=0.4)
    p3 = Part('遠眼線')
    p3.rib(R([(X(48), 181), (X(52), 178), (X(56), 180)]), [0.8 * K, 2.0 * K, 0.8 * K], hx('2a1a12'), hardness=0.8, flow=0.9)
    return [p1, p2, p3]


def face():
    p = Part('臉')
    pts = R(FACE)
    p.fill(pts, SKIN)
    band(p, [(X(-40), 110), (X(-58), 138), (X(-62), 182), (X(-52), 222)], 18, SKIN_SH, blur=6)
    p.air(R([(X(20), 104), (X(52), 104), (X(52), 124), (X(20), 124)]), SKIN_SH, blur=6)               # hat shadow
    p.air(R([(X(30), 130), (X(50), 130), (X(52), 160), (X(34), 160)]), SKIN_HI, blur=6)
    p.air(Rell(X(34), 212, 12, 8), hx('ef9a8a', 150), blur=6, raw=True)                               # cheek
    p.line(smooth(R(FACE[1:12]), closed=False), LW, SKIN_LN, raw=True)
    return p


def hair_side():
    p = Part('頭髮')
    pts = R([(X(-44), 106), (X(-2), 108), (X(-6), 146), (X(-22), 162), (X(-30), 196), (X(-34), 232), (X(-46), 244),
             (X(-58), 230), (X(-66), 190), (X(-64), 140)])
    p.fill(pts, HAIR)
    band(p, [(X(-44), 106), (X(-64), 140), (X(-66), 190), (X(-58), 230)], 12, HAIR_SH, blur=4)
    for i in range(7):
        x = X(-56 + i * 7)
        p.strand(R([(x + 6, 112), (x, 160), (x - 4, 214)]), 1.2, HAIR_HI if i % 2 else HAIR_SH)
    p.line(pts, LW, HAIR_LN, closed=True)
    return p


def ear():
    p = Part('耳朵')
    pts = R([(X(-12), 170), (X(-24), 166), (X(-30), 182), (X(-26), 202), (X(-14), 210), (X(-8), 198)])
    p.fill(pts, SKIN)
    p.cfill(R([(X(-24), 176), (X(-14), 176), (X(-14), 202), (X(-24), 202)]), SKIN_SH, blur=2)
    p.line(pts, LW, SKIN_LN, closed=True)
    return p


def beard():
    p = Part('鬍子')
    pts = R([(X(-6), 172), (X(4), 172), (X(12), 198), (X(30), 220), (X(50), 238), (X(60), 244), (X(64), 262),
             (X(58), 290), (X(42), 306), (X(18), 304), (X(-4), 290), (X(-20), 262), (X(-22), 220), (X(-12), 186)])
    p.fill(pts, HAIR)
    p.air(R([(X(-30), 270), (X(70), 270), (X(70), 310), (X(-30), 310)]), HAIR_SH, blur=8)
    band(p, [(X(-6), 172), (X(-12), 186), (X(-22), 220), (X(-20), 262), (X(-4), 290)], 14, HAIR_SH, blur=4)
    rng = np.random.default_rng(3)
    for i in range(12):
        x = X(-10 + i * 6 + rng.normal(0, 1.5))
        p.strand(R([(x, 250), (x + rng.normal(0, 2), 272), (x - 2, 296)]), 1.2, HAIR_HI if i % 3 == 0 else HAIR_SH)
    p.line(pts, LW, HAIR_LN, closed=True)
    return p


def mouth():
    p = Part('口腔')
    p.fill(R([(X(52), 240.5), (X(64), 240.2), (X(63.5), 242), (X(58), 243), (X(52.5), 242.2)]), MOUTH)
    return p


def mustache():
    p = Part('八字鬍')
    pts = R([(X(44), 224), (X(60), 221), (X(70), 228), (X(70), 240, 'c'), (X(62), 236), (X(52), 237), (X(40), 234)])
    p.fill(pts, HAIR)
    p.air(R([(X(40), 232), (X(72), 232), (X(72), 242), (X(40), 242)]), HAIR_SH, blur=3)
    p.line(pts, LW, HAIR_LN, closed=True)
    return p


def nose():
    p = Part('鼻子')
    pts = R([(X(56), 190), (X(64), 198), (X(72), 208), (X(74), 216), (X(68), 224), (X(58), 222)])
    p.fill(pts, SKIN)
    p.cfill(Rell(X(68), 214, 8, 8), NOSE_RED, raw=True, blur=4)
    p.air(Rell(X(68), 208, 3, 2.5), SKIN_HI, blur=2, raw=True)
    p.fill(Rell(X(63), 220, 2.4, 1.4), hx('8a4a3a'), raw=True)
    p.line(R([(X(56), 190), (X(64), 198), (X(72), 208), (X(74), 216), (X(68), 224), (X(60), 223)]), LW, SKIN_LN)
    return p


EYE_SHAPE = [(X(38), 184, 'c'), (X(43), 179), (X(49), 178), (X(52), 183), (X(50), 189), (X(43), 189)]


def eye_white():
    p = Part('眼白')
    p.fill(R(EYE_SHAPE), EYE_W)
    return p


def iris():
    p = Part('眼球')
    p.clip(R(EYE_SHAPE))
    p.cfill(Rell(X(48), 184, 3.8, 5.6), IRIS, raw=True, blur=0.4)
    p.cfill(Rell(X(48.5), 184, 1.8, 2.8), PUPIL, raw=True, blur=0.3)
    p.cfill(Rell(X(47), 181.5, 1.2, 1.4), hx('ffffff'), raw=True, blur=0.2)
    return p


def lids():
    p = Part('眼線')
    p.rib(R([(X(36), 184), (X(42), 178.5), (X(49), 177), (X(53), 181)]), [1.0 * K, 2.4 * K, 2.4 * K, 1.0 * K],
          hx('2a1a12'), hardness=0.8, flow=0.9)
    return p


def brow():
    p = Part('眉毛')
    p.rib(R([(X(34), 168), (X(44), 165), (X(56), 168)]), [1.4 * K, 3.6 * K, 1.8 * K], HAIR_LN, hardness=0.7, flow=0.8)
    return p


def hat():
    p = Part('帽子')
    crown = [(X(-42), 104), (X(-40), 70), (X(-28), 46), (X(-8), 38, 'c'), (X(14), 46), (X(30), 66), (X(36), 104)]
    p.fill(R(crown), HAT)
    band(p, [(X(-28), 46), (X(-40), 70), (X(-42), 104)], 14, HAT_SH, blur=3)
    p.air(R([(X(0), 40), (X(34), 40), (X(34), 100), (X(0), 100)]), HAT_HI, blur=8)
    p.line(R(crown), LW, HAT_LN, closed=True)
    p.fill(R([(X(-42), 90), (X(36), 90), (X(37), 104), (X(-43), 104)]), LEATHER, line=LEATHER_LN, lw=LW * 0.9)
    brim = [(X(-78), 112), (X(-60), 100), (X(0), 96), (X(62), 100), (X(84), 106), (X(62), 116), (X(0), 116),
            (X(-60), 118)]
    p.fill(R(brim), HAT)
    p.air(R([(X(-80), 108), (X(86), 108), (X(86), 120), (X(-80), 120)]), HAT_SH, blur=4)
    p.line(R(brim), LW, HAT_LN, closed=True)
    vane = [(X(-34), 96), (X(-48), 74), (X(-62), 50), (X(-78), 28, 'c'), (X(-64), 56), (X(-52), 78), (X(-38), 98)]
    p.fill(R(vane), FEATHER)
    p.air(R([(X(-80), 30), (X(-50), 30), (X(-50), 70), (X(-80), 70)]), FEATHER_SH, blur=6)
    p.line(R(vane), LW * 0.9, hx('5c1210'), closed=True)
    return p


# ------------------------------------------------------------------ assemble
def build():
    F = lambda c: c
    return [
        ('尾', [rifle()]),
        ('腿_後', [foot('後', far), shin('後', far), thigh('後', far)]),
        ('手_後', [forearm('後', far), upper_arm('後', far)]),
        ('身體', [neck(), torso(), jacket(), belt(), strap()]),
        ('腿_前', [foot('前', F), shin('前', F), thigh('前', F)]),
        ('頭', [back_hair(), ('遠眼', far_eye()), face(), hair_side(), ear(), beard(), mouth(), mustache(), nose(),
               ('眼', [eye_white(), iris(), lids()]), brow(), hat()]),
        ('手_前', [upper_arm('前', F), forearm('前', F)]),
    ]


SIDE_RIG = dict(
    bones=[('Body', None, WAIST), ('Head', 'Body', NECK),
           ('Thigh B', 'Body', HIP), ('Shin B', 'Thigh B', KNEE), ('Foot B', 'Shin B', ANKLE),
           ('Thigh F', 'Body', HIP), ('Shin F', 'Thigh F', KNEE), ('Foot F', 'Shin F', ANKLE),
           ('Arm B', 'Body', SHOULDER), ('Forearm B', 'Arm B', ELBOW),
           ('Arm F', 'Body', SHOULDER), ('Forearm F', 'Arm F', ELBOW)],
    parts={'大腿_後': 'Thigh B', '小腿_後': 'Shin B', '腳_後': 'Foot B',
           '大腿_前': 'Thigh F', '小腿_前': 'Shin F', '腳_前': 'Foot F',
           '上臂_後': 'Arm B', '下臂_後': 'Forearm B', '上臂_前': 'Arm F', '下臂_前': 'Forearm F'},
    head_groups=('頭',),
    rotations=[
        ('Leg:: Front:: Hip', 'Thigh F', -1), ('Leg:: Front:: Knee', 'Shin F', 1), ('Leg:: Front:: Foot', 'Foot F', -1),
        ('Leg:: Back:: Hip', 'Thigh B', -1), ('Leg:: Back:: Knee', 'Shin B', 1), ('Leg:: Back:: Foot', 'Foot B', -1),
        ('Arm:: Front:: Swing', 'Arm F', -1), ('Arm:: Front:: Elbow', 'Forearm F', -1),
        ('Arm:: Back:: Swing', 'Arm B', -1), ('Arm:: Back:: Elbow', 'Forearm B', -1),
        ('Head:: Nod', 'Head', -1), ('Body:: Lean', 'Body', -1),
    ],
    eye=EYE, eye_parts=('眼白', '眼球'), lash_parts=('眼線',), blink_drop=6,
    mouth=('口腔', MOUTHP, 1.0, 4.5),
    turn=dict(param='Head:: Turn', face_part='臉',
              far_eye=dict(parts=['遠眼白', '遠眼球', '遠眼線'], pivot=(X(52), 184), dx=10, dz=-0.6),
              near_eye_scale=1.2,
              shifts={'鼻子': (-4, 0), '八字鬍': (-3, 0), '口腔': (-3, 0), '眉毛': (2, 0)},
              face=[(150, 200, 7.0), (200, 240, -2.0), (240, 262, 2.0)], face_from=30),
    breath=['胸腔', '外套'],
)
