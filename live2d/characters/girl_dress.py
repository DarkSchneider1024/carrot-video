# -*- coding: utf-8 -*-
"""紫髮少女・平口洋裝版 (off-shoulder / strapless dress) — built on girl_v4 (the sailor-uniform girl).

Same face, hair, proportions and arms as girl_v4 (anime-girl-face / anime-girl-body rules). Changes:
  * sailor collar, scarf and sleeves removed -> bare shoulders, collarbones and upper arms (skin recolour)
  * blouse torso and bust layers become skin (the dress covers them below the straight neckline)
  * new: strapless bodice with a straight (平口) neckline, bust cups that follow the chest, white lace ruffle
    along the neckline, lavender choker, waist ribbon; the pleated skirt becomes the periwinkle dress skirt
Chest physics (Live2D Tips 04, VnNSFXYNQ04): RIG['chest'] -> Chest:: Sway X / Bounce Y / Squash, one
continuous warp field on skin + cups + bodice + trim, so the garment moves with the body (stage 4).
Nine-axis head (RIG['head3d']) like every puppet now.
"""
import numpy as np

import girl_v4 as G4
import red_hood as RH
from girl import Part, hx, M, smooth
from girl_v4 import R, Rell, CX, K, LW, SIDES, ID

DRESS, DRESS_SH, DRESS_DK, DRESS_HI, DRESS_LN = hx('b4c3f0'), hx('8c9fdc'), hx('6c7fc2'), hx('dde5fb'), hx('3e4a86')
RIB, RIB_SH, RIB_HI, RIB_LN = hx('9a82d6'), hx('7461b8'), hx('c3b3ef'), hx('3e2f7a')
LACE, LACE_SH, LACE_LN = hx('fbfbff'), hx('d9ddf0'), hx('8f95b0')
SKIN, SKIN_SH, SKIN_LN = G4.SKIN, G4.SKIN_SH, G4.SKIN_LN

# bigger bust than the uniform girl (user: too small to test the chest physics). girl_v4 reads these module
# globals inside build(), so setting them here only affects this character (each build runs in its own process).
G4.BUST_HW, G4.BUST_TOP, G4.BUST_BOT = 38.0, 32.0, 34.0      # user edit: the bust fills the whole chest
G4.BUST_DX = 35.0
G4.BUST_Y = G4.BUST_Y + 6.0
BX, BY = CX - G4.BUST_DX, G4.BUST_Y                     # right bust centre (reference px)
# hourglass side line (user sketch): full under the bust, curving in to the narrowest point just above the ribbon
# user edit: nearly straight from under the bust to the waist (the inverted triangle looked too brawny)
# user edit 2: waist half as thick ("Nami waist"): half-width 70 -> 40 at the ribbon, smooth S-curve from the ribs,
# the skirt flares straight back out to the original hips (skirt_warp)
WAIST_HW = 40.0
WAIST_CURVE = [(202, 366), (203, 380), (206, 393), (211.5, 405), (219.5, 417), (228.5, 429), (235.5, 441),
               (240.5, 453), (CX - WAIST_HW - 1.0, 465), (CX - WAIST_HW, 476)]
NECK_R = [(CX, 356, 'c'), (274, 353.5), (258, 350.5), (236, 349.5), (214, 351), (206, 353)]   # straight neckline


def neck_y(x):
    """neckline height at x (symmetric)"""
    xs = [p[0] for p in NECK_R][::-1]; ys = [p[1] for p in NECK_R][::-1]
    xm = x if x <= CX else 2 * CX - x
    return float(np.interp(xm, xs, ys))


LACE_BOT = 410.0                     # lace band ends just under the bust (scalloped edge)


def lace_bottom(x):
    """scalloped lower edge of the lace band"""
    return LACE_BOT + 2.2 * abs(np.sin((x - CX) / 7.0 * np.pi / 2))


