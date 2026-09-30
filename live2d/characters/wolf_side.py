# -*- coding: utf-8 -*-
"""大野狼 side view (profile, facing right) for walking shots -- v2, per the anime-side-view skill.

Construction (skeleton -> volumes -> contour, side face in three steps):
  * head: cranium circle + cross; the muzzle is the face plane pushed forward (brow ridge -> stop -> long
    bridge -> nose tip; upper lip -> grin corner; lower jaw); ear sits just behind the vertical line and
    tilts back; cheek ruff behind the jaw; the thick neck leaves from behind the jaw, slanted forward
  * sly predator posture: head and chest slightly forward, back rises over the shoulders (hump) then dips
    at the waist and rounds over the rump; barrel chest
  * legs: thigh fuller in front, calf behind a straight shin, big long paws; bushy S-curved tail
Volume: light from the upper front; core shadow + occlusion along every back edge, light along every
front edge, cast shadows (vest on chest, belt on trousers, jaw on neck), fur tufts on the shadow side.
Mouth opens by rotating the lower jaw about its hinge (Mouth:: Open -> Jaw bone).
Joints: hip 600, knee 760, ankle 925, sole 1003; shoulder 316, elbow 468, wrist 560.
"""
from girl import Part, hx, smooth
from girl_v4 import R, Rell, CX, K, LW
from red_hood_side import band, form
from wolf import (FUR, FUR_SH, FUR_DK, FUR_HI, FUR_LN, LIGHT, LIGHT_SH, NOSE, EYE_Y_, EYE_W_, VEST, VEST_SH,
                  VEST_HI, VEST_LN, PANTS, PANTS_SH, PANTS_LN, PATCH, MOUTH, TONGUE)

X = lambda dx: CX + dx

HIP, KNEE, ANKLE = (X(-2), 600), (X(0), 760), (X(-2), 925)
SHOULDER, ELBOW, WRIST = (X(-4), 316), (X(-10), 468), (X(-4), 560)
NECK, WAIST, JAW = (X(4), 265), (X(0), 470), (X(22), 238)
TAIL = (X(-40), 568)
EYE = (X(46), 180)
FUR_SHADE = hx('2a3040', 120)


def far(c):
    return (int(c[0] * 0.78), int(c[1] * 0.78), int(c[2] * 0.84), c[3])


def tufts(p, edge, col, n_every=2, length=7, seed=0):
    """little fur spikes poking out along an edge (ref px, top -> bottom), pointing backward-down"""
    import random
    rnd = random.Random(seed)
    for i in range(0, len(edge) - 1, n_every):
        (x0, y0), (x1, y1) = edge[i][:2], edge[i + 1][:2]
        for t in (0.3, 0.75):
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            L = length * (0.7 + 0.6 * rnd.random())
            p.fill(R([(x + 2, y - 3), (x - L, y + L * 0.5, 'c'), (x + 1, y + 4)]), col)


# ------------------------------------------------------------------ legs (trousers, paws)
def thigh(tag, f):
    p = Part(f'大腿_{tag}')
    front = [(X(30), 576), (X(36), 630), (X(33), 680), (X(26), 740), (X(22), 764)]
    back = [(X(-34), 576), (X(-36), 640), (X(-28), 700), (X(-22), 764)]
    pts = R(front + [(X(12), 778), (X(0), 782), (X(-12), 778)] + back[::-1])
    p.fill(pts, f(PANTS))
    form(p, front, back, f=f)
    p.cfill(R([(X(-4), 740), (X(24), 738), (X(26), 776), (X(-2), 778)]), f(PATCH), blur=0.3)      # knee patch
    for x in (4, 11, 18):
        p.line(R([(X(x), 740), (X(x + 1), 776)]), 0.8, f(hx('5b4a30')), clipped=True)
    p.cfill(R([(X(-44), 566), (X(44), 566), (X(44), 604), (X(-44), 604)]), f(hx('1a1810', 110)), blur=8)  # belt shadow
    p.line(R([(X(20), 610), (X(28), 660), (X(24), 700)]), 1.0, f(PANTS_LN), clipped=True)          # crease
    p.line(smooth(R(front), closed=False), LW, f(PANTS_LN), raw=True)
    p.line(smooth(R(back), closed=False), LW, f(PANTS_LN), raw=True)
    return p


