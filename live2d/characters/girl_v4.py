# -*- coding: utf-8 -*-
"""Version 4: a fresh drawing of the reference character, built with the two
project skills (.claude/skills/anime-girl-face + live2d-psd):

    體塊 (landmarks, checked by face_check.py)  ->  五官 (derived from the landmarks)  ->  頭髮 (grouped, with volume)

Coordinates are REFERENCE-IMAGE pixels (572 x 1024), mapped into the engine's 1000 x 1667
design space by R():  x_u = 500 + (x - 285.5) * K,  y_u = y * K.
Only the character's right half (viewer's left) is written; the left half is mirrored.
"""
import json, math
import numpy as np

from girl import Part, hx, M, smooth, ellipse, arc, ribbon

K = 1.628
CX = 285.5


WARP = None          # optional (x, y) -> (x, y) body warp in reference px, applied by R()


def R(pts):
    out = []
    for p in pts:
        x, y = WARP(p[0], p[1]) if WARP else (p[0], p[1])
        out.append((500 + (x - CX) * K, y * K) + tuple(p[2:]))
    return out


def RP(x, y):
    return R([(x, y)])[0]


def Rell(x, y, rx, ry, n=64, rot=0):
    cx, cy = RP(x, y)
    return ellipse(cx, cy, rx * K, ry * K, n=n, rot=rot)


ID = lambda pts: pts
SIDES = (('R', ID), ('L', M))

# =================================================================== 1. 體塊 / landmarks
# Every facial feature below is derived from these numbers ("液化" = edit one value here).
SKULL = dict(cx=CX, cy=150.0, r=62.0)            # 籃球: the cranium
CHIN = 256.0                                      # 漏斗 tip
EYE_RATIO = 0.575                                 # girl: a little below the middle of the head
EYE_W = 40.0                                      # eye width
EYE_GAP = 28.0                                    # 0.7 eye width: moe front view (0.88 looked too wide-set)
HAIR_GAP_TOP, HAIR_GAP_SIDE = 18.0, 22.0          # hair volume: never glued to the scalp

SKULL_TOP = SKULL['cy'] - SKULL['r']
EYE_Y = round(SKULL_TOP + EYE_RATIO * (CHIN - SKULL_TOP), 1)
B = CHIN - EYE_Y
NOSE_Y = EYE_Y + B / 2
MOUTH_Y = EYE_Y + B / 2 + B / 6
EYE_R = (CX - EYE_GAP / 2 - EYE_W, CX - EYE_GAP / 2)
EYE_L = (CX + EYE_GAP / 2, CX + EYE_GAP / 2 + EYE_W)
EYE_CX_R = (EYE_R[0] + EYE_R[1]) / 2
EYE_CX_L = (EYE_L[0] + EYE_L[1]) / 2
BROW_Y = EYE_Y - 0.43 * B
EAR = (EYE_Y + 1, EYE_Y + 1 + B / 2)
HAIR_R = SKULL['r'] + HAIR_GAP_SIDE
HAIR_CY = SKULL['cy'] + (HAIR_GAP_SIDE - HAIR_GAP_TOP)       # so the top gap is HAIR_GAP_TOP
HAIR_TOP = HAIR_CY - HAIR_R
HAIRLINE_Y = (BROW_Y + HAIR_TOP) / 2

# ------------------------------------------------------------------- body 體塊 (人體篇: 胸腔 box, 胯 box, 肩寬)
HEAD_W = 2 * 62.0                                  # head unit = skull width
SHOULDER_Y, WAIST_Y, CROTCH_Y = 300.0, 470.0, 622.0
KNEE_Y, ANKLE_Y, SOLE_Y = 760.0, 940.0, 1003.0
SHOULDER_EXTRA = 12.0      # widen the shoulders: the drawn torso was only 1.17 head widths (target 1.3..1.6)
SHOULDER_HALF = 72.5 + SHOULDER_EXTRA              # torso half width at the shoulder line after widening
# bust (drawn WITHOUT the shoulder warp, so widening the shoulders doesn't spread it sideways)
BUST_Y = SHOULDER_Y + 0.36 * (WAIST_Y - SHOULDER_Y)  # apex about 1/3 down the chest box
BUST_DX = 26.5                                       # centre offset from the midline
BUST_HW, BUST_TOP, BUST_BOT = 25.0, 24.0, 24.0       # half width, extent above / below the apex (user: 再大一點)


def shoulder_warp(x, y):
    """Push the shoulders outward: full strength above ~y320, fading to zero at the waist;
    points near the centre line (neck) are left alone, so only the shoulder girdle widens."""
    t = min(1.0, max(0.0, (WAIST_Y - y) / (WAIST_Y - 320.0)))
    t = t * t * (3 - 2 * t)
    d = abs(x - CX)
    ramp = min(1.0, max(0.0, (d - 15.0) / 40.0))
    dx = SHOULDER_EXTRA * t * ramp
    return (x - dx if x < CX else x + dx), y


def body_landmarks():
    return dict(head_w=HEAD_W, head_h=CHIN - SKULL_TOP, skull_top=SKULL_TOP, chin=CHIN,
                shoulder_y=SHOULDER_Y, shoulder_w=2 * SHOULDER_HALF, waist_y=WAIST_Y, crotch_y=CROTCH_Y,
                knee_y=KNEE_Y, ankle_y=ANKLE_Y, sole_y=SOLE_Y, waist_w=2 * 58.0, hip_w=2 * 77.5,
                bust_y=BUST_Y, bust_dx=BUST_DX, bust_w=2 * BUST_HW)


# jaw: half-width at fraction t of B below the eye line (steep at the cheek, flat at the chin -> V face)
JAW_T = [(0.0, 59.0), (0.2, 58.0), (0.38, 54.5), (0.52, 49.5), (0.66, 41.5), (0.78, 32.0),
         (0.88, 21.0), (0.95, 11.0), (0.985, 4.0)]


def landmarks():
    return dict(skull_top=SKULL_TOP, chin=CHIN, center_x=CX, hair_top=HAIR_TOP,
                hair_side=[CX - HAIR_R, CX + HAIR_R], skull_side=[CX - SKULL['r'], CX + SKULL['r']],
                eye_y=EYE_Y, eye_R=list(EYE_R), eye_L=list(EYE_L), brow_y=BROW_Y, hairline_y=HAIRLINE_Y,
                nose_y=NOSE_Y, mouth_y=MOUTH_Y, ear_top=EAR[0], ear_bottom=EAR[1], style='girl',
                face_half_width_at_eye=JAW_T[0][1])


def jaw_R():
    return [(CX - hw, EYE_Y + t * B) for t, hw in JAW_T]


def face_outline():
    """Full face base: skull cap on top (hidden by hair), cheeks, V jaw, chin point."""
    cap = [(SKULL['cx'] + SKULL['r'] * math.cos(math.radians(a)), SKULL['cy'] + SKULL['r'] * math.sin(math.radians(a)))
           for a in np.linspace(-20, -160, 15)]                     # right -> top -> left
    left = [(CX - 60.5, SKULL['cy'] + 12), (CX - 59.5, EYE_Y - 12)] + jaw_R()
    right = [(2 * CX - x, y) for x, y in reversed(jaw_R())] + [(CX + 59.5, EYE_Y - 12), (CX + 60.5, SKULL['cy'] + 12)]
    return cap + left + [(CX, CHIN, 'c')] + right