def lace_rings(p, x0, x1, y_top_fn, y_bot_fn, Rf):
    """the lace motif on one lattice for every part (so the pattern lines up across layers): small rings with a
    dot, on a staggered grid; only inside [top(x), bottom(x)]"""
    step = 7.0
    for j, y in enumerate(np.arange(334.0, LACE_BOT + 4, step * 0.866)):
        off = (step / 2) if j % 2 else 0.0
        for x in np.arange(200.0 + off, 372.0, step):
            if not (x0 <= x <= x1) or not (y_top_fn(x) + 1.8 < y < y_bot_fn(x) - 1.8):
                continue
            ring = [(x + 2.1 * np.cos(a), y + 2.1 * np.sin(a)) for a in np.linspace(0, 2 * np.pi, 10)]
            p.line(Rf(ring), 0.7, hx('b9bfdd'), raw=True, clipped=True)
            p.cfill(Rf([(x - 0.6, y - 0.6), (x + 0.6, y - 0.6), (x + 0.6, y + 0.6), (x - 0.6, y + 0.6)]),
                    hx('c8cde6'), raw=True, blur=0.2)


def with_warp(fn):
    G4.WARP = G4.shoulder_warp
    try:
        return fn()
    finally:
        G4.WARP = None


def R0(pts):
    w = G4.WARP; G4.WARP = None
    try:
        return R(pts)
    finally:
        G4.WARP = w


# ------------------------------------------------------------------ anatomy (vrR2fITO-ZE): breasts sit on the ribcage
# and grow out of the pectoral -- sloped top rising toward the armpit (axillary tail), fuller bottom, each one
# tilted outward with the curve of the ribs; the top is the attachment, the bottom is the free mass
BUST_TILT = 0.14                                          # ~8 deg outward (rounder, user sketch)
ATTACH_Y = BY - G4.BUST_TOP * 0.55                        # pectoral attachment line (physics anchor)


def bust_shape(side):
    """closed outline in reference px (character's right = viewer's left; the left one is mirrored)"""
    hw, tp, bt = G4.BUST_HW, G4.BUST_TOP, G4.BUST_BOT
    local = [(0.5, -0.88), (0.0, -1.0), (-0.6, -0.93), (-0.98, -0.5),          # round top, easing toward the armpit
             (-1.05, 0.08), (-0.86, 0.68), (-0.36, 1.0), (0.24, 0.98), (0.74, 0.7), (1.0, 0.16), (0.92, -0.42)]
    c, s_ = np.cos(BUST_TILT), np.sin(BUST_TILT)
    out = []
    for q in local:
        u, v = q[0] * hw, q[1] * (tp if q[1] < 0 else bt)
        x, y = u * c - v * s_, u * s_ + v * c                       # bottom swings outward (-x on this side)
        out.append((BX + x, BY + y) + tuple(q[2:]))
    return out if side == 'R' else [(2 * CX - p_[0],) + tuple(p_[1:]) for p_ in out]


def bust_skin(side):
    """skin breast (replaces girl_v4's front-facing teardrop): only the top shows above the neckline"""
    p = Part(f'胸_{side}')
    pts = R0(bust_shape(side))
    p.fill(pts, SKIN)
    cx = BX if side == 'R' else 2 * CX - BX
    # no highlight on the upper slope: it would outline the layer on the skin; the slope must melt into the chest
    # repeat the torso's own airbrush tones (as girl_v4 does) so the layer has the exact skin tone underneath it
    def torso_air():
        for q, c, b in [([(240, 320), (330, 320), (330, 345), (240, 345)], hx('f6d6cc', 190), 10),
                        ([(262, 380), (310, 380), (310, 450), (262, 450)], hx('f7dcd3', 150), 10),
                        ([(225, 455), (346, 455), (346, 475), (225, 475)], hx('f3cdc2', 190), 6)]:
            p.air(R(q), c, blur=b)
        for g in (ID, M):
            p.cfill(g(R([(338, 330), (372, 300), (372, 480), (344, 480), (350, 400)])), SKIN_SH, blur=4)
    with_warp(torso_air)
    inner = [(cx + (8 if side == 'R' else -8), BY - 30), (CX, BY - 30), (CX, BY + 4)]
    p.air(R0(inner + [(cx + (14 if side == 'R' else -14), BY)]), hx('f0bdb0', 120), blur=8)   # soft cleavage shadow
    return p