def shin(tag, f):
    p = Part(f'小腿_{tag}')
    front = [(X(21), 760), (X(20), 820), (X(18), 880), (X(18), 934)]
    back = [(X(-23), 760), (X(-28), 810), (X(-26), 860), (X(-20), 936)]
    pts = R([(X(-14), 745), (X(0), 740), (X(14), 745)] + front + back[::-1])
    p.fill(pts, f(PANTS))
    form(p, front, back, f=f)
    p.cfill(R([(X(-30), 736), (X(30), 736), (X(30), 764), (X(-30), 764)]), f(hx('1a1810', 70)), blur=5)
    p.line(R([(X(-18), 918), (X(-8), 926), (X(2), 920), (X(10), 927), (X(18), 920)]), 1.0, f(PANTS_LN))  # frayed hem
    p.line(smooth(R(front), closed=False), LW, f(PANTS_LN), raw=True)
    p.line(smooth(R(back), closed=False), LW, f(PANTS_LN), raw=True)
    return p


def foot(tag, f):
    p = Part(f'腳_{tag}')
    pts = R([(X(-20), 914), (X(14), 914), (X(28), 944), (X(56), 966), (X(70), 988), (X(64), 1004, 'c'),
             (X(-26), 1004, 'c'), (X(-30), 962)])
    p.fill(pts, f(FUR))
    band(p, [(X(-20), 914), (X(-30), 962), (X(-26), 1004)], 16, f(FUR_SHADE), blur=4)
    p.air(R([(X(20), 940), (X(50), 958), (X(58), 976), (X(26), 970)]), f(FUR_HI), blur=5)          # top of the paw
    p.cfill(R([(X(-40), 990), (X(80), 990), (X(80), 1010), (X(-40), 1010)]), f(FUR_SH), blur=2)
    for x in (46, 57, 67):
        p.fill(R([(X(x - 3), 998), (X(x + 3), 998), (X(x + 6), 1009, 'c')]), f(hx('e9e4d8')), line=f(FUR_LN), lw=0.8)
    for x in (40, 52):
        p.line(R([(X(x), 972), (X(x + 4), 998)]), 0.9, f(FUR_LN))
    p.line(pts, LW, f(FUR_LN), closed=True)
    return p


# ------------------------------------------------------------------ arms
def upper_arm(tag, f):
    p = Part(f'上臂_{tag}')
    front = [(X(14), 300), (X(12), 390), (X(2), 476)]
    back = [(X(-24), 300), (X(-28), 390), (X(-24), 478)]
    pts = R(front + back[::-1])
    p.fill(pts, f(FUR))
    form(p, front, back, w_sh=0.5, f=f)
    tufts(p, back, f(FUR_SH), seed=3)
    p.cfill(R([(X(-36), 294), (X(24), 294), (X(24), 330), (X(-36), 330)]), f(hx('1a1d26', 90)), blur=8)  # vest shadow
    p.line(pts, LW, f(FUR_LN), closed=True)
    return p