def construction_image(path, scale=3):
    """體塊 sketch: basketball + funnel, cross lines, AB zones, feature marks."""
    from PIL import Image, ImageDraw
    x0, y0 = CX - 110, 50
    W_, H_ = 220 * scale, 240 * scale
    im = Image.new('RGB', (W_, H_), (252, 250, 246))
    d = ImageDraw.Draw(im)
    P = lambda x, y: ((x - x0) * scale, (y - y0) * scale)
    c = SKULL
    d.ellipse([*P(c['cx'] - c['r'], c['cy'] - c['r']), *P(c['cx'] + c['r'], c['cy'] + c['r'])], outline=(200, 120, 120), width=2)
    d.ellipse([*P(CX - HAIR_R, HAIR_CY - HAIR_R), *P(CX + HAIR_R, HAIR_CY + HAIR_R)], outline=(150, 130, 210), width=1)
    fo = [q[:2] for q in face_outline()]
    d.line([P(*q) for q in fo + fo[:1]], fill=(120, 60, 60), width=2)
    d.line([P(CX, SKULL_TOP - 20), P(CX, CHIN + 10)], fill=(90, 90, 90), width=1)
    for y, col, t in ((SKULL_TOP, (230, 160, 0), 'top'), (EYE_Y, (220, 0, 0), 'eye  A|B'),
                      (NOSE_Y, (0, 90, 220), 'nose B/2'), (MOUTH_Y, (160, 0, 200), 'mouth'),
                      (CHIN, (230, 160, 0), 'chin'), (BROW_Y, (120, 90, 60), 'brow'),
                      (HAIRLINE_Y, (150, 130, 210), 'hairline')):
        d.line([P(CX - 100, y), P(CX + 100, y)], fill=col, width=1)
        d.text(P(CX + 70, y - 5), t, fill=col)
    for a, b in (EYE_R, EYE_L):
        d.ellipse([*P(a, EYE_Y - 13), *P(b, EYE_Y + 13)], outline=(220, 0, 0), width=2)
    d.rectangle([*P(CX - 64, EAR[0]), *P(CX - 58, EAR[1])], outline=(0, 140, 0), width=2)
    im.save(path)


# =================================================================== palette
SKIN, SKIN_SH, SKIN_SH2, SKIN_LN = hx('fdefe7'), hx('f6d0c6'), hx('eeb6a8'), hx('c68a7e')
HAIR, HAIR_SH, HAIR_SH2, HAIR_HI, HAIR_LN = hx('cebcf3'), hx('ae98e3'), hx('9480cf'), hx('f6f1ff'), hx('866bb8')
BHAIR, BHAIR_IN = hx('c0adec'), hx('9c87d6')
WHITE, WHITE_SH, WHITE_LN = hx('fbfbfd'), hx('dcdfee'), hx('8f95b0')
NAVY, NAVY_SH, NAVY_HI, NAVY_LN = hx('2f3867'), hx('20284e'), hx('4b5892'), hx('141933')
STRIPE = hx('f4f5fb')
RED, RED_SH, RED_HI, RED_LN = hx('d9363f'), hx('a7232d'), hx('f37177'), hx('721520')
SOCK, SOCK_HI, SOCK_LN = hx('2a2735'), hx('5d5872'), hx('15131b')
SHOE, SHOE_HI, SHOE_SH, SHOE_LN = hx('6b3e28'), hx('b07e5c'), hx('46230f'), hx('2a130a')
IRIS_D, IRIS_M, IRIS_L, PUPIL = hx('1a5a66'), hx('2aa7a8'), hx('97f4e1'), hx('11373e')
EYE_LN, LASH, LID_LN = hx('36222a'), hx('281a1f'), hx('b3584f')
MOUTH, TONGUE, MOUTH_LN = hx('9a3f47'), hx('e98a92'), hx('9c4d4c')
LW = 1.5


# =================================================================== hair shapes (3. 頭髮)
def cap_arc(a0, a1, n=12):
    return [(CX + HAIR_R * math.cos(math.radians(a)), HAIR_CY + HAIR_R * math.sin(math.radians(a)))
            for a in np.linspace(a0, a1, n)]


EYE_TOP = EYE_Y - 17
# (top x, top y, tip x, tip y, width, bend) -- tips land on the lash line, the outer one runs beside the eye
FRINGE_R = [(224, 118, 224, EYE_Y + 16, 15, -4), (234, 104, 236, EYE_TOP - 2, 16, 5),
            (244, 96, 249, EYE_TOP + 8, 17, 6), (255, 92, 258, EYE_TOP - 4, 14, 4),
            (264, 90, 268, EYE_TOP + 5, 15, 4), (273, 89, 276, EYE_TOP - 3, 12, 2)]
FRINGE_C = [(280, 88, 281, EYE_TOP + 9, 12, 1.5), (285.5, 88, 286, EYE_TOP + 15, 11, 0),
            (291, 88, 290, EYE_TOP + 4, 12, -1.5)]


def strand_poly(tx, ty, ex, ey, w, bend):
    c = [(tx, ty), (tx + (ex - tx) * 0.3 + bend * 0.5, ty + (ey - ty) * 0.35),
         (tx + (ex - tx) * 0.7 + bend, ty + (ey - ty) * 0.72), (ex, ey)]
    return ribbon(R(c), [w * K, w * 0.97 * K, w * 0.7 * K, 0.4])


def fringe_shapes(which, mirror=False):
    if which == 'C':
        base = R(cap_arc(246, 294) + [(297, 120), (274, 120)])
        strands = [strand_poly(*q) for q in FRINGE_C]
    else:
        base = R(cap_arc(203, 254) + [(276, 120), (231, 124)])
        strands = [strand_poly(*q) for q in FRINGE_R]
    if mirror:
        base, strands = M(base), [M(q) for q in strands]
    return base, strands


def side_lock_R():               # 中髮: falls in front of the shoulder, outside the cheek
    return [(233, 104), (228, 150), (226.5, EYE_Y), (226, 230), (222, 280), (218, 330), (214, 368),
            (212, 402, 'c'), (208, 384), (203, 398, 'c'), (200, 360), (198, 305), (198, 250), (200, 195),
            (204, 145), (213, 112)]


def back_hair_R():               # 後髮: long, flared, soft layered tips
    return [(CX + 0.5, HAIR_TOP - 1, 'c'), (262, HAIR_TOP + 1), (236, 80), (214, 100), (202, 132),
            (194, 188), (185, 255), (172, 325), (158, 395), (146, 455), (138, 505), (133, 540),
            (140, 562, 'c'), (151, 548), (163, 574, 'c'), (177, 552), (192, 568, 'c'), (205, 540),
            (219, 558, 'c'), (231, 522), (258, 526), (CX + 0.5, 526, 'c')]


def back_inner_R():              # darker inner layer seen between the neck and the side locks
    return [(CX + 0.5, 150), (258, 158), (240, 210), (234, 300), (238, 400), (252, 470), (CX + 0.5, 480)]


# =================================================================== painting helpers
def hair_flow(p, focus, a0, a1, r0, r1, n, col, w, seed, jitter=0.35, bend_sd=0.02):
    rng = np.random.default_rng(seed)
    fx, fy = RP(*focus)
    for i in range(n):
        a = math.radians(a0 + (a1 - a0) * (i + rng.random() * 0.8) / n)
        ra = (r0 + (r1 - r0) * rng.random() * jitter) * K
        rb = (r1 - (r1 - r0) * rng.random() * jitter) * K
        bend = rng.normal(0, bend_sd)
        pts = [(fx + r * math.cos(a + bend * j), fy + r * math.sin(a + bend * j))
               for j, r in enumerate(np.linspace(ra, rb, 4))]
        p.strand(pts, w * (0.6 + 0.8 * rng.random()), col)