# ------------------------------------------------------------------ recolour maps
def cmap(table):
    t = {k[:3]: v for k, v in table.items()}
    return lambda c: (t[c[:3]][:3] + (c[3],)) if c[:3] in t else c


SKIN_FROM_WHITE = cmap({G4.WHITE: SKIN, G4.WHITE_SH: SKIN_SH, G4.WHITE_LN: SKIN_LN,
                        hx('c7cbe3'): hx('f6d6cc'), hx('cfd2e8'): hx('f7dcd3'), hx('c9cde4'): hx('f3cdc2'),
                        hx('d0d4e8'): hx('f1c9be'), hx('d8dcec'): hx('f6d5cb'), hx('c3c7db'): hx('d9a596')})
DRESS_FROM_NAVY = cmap({G4.NAVY: DRESS, G4.NAVY_SH: DRESS_SH, G4.NAVY_HI: DRESS_HI, G4.NAVY_LN: DRESS_LN,
                        hx('141933'): hx('7d8fcf'), hx('1a2146'): hx('8596d4'), hx('45528c'): hx('e3e9fc'),
                        hx('3f4b84'): hx('c9d4f6'), hx('121731'): DRESS_DK})
RIB_FROM_NAVY = cmap({G4.NAVY: RIB, G4.NAVY_SH: RIB_SH, G4.NAVY_HI: RIB_HI, G4.NAVY_LN: RIB_LN})


def drop_cols(p, cols):
    keys = {c[:3] for c in cols}
    RH.drop_ops(p, lambda c: c[:3] in keys)


# ------------------------------------------------------------------ new parts
def bodice():
    def draw():
        p = Part('洋裝_上身')
        right = NECK_R + WAIST_CURVE + [(CX, 476)]
        pts = R(right + RH.mirror_list(right[1:-1]))
        p.fill(pts, DRESS)
        for g in (ID, M):
            p.air(g(R([(200, 350), (228, 350), (262, 474), (242, 474)])), DRESS_SH, blur=7)          # sides turn away
        xs = np.linspace(205, 2 * CX - 205, 60)
        band = R([(x, neck_y(x) - 1) for x in xs] + [(x, lace_bottom(x)) for x in xs[::-1]])
        p.cfill(band, LACE, raw=True, blur=0.2)                                                      # lace on top
        p.cfill(R([(200, 340), (228, 340), (232, 400), (206, 400)]), hx('c9cee8', 160), blur=5)
        p.cfill(M(R([(200, 340), (228, 340), (232, 400), (206, 400)])), hx('c9cee8', 160), blur=5)
        lace_rings(p, 200, 372, lambda x: neck_y(x), lace_bottom, R)
        p.line(R([(x, lace_bottom(x)) for x in xs]), 0.9, LACE_LN, raw=True, clipped=True)            # scalloped edge
        for g in (ID, M):                              # soft crescent under each bust
            arc = [(BX + dx, BY + G4.BUST_BOT * (0.62 + 0.38 * (1 - (dx / 34.0) ** 2)) + 2) for dx in np.linspace(-34, 30, 12)]
            p.air(g(R(arc + [(x, y + 11) for x, y in arc[::-1]])), hx('6f82c8', 170), blur=5)
        p.air(R([(CX - 4, 350), (CX + 4, 350), (CX + 3, 396), (CX - 3, 396)]), hx('8f9bcf', 150), blur=4)   # cleavage
        p.air(R([(262, 420), (309, 420), (309, 462), (262, 462)]), DRESS_HI, blur=10)                # light on the belly
        for y in (404, 412, 420):                                                                    # shirring
            p.line(R([(248, y), (268, y + 1.5), (CX, y + 2), (303, y + 1.5), (323, y)]), 0.8, DRESS_SH, clipped=True)
        p.line(R([(CX, 400), (CX, 472)]), 0.9, DRESS_SH, clipped=True)                                # centre seam
        p.line(pts, LW, DRESS_LN, closed=True)
        return p
    return with_warp(draw)