def forearm(tag, f):
    p = Part(f'下臂_{tag}')
    front = [(X(2), 456), (X(6), 510), (X(6), 566)]
    back = [(X(-24), 456), (X(-20), 510), (X(-14), 566)]
    pts = R(front + back[::-1])
    p.fill(pts, f(FUR))
    form(p, front, back, f=f)
    tufts(p, back, f(FUR_SH), seed=5)
    p.line(smooth(R(front), closed=False), LW, f(FUR_LN), raw=True)
    p.line(smooth(R(back), closed=False), LW, f(FUR_LN), raw=True)
    paw = R([(X(-20), 552), (X(10), 552), (X(18), 578), (X(12), 606), (X(-4), 614), (X(-18), 604), (X(-24), 578)])
    p.fill(paw, f(FUR))
    p.cfill(R([(X(-30), 588), (X(20), 588), (X(20), 618), (X(-30), 618)]), f(FUR_SH), blur=3)
    p.air(R([(X(0), 556), (X(14), 556), (X(16), 584), (X(2), 584)]), f(FUR_HI), blur=4)
    for (x, y) in [(X(12), 604), (X(4), 611), (X(-5), 613)]:
        p.fill(R([(x - 2, y), (x + 2, y), (x + 1, y + 7, 'c')]), f(hx('efeae0')), line=f(FUR_LN), lw=0.7)   # claws
    p.line(paw, LW, f(FUR_LN), closed=True)
    return p


# ------------------------------------------------------------------ torso, tail
def tail():
    p = Part('尾巴')
    top = [(X(-34), 552), (X(-76), 552), (X(-118), 574), (X(-150), 612), (X(-168), 660), (X(-166), 708)]
    bot = [(X(-36), 596), (X(-66), 610), (X(-94), 634), (X(-116), 664), (X(-128), 700)]
    pts = R(top + [(X(-150), 686), (X(-140), 712, 'c')] + bot[::-1])
    p.fill(pts, FUR)
    p.cfill(R([(X(-190), 650), (X(-112), 650), (X(-112), 730), (X(-190), 730)]), LIGHT, blur=6)       # light tip
    band(p, bot, -18, FUR_SHADE, blur=5)                                                            # underside
    band(p, top, 12, hx('ffffff', 60), blur=5)
    for a, b in [((X(-50), 566), (X(-130), 630)), ((X(-54), 586), (X(-118), 652)), ((X(-80), 572), (X(-150), 640))]:
        p.strand(R([a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 6), b]), 1.3, FUR_DK)
    tufts(p, bot, FUR_SH, seed=7, length=9)
    p.line(pts, LW, FUR_LN, closed=True)
    return p


def neck():
    p = Part('脖子')
    pts = R([(X(-26), 232), (X(24), 238), (X(32), 270), (X(38), 304), (X(-30), 304), (X(-34), 270)])
    p.fill(pts, FUR)
    p.cfill(R([(X(-40), 232), (X(40), 232), (X(40), 276), (X(-40), 276)]), FUR_DK, blur=6)          # under the jaw
    p.cfill(R([(X(18), 250), (X(46), 250), (X(46), 306), (X(22), 306)]), LIGHT, blur=4)             # throat fur
    return p


def torso():
    p = Part('胸腔')
    front = [(X(24), 284), (X(38), 310), (X(48), 350), (X(46), 410), (X(38), 470), (X(34), 540), (X(36), 606)]
    back = [(X(-30), 280), (X(-46), 330), (X(-46), 380), (X(-38), 450), (X(-36), 520), (X(-44), 580), (X(-40), 606)]
    pts = R(front + back[::-1])
    p.fill(pts, FUR)
    p.cfill(R([(X(16), 282), (X(56), 282), (X(56), 500), (X(22), 500), (X(14), 400)]), LIGHT, blur=2)  # chest fur
    band(p, front, -10, hx('ffffff', 90), blur=3)
    for y in (320, 350, 380):
        p.fill(R([(X(44), y), (X(52), y + 8, 'c'), (X(42), y + 12)]), LIGHT)                       # chest fur tufts
    p.line(pts, LW, FUR_LN, closed=True)
    return p


def vest():
    p = Part('背心')
    front = [(X(16), 290), (X(24), 330), (X(26), 390), (X(24), 450), (X(28), 536)]
    back = [(X(-42), 290), (X(-52), 340), (X(-50), 400), (X(-44), 470), (X(-46), 540)]
    pts = R(front + back[::-1])
    p.fill(pts, VEST)
    form(p, front, back, w_sh=0.45)
    p.air(R([(X(-40), 288), (X(20), 288), (X(20), 326), (X(-40), 326)]), VEST_HI, blur=8)
    for y in (400, 450, 500):
        p.fill(Rell(X(21), y, 3.2, 3.2), hx('d9c28a'), raw=True)
    p.line(R([(X(-44), 526), (X(-26), 534)]), 1.0, VEST_LN)                                      # torn edge
    p.line(pts, LW, VEST_LN, closed=True)
    return p