def gloss(p, seed):
    """Broad soft sheen + a few uneven streaks on the crown (not a comb)."""
    cx, cy = RP(CX, HAIR_CY + 2)
    outer = arc(cx, cy, (HAIR_R - 12) * K, 194, 346, 40)
    inner = arc(cx, cy + 2, (HAIR_R - 28) * K, 346, 194, 40)
    p.air(outer + inner, hx('f5f0ff', 185), blur=9, raw=True)
    rng = np.random.default_rng(seed)
    for ang in np.arange(204, 337, 16):
        a = math.radians(ang + rng.normal(0, 1.5))
        r_top = (HAIR_R - 14 + rng.random() * 5) * K
        r_bot = (HAIR_R - 22 - rng.random() * 8) * K
        pts = [(cx + r * math.cos(a), cy + r * math.sin(a)) for r in (r_top, (r_top + r_bot) / 2, r_bot)]
        p.strand(pts, 1.6 + rng.random() * 1.6, hx('fdfbff', 120 + int(rng.random() * 70)))


def outline_runs(p, pts, y_split, col_above, col_below, y_stop=None):
    """Side outlines split by colour at y_split (skin/sock etc.), none below y_stop."""
    outline = smooth(pts) + smooth(pts)[:1]
    ys, yb = RP(0, y_split)[1], (RP(0, y_stop)[1] if y_stop else 1e9)
    runs, cur = [], []
    for q in outline:
        key = 'a' if q[1] <= ys + 2 else ('b' if q[1] < yb else None)
        if cur and cur[0] != key:
            runs.append(cur); cur = []
        if not cur:
            cur = [key]
        cur.append(q)
    runs.append(cur)
    for r in runs:
        if r[0] and len(r) > 2:
            p.line(r[1:], LW, col_above if r[0] == 'a' else col_below, raw=True)


# =================================================================== 2. 五官
def eye(side):
    f = 1 if side == 'R' else -1
    cx, cy = (EYE_CX_R + 0.8, EYE_Y) if side == 'R' else (EYE_CX_L - 0.8, EYE_Y)
    SC = EYE_W / 44.0                           # the eye design below is 44 units wide
    VS = 1.1                                    # a little taller than wide-scaled: big moe eyes

    def E(pts):
        return R([(cx + f * q[0] * SC, cy + q[1] * SC * VS) + tuple(q[2:]) for q in pts])

    def Re(dx, dy, rx, ry):
        return Rell(cx + f * dx * SC, cy + dy * SC * VS, rx * SC, ry * SC * VS)

    parts = []
    p = Part(f'下眼皮_{side}')
    p.fill(E([(-22, 3), (-12, 13.5), (0, 17.5), (14, 12.5), (22, 2), (23, 7), (14, 16.5), (0, 20.5), (-13, 17.5), (-23, 8)]), SKIN)
    parts.append(p)
    p = Part(f'下眼線_{side}')
    p.rib(E([(-12, 14), (-2, 16.3), (8, 15), (14, 11)]), [0.3, 1.3, 1.1, 0.3], LID_LN)
    parts.append(p)
    p = Part(f'下睫毛_{side}')
    p.rib(E([(-18, 8), (-20.5, 11), (-22, 14)]), [1.4, 0.8, 0.2], LASH)
    p.rib(E([(-10, 14.5), (-11, 18)]), [0.9, 0.2], LASH)
    parts.append(p)
    p = Part(f'眼白_{side}')
    p.fill(E([(-22, 1), (-15, -10), (-4, -15), (8, -15), (17, -10), (21, -4), (20, 4), (13, 12),
              (2, 16), (-10, 14), (-18, 8)]), hx('ffffff'))
    p.cfill(E([(-30, -20), (30, -20), (30, -5), (0, -7), (-30, -4)]), hx('c9cde6'), blur=2.2)
    parts.append(p)
    p = Part(f'眼球_{side}')
    p.fill(Re(0, 1.5, 12.5, 15.5), IRIS_M, raw=True)
    p.air(Re(0, -7, 15, 8.5), IRIS_D, blur=3.0, raw=True)
    p.air(Re(0, 10, 9, 5.5), IRIS_L, blur=2.6, raw=True)
    for dx in (-6, -2.5, 2.5, 6):
        p.strand(E([(dx * 0.7, 3), (dx, 8), (dx * 1.15, 13)]), 1.3, hx('d6fff6', 170))
    p.cfill(Re(0, -1, 5.5, 8), PUPIL, raw=True, blur=1.0)
    p.air(Re(0, 12, 10, 4), hx('d8fff4', 150), blur=2.0, raw=True)          # bright rim at the bottom
    p.line(Re(0, 1.5, 12.5, 15.5), 1.0, hx('164b54'), closed=True, raw=True)
    parts.append(p)
    p = Part(f'上眼線_{side}')
    p.rib(E([(-23, 2.5), (-19, -5.5), (-11, -12), (0, -14.2), (10, -13.4), (17, -9.5), (21, -3)]),
          [3.0, 6.8, 8.2, 8.4, 7.6, 5.4, 1.8], EYE_LN, hardness=0.65, flow=0.5)
    p.rib(E([(-21, 3), (-12, -8), (0, -10.8), (10, -10.2), (17, -6.5)]), [0.6, 1.7, 1.9, 1.5, 0.4], LID_LN,
          hardness=0.5, flow=0.35)
    parts.append(p)
    p = Part(f'上眼皮_{side}')
    p.fill(E([(-25, 1), (-21, -9), (-12, -17), (0, -19.5), (11, -18.5), (18, -14), (23, -5),
              (25, -9), (19, -18), (11, -22), (0, -23), (-13, -21), (-23, -13), (-27, -3)]), SKIN)
    parts.append(p)
    p = Part(f'上睫毛_{side}')
    p.rib(E([(-19, -6), (-25, -8.5), (-29, -7)]), [3.8, 1.9, 0.3], LASH)
    p.rib(E([(-21, -1), (-27, 1), (-31, 4)]), [3.2, 1.6, 0.3], LASH)
    p.rib(E([(-14, -12), (-17, -17), (-18, -19)]), [2.0, 0.9, 0.2], LASH)
    p.rib(E([(-6, -14.5), (-7, -18.5)]), [1.4, 0.2], LASH)
    parts.append(p)
    p = Part(f'眼褶_{side}')
    p.rib(E([(-15, -19.5), (-5, -22.5), (7, -22.5), (15, -18.5)]), [0.3, 1.2, 1.1, 0.3], hx('b98480'))
    parts.append(p)
    p = Part(f'高光_{side}')
    p.fill(Re(-4, -7, 4.4, 4.8), hx('ffffff'), raw=True)
    p.fill(Re(-8, 9, 1.9, 1.9), hx('ffffff'), raw=True)
    p.fill(Re(6, 8, 1.2, 1.2), hx('ffffff', 220), raw=True)
    parts.append(p)
    return parts


