# -*- coding: utf-8 -*-
"""小紅帽 side view (profile, facing right) for walking shots -- v2.

Rebuilt from the 90-degree side-view construction (skeleton -> volumes -> contour):
  * S-curved back (shoulder blade out, small of the back in, buttocks out), chest forward, neck tilted forward
  * thigh fuller in front, calf bulging behind a straight shin, narrow ankle, long foot
  * upper arm hangs slightly behind the body line, forearm angles forward
  * hood hugs the skull with a small peak at the back
Volume (v1 read as flat cut-outs): light comes from the upper front. Every limb / torso part gets a core-shadow
band along its back edge, a darker occlusion strip at the very back, and a soft light band along its front
edge; cast shadows under the capelet, skirt, jaw and hood rim.

Same reference-px grid, landmarks and palette as the front view, so the stage can hand off between them:
  skull top 88, eye 184.6, chin 256, shoulder 300, waist 470, hip 585, knee 760, ankle 940, sole 1003.
Limbs are drawn hanging from their joints; rig_side.py turns them into a joint hierarchy.
"""
import numpy as np

import girl_v4 as G4
import red_hood as RH
from girl import Part, hx, smooth
from girl_v4 import R, Rell, CX, K, LW

SKIN, SKIN_SH, SKIN_LN = G4.SKIN, G4.SKIN_SH, G4.SKIN_LN
RED, RED_SH, RED_DK, RED_HI, RED_LN = RH.RED, RH.RED_SH, RH.RED_DK, RH.RED_HI, RH.RED_LN
HAIR, HAIR_SH, HAIR_HI, HAIR_LN = RH.HAIR, RH.HAIR_SH, RH.HAIR_HI, RH.HAIR_LN
SKIRT, SKIRT_SH, SKIRT_LN = RH.to_skirt_blue(G4.NAVY), RH.to_skirt_blue(G4.NAVY_SH), RH.to_skirt_blue(G4.NAVY_LN)
SOCK, SOCK_SH, SOCK_LN = hx('f3ece2'), hx('ddd2c4'), hx('9a8e80')
SHOE, SHOE_HI, SHOE_LN = G4.SHOE, G4.SHOE_HI, G4.SHOE_LN
WHITE, WHITE_SH, WHITE_LN = G4.WHITE, G4.WHITE_SH, G4.WHITE_LN
SHADE = hx('6a3450', 125)         # translucent core shadow (works over any base colour) -- v3: firm cel tone
SHADE2 = hx('3a1a30', 90)         # occlusion / deepest strip
LIGHT = hx('ffffff', 110)         # front light band

X = lambda dx: CX + dx            # body axis = CX; +x is the direction she faces
XB = lambda dx: CX + dx * 1.30    # v3: torso / clothes depth (v2 was only 0.49 x the front shoulder width)
XL = lambda dx: CX + dx * 1.15    # v3: thigh depth
XH = lambda dx: CX + dx * 1.12    # v3: hood (1.3 made it balloon)

HIP = (X(-2), 585)
KNEE = (X(0), 760)
ANKLE = (X(-1), 940)
SHOULDER = (X(-4), 318)
ELBOW = (X(-8), 456)
WRIST = (X(-2), 546)
NECK = (X(2), 262)
WAIST = (X(0), 470)
GRIP = (X(0), 568)
EYE = (X(44), 186)
MOUTH = (X(56), 235)


def far(c):
    """far-side limbs: a little darker and cooler."""
    return (int(c[0] * 0.80), int(c[1] * 0.80), int(c[2] * 0.86), c[3])


def band(p, edge, dx, col, blur=2.0):
    """soft band along an edge (ref px), dx ref px toward the inside -- the form-shading workhorse"""
    e = smooth(R(edge), closed=False)
    inner = [(x + dx * K, y) for x, y in reversed(e)]
    p.cfill(e + inner, col, raw=True, blur=blur)


SOCK_SHADE, SOCK_SHADE2 = hx('5c6078', 110), hx('3c4058', 80)


def form(p, front, back, w_sh=0.42, f=lambda c: c, cloth=False):
    """cylinder shading: core shadow + occlusion along the back edge, light along the front edge.
    front / back: edge polylines (ref px, top -> bottom); widths measured at the middle."""
    mid = len(back) // 2
    wid = abs(front[min(mid, len(front) - 1)][0] - back[mid][0])
    band(p, back, wid * w_sh, f(SOCK_SHADE if cloth else SHADE), blur=0.9)   # crisp cel edge: reads at video size
    band(p, back, wid * 0.14, f(SOCK_SHADE2 if cloth else SHADE2), blur=0.8)
    band(p, front, -wid * 0.16, LIGHT, blur=1.2)