def belt():
    p = Part('腰帶')
    p.fill(R([(X(-44), 558), (X(38), 558), (X(40), 580), (X(-45), 580)]), hx('3a2a1c'), line=hx('14100a'), lw=LW)
    p.fill(R([(X(28), 555), (X(42), 555), (X(42), 583), (X(28), 583)]), hx('c8b27a'), line=hx('5a4a26'), lw=1.0)
    return p


# ------------------------------------------------------------------ head (side face: circle + muzzle plane)
HEAD = [(X(-10), 110), (X(22), 112), (X(42), 132), (X(48), 158), (X(54), 176), (X(74), 186), (X(96), 194),
        (X(106), 202, 'c'), (X(104), 220), (X(92), 232, 'c'), (X(40), 234), (X(22), 242), (X(-10), 258),
        (X(-44), 252), (X(-64), 236, 'c'), (X(-52), 222), (X(-68), 204, 'c'), (X(-56), 190), (X(-62), 156),
        (X(-48), 126)]


def ear(name, f, dx):
    p = Part(name)
    pts = R([(X(-8 + dx), 128), (X(-22 + dx), 92), (X(-30 + dx), 54, 'c'), (X(2 + dx), 82), (X(14 + dx), 122)])
    p.fill(pts, f(FUR))
    p.cfill(R([(X(-16 + dx), 120), (X(-24 + dx), 72), (X(-2 + dx), 92), (X(6 + dx), 120)]), f(hx('c79aa0')), blur=2)
    p.cfill(R([(X(-44 + dx), 44), (X(8 + dx), 44), (X(8 + dx), 74), (X(-44 + dx), 74)]), f(FUR_DK), blur=5)
    band(p, [(X(-8 + dx), 128), (X(-22 + dx), 92), (X(-30 + dx), 54)], 8, f(FUR_SHADE), blur=3)
    p.line(pts, LW, f(FUR_LN), closed=True)
    return p


def cavity():
    p = Part('口腔')
    pts = R([(X(24), 233), (X(88), 233), (X(80), 246), (X(38), 252), (X(20), 244)])
    p.fill(pts, MOUTH)
    p.cfill(R([(X(34), 242), (X(72), 240), (X(68), 254), (X(38), 254)]), TONGUE, blur=1.5)
    return p


def head():
    p = Part('頭_底')
    pts = R(HEAD)
    p.fill(pts, FUR)
    p.cfill(R([(X(30), 208), (X(108), 208), (X(108), 242), (X(30), 242)]), LIGHT, blur=3)          # muzzle underside
    p.cfill(R([(X(-44), 204), (X(12), 208), (X(22), 258), (X(-44), 258)]), LIGHT, blur=5)          # cheek ruff
    band(p, [(X(-48), 126), (X(-62), 156), (X(-56), 190), (X(-68), 204)], 22, FUR_SHADE, blur=6)   # back of the skull
    p.air(R([(X(-30), 110), (X(30), 110), (X(40), 140), (X(-30), 140)]), FUR_HI, blur=10)          # crown light
    p.air(R([(X(54), 182), (X(98), 190), (X(98), 200), (X(54), 194)]), FUR_HI, blur=5)             # bridge light
    p.air(R([(X(30), 160), (X(50), 160), (X(52), 186), (X(34), 186)]), FUR_SHADE, blur=5)          # eye socket
    for a in [(X(-44), 206), (X(-34), 220), (X(-26), 236)]:
        p.strand(R([a, (a[0] - 10, a[1] + 12), (a[0] - 16, a[1] + 22)]), 1.3, LIGHT_SH)
    p.fill(R([(X(74), 232), (X(80), 232), (X(77), 243, 'c')]), hx('f6f2e8'), line=FUR_LN, lw=0.7)   # fang
    p.line(pts, LW, FUR_LN, closed=True)
    p.line(R([(X(92), 233), (X(64), 235), (X(40), 236), (X(28), 229)]), 1.4, FUR_LN)                # grin, corner up
    return p


