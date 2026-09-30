# -*- coding: utf-8 -*-
"""Live2D-ready female character PSD, drawn from scratch in pure Python.

Follows the split guide at https://moonku44.com/live2d-psd/ :
  - front-facing, left/right symmetric (right side is drawn, left is mirrored)
  - ~4000 px long side, RGB 8-bit sRGB, character on transparent background
  - every part on its own layer; line art merged with its colour (except the
    face, whose line is kept separate from the skin base as the guide asks)
  - hidden areas are drawn too (neck extends up to the mouth, thighs continue
    under the skirt, face continues under the bangs)
  - Normal blend mode, 100 % opacity, unique names, no hidden layers, no masks

Naming: <part>_<R|L>, R/L = the CHARACTER's right/left (R is on the viewer's left).

Coordinates are written in a 1000 x 1667 design space and scaled by S.
"""
import math, os, sys, zlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brush

W_U, H_U = 1000, 1667
S = float(os.environ.get('GIRL_S', 2.4))    # design unit -> px   (2400 x 4000 canvas)
W, H = int(W_U * S), int(H_U * S)
SS = int(os.environ.get('GIRL_SS', 3))       # supersampling for anti-aliasing

# ------------------------------------------------------------------ palette
def hx(s, a=255):
    s = s.lstrip('#'); return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)

SKIN, SKIN_SH, SKIN_SH2, SKIN_LN = hx('fde9df'), hx('f5c9bb'), hx('eeb4a6'), hx('b9786f')
HAIR, HAIR_SH, HAIR_SH2, HAIR_HI, HAIR_LN = hx('bfaef0'), hx('9887d6'), hx('7a69bd'), hx('ece6ff'), hx('4f4289')
BHAIR, BHAIR_SH = hx('a595e0'), hx('7c6cc0')
WHITE, WHITE_SH, WHITE_LN = hx('fbfbff'), hx('d8dcf0'), hx('6d7396')
NAVY, NAVY_SH, NAVY_HI, NAVY_LN = hx('33406f'), hx('232c52'), hx('4b5a92'), hx('141a33')
RED, RED_SH, RED_HI, RED_LN = hx('e5485f'), hx('b52d47'), hx('ff8fa0'), hx('741a2c')
SOCK, SOCK_HI, SOCK_LN = hx('2d2c38'), hx('4d4c60'), hx('101018')
SHOE, SHOE_HI, SHOE_SH, SHOE_LN = hx('70503f'), hx('a07e68'), hx('4c3328'), hx('2a1a12')
IRIS_D, IRIS_M, IRIS_L, PUPIL = hx('24566b'), hx('3a93a6'), hx('8ee6e0'), hx('17303e')
EYE_LN, LASH = hx('3b2838'), hx('2c1f2c')
MOUTH, TONGUE, MOUTH_LN = hx('8a2c3b'), hx('e97c8b'), hx('7a3444')
BLUSH = hx('ff8c9e')


# ------------------------------------------------------------------ geometry
def M(pts):
    """Mirror across the centre line (x=500)."""
    return [(W_U - p[0],) + tuple(p[1:]) for p in pts]

def shift(pts, dx, dy):
    return [(p[0] + dx, p[1] + dy) + tuple(p[2:]) for p in pts]

def smooth(pts, closed=True, n=10):
    """Catmull-Rom through anchor points; an anchor (x, y, 'c') is a sharp corner."""
    P = [np.array(p[:2], float) for p in pts]
    corner = [len(p) > 2 and p[2] == 'c' for p in pts]
    k = len(P)
    if k < 3:
        return [tuple(p) for p in P]
    def tan(i):
        if corner[i % k] and (closed or 0 < i < k - 1):
            return np.zeros(2)
        if not closed and i == 0:
            return (P[1] - P[0]) * 0.5
        if not closed and i == k - 1:
            return (P[-1] - P[-2]) * 0.5
        return (P[(i + 1) % k] - P[(i - 1) % k]) * 0.5
    out = []
    segs = k if closed else k - 1
    for i in range(segs):
        p0, p1 = P[i], P[(i + 1) % k]
        m0, m1 = tan(i), tan(i + 1)
        for t in np.linspace(0, 1, n, endpoint=False):
            h00 = 2*t**3 - 3*t**2 + 1; h10 = t**3 - 2*t**2 + t
            h01 = -2*t**3 + 3*t**2;    h11 = t**3 - t**2
            out.append(tuple(h00*p0 + h10*m0 + h01*p1 + h11*m1))
    if not closed:
        out.append(tuple(P[-1]))
    return out

def ribbon(pts, widths, n=10):
    """Tapered stroke as a polygon. widths: one per anchor (interpolated)."""
    c = np.array(smooth(pts, closed=False, n=n))
    wa = np.interp(np.linspace(0, len(widths) - 1, len(c)), range(len(widths)), widths)
    d = np.gradient(c, axis=0)
    d /= np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-6)
    nrm = np.stack([-d[:, 1], d[:, 0]], 1) * (wa[:, None] / 2)
    return [tuple(p) for p in np.vstack([c + nrm, (c - nrm)[::-1]])]

def ellipse(cx, cy, rx, ry, n=64, rot=0):
    a = np.linspace(0, 2 * math.pi, n, endpoint=False)
    x, y = rx * np.cos(a), ry * np.sin(a)
    r = math.radians(rot)
    return [(cx + x[i]*math.cos(r) - y[i]*math.sin(r), cy + x[i]*math.sin(r) + y[i]*math.cos(r)) for i in range(n)]

def arc(cx, cy, r, a0, a1, n=24):
    return [(cx + r*math.cos(math.radians(a)), cy + r*math.sin(math.radians(a))) for a in np.linspace(a0, a1, n)]


# ------------------------------------------------------------------ layer painter
LIGHT = np.array([0.55, 0.83]) / np.linalg.norm([0.55, 0.83])   # light from top-left -> shadow side down-right
SOFT = 0.8            # default soft edge (design units) for painted shading


def _seed(*parts):
    return zlib.crc32(repr(parts).encode()) & 0x7fffffff