def cup(side):
    """lace over one bust (kept as its own layer for the chest physics). Same lace and pattern lattice as the
    bodice band, no outline and no round highlight -- the user found two visible round cups ugly."""
    f = ID if side == 'R' else M
    p = Part(f'洋裝_胸_{side}')
    hw, tp, bt = G4.BUST_HW + 1.5, G4.BUST_TOP, G4.BUST_BOT + 1.0
    pts = []
    for x, y in (q[:2] for q in smooth(bust_shape('R'), closed=True, n=8)):
        pts.append((x, min(max(y, neck_y(x) + 0.4), lace_bottom(x) - 0.3)))
    poly = f(R0(pts))
    p.fill(poly, LACE, raw=True)
    p.cfill(R([(200, 340), (228, 340), (232, 400), (206, 400)]), hx('c9cee8', 160), blur=5)       # same side shading
    p.cfill(M(R([(200, 340), (228, 340), (232, 400), (206, 400)])), hx('c9cee8', 160), blur=5)   # as the bodice
    B = lambda q: f(R0([(BX + a_, BY + b_) for a_, b_ in q]))
    # soft form only (no outline, no hard highlight): lower-outer turns away, upper-inner catches the light
    p.air(B([(-hw - 8, bt * 0.1), (hw * 0.2, bt * 0.5), (hw * 0.4, bt + 8), (-hw - 8, bt + 8)]), hx('aab3da', 150), blur=9)
    p.air(B([(hw * 0.35, -tp * 0.6), (hw + 6, -tp * 0.6), (hw + 6, bt * 0.8), (hw * 0.6, bt * 0.8)]), hx('b4bde2', 120), blur=7)
    p.air(B([(-hw * 0.4, -tp * 0.55), (hw * 0.35, -tp * 0.55), (hw * 0.25, -tp * 0.05), (-hw * 0.4, 0)]),
          hx('ffffff', 170), blur=8)
    xr = (BX - hw - 2, BX + hw + 2)
    if side == 'L':
        xr = (2 * CX - xr[1], 2 * CX - xr[0])
    lace_rings(p, xr[0], xr[1], lambda x: neck_y(x), lace_bottom, R0)
    return p


def ruffle():
    """white lace ruffle along the straight neckline (scalloped top edge)"""
    def draw():
        p = Part('洋裝_荷葉邊')
        xs = np.linspace(205, 2 * CX - 205, 25)
        top = []
        for i, x in enumerate(xs):
            y = neck_y(x)
            top.append((x, y - (4.8 if i % 2 else 2.2)))                                   # scallops
        bot = [(x, neck_y(x) + 3.2) for x in xs[::-1]]
        band = R(top + bot)
        p.fill(band, LACE, raw=False)
        p.cfill(R([(xs[0] - 5, 0), (xs[-1] + 5, 0), (xs[-1] + 5, 400), (xs[0] - 5, 400)]), hx('ffffff', 0))
        for x in xs[1:-1:2]:
            p.line(R([(x, neck_y(x) - 3.4), (x, neck_y(x) + 2.4)]), 0.7, LACE_SH)                 # gathers
        p.line(R([(x, neck_y(x) + 0.6) for x in xs]), 0.6, LACE_SH)
        p.line(band, LW * 0.8, LACE_LN, closed=True)
        return p
    return with_warp(draw)


def choker():
    p = Part('頸飾')
    band = R([(270.5, 281), (CX, 283.5), (300.5, 281), (300.5, 287), (CX, 289.5), (270.5, 287)])
    p.fill(band, RIB, line=RIB_LN, lw=LW * 0.8)
    p.air(R([(270, 280), (301, 280), (301, 284), (270, 284)]), RIB_HI, blur=1.5)
    p.fill(Rell(CX, 292.5, 2.6, 3.2), hx('f2e6ff'), line=RIB_LN, lw=0.7, raw=True)                    # small pearl
    return p