def jaw():
    p = Part('下顎')
    pts = R([(X(22), 235), (X(90), 235), (X(88), 244), (X(62), 252), (X(34), 258), (X(14), 252)])
    p.fill(pts, LIGHT)
    p.air(R([(X(10), 248), (X(92), 248), (X(92), 260), (X(10), 260)]), LIGHT_SH, blur=4)
    p.line(pts, LW, FUR_LN, closed=True)
    return p


def nose():
    p = Part('鼻子')
    pts = R([(X(94), 196), (X(104), 199), (X(109), 208, 'c'), (X(100), 214), (X(90), 208)])
    p.fill(pts, NOSE)
    p.cfill(Rell(X(101), 201, 3, 1.6), hx('6b6f7a'), raw=True, blur=1)
    return p


def eye_white():
    p = Part('眼白')
    p.fill(R([(X(34), 181), (X(46), 174), (X(54), 177), (X(50), 187), (X(38), 188)]), EYE_W_)
    return p


def iris():
    p = Part('眼球')
    p.clip(R([(X(34), 181), (X(46), 174), (X(54), 177), (X(50), 187), (X(38), 188)]))
    p.cfill(Rell(X(47), 181, 5, 6.5), EYE_Y_, raw=True, blur=0.5)
    p.cfill(Rell(X(48), 181, 1.3, 5.5), hx('1c1a14'), raw=True, blur=0.4)                          # slit pupil
    p.cfill(Rell(X(45.5), 178.5, 1.3, 1.6), hx('ffffff'), raw=True, blur=0.3)
    return p


def lids():
    p = Part('眼線')
    p.rib(R([(X(30), 183), (X(38), 176), (X(48), 173), (X(56), 177)]), [1.0 * K, 2.8 * K, 2.8 * K, 1.2 * K],
          hx('1c1e24'), hardness=0.8, flow=0.9)
    p.line(R([(X(37), 189), (X(50), 188)]), 0.9, FUR_LN)
    return p


def far_eye():
    """far eye (70 deg only): at rest it sits behind the head layer (hidden, the profile has ONE eye);
    Head:: Turn slides it out above the muzzle bridge and brings it in front"""
    shape = [(X(46), 182), (X(52), 177), (X(56), 179), (X(54), 187), (X(48), 188)]
    p1 = Part('遠眼白')
    p1.fill(R(shape), EYE_W_)
    p2 = Part('遠眼球')
    p2.clip(R(shape))
    p2.cfill(Rell(X(52), 182.5, 3.0, 5.5), EYE_Y_, raw=True, blur=0.4)
    p2.cfill(Rell(X(52.5), 182.5, 0.9, 4.5), hx('1c1a14'), raw=True, blur=0.3)
    p3 = Part('遠眼線')
    p3.rib(R([(X(45), 183), (X(51), 177), (X(57), 178)]), [0.8 * K, 2.2 * K, 0.8 * K], hx('1c1e24'), hardness=0.8, flow=0.9)
    return [p1, p2, p3]


def brow():
    p = Part('眉毛')
    p.rib(R([(X(28), 162), (X(42), 167), (X(58), 173)]), [1.0 * K, 3.0 * K, 1.2 * K], FUR_DK, hardness=0.8, flow=0.9)
    return p


def tuft():
    p = Part('頭毛')
    pts = R([(X(-34), 118), (X(-22), 94), (X(-12), 110), (X(-2), 90), (X(8), 108), (X(20), 98), (X(24), 122)])
    p.fill(pts, FUR)
    p.air(R([(X(-30), 96), (X(20), 96), (X(20), 110), (X(-30), 110)]), FUR_HI, blur=4)
    p.line(pts[:-1], LW, FUR_LN)
    return p