# ------------------------------------------------------------------ legs
def thigh(tag, f):
    p = Part(f'大腿_{tag}')
    front = [(XL(28), 556), (XL(34), 600), (XL(33), 650), (XL(26), 705), (XL(20), 745), (XL(19), 762)]
    back = [(XL(-30), 556), (XL(-32), 620), (XL(-24), 680), (XL(-20), 730), (XL(-18), 762)]
    pts = R([(XL(-30), 556)] + front + [(XL(12), 774), (XL(0), 779), (XL(-12), 774)] + back[::-1][:-1])
    p.fill(pts, f(SKIN))
    p.cfill(R([(XL(-40), 662), (XL(40), 662), (XL(40), 790), (XL(-40), 790)]), f(SOCK), blur=0.4)       # stocking top
    p.cfill(R([(XL(-40), 659), (XL(40), 659), (XL(40), 669), (XL(-40), 669)]), f(SOCK_SH), blur=1.5)
    form(p, front, back + [(XL(-14), 776), (XL(-2), 781)], f=f, cloth=True)   # band continues round the knee cap
    p.cfill(R([(XL(-40), 540), (XL(40), 540), (XL(40), 596), (XL(-40), 596)]), f(hx('5a3040', 110)), blur=10)  # skirt shadow
    p.air(R([(XL(10), 700), (XL(22), 700), (XL(18), 758), (XL(8), 758)]), hx('ffffff', 110), blur=5)     # kneecap light
    p.line(smooth(R(front), closed=False), LW, f(SOCK_LN), raw=True)
    p.line(smooth(R(back), closed=False), LW, f(SOCK_LN), raw=True)
    return p


def shin(tag, f):
    p = Part(f'小腿_{tag}')
    front = [(X(19), 758), (X(17), 800), (X(13), 860), (X(9), 915), (X(8), 944)]
    back = [(X(-20), 758), (X(-25), 785), (X(-28), 825), (X(-20), 870), (X(-11), 915), (X(-10), 944)]
    pts = R([(X(-12), 745), (X(0), 741), (X(13), 745)] + front + back[::-1])
    p.fill(pts, f(SOCK))
    form(p, front, back, f=f, cloth=True)
    p.cfill(R([(X(-30), 736), (X(30), 736), (X(30), 764), (X(-30), 764)]), f(hx('5a3a4a', 60)), blur=5)  # under the knee
    p.line(smooth(R(front), closed=False), LW, f(SOCK_LN), raw=True)
    p.line(smooth(R(back), closed=False), LW, f(SOCK_LN), raw=True)
    return p


def shoe(tag, f):
    p = Part(f'鞋_{tag}')
    pts = R([(X(-14), 926), (X(10), 926), (X(18), 948), (X(38), 966), (X(54), 980), (X(60), 994), (X(54), 1003, 'c'),
             (X(-18), 1003, 'c'), (X(-21), 984), (X(-18), 956)])
    p.fill(pts, f(SHOE))
    p.cfill(R([(X(-30), 996), (X(70), 996), (X(70), 1010), (X(-30), 1010)]), f(G4.SHOE_SH), blur=1.5)   # sole
    p.cfill(R([(X(24), 962), (X(44), 970), (X(52), 988), (X(32), 988)]), f(SHOE_HI), blur=3)            # toe shine
    p.air(R([(X(-26), 930), (X(-4), 930), (X(-4), 1003), (X(-26), 1003)]), f(hx('2a1208', 170)), blur=6)  # heel in shadow
    p.line(R([(X(-16), 950), (X(6), 946), (X(20), 952)]), 1.2, f(SHOE_LN))                                 # strap
    p.fill(Rell(X(2), 948, 2.2, 2.2), f(hx('d8b872')), raw=True)                                          # buckle
    p.line(pts, LW, f(SHOE_LN), closed=True)
    return p


# ------------------------------------------------------------------ arms
def upper_arm(tag, f):
    p = Part(f'上臂_{tag}')
    front = [(X(10), 304), (X(9), 380), (X(4), 456)]
    back = [(X(-17), 304), (X(-20), 380), (X(-18), 458)]
    pts = R(front + back[::-1])
    p.fill(pts, f(WHITE))
    form(p, front, back, w_sh=0.5, f=f, cloth=True)
    p.cfill(R([(X(-30), 296), (X(20), 296), (X(20), 340), (X(-30), 340)]), f(hx('5a3040', 90)), blur=8)  # capelet shadow
    p.line(pts, LW, f(WHITE_LN), closed=True)
    return p


def forearm(tag, f, hand=True):
    p = Part(f'下臂_{tag}')
    front = [(X(3), 446), (X(5), 500), (X(5), 544)]
    back = [(X(-17), 446), (X(-12), 500), (X(-9), 548)]
    pts = R(front + back[::-1])
    p.fill(pts, f(SKIN))
    form(p, front, back, f=f)
    cuff = R([(X(-19), 444), (X(5), 444), (X(6), 466), (X(-17), 468)])                                 # blouse cuff
    p.fill(cuff, f(WHITE))
    p.cfill(R([(X(-24), 440), (X(-10), 440), (X(-8), 470), (X(-24), 470)]), f(WHITE_SH), blur=3)
    p.line(cuff, LW * 0.9, f(WHITE_LN), closed=True)
    p.line(smooth(R(front), closed=False), LW, f(SKIN_LN), raw=True)
    p.line(smooth(R(back), closed=False), LW, f(SKIN_LN), raw=True)
    if hand:
        palm(p, f)
    return p