# =================================================================== build
def build():
    G = []
    face = R(face_outline())

    # ---------------------------------------------------------------- background
    bg = []
    p = Part('背景色')
    p.fill([(0, 0), (1000, 0), (1000, 1667), (0, 1667)], hx('f8f0e8'), raw=True)
    for (x, y, rx, ry, c) in [(150, 250, 380, 420, hx('fdf8ee', 230)), (880, 520, 300, 260, hx('dde8dc', 190)),
                              (900, 1150, 420, 300, hx('f0cfd2', 210)), (120, 1350, 420, 260, hx('f4d9c8', 200)),
                              (620, 1500, 500, 200, hx('e8c4c8', 180)), (700, 180, 300, 180, hx('f7efe5', 200))]:
        p.air(ellipse(x, y, rx, ry), c, blur=60, raw=True)
    for (x, y, r, c) in [(120, 300, 40, hx('ffffff', 90)), (860, 380, 55, hx('ffffff', 80)), (900, 900, 35, hx('fff4f4', 90)),
                         (90, 1000, 50, hx('fff8f0', 80)), (820, 1300, 45, hx('ffffff', 70))]:
        p.air(ellipse(x, y, r, r), c, blur=6, raw=True)                    # soft bokeh
    bg.append(p)
    p = Part('影子')
    p.soft(Rell(CX, 1003, 90, 12), hx('b88b86', 150), 10)
    bg.append(p)
    G.append(('背景', bg))

    # ---------------------------------------------------------------- back hair (後髮) -- back layer first
    parts = []
    for side, f in SIDES:
        p = Part(f'後髮內層_{side}')
        pts = f(R(back_inner_R()))
        p.fill(pts, BHAIR_IN)
        p.air(f(R([(CX, 150), (250, 170), (245, 300), (260, 470), (CX, 480)])), hx('7d68bf', 160), blur=14)
        rng = np.random.default_rng(51 if side == 'R' else 52)
        for i in range(12):
            x0 = 240 + i * 4
            p.strand(f(R([(x0 + 4, 170), (x0, 300), (x0 + 2 + rng.normal(0, 3), 470)])), 1.3, hx('8670c4', 150))
        parts.append(p)
    for side, f in SIDES:
        p = Part(f'後髮_{side}')
        pts = f(R(back_hair_R()))
        p.fill(pts, BHAIR)
        p.cgrad(pts, hx('c0adec', 0), hx('9e88d6'), 260 * K, 560 * K)
        p.air(f(R([(CX, 180), (240, 200), (230, 350), (240, 480), (CX, 520)])), hx('8a74c4', 140), blur=18)
        p.air(f(R([(150, 380), (198, 300), (214, 330), (170, 450), (142, 520)])), hx('f4edff', 150), blur=14)
        if side == 'L':      # rim light on the shadow side
            p.air(M(R([(140, 400), (150, 400), (140, 540), (132, 540)])), hx('ffffff', 110), blur=6)
        rng = np.random.default_rng(21 if side == 'R' else 22)
        for i in range(36):
            x0 = 205 + i * 2.1 + rng.normal(0, 2)
            s_ = [(x0 + 10, 108 + rng.random() * 50), (x0 - 12, 250), (x0 - 40 - i * 1.4, 400),
                  (x0 - 62 - i * 1.6 + rng.normal(0, 4), 532 + rng.random() * 30)]
            p.strand(f(R(s_)), 1.2 + rng.random() * 0.8, hx('8a73c8', 120) if i % 2 else hx('f2ebff', 170))
        p.line(f(R(back_hair_R()))[:-1], LW, HAIR_LN)
        parts.append(p)
    G.append(('後髮', parts))

    # ---------------------------------------------------------------- body
    global WARP
    WARP = shoulder_warp          # 肩寬: only affects y < waist, far from the centre line
    body = []
    for side, f in SIDES:
        p = Part(f'小腿_{side}')
        pts = f(R([(229, 745, 'c'), (274, 745, 'c'), (272.5, 790), (271, 850), (268, 900), (266, 930), (265, 944),
                   (240, 944), (240, 930), (235.5, 900), (229.5, 850), (227, 790)]))
        p.fill(pts, SOCK)
        p.cfill(f(R([(231.5, 740), (238.5, 740), (241, 850), (243, 940), (238, 940), (234, 850)])), SOCK_HI, blur=3)
        p.cfill(f(R([(265, 740, 'c'), (280, 740, 'c'), (280, 944, 'c'), (262, 944, 'c'), (264, 860)])), hx('1b1924'), blur=3)
        p.air(f(R([(236, 800), (250, 800), (250, 850), (236, 850)])), hx('6a6582', 90), blur=8)      # calf roundness
        p.line(pts, LW, SOCK_LN, closed=True)
        body.append(p)

    for side, f in SIDES:
        p = Part(f'鞋_{side}')
        pts = f(R([(240, 938), (265, 938), (272, 951), (277.5, 970), (278.5, 988), (273, 1000), (257, 1004.5),
                   (241, 1002), (233.5, 991), (232.5, 971), (234.5, 951)]))
        p.fill(pts, SHOE)
        p.cfill(f(R([(238, 938), (268, 938), (268, 949), (238, 949)])), hx('3a1d0e'), blur=1.5)    # opening / shadow of the sock
        p.cfill(f(R([(222, 994), (292, 994), (292, 1010), (222, 1010)])), SHOE_SH, blur=2)
        p.air(f(R([(260, 955), (280, 955), (280, 995), (260, 995)])), hx('4f2915', 150), blur=6)   # shadow side
        p.cfill(f(R([(239, 968), (245, 963), (248, 987), (242, 992)])), SHOE_HI, blur=2.5)         # toe highlight
        p.line(f(R([(234, 958), (246, 954.5), (261, 954.5), (275, 959)])), 1.2, SHOE_LN)          # strap
        p.line(f(R([(245.5, 963), (254.5, 960), (263.5, 963), (254.5, 966.5), (245.5, 963)])), 0.9, SHOE_LN)
        p.line(f(R([(235, 991), (245, 998), (258, 1000), (272, 996)])), 0.9, hx('3b1d0e'))         # sole edge
        p.line(pts, LW, SHOE_LN, closed=True)
        body.append(p)

    for side, f in SIDES:
        p = Part(f'大腿_{side}')
        pts = f(R([(208, 585), (281, 585), (280, 620), (279, 660), (277, 700), (275.5, 740), (274, 772, 'c'),
                   (229, 772, 'c'), (229, 735), (226, 700), (219, 660), (212, 620)]))
        p.fill(pts, SKIN)
        p.cfill(f(R([(268, 585), (284, 585), (284, 662), (270, 662)])), SKIN_SH, blur=3)
        p.air(f(R([(205, 585), (285, 585), (285, 628), (205, 628)])), hx('e8aea0', 190), blur=12)
        p.air(f(R([(222, 628), (236, 628), (236, 655), (222, 655)])), hx('ffffff', 120), blur=6)    # skin sheen
        sock = f(R([(200, 659, 'c'), (225, 660.5), (255, 662), (286, 663, 'c'), (286, 790, 'c'), (200, 790, 'c')]))
        p.cfill(sock, SOCK, blur=0.3)
        p.cfill(f(R([(227, 675, 'c'), (234, 675, 'c'), (239.5, 790, 'c'), (232.5, 790, 'c')])), SOCK_HI, blur=3)
        p.cfill(f(R([(266, 675, 'c'), (286, 675, 'c'), (286, 790, 'c'), (265, 790, 'c')])), hx('1b1924'), blur=3)
        # knee: soft rounded highlight and a small crease (the reference has a visible knee)
        p.air(f(R([(240, 738), (262, 738), (262, 758), (240, 758)])), hx('57536c', 150), blur=5)
        p.line(f(R([(242, 762), (251, 765), (261, 762)])), 0.9, hx('141219', 200), clipped=True)
        p.line(f(R([(219, 665), (240, 667), (258, 668), (278, 668)])), 1.0, hx('4a465c'), clipped=True)
        outline_runs(p, pts, 660, SKIN_LN, SOCK_LN, y_stop=760)
        body.append(p)

    p = Part('裙_後')
    back = R([(232, 480), (340, 480), (400, 612), (382, 620), (CX, 626), (190, 620), (172, 612)])
    p.fill(back, NAVY_SH)
    p.air(R([(170, 590), (400, 590), (400, 630), (170, 630)]), hx('121731', 200), blur=6)
    p.line(back, LW, NAVY_LN, closed=True)
    body.append(p)

    p = Part('領子_後')                   # drawn BEHIND the neck; only its sides show
    back_collar = R([(226, 290), (240, 281), (254, 274), (262, 270.5), (CX, 269), (309, 270.5), (317, 274),
                     (331, 281), (345, 290), (345, 306), (226, 306)])
    p.fill(back_collar, NAVY)
    p.air(R([(250, 266), (321, 266), (321, 300), (250, 300)]), hx('141a36', 220), blur=5)   # inside of the collar, in shadow
    p.air(R([(226, 282), (250, 282), (250, 296), (226, 296)]), NAVY_HI, blur=6)
    p.air(M(R([(226, 282), (250, 282), (250, 296), (226, 296)])), NAVY_HI, blur=6)
    p.line(R([(226, 290), (240, 281), (254, 274), (262, 270.5), (CX, 269)]), LW, NAVY_LN)
    p.line(M(R([(226, 290), (240, 281), (254, 274), (262, 270.5), (CX, 269)])), LW, NAVY_LN)
    body.append(p)

    p = Part('脖子')
    ny0 = MOUTH_Y - 6                                   # neck extends up to mouth height (Live2D)
    neck = R([(271, ny0), (300, ny0), (299.5, 272), (303, 290), (309, 300), (300, 310), (271, 310), (262, 300),
              (268, 290), (271.5, 272)])
    p.fill(neck, SKIN, raw=True)
    p.cfill(R([(262, ny0), (309, ny0), (309, CHIN - 6), (298, CHIN + 1), (CX, CHIN + 7), (273, CHIN + 1), (262, CHIN - 6)]),
            SKIN_SH, blur=2.5)
    p.air(R([(262, 272), (309, 272), (309, 288), (262, 288)]), hx('eeb4a6', 150), blur=6)      # shadow under the jaw/collar
    p.air(R([(262, 300), (309, 300), (309, 312), (262, 312)]), hx('f0bdb1', 140), blur=4)
    p.air(R([(266, 262), (276, 262), (276, 300), (266, 300)]), hx('e9b3a8', 140), blur=5)       # hair shadow
    p.air(M(R([(266, 262), (276, 262), (276, 300), (266, 300)])), hx('e9b3a8', 140), blur=5)
    p.line(R([(271.5, 262), (270.5, 280), (266, 294)]), LW * 0.9, SKIN_LN)
    p.line(M(R([(271.5, 262), (270.5, 280), (266, 294)])), LW * 0.9, SKIN_LN)
    for g in (ID, M):                                  # collarbones
        p.line(g(R([(271, 294.5), (277, 297.5), (283.5, 296.5)])), 0.9, hx('d9a092'))
    body.append(p)

    p = Part('胸腔')
    torso = R([(250, 279), (240, 292), (213, 301), (205, 318), (208, 350), (213, 385), (220, 420),
               (225.5, 446), (227.5, 462), (227, 472), (344, 472), (343.5, 462), (345.5, 446), (351, 420),
               (358, 385), (363, 350), (366, 318), (358, 301), (331, 292), (321, 279), (308, 297), (298, 301.5),
               (CX, 303.5, 'c'), (273, 301.5), (263, 297)])
    p.fill(torso, WHITE)
    for g in (ID, M):
        p.cfill(g(R([(338, 330), (372, 300), (372, 480), (344, 480), (350, 400)])), WHITE_SH, blur=4)
    AIR_TORSO = [([(240, 320), (330, 320), (330, 345), (240, 345)], hx('c7cbe3', 190), 10),
                 ([(262, 380), (310, 380), (310, 450), (262, 450)], hx('cfd2e8', 150), 10),
                 ([(225, 455), (346, 455), (346, 475), (225, 475)], hx('c9cde4', 190), 6)]
    for q, c, b in AIR_TORSO:
        p.air(R(q), c, blur=b)
    for dy in (4.5, 10.5):                              # dickey: two navy lines following the neckline curve
        p.line(R([(262, 299 + dy), (273, 302.5 + dy), (CX, 305 + dy), (298, 302.5 + dy), (309, 299 + dy)]), 2.6, NAVY,
               clipped=True)
    p.line(torso, LW, WHITE_LN, closed=True)
    # (no fold lines on the blouse: thin diagonal strokes read as abdominal muscles, not cloth — user feedback)
    body.append(p)

    def R0(pts):                           # R() without the shoulder warp
        w = globals()['WARP']
        globals()['WARP'] = None
        try:
            return R(pts)
        finally:
            globals()['WARP'] = w

    for side, f in SIDES:
        p = Part(f'胸_{side}')
        bx, by = CX - BUST_DX, BUST_Y
        B_ = lambda pts: f(R0([(bx + dx, by + dy) + tuple(rest) for dx, dy, *rest in pts]))
        hw, tp, bt = BUST_HW, BUST_TOP, BUST_BOT
        # soft teardrop: flat top that melts into the chest, fuller rounded bottom
        shape = [(-hw, 3), (-hw * 0.85, -tp * 0.45), (-hw * 0.35, -tp * 0.9), (hw * 0.35, -tp), (hw * 0.85, -tp * 0.5),
                 (hw, 2), (hw * 0.78, bt * 0.72), (hw * 0.2, bt), (-hw * 0.45, bt * 0.9), (-hw * 0.88, bt * 0.55)]
        p.fill(B_(shape), WHITE)
        for q, c, b in AIR_TORSO:              # same airbrush as the torso so the layer blends in
            p.air(R(q), c, blur=b)
        # form comes from shading only (a clipped highlight showed the layer's top edge under the collar)
        p.air(B_([(-hw - 4, bt * 0.2), (hw + 4, bt * 0.2), (hw + 4, bt + 6), (-hw - 4, bt + 6)]), hx('d0d4e8', 185), blur=6)  # underside
        p.air(B_([(-hw - 6, -tp * 0.2), (-hw * 0.6, -tp * 0.2), (-hw * 0.6, bt), (-hw - 6, bt)]), hx('d8dcec', 150), blur=6)   # outer side
        # only a short, faint fold on the lower-outer edge (a full outline reads like underwear)
        p.line(B_([(-hw * 0.95, bt * 0.35), (-hw * 0.7, bt * 0.78), (-hw * 0.2, bt * 0.98)]), 0.8, hx('c3c7db', 200))
        body.append(p)

    p = Part('腰')
    waist = R([(227, 462, 'c'), (256, 464), (CX, 464.5), (315, 464), (344, 462, 'c'), (345.5, 477, 'c'),
               (315, 478.5), (CX, 479), (256, 478.5), (225.5, 477, 'c')])
    p.fill(waist, NAVY)
    p.air(R([(220, 470), (350, 470), (350, 482), (220, 482)]), NAVY_SH, blur=4)
    p.air(R([(240, 458), (270, 458), (270, 466), (240, 466)]), NAVY_HI, blur=5)
    p.line(waist, LW, NAVY_LN, closed=True)
    body.append(p)

    TOP, HEM = 476, 612
    NP = 11

    def sx(t, y):
        top = 227 + 118 * t; bot = 172 + 228 * t
        return top + (bot - top) * (y - TOP) / (HEM - TOP)

    def hy(t):
        frac = t * NP - math.floor(t * NP)
        return HEM + 5 * math.sin(math.pi * t) + (1.2 if 0.35 < frac < 0.65 else 0)

    def slice_(t0, t1):
        n = max(2, int(round((t1 - t0) * 40)))
        bottom = [(sx(t0 + (t1 - t0) * i / n, HEM), hy(t0 + (t1 - t0) * i / n)) for i in range(n + 1)]
        return [(sx(t0, TOP), TOP), (sx(t1, TOP), TOP)] + bottom[::-1]

    def skirt_piece(name, t0, t1):
        p = Part(name)
        pts = R(slice_(t0, t1))
        p.fill(pts, NAVY, raw=True)
        p.air(R([(160, TOP - 5), (420, TOP - 5), (420, TOP + 22), (160, TOP + 22)]), hx('141933', 190), blur=8)
        for g in (ID, M):
            p.air(g(R([(160, 520), (230, 520), (230, 620), (160, 620)])), hx('1a2146', 150), blur=16)
        p.air(R([(250, 560), (300, 560), (300, 600), (250, 600)]), hx('45528c', 110), blur=14)   # light on the front
        for kk in range(NP + 1):
            t = kk / NP
            tb = t + 0.35 / NP
            if t < t1 + 1e-6 and tb > t0 - 1e-6:
                q = R([(sx(t, TOP + 12), TOP + 12), (sx(tb, TOP + 12), TOP + 12),
                       (sx(tb, HEM + 12), HEM + 12), (sx(t, HEM + 12), HEM + 12)])
                p.cfill(q, NAVY_SH, raw=True, blur=1.6)
                q2 = R([(sx(t + 0.55 / NP, TOP + 18), TOP + 18), (sx(t + 0.75 / NP, TOP + 18), TOP + 18),
                        (sx(t + 0.75 / NP, HEM), HEM), (sx(t + 0.55 / NP, HEM), HEM)])
                p.cfill(q2, hx('3f4b84', 150), raw=True, blur=2.5)
            if t0 + 1e-6 < t < t1 - 1e-6:
                p.line(R([(sx(t, TOP + 4), TOP + 4), (sx(t, HEM), hy(t))]), 1.1, NAVY_LN, raw=True, clipped=True)
        for off in (8, 14):
            stripe = R([(sx(t0 + (t1 - t0) * i / 24, HEM - off), HEM + 5 * math.sin(math.pi * (t0 + (t1 - t0) * i / 24)) - off)
                        for i in range(25)])
            p.line(stripe, 2.3, STRIPE, raw=True, clipped=True)
        p.line(pts + pts[:1], LW, NAVY_LN, raw=True)
        return p

    body.append(skirt_piece('裙_R', 0.0, 0.38))
    body.append(skirt_piece('裙_L', 0.62, 1.0))
    body.append(skirt_piece('裙_中', 0.3, 0.7))

    for side, f in SIDES:
        p = Part(f'領巾_{side}')
        pts = f(R([(238, 318), (256, 322), (272, 340), (283, 362), (276, 368), (258, 350), (240, 332)]))
        p.fill(pts, RED)             # flat colour: no shading on the scarf for now (user feedback)
        p.line(pts, LW, RED_LN, closed=True)
        body.append(p)
    for side, f in SIDES:
        p = Part(f'領巾尾_{side}')
        pts = f(R([(281, 372), (272, 392), (262, 420), (256, 442, 'c'), (268, 432), (278, 440, 'c'),
                   (284, 410), (288, 378)]))
        p.fill(pts, RED)
        p.line(f(R([(279, 385), (272, 410), (268, 430)])), 0.9, RED_LN)
        p.line(pts, LW, RED_LN, closed=True)
        body.append(p)
    p = Part('領巾結')
    knot = R([(277, 360), (294, 360), (298, 370), (294, 381), (277, 381), (273, 370)])
    p.fill(knot, RED)
    p.line(R([(281, 362), (283, 380)]), 0.8, RED_LN)
    p.line(knot, LW, RED_LN, closed=True)
    body.append(p)

    for side, f in SIDES:
        p = Part(f'領子_{side}')
        pts = f(R([(255.5, 272, 'c'), (240, 283), (216, 297), (205, 309), (220, 318), (246, 330), (268, 344),
                   (CX, 360, 'c'), (280, 335), (273, 320), (265.5, 304), (259.5, 288)]))
        p.fill(pts, NAVY)
        p.air(f(R([(215, 296), (262, 296), (262, 312), (215, 312)])), NAVY_HI, blur=8)
        p.cfill(f(R([(255, 272), (268, 272), (290, 360), (270, 330), (258, 296)])), NAVY_SH, blur=2.5)
        for off in (4.5, 8.5):
            p.line(f(R([(209, 309 - off * 0.6), (222, 318 - off), (247, 330 - off), (269, 344 - off), (283, 356 - off)])),
                   1.7, STRIPE, clipped=True)
        p.line(pts, LW, NAVY_LN, closed=True)
        body.append(p)

    # arm silhouette measured on the reference: slim, hanging slightly outward, elbow ~y470, wrist ~y556
    ARM_OUT = [(186, 382), (184.5, 420), (183, 455), (180, 490), (175, 520), (169, 548), (166, 560)]
    ARM_IN = [(213, 382), (210, 420), (206, 455), (200, 488), (193, 518), (187, 546), (185.5, 560)]

    ARM_SHADE = [(203, 340), (216, 340), (214, 420), (208, 460), (201, 495), (193, 530), (188, 575),
                 (176, 575), (184, 530), (192, 495), (199, 460), (204, 420)]

    def arm_poly(y0, y1):
        o = [q for q in ARM_OUT if y0 <= q[1] <= y1]
        i = [q for q in ARM_IN if y0 <= q[1] <= y1]
        return o, i

    for side, f in SIDES:
        p = Part(f'上臂_{side}')
        o, i = arm_poly(380, 490)
        o = [(186.5, 372)] + o + [(179.5, 494)]
        i = [(213.5, 372)] + i + [(199, 494)]
        p.fill(f(R(o + i[::-1])), SKIN)
        p.cfill(f(R(ARM_SHADE)), SKIN_SH, blur=3)
        p.air(f(R([(184, 398), (214, 398), (214, 418), (184, 418)])), hx('e9ada0', 170), blur=6)   # under the sleeve
        # sides only (the forearm continues below). The stroke runs to the layer's bottom so it OVERLAPS the
        # forearm's stroke: two tapered ends meeting at one point leave a gap in the outline at the elbow.
        p.line(f(R(o[1:])), LW, SKIN_LN)
        p.line(f(R(i[1:])), LW, SKIN_LN)
        sleeve = f(R([(214, 300), (198, 312), (187, 336), (181, 366), (181, 392), (196, 399), (212, 398),
                      (219, 370), (217, 330)]))
        p.fill(sleeve, WHITE)
        p.cfill(f(R([(205, 300), (224, 300), (222, 400), (206, 400), (214, 350)])), WHITE_SH, blur=3)
        p.cfill(f(R([(176, 385), (224, 383), (224, 402), (176, 402)])), NAVY, blur=0.3)
        for yy in (389.5, 394):
            p.line(f(R([(179, yy - 1), (198, yy + 1), (220, yy)])), 1.3, STRIPE, clipped=True)
        p.line(f(R([(191, 330), (188, 350), (191, 368)])), 0.9, hx('b6bbd2'))
        p.line(f(R([(200, 340), (203, 360)])), 0.8, hx('c2c6da'))
        p.line(sleeve, LW, WHITE_LN, closed=True)
        body.append(p)

    for side, f in SIDES:
        p = Part(f'下臂_{side}')
        o, i = arm_poly(472, 560)
        o = [(182.2, 470)] + o + [(165, 566)]
        i = [(203.5, 470)] + i + [(186, 566)]
        p.fill(f(R(o + i[::-1])), SKIN)
        p.cfill(f(R(ARM_SHADE)), SKIN_SH, blur=3)
        p.air(f(R([(178, 505), (186, 505), (179, 548), (172, 548)])), hx('ffffff', 100), blur=4)   # soft skin sheen
        p.line(f(R([(197, 468), (201.5, 473)])), 0.8, SKIN_LN)                                    # elbow crease
        p.line(f(R(o)), LW, SKIN_LN)                           # sides only, overlapping the upper-arm stroke
        p.line(f(R(i)), LW, SKIN_LN)
        body.append(p)

    for side, f in SIDES:
        p = Part(f'手掌_{side}')
        # hand seen from the thumb side, relaxed, fingers pinching the skirt hem
        palm = f(R([(167, 552), (185.5, 553), (189, 565), (189.5, 578), (185.5, 588), (176, 592), (166.5, 590),
                    (162.5, 581), (163, 566)]))
        p.fill(palm, SKIN)
        p.cfill(f(R([(181, 550), (196, 550), (194, 598), (182, 598)])), SKIN_SH, blur=2.2)
        p.air(f(R([(162, 572), (174, 572), (174, 590), (162, 590)])), hx('f7c3b9', 130), blur=4)
        p.line(f(R([(166, 558), (163, 569), (162.5, 581), (166, 589)])), LW * 0.9, SKIN_LN)       # back of the hand
        p.line(f(R([(186, 556), (189.5, 567), (190.5, 580)])), LW * 0.9, SKIN_LN)
        thumb = [(187, 568), (192, 574), (195.5, 584), (195, 593), (191, 597), (187.5, 591), (185, 580)]
        p.fill(f(R(thumb)), SKIN)
        p.cfill(f(R([(191, 572), (199, 572), (199, 600), (191, 600)])), SKIN_SH, blur=1.4)
        p.air(f(R([(188, 589), (197, 589), (197, 598), (188, 598)])), hx('f3a9a1', 150), blur=2.5)
        p.line(f(R(thumb)), LW * 0.85, SKIN_LN, closed=True)
        body.append(p)

    for side, f in SIDES:
        p = Part(f'手指_{side}')
        # rounded tapered fingers drawn as brush strokes (outline stroke + skin stroke), curling toward the body
        FINGERS = [([(166, 585), (165, 594), (167, 601), (170, 604)], 4.2),
                   ([(171.5, 587), (171, 597), (173.5, 605), (177, 608)], 4.6),
                   ([(177, 587), (177.5, 596), (180, 603), (183, 605)], 4.4),
                   ([(182, 585), (183.5, 592), (185.5, 597), (188, 598.5)], 3.8)]
        for pts, w in FINGERS:
            c = f(R(pts))
            p.rib(c, [w * K + 2.2, w * K + 2.0, w * 0.92 * K + 1.8, w * 0.7 * K + 1.4], SKIN_LN, hardness=0.7, flow=0.8)
            p.rib(c, [w * K, w * K * 0.98, w * 0.9 * K, w * 0.66 * K], SKIN, hardness=0.8, flow=0.9)
        for pts, w in FINGERS:                                   # warm tips + light knuckle shading
            tip = f(R([pts[-2], pts[-1]]))
            p.rib(tip, [w * 0.55 * K, w * 0.45 * K], hx('f5b0a6', 160), hardness=0.4, flow=0.35)
            p.rib(f(R([pts[1], pts[2]])), [w * 0.3 * K, w * 0.2 * K], hx('efbdb1', 120), hardness=0.4, flow=0.3)
        body.append(p)
    WARP = None
    G.append(('身體', body))

    # ---------------------------------------------------------------- head
    head = []
    for side, f in SIDES:
        p = Part(f'耳朵_{side}')
        ex0 = CX - 59
        pts = f(R([(ex0 + 2, EAR[0] + 2), (ex0 - 6, EAR[0] - 1), (ex0 - 10, EAR[0] + 8), (ex0 - 9, EAR[0] + 22),
                   (ex0 - 5, EAR[1] - 4), (ex0 + 2, EAR[1]), (ex0 + 5, EAR[1] - 8)]))
        p.fill(pts, SKIN, line=SKIN_LN, lw=LW)
        p.rib(f(R([(ex0 - 5, EAR[0] + 6), (ex0 - 6, EAR[0] + 18), (ex0 - 2, EAR[1] - 8)])), [0.3, 1.3, 0.3], SKIN_SH2)
        head.append(p)

    p = Part('臉')
    p.fill(face, SKIN)
    p.air(R([(CX - 20, 118), (CX + 20, 118), (CX + 20, 150), (CX - 20, 150)]), hx('fff7f2', 160), blur=10)   # forehead light
    head.append(p)

    p = Part('臉陰影')
    p.clip(face)
    jaw_in = [(x + 3, y + 1) for x, y in jaw_R()]
    shade = [(CX - 70, EYE_Y - 4), (CX - 57, EYE_Y - 4)] + jaw_in[1:] + [(CX, CHIN + 2), (CX, CHIN + 20), (CX - 70, CHIN + 20)]
    p.cfill(R(shade), SKIN_SH, blur=2.2)
    p.cfill(M(R(shade)), SKIN_SH, blur=2.2)
    head.append(p)

    p = Part('臉線')
    jaw_line = [(CX - 59.5, EYE_Y - 14)] + jaw_R() + [(CX, CHIN)] + [(2 * CX - x, y) for x, y in reversed(jaw_R())] + [(CX + 59.5, EYE_Y - 14)]
    n = len(jaw_line)
    widths = [0.3] + [1.2 + 0.9 * math.sin(math.pi * i / (n - 1)) for i in range(1, n - 1)] + [0.3]
    widths = [w * (1.08 if i > n // 2 else 1.0) for i, w in enumerate(widths)]        # shadow side a bit heavier
    p.rib(R(jaw_line), widths, SKIN_LN, hardness=0.5, flow=0.42)
    head.append(p)

    p = Part('鼻子')
    p.air(R([(CX - 4, NOSE_Y - 10), (CX + 3, NOSE_Y - 10), (CX + 3, NOSE_Y - 2), (CX - 4, NOSE_Y - 2)]), hx('f5d2c8', 150), blur=3)
    p.rib(R([(CX + 0.1, NOSE_Y - 1.2), (CX + 0.7, NOSE_Y + 0.8)]), [1.5, 0.6], hx('c9897f'))
    head.append(p)

    for name, which, mir in (('髮陰影_R', 'R', False), ('髮陰影_中', 'C', False), ('髮陰影_L', 'R', True)):
        p = Part(name)
        p.clip(face)
        base, strands = fringe_shapes(which, mir)
        for q in [base] + strands:
            p.cfill([(x, y + 3.5 * K) for x, y in q], hx('f3cbbf', 200), raw=True, blur=1.8)
        head.append(p)

    mouth = []
    my = MOUTH_Y
    # closed smile, like the reference: one soft curve. The Live2D open-mouth parts sit INSIDE
    # the lip stroke, so they exist for the modeller but don't read as bared teeth when closed.
    p = Part('下唇陰影')
    p.rib(R([(CX - 2.8, my + 3.6), (CX, my + 4.2), (CX + 2.8, my + 3.6)]), [0.2, 0.9, 0.2], hx('f6d2ca', 150))
    mouth.append(p)
    p = Part('口腔')
    p.fill(R([(CX - 3.2, my - 0.55), (CX, my - 0.2), (CX + 3.2, my - 0.55), (CX + 2.6, my + 0.15), (CX, my + 0.45),
              (CX - 2.6, my + 0.15)]), MOUTH)
    mouth.append(p)
    p = Part('舌頭')
    p.fill(R([(CX - 1.4, my + 0.1), (CX, my), (CX + 1.4, my + 0.1), (CX + 0.8, my + 0.35), (CX - 0.8, my + 0.35)]), TONGUE)
    mouth.append(p)
    p = Part('下排牙齒')
    p.fill(R([(CX - 1.6, my + 0.05), (CX + 1.6, my + 0.05), (CX + 1.4, my + 0.25), (CX - 1.4, my + 0.25)]), hx('fafafa'), raw=True)
    mouth.append(p)
    p = Part('上排牙齒')
    p.fill(R([(CX - 2.2, my - 0.35), (CX + 2.2, my - 0.35), (CX + 1.9, my - 0.1), (CX - 1.9, my - 0.1)]), hx('ffffff'), raw=True)
    mouth.append(p)
    p = Part('上唇')
    p.rib(R([(CX - 9.5, my - 3.4), (CX - 6, my - 1.3), (CX - 2.5, my - 0.2), (CX, my), (CX + 2.5, my - 0.2),
             (CX + 6, my - 1.3), (CX + 9.5, my - 3.4)]), [0.25, 1.1, 1.55, 1.7, 1.55, 1.1, 0.25], MOUTH_LN,
          hardness=0.55, flow=0.5)
    mouth.append(p)
    head.append(('嘴', mouth))

    head.append(('眼_R', eye('R')))
    head.append(('眼_L', eye('L')))

    for side, f in SIDES:                       # blush above the eyes so the blink patch is tinted too
        p = Part(f'腮紅_{side}')
        bx, by = f(R([(EYE_CX_R - 3, EYE_Y + 0.3 * B)]))[0]
        p.soft(ellipse(bx, by, 15 * K, 6.5 * K), hx('ff9aa6', 140), 5)
        for dx in (-5, 0, 5):
            p.rib(f(R([(EYE_CX_R - 3 + dx + 2.2, EYE_Y + 0.3 * B - 3), (EYE_CX_R - 3 + dx - 1.8, EYE_Y + 0.3 * B + 3)])),
                  [1.0, 0.2], hx('f3818f', 130))
        head.append(p)

    for side, f in SIDES:
        p = Part(f'鬢角_{side}')
        pts = f(R(side_lock_R()))
        p.fill(pts, HAIR)
        p.cgrad(pts, hx('cebcf3', 0), hx('ae98e3', 200), 240 * K, 400 * K)
        rng = np.random.default_rng(31 if side == 'R' else 32)
        for i, xx in enumerate(np.linspace(202, 224, 8)):
            p.strand(f(R([(xx + 6, 140), (xx + 3, 230), (xx - 3, 320), (xx - 8 + rng.normal(0, 2), 392)])), 1.5,
                     hx('8672c6', 170) if i % 2 else hx('eee6ff', 170))
        p.air(f(R([(200, 150), (228, 150), (228, 205), (200, 205)])), hx('eee6ff', 140), blur=8)
        p.outline_clip(LW, HAIR_LN, skip_above=RP(0, 140)[1])
        head.append(p)

    for name, which, mir, seed in (('瀏海_R', 'R', False, 41), ('瀏海_L', 'R', True, 42), ('瀏海_中', 'C', False, 43)):
        p = Part(name)
        base, strands = fringe_shapes(which, mir)
        p.fill(base, HAIR, raw=True)
        for q in strands:
            p.fill(q, HAIR, raw=True)
        ys = [y for q in strands for _, y in q]
        p.cgrad(base + [pt for q in strands for pt in q], hx('cebcf3', 0), hx('a993e0', 210), RP(0, 130)[1], max(ys), raw=True)
        p.air(R([(195, EYE_TOP - 18), (376, EYE_TOP - 18), (376, EYE_TOP + 16), (195, EYE_TOP + 16)]), hx('9c86d8', 120), blur=8)
        x0, y0 = RP(195, HAIR_TOP - 2); x1, y1 = RP(376, HAIR_TOP + 40)
        p.air([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], hx('ddd1ff', 140), blur=14, raw=True)
        src = FRINGE_C if which == 'C' else FRINGE_R
        rng = np.random.default_rng(seed)
        for (tx, ty, ex, ey, w, b) in src:
            for off, col, wid in ((-w * 0.42, hx('7e69c2', 200), 1.2), (w * 0.1, hx('f4efff', 170), 1.4)):
                c = R([(tx + off, ty + 25), (tx + off + (ex - tx) * 0.5 + b * 0.7, ty + (ey - ty) * 0.55),
                       (ex + off * 0.35 + b * 0.4, ey - 4 - rng.random() * 6)])
                p.strand(M(c) if mir else c, wid, col)
        gloss(p, seed + 2)
        p.outline_clip(LW, HAIR_LN, skip_above=RP(0, 128)[1])
        head.append(p)

    # 碎髮: flyaways added at the finishing stage
    p = Part('碎髮')
    for g in (ID, M):
        for pts, w in (([(258, 102), (262, 140), (268, EYE_TOP + 9)], 2.2), ([(247, 106), (249, 150), (246, EYE_TOP + 3)], 1.8),
                       ([(214, 118), (206, 132), (199, 146)], 2.4), ([(209, 150), (201, 175), (197, 196)], 2.0),
                       ([(228, 120), (222, 158), (221, EYE_Y + 10)], 1.6)):
            c = g(R(pts))
            p.rib(c, [w * 1.6, w * 1.2, 0.2], HAIR_LN, hardness=0.5, flow=0.5)
            p.rib(c, [w, w * 0.7, 0.05], HAIR, hardness=0.65, flow=0.6)
    head.append(p)

    for side, f in SIDES:
        p = Part(f'眉毛_{side}')
        ex = EYE_CX_R
        p.rib(f(R([(ex - 16, BROW_Y + 4), (ex - 9, BROW_Y + 0.5), (ex + 2, BROW_Y - 1), (ex + 13, BROW_Y + 2)])),
              [0.5, 1.8, 1.6, 0.4], hx('6d5796', 200), hardness=0.55, flow=0.45)
        head.append(p)

    p = Part('呆毛')
    top = HAIR_TOP
    curl = R([(284, top + 4), (279, top - 18), (284, top - 44), (298, top - 60), (316, top - 62), (325, top - 50),
              (320, top - 35), (311, top - 31)])
    p.rib(curl, [9.5, 9.0, 7.5, 6.0, 4.6, 3.2, 1.8, 0.4], HAIR_LN, hardness=0.55, flow=0.5)
    p.rib(curl, [6.8, 6.4, 5.3, 4.2, 3.1, 2.0, 0.9, 0.05], HAIR, hardness=0.7, flow=0.6)
    p.rib(R([(282, top - 6), (283, top - 30), (292, top - 50)]), [0.3, 1.2, 0.3], HAIR_HI)
    head.append(p)

    p = Part('髮飾')
    cx, cy = RP(345, 116)
    star = []
    for i in range(10):
        r = (14 if i % 2 == 0 else 6.6) * K
        a = math.radians(-90 + i * 36 + 14)
        star.append((cx + r * math.cos(a), cy + r * math.sin(a), 'c'))
    p.fill(star, hx('ffd24f'), line=hx('b27b12'), lw=LW)
    p.air(ellipse(cx + 5, cy + 6, 9, 7), hx('e9a21c', 170), blur=4, raw=True)
    p.cfill(ellipse(cx - 4, cy - 4, 4, 3), hx('fff6c8'), raw=True, blur=1.2)
    head.append(p)
    G.append(('頭', head))
    return G


if __name__ == '__main__':
    import os, sys
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    with open(os.path.join(out, 'girl_v4_landmarks.json'), 'w', encoding='utf-8') as f:
        json.dump(landmarks(), f, indent=1)
    construction_image(os.path.join(out, 'girl_v4_construction.png'))
    with open(os.path.join(out, 'girl_v4_body_landmarks.json'), 'w', encoding='utf-8') as f:
        json.dump(body_landmarks(), f, indent=1)
    print(json.dumps(landmarks(), indent=1))