def waist_bow():
    p = Part('腰蝴蝶結')
    for g in (ID, M):
        loop = g(R([(CX - 2, 468), (272, 460), (264, 462), (262, 470), (266, 478), (274, 478)]))
        p.fill(loop, RIB, line=RIB_LN, lw=LW * 0.9)
        p.air(g(R([(262, 460), (276, 460), (276, 466), (262, 466)])), RIB_HI, blur=2)
        tail = g(R([(CX - 3, 472), (278, 492), (274, 506, 'c'), (280, 502), (284, 508, 'c'), (CX, 476)]))
        p.fill(tail, RIB, line=RIB_LN, lw=LW * 0.9)
    knot = R([(CX - 4, 464), (CX + 4, 464), (CX + 5, 471), (CX + 4, 478), (CX - 4, 478), (CX - 5, 471)])
    p.fill(knot, RIB_SH, line=RIB_LN, lw=LW * 0.9)
    return p


def smooth_shoulders(p):
    """the uniform's torso had two peaks beside the neck (hidden under the sailor collar); bare shoulders need a
    smooth trapezius slope: swap the base fill and the outline for a new outline"""
    right = [(CX, 292), (309, 284.5), (322, 289.5), (340, 295.5), (358, 302), (366, 318), (367, 350)] +             [(2 * CX - x + 1.0, y) for x, y in WAIST_CURVE[1:]] + [(CX, 476)]
    def draw():
        t = Part('tmp')
        pts = R(right + RH.mirror_list(right[1:-1]))
        t.fill(pts, SKIN)
        t.line(R(right[1:-1]), LW, SKIN_LN)
        t.line(M(R(right[1:-1])), LW, SKIN_LN)
        return t
    t = with_warp(draw)
    i_fill = next(i for i, op in enumerate(p.ops) if op[0] == 'fill')
    p.ops[i_fill] = t.ops[0]
    p.ops = [op for op in p.ops if not (op[0] == 'ink' and op[4])]      # old closed outline
    p.ops += t.ops[1:]


def skirt_warp(p, top=476.0, hip=540.0):
    """pull the skirt's top in to the narrow waist, easing back to the original width at the hips (below `hip`
    nothing changes) -- the straight skirt sides become a curved hip flare"""
    k0 = (WAIST_HW + 2.0) / 58.5                         # girl_v4 skirt top half-width is 58.5 (ref px)
    def f(q):
        x, y = q[0], q[1]
        yr = y / K                                        # design -> reference px (y has no offset)
        t = min(1.0, max(0.0, (yr - top) / (hip - top)))
        t = 1 - (1 - t) ** 2                              # ease-out: the hip rounds out quickly
        k = k0 + (1 - k0) * t
        return (500 + (x - 500) * k, y) + tuple(q[2:])
    out = []
    for op in p.ops:
        if len(op) > 1 and isinstance(op[1], list) and op[1] and isinstance(op[1][0], tuple):
            op = (op[0], [f(q) for q in op[1]]) + tuple(op[2:])
        elif len(op) > 1 and hasattr(op[1], 'shape'):
            a = np.array(op[1], dtype=float)
            a = np.array([f(tuple(r)) for r in a])
            op = (op[0], a) + tuple(op[2:])
        out.append(op)
    p.ops = out


# ------------------------------------------------------------------ assemble
DROP = {'背景色', '領子_後', '領子_R', '領子_L', '領巾_R', '領巾_L', '領巾尾_R', '領巾尾_L', '領巾結'}