def palm(p, f):
    h = R([(X(-9), 538), (X(8), 538), (X(12), 558), (X(8), 580), (X(-3), 586), (X(-10), 572), (X(-12), 556)])
    p.fill(h, f(SKIN))
    p.cfill(R([(X(-16), 540), (X(-4), 540), (X(-4), 588), (X(-16), 588)]), f(SKIN_SH), blur=3)
    p.cfill(R([(X(-14), 574), (X(14), 574), (X(14), 590), (X(-14), 590)]), f(hx('d9998c')), blur=3)
    p.line(R([(X(6), 566), (X(-2), 572)]), 0.9, f(SKIN_LN))
    p.line(h, LW, f(SKIN_LN), closed=True)


def hand_front():
    """near hand drawn over the basket handle (the fingers wrap around it)."""
    p = Part('手_前')
    palm(p, lambda c: c)
    return p


def basket():
    p = Part('籃子')
    B = RH.BASKET, RH.BASKET_SH, RH.BASKET_HI, RH.BASKET_LN
    handle = R([(X(-34), 612), (X(-28), 590), (X(-12), 572), (X(0), 568), (X(12), 572), (X(28), 590), (X(34), 612)])
    p.rib(handle, [5.5 * K] * 7, B[3], hardness=0.7, flow=0.8)
    p.rib(handle, [3.4 * K] * 7, B[0], hardness=0.8, flow=0.9)
    cloth = [(X(-30), 608), (X(-16), 594), (X(2), 600), (X(20), 590), (X(32), 606), (X(0), 612)]
    p.fill(R(cloth), RH.CLOTH_B)
    for i in range(5):
        x = X(-26) + i * 12
        p.cfill(R([(x, 588), (x + 6, 588), (x + 6, 614), (x, 614)]), RH.CLOTH_A, blur=0.3)
    p.line(R(cloth), LW * 0.8, hx('7d2a2f'), closed=True)
    body = R([(X(-38), 610), (X(38), 610), (X(32), 652), (X(20), 668), (X(-20), 668), (X(-32), 652)])
    p.fill(body, B[0])
    for y in np.arange(618, 668, 7):
        p.line(R([(X(-36), y), (X(0), y + 1.5), (X(36), y)]), 1.0, B[1], clipped=True)
    for x in np.arange(X(-30), X(34), 9):
        p.line(R([(x, 614), (x + (CX - x) * 0.12, 668)]), 0.8, B[2], clipped=True)
    p.air(R([(X(-40), 610), (X(-14), 610), (X(-20), 670), (X(-40), 670)]), B[1], blur=6)
    p.air(R([(X(-40), 650), (X(40), 650), (X(40), 672), (X(-40), 672)]), hx('3a2010', 110), blur=5)
    p.air(R([(X(14), 616), (X(30), 616), (X(26), 650), (X(12), 650)]), B[2], blur=5)
    p.line(body, LW, B[3], closed=True)
    rim = R([(X(-42), 606), (X(42), 606), (X(42), 616), (X(-42), 616)])
    p.fill(rim, B[0], line=B[3], lw=LW)
    return p


# ------------------------------------------------------------------ torso
def neck():
    p = Part('脖子')
    pts = R([(XB(-14), 232), (XB(16), 238), (XB(22), 270), (XB(26), 304), (XB(-20), 306), (XB(-18), 270)])  # tilted forward
    p.fill(pts, SKIN)
    p.cfill(R([(XB(-30), 232), (XB(30), 232), (XB(30), 272), (XB(-30), 272)]), hx('e9a99a'), blur=4)      # under the jaw
    band(p, [(XB(-14), 232), (XB(-18), 270), (XB(-20), 306)], 12, SHADE, blur=3)
    p.line(R([(XB(16), 240), (XB(22), 272), (XB(26), 300)]), LW * 0.9, SKIN_LN)
    return p


def torso():
    p = Part('胸腔')
    front = [(XB(16), 288), (XB(24), 306), (XB(36), 330), (XB(47), 352), (XB(48), 364), (XB(40), 382), (XB(32), 398),
             (XB(27), 430), (XB(25), 462), (XB(28), 490)]
    back = [(XB(-18), 286), (XB(-28), 300), (XB(-34), 330), (XB(-32), 370), (XB(-24), 420), (XB(-22), 462), (XB(-26), 490)]
    pts = R(front + back[::-1])
    p.fill(pts, WHITE)
    form(p, front, back, w_sh=0.4, cloth=True)
    p.cfill(R([(XB(18), 364), (XB(50), 364), (XB(42), 402), (XB(18), 402)]), WHITE_SH, blur=4)           # under the bust
    p.air(R([(XB(22), 330), (XB(40), 330), (XB(44), 356), (XB(26), 356)]), hx('ffffff'), blur=4)          # bust highlight
    p.line(pts, LW, WHITE_LN, closed=True)
    return p