# ------------------------------------------------------------------ assemble
def build():
    F = lambda c: c
    return [
        ('尾', [tail()]),
        ('腿_後', [foot('後', far), shin('後', far), thigh('後', far)]),
        ('手_後', [forearm('後', far), upper_arm('後', far)]),
        ('身體', [neck(), torso(), vest(), belt()]),
        ('腿_前', [foot('前', F), shin('前', F), thigh('前', F)]),
        ('頭', [ear('耳朵_後', far, 12), ('遠眼', far_eye()), cavity(), head(), jaw(), nose(),
               ('眼', [eye_white(), iris(), lids()]),
               brow(), tuft(), ear('耳朵_前', F, 0)]),
        ('手_前', [upper_arm('前', F), forearm('前', F)]),
    ]


SIDE_RIG = dict(
    bones=[('Body', None, WAIST), ('Head', 'Body', NECK), ('Jaw', 'Head', JAW), ('Tail', 'Body', TAIL),
           ('Thigh B', 'Body', HIP), ('Shin B', 'Thigh B', KNEE), ('Foot B', 'Shin B', ANKLE),
           ('Thigh F', 'Body', HIP), ('Shin F', 'Thigh F', KNEE), ('Foot F', 'Shin F', ANKLE),
           ('Arm B', 'Body', SHOULDER), ('Forearm B', 'Arm B', ELBOW),
           ('Arm F', 'Body', SHOULDER), ('Forearm F', 'Arm F', ELBOW)],
    parts={'大腿_後': 'Thigh B', '小腿_後': 'Shin B', '腳_後': 'Foot B',
           '大腿_前': 'Thigh F', '小腿_前': 'Shin F', '腳_前': 'Foot F',
           '上臂_後': 'Arm B', '下臂_後': 'Forearm B', '上臂_前': 'Arm F', '下臂_前': 'Forearm F',
           '下顎': 'Jaw', '尾巴': 'Tail'},
    head_groups=('頭',),
    rotations=[
        ('Leg:: Front:: Hip', 'Thigh F', -1), ('Leg:: Front:: Knee', 'Shin F', 1), ('Leg:: Front:: Foot', 'Foot F', -1),
        ('Leg:: Back:: Hip', 'Thigh B', -1), ('Leg:: Back:: Knee', 'Shin B', 1), ('Leg:: Back:: Foot', 'Foot B', -1),
        ('Arm:: Front:: Swing', 'Arm F', -1), ('Arm:: Front:: Elbow', 'Forearm F', -1),
        ('Arm:: Back:: Swing', 'Arm B', -1), ('Arm:: Back:: Elbow', 'Forearm B', -1),
        ('Head:: Nod', 'Head', -1), ('Body:: Lean', 'Body', -1), ('Tail:: Sway', 'Tail', 1),
    ],
    eye=EYE, eye_parts=('眼白', '眼球'), lash_parts=('眼線',), blink_drop=6,
    mouth_rot=('Jaw', 0.30),
    # Head:: Turn  0 = 90 deg profile, 1 = 70 deg half-profile: far eye slides out over the muzzle bridge, near eye
    # widens, brow area fills forward, the muzzle foreshortens a little, the far ear shows more
    turn=dict(param='Head:: Turn', face_part='頭_底',
              far_eye=dict(parts=['遠眼白', '遠眼球', '遠眼線'], pivot=(X(46), 182), dx=12, dz=-0.6),
              near_eye_scale=1.25,
              shifts={'鼻子': (-6, 0), '下顎': (-4, 0), '口腔': (-4, 0), '耳朵_後': (8, 0), '耳朵_前': (-3, 0),
                      '眉毛': (3, 0)},
              face=[(150, 192, 9.0), (192, 244, -5.0), (244, 262, 3.0)], face_from=40),
    breath=['胸腔', '背心'],
)