def ink_plan(poly, lw, closed, seed):
    """Split a path into hand-inked strokes: [(pts, radii)] in design units.

    Closed outlines become several overlapping strokes (breaks at sharp corners
    and every ~200 units); each stroke tapers in/out and wobbles like pen
    pressure; lines on the shadow side (facing down-right) are drawn heavier.
    """
    P = np.asarray(poly, float)
    if closed and np.allclose(P[0], P[-1]):
        P = P[:-1]
    n = len(P)
    if n < 2:
        return []
    rng = np.random.default_rng(seed)
    if closed:
        area = 0.5 * np.sum(P[:, 0] * np.roll(P[:, 1], -1) - np.roll(P[:, 0], -1) * P[:, 1])
        d = np.roll(P, -1, 0) - np.roll(P, 1, 0)
    else:
        area = 1.0
        d = np.gradient(P, axis=0)
    d /= np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)
    nrm = np.stack([d[:, 1], -d[:, 0]], 1) * (1 if area > 0 else -1)
    shade = 1 + (0.38 * (nrm @ LIGHT) if closed else 0)

    seg = np.linalg.norm(np.diff(np.vstack([P, P[:1]]) if closed else P, axis=0), axis=1)
    per = seg.sum()
    if not closed:
        pr = brush.pressure(n, taper_in=min(0.3, 10 / max(per, 1)) + 0.05,
                            taper_out=min(0.4, 16 / max(per, 1)) + 0.08, seed=seed, min_p=0.15)
        return [(P, lw / 2 * pr * shade)]

    # break points: sharp corners + roughly every 200 units
    ang = np.degrees(np.arccos(np.clip(np.sum(np.roll(d, 1, 0) * d, 1), -1, 1)))
    cum = np.concatenate([[0], np.cumsum(seg)])[:n]
    start = rng.random() * per
    brk = set(int(i) for i in np.nonzero(ang > 55)[0])
    k = max(2, int(round(per / 200)))
    for j in range(k):
        target = (start + j * per / k + rng.normal(0, per / k * 0.1)) % per
        brk.add(int(np.argmin(np.abs(cum - target))))
    merged = []
    for b in sorted(brk):
        if not merged or cum[b] - cum[merged[-1]] > 25:
            merged.append(b)
    if len(merged) > 1 and (per - cum[merged[-1]] + cum[merged[0]]) < 25:
        merged.pop()
    if len(merged) < 2:
        merged = [0, n // 2]
    strokes = []
    ov = 3                                        # overlap (samples) on each side of a break
    for j, b0 in enumerate(merged):
        b1 = merged[(j + 1) % len(merged)]
        idx, i, end = [], (b0 - ov) % n, (b1 + ov) % n
        while True:
            idx.append(i)
            if i == end or len(idx) > n + 2 * ov:
                break
            i = (i + 1) % n
        pts = P[idx]
        m = len(pts)
        if m < 2:
            continue
        ln = np.sum(np.linalg.norm(np.diff(pts, axis=0), axis=1))
        pr = brush.pressure(m, taper_in=min(0.35, 7 / max(ln, 1)), taper_out=min(0.45, 11 / max(ln, 1)),
                            wobble=0.12, seed=seed + j, min_p=0.2)
        strokes.append((pts, lw / 2 * pr * shade[idx]))
    return strokes


class Part:
    """Collects drawing ops in design units, then renders into a tight RGBA crop.

    Fills are flat (the colour base); everything that reads as "drawn" -- line
    art, shading edges, strands, lashes -- goes through the dab brush engine or
    is softened, so nothing has a hard vector edge except the base silhouette,
    which the line art covers anyway.
    """
    def __init__(self, name):
        self.name, self.ops = name, []

    def _poly(self, pts, raw):
        return list(pts) if raw else smooth(pts)

    def _s(self):
        return _seed(self.name, len(self.ops))

    def fill(self, pts, col, line=None, lw=2.2, raw=False):
        poly = self._poly(pts, raw)
        self.ops.append(('fill', poly, col))
        if line:
            self.ops.append(('ink', poly, lw, line, True, self._s(), False))
        return poly

    def clip(self, pts, raw=False):
        self.ops.append(('clip', self._poly(pts, raw)))

    def cfill(self, pts, col, raw=False, blur=SOFT):
        """Shading shape clipped to the part, with a soft (brushed) edge."""
        self.ops.append(('cfill', self._poly(pts, raw), col, blur))

    def air(self, pts, col, blur=10, raw=False):
        """Airbrush: very soft, clipped."""
        self.ops.append(('cfill', self._poly(pts, raw), col, blur))

    def cgrad(self, pts, c0, c1, y0, y1, raw=False):
        self.ops.append(('cgrad', self._poly(pts, raw), c0, c1, y0, y1))

    def line(self, pts, lw, col, closed=False, raw=False, clipped=False):
        poly = list(pts) if raw else smooth(pts, closed=closed)
        self.ops.append(('ink', poly, lw, col, closed, self._s(), clipped))

    def rib(self, pts, widths, col, clipped=False, hardness=0.6, flow=0.45):
        """Brush stroke with an explicit width (pressure) profile."""
        c = smooth(pts, closed=False)
        w = np.interp(np.linspace(0, len(widths) - 1, len(c)), range(len(widths)), widths)
        self.ops.append(('stroke', c, list(w / 2), col, clipped, hardness, flow, self._s()))

    def strand(self, pts, w, col, clipped=True):
        """Thin tapered hair strand."""
        c = smooth(pts, closed=False)
        pr = brush.pressure(len(c), 0.25, 0.45, wobble=0.15, seed=self._s(), min_p=0.05)
        self.ops.append(('stroke', c, list(w / 2 * pr), col, clipped, 0.45, 0.35, self._s()))

    def soft(self, pts, col, blur, raw=True):
        self.ops.append(('soft', self._poly(pts, raw), col, blur))

    def outline_clip(self, lw, col, skip_above=None):
        """Ink the silhouette of everything filled so far (union of the shapes),
        e.g. a fringe built from many overlapping strands. Parts of the contour
        above y=skip_above (design units) are left unlined."""
        self.ops.append(('inkclip', lw, col, skip_above, self._s()))

    # ---------------------------------------------------------------- render
    def bbox(self):
        xs, ys = [], []
        for op in self.ops:
            pad = 0
            if op[0] == 'inkclip':
                continue
            if op[0] == 'ink': pad = op[2] * 1.5
            if op[0] == 'stroke': pad = max(op[2]) * 1.5
            if op[0] == 'soft': pad = op[3] * 3
            for x, y in op[1]:
                xs += [x - pad, x + pad]; ys += [y - pad, y + pad]
        l = max(0, int(math.floor(min(xs) * S)) - 4); t = max(0, int(math.floor(min(ys) * S)) - 4)
        r = min(W, int(math.ceil(max(xs) * S)) + 4); b = min(H, int(math.ceil(max(ys) * S)) + 4)
        return l, t, r, b

    def render(self):
        l, t, r, b = self.bbox()
        w, h = (r - l) * SS, (b - t) * SS
        k = S * SS
        tp = lambda poly: [((x * S - l) * SS, (y * S - t) * SS) for x, y in poly]
        rgb = np.zeros((h, w, 3), np.float32)
        alpha = np.zeros((h, w), np.float32)
        clipm = np.zeros((h, w), np.float32)

        def mask(poly, blur=0):
            m = Image.new('L', (w, h), 0)
            ImageDraw.Draw(m).polygon(tp(poly), fill=255)
            if blur > 0:
                m = m.filter(ImageFilter.GaussianBlur(blur * k))
            return np.asarray(m, np.float32) / 255

        def paint(m, col):
            nonlocal rgb, alpha
            a = m * (col[3] / 255)
            c = np.array(col[:3], np.float32)
            out_a = a + alpha * (1 - a)
            rgb = (c * a[..., None] + rgb * (alpha * (1 - a))[..., None]) / np.maximum(out_a, 1e-6)[..., None]
            alpha = out_a

        def brushed(strokes, hardness, flow, grain=0.14):
            inv = np.ones((h, w), np.float32)          # remaining transparency
            for pts, rad in strokes:
                brush.stroke(inv, tp(pts), np.asarray(rad) * k, flow=flow, hardness=hardness, grain=grain)
            return 1 - inv

        for op in self.ops:
            kind = op[0]
            if kind == 'fill':
                m = mask(op[1]); paint(m, op[2]); clipm = np.maximum(clipm, m)
            elif kind == 'clip':
                clipm = mask(op[1])
            elif kind == 'cfill':
                paint(mask(op[1], op[3]) * clipm, op[2])
            elif kind == 'cgrad':
                _, poly, c0, c1, y0, y1 = op
                m = mask(poly) * clipm
                ys = (np.arange(h, dtype=np.float32) / SS + t) / S
                f = np.clip((ys - y0) / (y1 - y0), 0, 1)[:, None]
                a0, a1 = c0[3] / 255, c1[3] / 255
                col = np.array(c0[:3], np.float32) * (1 - f)[..., None] + np.array(c1[:3], np.float32) * f[..., None]
                aa = m * (a0 * (1 - f) + a1 * f)
                col = np.broadcast_to(col, (h, w, 3))
                out_a = aa + alpha * (1 - aa)
                rgb = (col * aa[..., None] + rgb * (alpha * (1 - aa))[..., None]) / np.maximum(out_a, 1e-6)[..., None]
                alpha = out_a
            elif kind == 'ink':
                _, poly, lw, col, closed, seed, clipped = op
                m = brushed(ink_plan(poly, lw * 1.3, closed, seed), hardness=0.5, flow=0.33)
                paint(m * clipm if clipped else m, col)
            elif kind == 'stroke':
                _, pts, rad, col, clipped, hard, flow, seed = op
                m = brushed([(np.asarray(pts), np.asarray(rad))], hardness=hard, flow=flow)
                paint(m * clipm if clipped else m, col)
            elif kind == 'soft':
                _, poly, col, blur = op
                paint(mask(poly, blur), col)
            elif kind == 'inkclip':
                import cv2
                _, lw, col, skip, seed = op
                cs, _h = cv2.findContours((clipm > 0.5).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                strokes = []
                for ci, c in enumerate(cs):
                    if cv2.contourArea(c) < (4 * k) ** 2:
                        continue
                    c = c[:, 0, :].astype(float)[::max(1, int(k))]
                    pts = [((x / SS + l) / S, (y / SS + t) / S) for x, y in c]
                    if skip is None:
                        strokes += ink_plan(pts + pts[:1], lw * 1.3, True, seed + ci)
                        continue
                    # rotate so the run starts at a skipped point, then split into visible runs
                    keep = [q[1] >= skip for q in pts]
                    if all(keep):
                        strokes += ink_plan(pts + pts[:1], lw * 1.3, True, seed + ci)
                        continue
                    i0 = keep.index(False)
                    pts, keep = pts[i0:] + pts[:i0], keep[i0:] + keep[:i0]
                    run = []
                    for q, kp in zip(pts + [None], keep + [False]):
                        if kp:
                            run.append(q)
                        elif len(run) > 3:
                            strokes += ink_plan(run, lw * 1.3, False, seed + ci + len(strokes)); run = []
                        else:
                            run = []
                m = brushed(strokes, hardness=0.5, flow=0.33)
                paint(m, col)

        img = np.dstack([np.clip(rgb, 0, 255), np.clip(alpha * 255, 0, 255)]).astype(np.uint8)
        im = Image.fromarray(img, 'RGBA').reduce(SS)
        a = np.asarray(im)
        ys, xs = np.nonzero(a[..., 3] > 0)
        if len(xs) == 0:
            raise ValueError(f'{self.name}: empty layer')
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        return im.crop((x0, y0, x1, y1)), l + x0, t + y0


# ================================================================== the character
FACE = [(392, 262), (393, 320), (398, 362), (411, 398), (434, 424), (466, 442), (500, 449),
        (534, 442), (566, 424), (589, 398), (602, 362), (607, 320), (608, 262),
        (596, 222), (560, 192), (500, 180), (440, 192), (404, 222)]
HAIR_C = (500, 292)

def bang_R():
    top = arc(*HAIR_C, 123, 197, 257, 10)
    return top + [(478, 232), (477, 276), (468, 318, 'c'), (457, 288), (446, 294), (432, 330, 'c'),
                  (423, 300), (411, 306), (398, 350, 'c'), (390, 306)]

def bang_C():
    top = arc(*HAIR_C, 123, 243, 297, 10)
    return top + [(549, 232), (542, 286), (533, 322, 'c'), (523, 294), (511, 300), (502, 336, 'c'),
                  (492, 300), (480, 294), (468, 320, 'c'), (458, 286), (452, 232)]

def sidelock_R():
    return [(394, 246), (412, 300), (414, 372), (408, 452), (400, 532), (407, 616, 'c'),
            (389, 584), (377, 522), (371, 442), (371, 362), (376, 296)]

def backhair_R():
    return [(503, 168, 'c'), (458, 172), (418, 188), (386, 218), (364, 264), (350, 330), (342, 420),
            (336, 520), (330, 620), (324, 720), (326, 820), (338, 910, 'c'), (356, 872),
            (372, 940, 'c'), (392, 884), (412, 952, 'c'), (432, 890), (454, 936, 'c'),
            (472, 884), (490, 922, 'c'), (503, 884, 'c')]


def hair_flow(p, focus, a0, a1, r0, r1, n, col, w, seed, jitter=0.35):
    """Strands radiating from focus (the crown), clipped to the piece -- hair flow."""
    rng = np.random.default_rng(seed)
    for i in range(n):
        a = math.radians(a0 + (a1 - a0) * (i + rng.random() * 0.8) / n)
        ra = r0 + (r1 - r0) * rng.random() * jitter
        rb = r1 - (r1 - r0) * rng.random() * jitter
        bend = rng.normal(0, 0.02)
        pts = [(focus[0] + r * math.cos(a + bend * j), focus[1] + r * math.sin(a + bend * j))
               for j, r in enumerate(np.linspace(ra, rb, 4))]
        p.strand(pts, w * (0.6 + 0.8 * rng.random()), col)


def angel_ring(p, seed):
    """Painted highlight band: a soft glow plus short vertical brush flicks."""
    outer = arc(*HAIR_C, 107, 196, 344, 40)
    inner = arc(HAIR_C[0], HAIR_C[1] + 2, 91, 344, 196, 40)
    p.air(outer + inner, hx('ece6ff', 150), blur=3, raw=True)
    rng = np.random.default_rng(seed)
    for ang in np.arange(198, 343, 3.2):
        a = math.radians(ang + rng.normal(0, 0.6))
        r_top = 109 + rng.random() * 4
        r_bot = 88 - rng.random() * 9
        pts = [(HAIR_C[0] + r * math.cos(a), HAIR_C[1] + 2 + r * math.sin(a)) for r in (r_top, (r_top + r_bot) / 2, r_bot)]
        p.strand(pts, 2.6 + rng.random() * 1.6, hx('f6f2ff', 235))


def hair_piece(p, pts, band=True, strands=(), seed=0):
    p.fill(pts, HAIR)
    p.cgrad(pts, hx('bfaef0', 0), HAIR_SH, 250, 345)
    p.air([(380, 170), (620, 170), (620, 215), (380, 215)], hx('d7ccff', 120), blur=12)   # top light
    hair_flow(p, (500, 110), 38, 142, 90, 240, 40, hx('7f6dc4', 200), 2.2, seed)       # shadow strands
    p.air([(380, 300), (620, 300), (620, 360), (380, 360)], hx('8c7bd0', 150), blur=9)   # darker toward the tips
    hair_flow(p, (500, 110), 38, 142, 80, 190, 18, hx('e8e1ff', 200), 1.8, seed + 1)   # light strands
    if band:
        angel_ring(p, seed + 2)
    for s in strands:
        p.strand(s, 1.9, HAIR_SH2)
    p.line(pts, 2.2, HAIR_LN, closed=True)


def eye(side):
    """Returns list of (name, Part) bottom -> top for one eye. side: 'R' or 'L'."""
    f = 1 if side == 'R' else -1
    cx, cy = (452, 348) if side == 'R' else (548, 348)
    E = lambda pts: [(cx + f * p[0], cy + p[1]) + tuple(p[2:]) for p in pts]
    parts = []

    p = Part(f'下眼皮_{side}')
    p.fill(E([(-34, 8), (-20, 20), (0, 27), (22, 21), (34, 7), (37, 30), (0, 42), (-37, 30)]), SKIN)
    parts.append(p)

    p = Part(f'下眼線_{side}')
    p.rib(E([(-24, 13), (-8, 21), (8, 22), (21, 16)]), [0.4, 1.9, 1.6, 0.4], EYE_LN)
    parts.append(p)

    p = Part(f'下睫毛_{side}')
    p.rib(E([(-25, 11), (-30, 16), (-33, 22)]), [1.6, 1.0, 0.2], LASH)
    p.rib(E([(-15, 17), (-17, 22)]), [1.2, 0.2], LASH)
    parts.append(p)

    WHITE_PTS = E([(-33, 2), (-24, -14), (-8, -23), (10, -24), (24, -17), (31, -6), (30, 6),
                   (20, 17), (4, 22), (-12, 20), (-25, 12)])
    p = Part(f'眼白_{side}')
    p.fill(WHITE_PTS, hx('ffffff'))
    p.cfill(E([(-40, -30), (40, -30), (40, -10), (0, -14), (-40, -8)]), hx('c9cde8'), blur=2.2)   # lid shadow
    parts.append(p)

    p = Part(f'眼球_{side}')
    ix, iy = cx + f * 1, cy
    p.fill(ellipse(ix, iy, 17, 22), IRIS_M, raw=True)
    p.air(ellipse(ix, iy - 14, 22, 13), IRIS_D, blur=3.5, raw=True)
    p.air(ellipse(ix, iy + 11, 12, 8), IRIS_L, blur=2.5, raw=True)
    for dx in (-8, -3, 3, 8):
        p.strand([(ix + dx * 0.7, iy + 2), (ix + dx, iy + 10), (ix + dx * 1.2, iy + 17)], 1.6, hx('c8fff6', 170))
    p.cfill(ellipse(ix, iy - 3, 7.5, 11), PUPIL, raw=True, blur=0.9)
    p.line(ellipse(ix, iy, 17, 22), 1.4, hx('1b3e4e'), raw=True)
    parts.append(p)

    p = Part(f'上眼線_{side}')
    p.rib(E([(-37, 5), (-31, -8), (-18, -20), (-2, -26), (14, -26), (26, -19), (33, -8)]),
          [2.5, 5.5, 7, 7, 6, 4.5, 1.5], EYE_LN)
    parts.append(p)

    p = Part(f'上眼皮_{side}')
    p.fill(E([(-40, 2), (-34, -11), (-20, -24), (-3, -31), (15, -31), (29, -24), (37, -10),
              (40, -32), (30, -46), (0, -52), (-32, -46), (-44, -24)]), SKIN)
    parts.append(p)

    p = Part(f'上睫毛_{side}')
    p.rib(E([(-30, -8), (-40, -13), (-47, -12)]), [4.5, 2.5, 0.3], LASH)
    p.rib(E([(-35, -1), (-44, 2), (-50, 7)]), [4, 2, 0.3], LASH)
    p.rib(E([(-22, -19), (-28, -26), (-31, -30)]), [3, 1.5, 0.2], LASH)
    p.rib(E([(29, -15), (35, -18), (38, -17)]), [2.5, 1.2, 0.2], LASH)
    parts.append(p)

    p = Part(f'眼褶_{side}')
    p.rib(E([(-27, -29), (-12, -36), (8, -37), (25, -30)]), [0.4, 1.7, 1.5, 0.4], hx('a36f73'))
    parts.append(p)

    p = Part(f'高光_{side}')
    p.fill(ellipse(cx + f * -6, cy - 9, 6.5, 7.5), hx('ffffff'), raw=True)
    p.fill(ellipse(cx + f * 9, cy + 9, 3, 3), hx('ffffff'), raw=True)
    p.fill(ellipse(cx + f * -11, cy + 7, 1.8, 1.8), hx('ffffff', 220), raw=True)
    parts.append(p)
    return parts


def build():
    """Returns [(group_name, [Part, ...bottom->top])] bottom -> top."""
    G = []

    # ---------------------------------------------------------------- back hair
    parts = []
    for side, f in (('R', lambda x: x), ('L', M)):
        p = Part(f'後髮_{side}')
        pts = f(backhair_R())
        p.fill(pts, BHAIR)
        p.cgrad(pts, hx('a595e0', 0), BHAIR_SH, 420, 900)
        inner = f([(503, 300), (470, 330), (440, 420), (430, 560), (440, 700), (460, 820), (503, 860)])
        p.cfill(inner, hx('6b5caf', 170))
        rng = np.random.default_rng(11 if side == 'R' else 12)
        for i in range(26):
            x0 = 340 + i * 6 + rng.normal(0, 3)
            s_ = [(x0 + 30, 230 + rng.random() * 60), (x0 - 4, 450), (x0 - 10 + rng.normal(0, 4), 700),
                  (x0 + rng.normal(0, 6), 880 + rng.random() * 40)]
            p.strand(f(s_), 1.3 + rng.random(), hx('6a5bb0', 140) if i % 3 else hx('cfc3fa', 140))
        p.line(f(backhair_R())[:-1], 2.2, HAIR_LN, raw=False)
        parts.append(p)
    G.append(('後髮', parts))

    # ---------------------------------------------------------------- body
    body = []

    def leg_parts(side, f):
        out = []
        # lower leg (sock)
        p = Part(f'小腿_{side}')
        pts = f([(450, 1200), (489, 1200), (494, 1280), (488, 1380), (480, 1470), (476, 1522),
                 (456, 1524), (452, 1470), (444, 1380), (441, 1280)])
        p.fill(pts, SOCK)
        p.cfill(f([(452, 1220), (462, 1220), (458, 1400), (456, 1520), (450, 1520), (446, 1300)]), SOCK_HI)
        p.line(pts, 2.2, SOCK_LN, closed=True)
        out.append(p)
        # shoe
        p = Part(f'鞋_{side}')
        pts = f([(447, 1498), (480, 1498), (484, 1536), (490, 1572), (484, 1597), (446, 1599),
                 (438, 1574), (442, 1536)])
        p.fill(pts, SHOE)
        p.cfill(f([(430, 1586), (500, 1586), (500, 1610), (430, 1610)]), SHOE_SH)
        p.cfill(ellipse(*f([(458, 1560)])[0], 7, 16, rot=-8 if f is M else 8), SHOE_HI, raw=True)
        p.line(f([(441, 1540), (464, 1532), (486, 1540)]), 1.6, SHOE_LN)
        p.line(pts, 2.2, SHOE_LN, closed=True)
        out.append(p)
        return out

    def thigh(side, f):
        p = Part(f'大腿_{side}')
        pts = f([(436, 930), (501, 930), (500, 1040), (494, 1140), (488, 1226), (450, 1226),
                 (443, 1140), (437, 1040)])
        p.fill(pts, SKIN)
        p.cfill(f([(490, 930), (502, 930), (502, 1250), (478, 1250), (486, 1100)]), SKIN_SH, blur=2.5)
        p.air(f([(430, 930), (510, 930), (510, 1000), (430, 1000)]), hx('e9ada0', 170), blur=10)
        sock = f([(426, 1082, 'c'), (445, 1086), (460, 1080), (475, 1086), (490, 1080), (510, 1084, 'c'),
                  (510, 1260, 'c'), (426, 1260, 'c')])
        p.cfill(sock, SOCK, raw=False)
        p.cfill(f([(446, 1092, 'c'), (458, 1092, 'c'), (454, 1250, 'c'), (446, 1250, 'c')]), SOCK_HI)
        p.line(f([(440, 1084), (452, 1088), (466, 1083), (480, 1088), (494, 1083)]), 1.4, hx('585870'))
        # side outlines only: skin above the sock, dark on the sock, none at the knee
        # (the lower leg continues underneath, so a bottom line would read as a seam)
        outline = girl_smooth_closed(pts)
        def runs(cond):
            cur, out = [], []
            for q in outline + outline[:1]:
                if cond(q): cur.append(q)
                elif cur: out.append(cur); cur = []
            if cur: out.append(cur)
            return [r for r in out if len(r) > 1]
        for r in runs(lambda q: q[1] <= 1086):
            p.line(r, 2.2, SKIN_LN, raw=True)
        for r in runs(lambda q: 1080 < q[1] < 1212):
            p.line(r, 2.4, SOCK_LN, raw=True)
        return p

    # skirt back (lining, behind the legs)
    SK_TOP_Y, SK_HEM_Y = 772, 1000
    def sk_x(t, y):
        top = 418 + 164 * t; bot = 346 + 308 * t
        return top + (bot - top) * (y - SK_TOP_Y) / (SK_HEM_Y - SK_TOP_Y)
    def hem_y(t):
        k = t * 12
        return SK_HEM_Y + (10 if int(round(k)) % 2 else 0) + (4 * math.sin(k * math.pi))
    def skirt_slice(t0, t1):
        n = int(round((t1 - t0) * 24))
        bottom = [(sk_x(t0 + (t1 - t0) * i / n, SK_HEM_Y), hem_y(t0 + (t1 - t0) * i / n)) for i in range(n + 1)]
        return [(sk_x(t0, SK_TOP_Y), SK_TOP_Y), (sk_x(t1, SK_TOP_Y), SK_TOP_Y)] + bottom[::-1]

    p = Part('裙_後')
    back = [(sk_x(0, 800), 800), (sk_x(1, 800), 800)] + \
           [(sk_x(1 - i / 24, SK_HEM_Y) + (0.04 - i / 600) * 0, hem_y(1 - i / 24) + 8) for i in range(25)]
    p.fill(back, NAVY_SH, line=NAVY_LN, raw=True)
    body.append(p)

    for side, f in (('R', lambda x: x), ('L', M)):
        body += leg_parts(side, f)
    for side, f in (('R', lambda x: x), ('L', M)):
        body.append(thigh(side, f))

    # neck (extended up to mouth height)
    p = Part('脖子')
    neck = [(470, 380), (530, 380), (531, 450), (536, 486), (548, 506), (452, 506), (464, 486), (469, 450)]
    p.fill(neck, SKIN, raw=True)
    p.cfill(smooth([(456, 380), (544, 380), (544, 432), (520, 452), (500, 470), (480, 452), (456, 432)]), SKIN_SH, raw=True, blur=2.5)
    p.air([(452, 480), (548, 480), (548, 520), (452, 520)], hx('eeb4a6', 150), blur=7)
    p.line([(469, 430), (468, 470), (463, 492)], 2.0, SKIN_LN)
    p.line(M([(469, 430), (468, 470), (463, 492)]), 2.0, SKIN_LN)
    body.append(p)

    # torso / blouse
    p = Part('胸腔')
    torso = [(466, 480), (534, 480), (574, 490), (606, 506), (621, 530), (613, 600), (598, 680),
             (584, 742), (582, 778), (418, 778), (416, 742), (402, 680), (387, 600), (379, 530),
             (394, 506), (426, 490)]
    p.fill(torso, WHITE)
    p.cfill([(560, 560), (625, 520), (625, 790), (578, 790), (590, 700)], WHITE_SH, blur=2.5)
    p.cfill(M([(560, 560), (625, 520), (625, 790), (578, 790), (590, 700)]), WHITE_SH, blur=2.5)
    p.cfill([(418, 740), (582, 740), (582, 790), (418, 790)], WHITE_SH, blur=3)
    p.air([(430, 560), (570, 560), (570, 610), (430, 610)], hx('c3c8e6', 200), blur=12)     # under collar
    p.air([(470, 640), (530, 640), (530, 700), (470, 700)], hx('c9cde8', 170), blur=8)      # under ribbon
    p.line(torso, 2.2, WHITE_LN, closed=True)
    body.append(p)

    for side, f in (('R', lambda x: x), ('L', M)):
        p = Part(f'胸_{side}')
        pts = f([(430, 600), (446, 578), (472, 572), (496, 584), (500, 612), (490, 638), (464, 646), (440, 636)])
        p.fill(pts, WHITE)
        # same airbrush as the torso underneath, so the bust layer blends in
        p.air([(430, 560), (570, 560), (570, 610), (430, 610)], hx('c3c8e6', 200), blur=12)
        p.air([(470, 640), (530, 640), (530, 700), (470, 700)], hx('c9cde8', 170), blur=8)
        p.cfill(f([(426, 622), (460, 634), (502, 616), (502, 660), (426, 660)]), WHITE_SH, blur=2.5)
        p.line(f([(436, 630), (458, 644), (482, 642), (498, 626)]), 1.8, WHITE_LN)
        body.append(p)

    p = Part('腰')
    waist = [(417, 742), (460, 746), (500, 747), (540, 746), (583, 742), (585, 782), (540, 786),
             (500, 787), (460, 786), (415, 782)]
    p.fill(waist, NAVY)
    p.cfill([(410, 770), (590, 770), (590, 790), (410, 790)], NAVY_SH)
    p.line(waist, 2.0, NAVY_LN, closed=True)
    body.append(p)

    def skirt_piece(name, t0, t1):
        p = Part(name)
        pts = skirt_slice(t0, t1)
        p.fill(pts, NAVY, raw=True)
        p.air([(300, 760), (700, 760), (700, 800), (300, 800)], hx('141a33', 170), blur=9)       # under waistband
        p.air([(300, 1000), (700, 1000), (700, 1020), (300, 1020)], hx('1b2242', 160), blur=10)  # hem shadow
        k0, k1 = math.ceil(t0 * 12 - 1e-6), math.floor(t1 * 12 + 1e-6)
        for k in range(k0, k1 + 1):
            t = k / 12
            if k % 2 == 0 and t + 1 / 24 <= t1 + 1e-6:
                ta, tb = t, t + 1 / 24
                q = [(sk_x(ta, SK_TOP_Y + 20), SK_TOP_Y + 20), (sk_x(tb, SK_TOP_Y + 20), SK_TOP_Y + 20),
                     (sk_x(tb, SK_HEM_Y), SK_HEM_Y + 20), (sk_x(ta, SK_HEM_Y), SK_HEM_Y + 20)]
                p.cfill(q, NAVY_SH, raw=True)
            if t0 + 1e-6 < t < t1 - 1e-6:
                p.line([(sk_x(t, SK_TOP_Y + 6), SK_TOP_Y + 6), (sk_x(t, SK_HEM_Y), hem_y(t))], 1.6, NAVY_LN, raw=True)
        # white line near the hem
        stripe = [(sk_x(t0 + (t1 - t0) * i / 20, SK_HEM_Y - 22), hem_y(t0 + (t1 - t0) * i / 20) - 22) for i in range(21)]
        p.line(stripe, 4, hx('f3f3ff'), raw=True, clipped=True)
        p.line(pts + pts[:1], 2.2, NAVY_LN, raw=True)
        return p

    body.append(skirt_piece('裙_R', 0.0, 0.375))
    body.append(skirt_piece('裙_L', 0.625, 1.0))
    body.append(skirt_piece('裙_中', 0.29, 0.71))

    # sailor collar
    for side, f in (('R', lambda x: x), ('L', M)):
        p = Part(f'領子_{side}')
        pts = f([(472, 470), (432, 480), (398, 498), (382, 522), (390, 556), (428, 572), (462, 590),
                 (500, 646, 'c'), (486, 604), (476, 552), (470, 500)])
        p.fill(pts, NAVY)
        p.cfill(f([(470, 470), (380, 510), (380, 530), (470, 490)]), NAVY_SH, blur=2.5)
        p.air(f([(420, 500), (470, 500), (470, 540), (420, 540)]), NAVY_HI, blur=10)
        p.rib(f([(396, 510), (392, 532), (402, 552), (436, 564), (468, 580), (492, 620)]), [2.6] * 6, hx('f6f6ff'), clipped=True)
        p.line(pts, 2.2, NAVY_LN, closed=True)
        body.append(p)

    # ribbon
    for side, f in (('R', lambda x: x), ('L', M)):
        p = Part(f'蝴蝶結尾_{side}')
        pts = f([(496, 636), (486, 668), (477, 708, 'c'), (489, 700), (499, 711, 'c'), (505, 644)])
        p.fill(pts, RED)
        p.cfill(f([(490, 660), (510, 660), (510, 720), (494, 720)]), RED_SH)
        p.line(pts, 2.0, RED_LN, closed=True)
        body.append(p)
    for side, f in (('R', lambda x: x), ('L', M)):
        p = Part(f'蝴蝶結_{side}')
        pts = f([(494, 620), (476, 604), (456, 604), (448, 622), (452, 642), (472, 648), (494, 638)])
        p.fill(pts, RED)
        p.cfill(f([(440, 632), (496, 628), (496, 660), (440, 660)]), RED_SH, blur=2)
        p.cfill(f([(458, 610), (470, 608), (468, 616), (458, 618)]), RED_HI)
        p.line(f([(466, 614), (478, 622), (490, 626)]), 1.4, RED_LN)
        p.line(pts, 2.0, RED_LN, closed=True)
        body.append(p)
    p = Part('蝴蝶結_中')
    pts = [(490, 618), (510, 618), (513, 630), (510, 643), (490, 643), (487, 630)]
    p.fill(pts, RED)
    p.cfill([(484, 634), (516, 634), (516, 650), (484, 650)], RED_SH)
    p.line(pts, 2.0, RED_LN, closed=True)
    body.append(p)

    # arms
    for side, f in (('R', lambda x: x), ('L', M)):
        p = Part(f'上臂_{side}')
        arm = f([(364, 588), (402, 598), (397, 650), (390, 708), (355, 706), (355, 650)])
        p.fill(arm, SKIN)
        p.cfill(f([(380, 590), (402, 590), (396, 710), (378, 710), (386, 650)]), SKIN_SH)
        p.line(arm, 2.2, SKIN_LN, closed=True)
        sleeve = f([(394, 504), (372, 518), (359, 556), (356, 598), (364, 628), (394, 638), (410, 600), (410, 540)])
        p.fill(sleeve, WHITE)
        p.cfill(f([(395, 520), (415, 520), (415, 640), (390, 640), (402, 580)]), WHITE_SH)
        p.line(f([(376, 540), (372, 580), (378, 612)]), 1.4, WHITE_LN)
        p.line(sleeve, 2.2, WHITE_LN, closed=True)
        p.rib(f([(359, 612), (378, 628), (402, 628)]), [5, 5, 5], NAVY)
        body.append(p)
    for side, f in (('R', lambda x: x), ('L', M)):
        p = Part(f'下臂_{side}')
        pts = f([(355, 692), (390, 696), (383, 772), (374, 850), (344, 848), (347, 772)])
        p.fill(pts, SKIN)
        p.cfill(f([(376, 690), (392, 690), (380, 860), (366, 860), (374, 772)]), SKIN_SH, blur=2)
        p.air(f([(356, 690), (388, 690), (388, 720), (356, 720)]), hx('f7b4ab', 130), blur=6)
        p.line(f([(362, 716), (372, 714)]), 1.4, SKIN_LN)
        p.line(pts, 2.2, SKIN_LN, closed=True)
        body.append(p)
    for side, f in (('R', lambda x: x), ('L', M)):
        p = Part(f'手掌_{side}')
        pts = f([(344, 838), (375, 842), (383, 872), (379, 902), (362, 910), (341, 906), (332, 882), (336, 856)])
        p.fill(pts, SKIN)
        p.cfill(f([(366, 850), (382, 850), (378, 906), (362, 906)]), SKIN_SH, blur=2)
        p.line(pts, 2.0, SKIN_LN, closed=True)
        thumb = f([(372, 864), (386, 875), (388, 892), (379, 899), (372, 886)])
        p.fill(thumb, SKIN, line=SKIN_LN, lw=1.8)
        body.append(p)
    for side, f in (('R', lambda x: x), ('L', M)):
        p = Part(f'手指_{side}')
        for i, (x, y, l) in enumerate([(339, 900, 24), (348, 905, 29), (357, 905, 27), (366, 901, 21)]):
            pts = f([(x - 5, y), (x + 5, y), (x + 4.6, y + l - 4.5), (x, y + l, 'c'), (x - 4.6, y + l - 4.5)])
            p.fill(pts, SKIN)
            p.cfill(f([(x + 1.5, y), (x + 6, y), (x + 6, y + l + 2), (x + 1.5, y + l + 2)]), SKIN_SH, blur=1.2)
            p.air(f([(x - 5, y + l - 8), (x + 5, y + l - 8), (x + 5, y + l), (x - 5, y + l)]), hx('f5a9a3', 150), blur=3)
            p.line(pts, 1.6, SKIN_LN, closed=True)
        body.append(p)
    G.append(('身體', body))

    # ---------------------------------------------------------------- head
    head = []
    for side, f in (('R', lambda x: x), ('L', M)):
        p = Part(f'耳朵_{side}')
        pts = f([(398, 314), (385, 306), (376, 316), (375, 340), (381, 360), (394, 372), (401, 366)])
        p.fill(pts, SKIN, line=SKIN_LN, lw=2.0)
        p.rib(f([(386, 320), (383, 340), (390, 358)]), [0.4, 1.6, 0.4], SKIN_SH2)
        head.append(p)

    p = Part('臉')
    p.fill(FACE, SKIN)
    head.append(p)

    p = Part('臉陰影')
    p.clip(FACE)
    p.cfill([(380, 330), (404, 330), (414, 380), (440, 420), (480, 446), (500, 452), (500, 470), (380, 470)], SKIN_SH, blur=2.2)
    p.cfill(M([(380, 330), (404, 330), (414, 380), (440, 420), (480, 446), (500, 452), (500, 470), (380, 470)]), SKIN_SH, blur=2.2)
    p.air([(470, 436), (530, 436), (530, 470), (470, 470)], hx('f2b7aa', 120), blur=6)
    head.append(p)

    p = Part('臉線')
    p.rib([(392, 300), (394, 336), (400, 368), (414, 400), (438, 426), (468, 443), (500, 449),
           (532, 443), (562, 426), (586, 400), (600, 368), (606, 336), (608, 300)],
          [0.5, 2, 2.4, 2.6, 2.6, 2.4, 2.2, 2.4, 2.6, 2.6, 2.4, 2, 0.5], SKIN_LN)
    head.append(p)

    for side, f in (('R', lambda x: x), ('L', M)):
        p = Part(f'腮紅_{side}')
        c = f([(436, 392)])[0]
        p.soft(ellipse(c[0], c[1], 22, 10), hx('ff8c9e', 150), 5)
        for dx in (-9, 0, 9):
            p.rib(f([(438 + dx + 4, 386), (438 + dx - 3, 398)]), [1.4, 0.3], hx('f06f86', 200))
        head.append(p)

    p = Part('鼻子')
    p.rib([(498, 390), (501, 395), (499, 399)], [0.4, 2.2, 0.4], SKIN_LN)
    head.append(p)

    mouth = []
    p = Part('下唇陰影')
    p.rib([(493, 438), (500, 440), (507, 438)], [0.4, 2.0, 0.4], hx('f0b7b0'))
    mouth.append(p)
    p = Part('口腔')
    p.fill([(486, 414), (500, 416), (514, 414), (511, 425), (500, 431), (489, 425)], MOUTH)
    mouth.append(p)
    p = Part('舌頭')
    p.fill([(490, 426), (500, 421), (510, 426), (505, 430), (500, 431), (495, 430)], TONGUE)
    mouth.append(p)
    p = Part('上排牙齒')
    p.fill([(488, 414.5), (512, 414.5), (510, 418.5), (490, 418.5)], hx('ffffff'), raw=True)
    mouth.append(p)
    p = Part('上唇')
    p.rib([(478, 409), (486, 413), (500, 415), (514, 413), (522, 409)], [0.4, 2, 2.3, 2, 0.4], MOUTH_LN)
    mouth.append(p)
    head.append(('嘴', mouth))

    head.append(('眼_R', eye('R')))
    head.append(('眼_L', eye('L')))

    for side, f in (('R', lambda x: x), ('L', M)):
        p = Part(f'眉毛_{side}')
        p.rib(f([(417, 311), (432, 304), (452, 301), (470, 305)]), [0.8, 3.0, 2.6, 0.6], hx('6f5ea8'))
        head.append(p)
    # hair shadow on the face (bangs shape pushed down, clipped by the face)
    for name, pts in (('髮陰影_R', bang_R()), ('髮陰影_中', bang_C()), ('髮陰影_L', M(bang_R()))):
        p = Part(name)
        p.clip(FACE)
        p.cfill(shift(pts, 0, 9), hx('f1c0b3'), blur=1.6)
        head.append(p)

    for side, f in (('R', lambda x: x), ('L', M)):
        p = Part(f'鬢角_{side}')
        pts = f(sidelock_R())
        p.fill(pts, HAIR)
        p.cgrad(pts, hx('bfaef0', 0), HAIR_SH, 300, 600)
        for k2, xx in enumerate((380, 386, 392, 398, 404)):
            p.strand(f([(xx + 4, 262), (xx + 2, 380), (xx - 2, 500), (xx + 4, 590)]), 1.4,
                     hx('7a69bd', 150) if k2 % 2 else hx('e3dbff', 150))
        p.air(f([(360, 250), (420, 250), (420, 330), (360, 330)]), hx('e8e0ff', 130), blur=8)
        p.line(pts, 2.2, HAIR_LN, closed=True)
        head.append(p)

    for name, pts, strands in (
            ('瀏海_R', bang_R(), [[(430, 230), (436, 280), (432, 322)], [(452, 214), (458, 262), (457, 290)]]),
            ('瀏海_L', M(bang_R()), [M([(430, 230), (436, 280), (432, 322)]), M([(452, 214), (458, 262), (457, 290)])]),
            ('瀏海_中', bang_C(), [[(500, 214), (503, 280), (502, 330)], [(478, 222), (478, 270), (470, 314)],
                                  [(524, 222), (526, 270), (531, 316)]])):
        p = Part(name)
        hair_piece(p, pts, strands=strands, seed=len(name) * 97 + len(pts))
        head.append(p)

    p = Part('呆毛')
    p.rib([(496, 176), (491, 146), (504, 122), (530, 116), (545, 130)], [8, 7, 5, 3, 0.4], HAIR_LN)
    p.rib([(496, 176), (491, 146), (504, 122), (530, 116), (545, 130)], [4.5, 3.6, 2.4, 1.2, 0.1], HAIR)
    head.append(p)


    # hair clip: small star on the character's left
    p = Part('髮飾')
    cx, cy = 590, 232
    star = []
    for i in range(10):
        r = 17 if i % 2 == 0 else 7.5
        a = math.radians(-90 + i * 36 + 12)
        star.append((cx + r * math.cos(a), cy + r * math.sin(a), 'c'))
    p.fill(star, hx('ffd65a'), line=hx('9a6a14'), lw=1.8)
    p.cfill(ellipse(cx - 4, cy - 4, 4, 3), hx('fff4c0'), raw=True)
    head.append(p)
    G.append(('頭', head))
    return G


def girl_smooth_closed(pts):
    q = smooth(pts)
    return q + q[:1]


def ribbon_raw(pts, w):
    c = np.array(pts, float)
    d = np.gradient(c, axis=0)
    d /= np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-6)
    nrm = np.stack([-d[:, 1], d[:, 0]], 1) * (w / 2)
    return [tuple(p) for p in np.vstack([c + nrm, (c - nrm)[::-1]])]