def bodice():
    p = Part('馬甲')
    front = [(XB(38), 384), (XB(30), 410), (XB(26), 440), (XB(25), 462), (XB(28), 488)]
    back = [(XB(-28), 384), (XB(-25), 420), (XB(-22), 462), (XB(-27), 490)]
    pts = R(front + back[::-1])
    p.fill(pts, RH.BODICE)
    form(p, front, back, w_sh=0.45, cloth=True)
    ys = np.linspace(392, 482, 6)
    for i in range(len(ys) - 1):
        p.line(R([(XB(22), ys[i]), (XB(29), ys[i + 1])]), 1.8, RH.LACE, clipped=True)
    p.line(pts, LW, RH.BODICE_LN, closed=True)
    return p


def skirt():
    p = Part('裙')
    # flares over the hips; fuller at the back (buttocks), which also hangs a little lower
    front = [(XB(24), 464), (XB(40), 500), (XB(58), 545), (XB(78), 590), (XB(86), 606)]
    back = [(XB(-32), 466), (XB(-50), 500), (XB(-64), 530), (XB(-86), 574), (XB(-98), 608)]
    pts = R(front[:-1] + [(XB(86), 606, 'c'), (XB(40), 612), (XB(-10), 616), (XB(-62), 616), (XB(-98), 608, 'c')]
            + back[::-1][1:])
    p.fill(pts, SKIRT)
    # pleats: alternate lit / shaded panels -> the skirt reads as a cone, not a flat sheet
    xs_top = [-30, -18, -6, 6, 18]
    xs_bot = [-96, -64, -30, 6, 44, 86]
    for i in range(len(xs_top) - 1):
        if i % 2 == 0:
            poly = [(XB(xs_top[i]), 470), (XB(xs_top[i + 1]), 470), (XB(xs_bot[i + 1]), 616), (XB(xs_bot[i]), 616)]
            p.cfill(R(poly), hx('2a4a86', 90), blur=3)
    band(p, back, 30, SHADE, blur=4)
    band(p, back, 10, SHADE2, blur=2)
    p.cfill(R([(XB(-110), 596), (XB(96), 596), (XB(96), 622), (XB(-110), 622)]), hx('1d2f5c', 110), blur=4)  # hem underside
    p.air(R([(XB(-20), 470), (XB(26), 470), (XB(40), 520), (XB(-10), 520)]), hx('8fb0e8', 110), blur=10)   # light on the hip
    for x0, x1 in [(XB(-18), XB(-64)), (XB(-6), XB(-30)), (XB(6), XB(6)), (XB(18), XB(44))]:
        p.line(R([(x0, 480), ((x0 + x1) / 2, 545), (x1, 612)]), 1.1, SKIRT_LN, clipped=True)            # pleat folds
    p.line(pts, LW, SKIRT_LN, closed=True)
    return p


def apron():
    p = Part('圍裙')
    pts = R([(XB(22), 474), (XB(34), 478), (XB(48), 520), (XB(72), 588), (XB(78), 600, 'c'), (XB(50), 604),
             (XB(32), 556), (XB(18), 500)])
    p.fill(pts, RH.APRON)
    band(p, [(XB(18), 500), (XB(32), 556), (XB(50), 604)], 12, hx('8a8070', 70), blur=3)
    p.air(R([(XB(28), 480), (XB(40), 480), (XB(60), 560), (XB(46), 560)]), hx('ffffff'), blur=5)
    p.line(pts, LW, RH.APRON_LN, closed=True)
    return p


def capelet():
    p = Part('斗篷')
    # open at the front like the front view: the edge hangs from the bow BEHIND the bust, so the chest line shows
    front = [(XB(12), 270), (XB(22), 292), (XB(28), 322), (XB(30), 360), (XB(28), 420), (XB(26), 476)]
    back = [(XB(-24), 282), (XB(-46), 310), (XB(-58), 360), (XB(-64), 420), (XB(-64), 482)]
    pts = R(front[:-1] + [(XB(26), 476, 'c'), (XB(0), 486), (XB(-24), 490), (XB(-64), 482, 'c')] + back[::-1][1:])
    p.fill(pts, RED)
    band(p, back, 34, hx('4a0e16', 110), blur=6)                                                    # back of the cape
    band(p, back, 10, hx('2a0508', 90), blur=3)
    band(p, front, -14, hx('ff9a9e', 90), blur=5)                                                   # lit front edge
    p.air(R([(XB(-24), 276), (XB(30), 276), (XB(34), 326), (XB(-20), 326)]), RED_HI, blur=12)           # shoulder top
    for a, b in [((XB(-6), 336), (XB(0), 482)), ((XB(-32), 346), (XB(-40), 484))]:                      # soft folds
        p.air(R([a, (a[0] + 9, a[1]), (b[0] + 9, b[1]), b]), hx('8e1826', 140), blur=5)
        p.air(R([(a[0] + 10, a[1]), (a[0] + 16, a[1]), (b[0] + 16, b[1]), (b[0] + 10, b[1])]), hx('ff8a90', 90), blur=4)
    p.cfill(R([(XB(-70), 466), (XB(60), 466), (XB(60), 494), (XB(-70), 494)]), hx('6a1420', 120), blur=5)  # hem underside
    p.line(pts, LW, RED_LN, closed=True)
    return p


