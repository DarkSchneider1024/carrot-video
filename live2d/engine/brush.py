# -*- coding: utf-8 -*-
"""A small dab-based brush engine (the way Photoshop / CSP brushes work).

A stroke is a polyline in pixel space plus a per-point radius (pressure).
The path is resampled at a spacing proportional to the current radius and a
round, soft-edged, slightly grainy tip is stamped at each sample.  Dabs build
up with  m = 1 - (1 - m) * (1 - flow * tip)  so overlaps darken gradually and
the edges stay soft, instead of the hard polygon edge of a vector stroke.
"""
import math
import numpy as np

_TIPS = {}
_GRAIN = None


def _grain(seed=7, n=256):
    global _GRAIN
    if _GRAIN is None:
        rng = np.random.default_rng(seed)
        g = rng.random((n, n)).astype(np.float32)
        # soften the noise a little so it reads as paper/bristle grain, not static
        g = (g + np.roll(g, 1, 0) + np.roll(g, 1, 1) + np.roll(g, (1, 1), (0, 1))) / 4
        _GRAIN = g
    return _GRAIN


def tip(r, hardness, grain):
    """Round tip of radius r (px). hardness 0..1 = how far out the core stays opaque."""
    key = (round(r * 4) / 4, round(hardness, 2), round(grain, 2))
    t = _TIPS.get(key)
    if t is None:
        rr = key[0]
        n = int(math.ceil(rr)) + 2
        y, x = np.mgrid[-n:n + 1, -n:n + 1].astype(np.float32)
        d = np.sqrt(x * x + y * y) / max(rr, 0.5)
        h = min(hardness, 0.98)
        a = np.clip((1 - d) / (1 - h), 0, 1)
        a = a * a * (3 - 2 * a)                          # smoothstep falloff
        if grain > 0:
            g = _grain()[:a.shape[0], :a.shape[1]]
            a = a * (1 - grain + grain * g * 1.6).clip(0, 1)
        t = a.astype(np.float32)
        _TIPS[key] = t
    return t


def resample(pts, radii, spacing):
    """Walk the polyline, emitting dab centres every spacing*radius px."""
    pts = np.asarray(pts, np.float32)
    radii = np.asarray(radii, np.float32)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    L = np.concatenate([[0], np.cumsum(seg)])
    out, s = [], 0.0
    total = L[-1]
    while s <= total:
        i = min(np.searchsorted(L, s, side='right') - 1, len(seg) - 1)
        f = 0 if seg[i] == 0 else (s - L[i]) / seg[i]
        p = pts[i] + (pts[i + 1] - pts[i]) * f
        r = radii[i] + (radii[i + 1] - radii[i]) * f
        out.append((p[0], p[1], r))
        s += max(0.6, spacing * r)
    return out


def stroke(mask, pts, radii, flow=0.35, hardness=0.55, grain=0.12, spacing=0.12):
    """Stamp a stroke into mask (float32 HxW, 0..1), in place."""
    H, W = mask.shape
    for x, y, r in resample(pts, radii, spacing):
        if r < 0.35:
            continue
        t = tip(r, hardness, grain)
        n = t.shape[0] // 2
        cx, cy = int(round(x)), int(round(y))
        x0, y0 = cx - n, cy - n
        x1, y1 = x0 + t.shape[1], y0 + t.shape[0]
        if x1 <= 0 or y1 <= 0 or x0 >= W or y0 >= H:
            continue
        tx0, ty0 = max(0, -x0), max(0, -y0)
        tx1, ty1 = t.shape[1] - max(0, x1 - W), t.shape[0] - max(0, y1 - H)
        sub = mask[max(0, y0):min(H, y1), max(0, x0):min(W, x1)]
        sub *= 1 - flow * t[ty0:ty1, tx0:tx1]
    return mask


def pressure(n, taper_in=0.18, taper_out=0.25, wobble=0.10, seed=0, min_p=0.12):
    """Pen-pressure curve along n samples: ease-in, ease-out, low-frequency wobble."""
    t = np.linspace(0, 1, n)
    a = np.clip(t / max(taper_in, 1e-3), 0, 1) if taper_in > 0 else np.ones(n)
    b = np.clip((1 - t) / max(taper_out, 1e-3), 0, 1) if taper_out > 0 else np.ones(n)
    p = (a ** 0.6) * (b ** 0.8)
    rng = np.random.default_rng(seed)
    ph = rng.random(3) * 6.28
    w = 1 + wobble * (0.6 * np.sin(t * 5.1 + ph[0]) + 0.4 * np.sin(t * 11.7 + ph[1]))
    return np.clip(min_p + (1 - min_p) * p, 0, 1) * w