def build():
    groups = G4.build()

    def fix(p):
        if p.name in ('胸腔',):
            drop_cols(p, [G4.NAVY])                                       # sailor dickey lines
            RH.recolor(p, SKIN_FROM_WHITE)
            if p.name == '胸腔':
                smooth_shoulders(p)
        elif p.name.startswith('上臂'):
            # sleeve -> bare shoulder: skin fill, no navy band / stripes / fold lines / sleeve outline
            drop_cols(p, [G4.NAVY, G4.STRIPE, hx('b6bbd2'), hx('c2c6da'), hx('e9ada0'), G4.WHITE_LN])
            RH.recolor(p, SKIN_FROM_WHITE)
        elif p.name.startswith('裙'):
            drop_cols(p, [G4.STRIPE])
            RH.recolor(p, DRESS_FROM_NAVY)
            skirt_warp(p)
        elif p.name == '腰':                       # ribbon band follows the narrowed waist (hourglass)
            def band():
                t = Part('tmp')
                right = [(CX, 464.5), (CX - WAIST_HW - 1.5, 463, 'c'), (CX - WAIST_HW - 0.5, 477.5, 'c'), (CX, 479)]
                pts = R(right + RH.mirror_list(right[1:-1]))
                t.fill(pts, RIB)
                t.air(R([(220, 472), (350, 472), (350, 482), (220, 482)]), RIB_SH, blur=4)
                t.air(R([(240, 460), (270, 460), (270, 467), (240, 467)]), RIB_HI, blur=4)
                t.line(pts, LW, RIB_LN, closed=True)
                return t
            p.ops = with_warp(band).ops

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
        items = walk(items)
        if name == '身體':
            body = []
            for p in items:
                body.append(p)
                if p.name == '脖子':
                    body.append(choker())
                if p.name == '胸_L':
                    body[-2:] = [bust_skin('R'), bust_skin('L')]           # anatomical shape (see bust_shape)
                    body += [bodice(), cup('R'), cup('L'), ruffle()]
                if p.name == '腰':
                    body.append(waist_bow())
                if p.name.startswith('上臂'):
                    # shoulder outline (the sleeve outline used to draw it)
                    f = ID if p.name.endswith('_R') else M
                    def add(p=p, f=f):
                        p.line(f(R([(214, 301), (198, 312), (187, 336), (182, 366), (185.5, 382)])), LW, SKIN_LN)
                    with_warp(add)
            new.append((name, body))
        else:
            new.append((name, items))
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
        '瀏海': (1, 14), '碎髮': (1, 12), '鬢角': (1, 9), '呆毛': (1, 16), '髮飾': (1, 15), '髮陰影': (1, 1),
        '眉毛': (1, 3), '鼻子': (1, 5), '高光': (1, 1.5), '眼': (1, 1), '上': (1, 1), '下': (1, 1),
        '口腔': (1, 1), '舌頭': (1, 1), '腮紅': (1, 0.5), '耳朵': (1, -4), '後髮': (-1, 2)}),
    hair_deform=['鬢角_R', '鬢角_L', '碎髮', '後髮_R', '後髮_L', '後髮內層_R', '後髮內層_L'],
    arm_parts={'R': ['上臂_R', '下臂_R', '手掌_R', '手指_R'], 'L': ['上臂_L', '下臂_L', '手掌_L', '手指_L']},
    arm_pivots=((205, 318), (193, 472), (176, 556)), arm_warp=G4.shoulder_warp,
    breath_scale=['胸腔', '胸_R', '胸_L', '洋裝_上身', '洋裝_胸_R', '洋裝_胸_L'],
    breath_lift=['洋裝_荷葉邊', '上臂_R', '上臂_L'],
    lifts=[{'param': 'Leg:: Right:: Step', 'parts': ['大腿_R', '小腿_R', '鞋_R'], 'dy': -14},
           {'param': 'Leg:: Left:: Step', 'parts': ['大腿_L', '小腿_L', '鞋_L'], 'dy': -14}],
    # chest physics (VnNSFXYNQ04): one warp field around both busts, applied to every part in that area
    chest=dict(centers=[(BX, BY), (2 * CX - BX, BY)], radius=(50, 54), sway=8.0, bounce=7.0, squash=0.10,
               attach_y=ATTACH_Y, free_y=BY + G4.BUST_BOT,      # anchored at the pectoral, free at the bottom
               parts=['胸腔', '胸_R', '胸_L', '洋裝_上身', '洋裝_胸_R', '洋裝_胸_L', '洋裝_荷葉邊']),
)