def neck_bow():
    p = Part('斗篷結')
    for pts in ([(XB(22), 290), (XB(12), 280), (XB(8), 292), (XB(20), 298)],
                [(XB(24), 292), (XB(34), 282), (XB(38), 294), (XB(26), 300)],
                [(XB(22), 296), (XB(18), 322, 'c'), (XB(24), 316), (XB(30), 324, 'c'), (XB(26), 296)]):
        p.fill(R(pts), RED, line=RED_LN, lw=LW * 0.9)
    p.fill(Rell(XB(23), 293, 4, 4), RED_SH, raw=True)
    p.cfill(Rell(XB(33), 286, 2.5, 1.5), RED_HI, raw=True, blur=1)
    return p


# ------------------------------------------------------------------ head (profile)
FACE = [(X(2), 96), (X(30), 104), (X(48), 124), (X(56), 150), (X(57), 172), (X(54), 186), (X(57), 200),
        (X(63), 212), (X(67), 219, 'c'), (X(58), 224, 'c'), (X(59), 230), (X(61), 233, 'c'), (X(56), 237, 'c'),
        (X(58), 242), (X(53), 249), (X(47), 256, 'c'), (X(30), 262), (X(12), 262), (X(-6), 252),
        (X(-18), 238, 'c'), (X(-24), 214), (X(-40), 190), (X(-50), 150), (X(-30), 105)]


def hood_back():
    """the hood hugs the skull (small gap for the hair), a slight peak at the back, drapes onto the capelet."""
    p = Part('兜帽')
    back = [(XH(-54), 84), (XH(-70), 110), (XH(-76), 160), (XH(-72), 214), (XH(-60), 262), (XH(-44), 298)]
    pts = R([(XH(44), 98), (XH(30), 82), (XH(4), 72), (XH(-28), 72), (XH(-54), 84, 'c'), (XH(-70), 110), (XH(-76), 160),
             (XH(-72), 214), (XH(-60), 262), (XH(-44), 298), (XH(-10), 304), (XH(12), 292), (XH(6), 262), (XH(0), 226),
             (XH(4), 186), (XH(12), 150), (XH(26), 118)])
    p.fill(pts, RED)
    p.air(R([(XH(-40), 66), (XH(36), 66), (XH(36), 104), (XH(-40), 104)]), RED_HI, blur=14)             # crown catches light
    band(p, back, 36, hx('4a0e16', 110), blur=7)                                                     # round back of the head
    band(p, back, 10, hx('2a0508', 90), blur=3)
    p.air(R([(XH(-60), 250), (XH(10), 250), (XH(10), 310), (XH(-60), 310)]), RED_SH, blur=10)
    p.air(R([(XH(-36), 110), (XH(-26), 110), (XH(-36), 280), (XH(-48), 280)]), hx('8e1826', 150), blur=7)  # fold
    p.air(R([(XH(-24), 110), (XH(-18), 110), (XH(-26), 280), (XH(-34), 280)]), hx('ff8a90', 90), blur=5)
    p.line(pts, LW, RED_LN, closed=True)
    return p


def hood_rim():
    p = Part('兜帽_前')
    outer = [(XH(46), 98), (XH(26), 118), (XH(12), 150), (XH(4), 186), (XH(0), 226), (XH(6), 262), (XH(12), 292)]
    inner = [(XH(2), 292), (XH(-4), 262), (XH(-10), 226), (XH(-6), 186), (XH(2), 150), (XH(16), 114), (XH(36), 92)]
    p.fill(R(outer + inner), RED)
    p.air(R([(XH(-10), 90), (XH(60), 90), (XH(60), 140), (XH(-10), 140)]), RED_HI, blur=8)
    p.air(R([(XH(-14), 230), (XH(20), 230), (XH(20), 296), (XH(-14), 296)]), RED_SH, blur=8)
    p.line(smooth(R(outer), closed=False), LW, RED_LN, raw=True)
    return p


def face():
    p = Part('臉')
    pts = R(FACE)
    p.fill(pts, SKIN)
    p.cfill(R([(X(-30), 236), (X(40), 250), (X(40), 270), (X(-30), 270)]), SKIN_SH, blur=4)          # under the jaw
    band(p, [(X(26), 114), (X(12), 150), (X(4), 186), (X(0), 226), (X(6), 262)], -14,
         hx('c0706a', 90), blur=4)                                                                   # hood-rim shadow
    p.air(R([(X(40), 140), (X(56), 140), (X(58), 176), (X(42), 176)]), hx('ffffff', 110), blur=5)    # forehead light
    p.air(R([(X(52), 200), (X(64), 200), (X(64), 222), (X(52), 222)]), hx('ffffff', 110), blur=3)    # nose light
    p.air(Rell(X(34), 212, 13, 8), hx('ffb0b0', 170), blur=6, raw=True)                              # blush
    for i in range(3):
        p.line(R([(X(28 + 5 * i), 208), (X(31 + 5 * i), 204)]), 0.8, hx('f08a8a', 200))
    prof = smooth(R(FACE[1:20]), closed=False)
    p.line(prof, LW, SKIN_LN, raw=True)
    p.line(R([(X(56), 236), (X(60), 235.5)]), 1.0, G4.MOUTH_LN)
    p.line(R([(X(60), 219), (X(56), 221)]), 0.9, SKIN_LN)
    return p


# profile eye (per the side-eye reference sheet): a triangle whose point is at the BACK (toward the ear) and whose
# FRONT is an open, slightly bulging vertical curve (the cornea); tall narrow iris near the front; thick upper lash
# that runs past the back corner and flicks up; short soft lower lash. Big + small highlight = cute.
EYE_SHAPE = [(X(30), 185, 'c'), (X(38), 176), (X(47), 171.5), (X(52), 177), (X(53.5), 186), (X(51.5), 196),
             (X(46), 200.5), (X(38), 195)]


def eye_white():
    p = Part('眼白')
    pts = R(EYE_SHAPE)
    p.fill(pts, hx('ffffff'))
    p.cfill(R([(X(26), 168), (X(56), 168), (X(56), 181), (X(26), 181)]), hx('d9def2'), blur=1.5)   # lid shadow
    return p


def iris():
    p = Part('眼球')
    p.clip(R(EYE_SHAPE))
    p.cfill(Rell(X(47.5), 187, 5.9, 12.5), RH.to_amber(G4.IRIS_M), raw=True, blur=0.4)            # tall narrow iris
    p.cfill(Rell(X(47.5), 182, 5.9, 7.5), RH.to_amber(G4.IRIS_D), raw=True, blur=1.6)             # dark top
    p.cfill(Rell(X(48.5), 188, 2.4, 6.2), RH.to_amber(G4.PUPIL), raw=True, blur=0.5)
    p.cfill(Rell(X(47), 194.5, 4.2, 3.6), RH.to_amber(G4.IRIS_L), raw=True, blur=1.6)             # glow at the bottom
    p.cfill(Rell(X(48.5), 179.5, 2.6, 3.4), hx('ffffff'), raw=True, blur=0.3)                     # big highlight
    p.cfill(Rell(X(45.5), 193.5, 1.1, 1.3), hx('ffffff', 230), raw=True, blur=0.2)                # small highlight
    return p


def lashes():
    p = Part('上睫毛')
    # upper lash line: thick in the middle, runs past the back corner
    p.rib(R([(X(26.5), 183), (X(31), 178.5), (X(39), 173.5), (X(47), 170.8), (X(52.5), 175)]),
          [0.8 * K, 2.6 * K, 3.4 * K, 3.0 * K, 1.2 * K], G4.LASH, hardness=0.85, flow=0.95)
    for pts, w in (([(X(30), 179), (X(25), 174), (X(21.5), 172.5)], 1.9),        # curled flicks at the back
                   ([(X(34), 176), (X(30), 170), (X(28), 167.5)], 1.6),
                   ([(X(52), 174), (X(55.5), 171), (X(57), 169.5)], 1.2)):     # tiny front flick
        p.rib(R(pts), [w * K, w * 0.7 * K, 0.3 * K], G4.LASH, hardness=0.85, flow=0.95)
    # lower lash: short, soft, warm
    p.rib(R([(X(38), 196), (X(44), 200), (X(50), 198.5)]), [0.3 * K, 0.9 * K, 0.3 * K], G4.LID_LN, hardness=0.7, flow=0.8)
    p.rib(R([(X(40), 200.5), (X(38.5), 203.5)]), [0.5 * K, 0.2 * K], G4.LID_LN, hardness=0.7, flow=0.7)
    return p


def far_eye():
    """the far eye (70 deg only). At rest (= 90 deg, what the PSD shows) it sits 10 px back BEHIND the face layer, so a
    profile never shows two eyes; Head:: Turn slides it out past the nose bridge and brings it in front."""
    shape = [(X(48), 177), (X(52.5), 175.5), (X(54.5), 182), (X(53.5), 192), (X(49.5), 196), (X(47.5), 187)]
    p1 = Part('遠眼白')
    p1.fill(R(shape), hx('ffffff'))
    p2 = Part('遠眼球')
    p2.clip(R(shape))
    p2.cfill(Rell(X(51.5), 186.5, 3.0, 9.5), RH.to_amber(G4.IRIS_M), raw=True, blur=0.4)
    p2.cfill(Rell(X(51.5), 182, 3.0, 5.5), RH.to_amber(G4.IRIS_D), raw=True, blur=1.2)
    p2.cfill(Rell(X(51.8), 180.5, 1.2, 1.8), hx('ffffff'), raw=True, blur=0.2)
    p3 = Part('遠睫毛')
    p3.rib(R([(X(47), 177), (X(51), 174.5), (X(55), 176.5), (X(56.5), 174)]), [1.0 * K, 2.2 * K, 1.6 * K, 0.4 * K],
           G4.LASH, hardness=0.85, flow=0.95)
    return [p1, p2, p3]


def brow():
    p = Part('眉毛')      # above the bangs, semi-transparent (seen through the fringe)
    p.rib(R([(X(34), 158), (X(44), 155.5), (X(54), 157)]), [0.6 * K, 1.4 * K, 0.6 * K], hx('45271a', 150),
          hardness=0.7, flow=0.7)
    return p


def mouth():
    p = Part('口腔')      # a thin slit hidden in the lip line at rest (PSD = closed mouth); Mouth:: Open scales it up
    pts = R([(X(52), 235.0), (X(60.5), 234.8), (X(60), 236.4), (X(56), 237.4), (X(52.5), 236.6)])
    p.fill(pts, G4.MOUTH)
    return p


def bangs():
    """profile fringe: comes over the forehead with thickness in front of it; strand tips end just above the lashes"""
    p = Part('瀏海')
    pts = R([(X(-12), 86), (X(24), 86), (X(46), 98), (X(58), 116), (X(63), 138), (X(62), 162, 'c'), (X(55), 150),
             (X(51), 167, 'c'), (X(45), 150), (X(39), 165, 'c'), (X(32), 148), (X(25), 160, 'c'), (X(14), 140),
             (X(2), 150, 'c'), (X(-6), 118)])
    p.fill(pts, HAIR)
    p.air(R([(X(-4), 86), (X(56), 86), (X(60), 112), (X(-4), 112)]), HAIR_HI, blur=8)
    p.air(R([(X(10), 132), (X(66), 132), (X(66), 170), (X(10), 170)]), HAIR_SH, blur=7)
    p.air(R([(X(48), 100), (X(62), 116), (X(64), 150), (X(56), 150)]), hx('ffffff', 60), blur=5)      # rim light in front
    for a, b in [((X(22), 96), (X(48), 150)), ((X(34), 94), (X(58), 142)), ((X(8), 102), (X(30), 150)),
                 ((X(44), 100), (X(61), 128))]:
        p.strand(R([a, ((a[0] + b[0]) / 2 + 4, (a[1] + b[1]) / 2), b]), 1.2, HAIR_HI)
    p.line(pts, LW, HAIR_LN, closed=True)
    return p


def side_lock():
    p = Part('側髮')
    pts = R([(X(4), 140), (X(18), 152), (X(22), 212), (X(16), 250, 'c'), (X(8), 214), (X(-2), 180)])
    p.fill(pts, HAIR)
    p.air(R([(X(-6), 140), (X(8), 140), (X(8), 250), (X(-6), 250)]), HAIR_SH, blur=6)
    p.line(pts, LW, HAIR_LN, closed=True)
    return p


def braid():
    p = Part('麻花辮')
    path = [(X(6), 250), (X(10), 290), (X(14), 330), (X(16), 366), (X(18), 396)]
    c = np.array(smooth(path, closed=False, n=12))
    for i in range(8):
        t = (i + 0.5) / 8
        x, y = c[int(t * (len(c) - 1))]
        w = 11 - 3.5 * t
        off = (1 if i % 2 else -1) * 2.2
        lobe = [(x + off - w, y - 6), (x + off, y - 12), (x + off + w, y - 4), (x + off + w * 0.6, y + 9),
                (x + off - w * 0.3, y + 11), (x + off - w, y + 3)]
        p.fill(R(lobe), HAIR)
        p.cfill(R([(x - 20, y + 2), (x + 20, y + 2), (x + 20, y + 14), (x - 20, y + 14)]), HAIR_SH, blur=2)
        p.strand(R([(x + off - w * 0.6, y - 5), (x + off, y - 1), (x + off + w * 0.5, y + 5)]), 1.3, HAIR_HI)
        p.line(R(lobe), LW * 0.9, HAIR_LN, closed=True)
    x, y = c[-1]
    p.fill(R([(x - 8, y), (x + 8, y), (x + 10, y + 18), (x + 3, y + 32, 'c'), (x - 1, y + 20), (x - 6, y + 30, 'c'),
              (x - 9, y + 16)]), HAIR, line=HAIR_LN, lw=LW * 0.9)
    p.fill(R([(x - 10, y - 8), (x, y - 2), (x + 10, y - 8), (x + 10, y + 4), (x, y + 2), (x - 10, y + 4)]),
           RED, line=RED_LN, lw=LW * 0.9)
    return p


# ------------------------------------------------------------------ assemble
def build():
    F = lambda c: c
    return [
        ('腿_後', [shoe('後', far), shin('後', far), thigh('後', far)]),
        ('手_後', [forearm('後', far), upper_arm('後', far)]),
        ('身體', [neck(), torso(), bodice()]),
        ('腿_前', [shoe('前', F), shin('前', F), thigh('前', F)]),
        ('裙裝', [skirt(), apron()]),
        ('前手臂', [upper_arm('前', F), forearm('前', F, hand=False), basket(), hand_front()]),
        ('披風', [capelet(), neck_bow()]),
        ('頭', [side_lock(), ('遠眼', far_eye()), face(), ('眼', [eye_white(), iris(), lashes()]), mouth(), bangs(),
               brow(),
               hood_back(), hood_rim(), braid()]),
    ]


# ------------------------------------------------------------------ rig (live2d/engine/rig_side.py)
SIDE_RIG = dict(
    bones=[  # name, parent, pivot (reference px)
        ('Body', None, WAIST), ('Head', 'Body', NECK),
        ('Thigh B', 'Body', HIP), ('Shin B', 'Thigh B', KNEE), ('Foot B', 'Shin B', ANKLE),
        ('Thigh F', 'Body', HIP), ('Shin F', 'Thigh F', KNEE), ('Foot F', 'Shin F', ANKLE),
        ('Arm B', 'Body', SHOULDER), ('Forearm B', 'Arm B', ELBOW),
        ('Arm F', 'Body', SHOULDER), ('Forearm F', 'Arm F', ELBOW), ('Basket', 'Forearm F', GRIP),
        ('Braid', 'Head', (X(6), 252)),
    ],
    parts={'大腿_後': 'Thigh B', '小腿_後': 'Shin B', '鞋_後': 'Foot B',
           '大腿_前': 'Thigh F', '小腿_前': 'Shin F', '鞋_前': 'Foot F',
           '上臂_後': 'Arm B', '下臂_後': 'Forearm B', '上臂_前': 'Arm F', '下臂_前': 'Forearm F',
           '手_前': 'Forearm F', '籃子': 'Basket', '麻花辮': 'Braid'},
    head_groups=('頭',),
    rotations=[  # param name, bone, sign  (param value = radians, + = forward for limbs)
        ('Leg:: Front:: Hip', 'Thigh F', -1), ('Leg:: Front:: Knee', 'Shin F', 1), ('Leg:: Front:: Foot', 'Foot F', -1),
        ('Leg:: Back:: Hip', 'Thigh B', -1), ('Leg:: Back:: Knee', 'Shin B', 1), ('Leg:: Back:: Foot', 'Foot B', -1),
        ('Arm:: Front:: Swing', 'Arm F', -1), ('Arm:: Front:: Elbow', 'Forearm F', -1),
        ('Arm:: Back:: Swing', 'Arm B', -1), ('Arm:: Back:: Elbow', 'Forearm B', -1),
        ('Head:: Nod', 'Head', -1), ('Body:: Lean', 'Body', -1),
        ('Basket:: Swing', 'Basket', -1), ('Hair:: Sway', 'Braid', -1),
    ],
    eye=EYE, eye_parts=('眼白', '眼球'), lash_parts=('上睫毛',), blink_drop=13,
    mouth=('口腔', MOUTH, 1.0, 5.5),
    # Head:: Turn  0 = 90 deg profile, 1 = 70 deg half-profile (the front view hands over at 30 -> 70 deg)
    turn=dict(param='Head:: Turn',
              far_eye=dict(parts=['遠眼白', '遠眼球', '遠睫毛'], pivot=(X(47.5), 186), dx=10, dz=-0.6),  # slide out
              near_eye_scale=1.3,                                                          # half almond -> tall almond
              shifts={'兜帽_前': (-4, 0), '兜帽': (-4, 0), '側髮': (-5, 0), '麻花辮': (-3, 0), '瀏海': (3, 0),
                      '口腔': (-2.5, 0), '眉毛': (2, 0)},
              # face contour: (y from, y to, dx at the front edge) -- far brow / eye socket fill out forward,
              # nose stays, lips sink a little behind the contour, far cheek/jaw fill out
              face=[(150, 205, 8.0), (205, 226, 1.0), (226, 246, -1.5), (246, 262, 4.0)], face_from=40),      # (part, pivot, scale-y closed, scale-y open)
    breath=['胸腔', '馬甲', '斗篷', '斗篷結'],
)
