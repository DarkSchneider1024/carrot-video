# -*- coding: utf-8 -*-
"""大野狼 disguised as grandma (act 4): glasses + frilly floral nightcap (ears poke through) + floral nightgown
with a ruffled collar. In the story he lies in bed under the blanket, so only the upper body matters."""
import copy
import numpy as np

import wolf as W
import wolf_glasses as WG
from girl import Part, hx, M
from girl_v4 import R, Rell, CX, K, LW
import red_hood as RH

PINK, PINK_SH, PINK_LN = hx('f3b8c8'), hx('d98aa3'), hx('8e4a62')
FRILL, FRILL_SH = hx('fff8fb'), hx('e7d5dc')
FLOWER = [hx('ffffff'), hx('ffe27a'), hx('c8e8a8')]

GOWN_FROM_VEST = (lambda t: (lambda c: (t[c[:3]][:3] + (c[3],)) if c[:3] in t else c))(
    {W.VEST[:3]: PINK, W.VEST_SH[:3]: PINK_SH, W.VEST_HI[:3]: hx('ffd6e2'), W.VEST_LN[:3]: PINK_LN})


def flowers(p, box, seed):
    rng = np.random.default_rng(seed)
    x0, y0, x1, y1 = box
    for _ in range(40):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        c = FLOWER[rng.integers(0, len(FLOWER))]
        for a in np.linspace(0, 2 * np.pi, 5, endpoint=False):
            p.cfill(Rell(x + 2.6 * np.cos(a), y + 2.6 * np.sin(a), 1.7, 1.7), c, raw=True, blur=0.2)
        p.cfill(Rell(x, y, 1.1, 1.1), hx('f08aa8'), raw=True, blur=0.2)


def nightcap():
    p = Part('睡帽')
    cap = [(CX, 96), (256, 100), (228, 116), (214, 142), (222, 150), (250, 136), (CX, 132)]
    pts = R(cap + RH.mirror_list(cap[1:-1]))
    p.fill(pts, PINK)
    flowers(p, (206, 92, 366, 150), 3)
    p.air(R([(206, 92), (366, 92), (366, 110), (206, 110)]), hx('ffffff', 90), blur=6)
    p.line(pts, LW, PINK_LN, closed=True)
    # frilled brim
    xs = np.linspace(214, 2 * CX - 214, 23)
    brim_top = [(x, 138 + 0.0008 * (x - CX) ** 2 * 0 - 4 + 6 * abs(np.sin((x - CX) / 60))) for x in xs]
    band = [(x, y - (3.5 if i % 2 else 0.5)) for i, (x, y) in enumerate(brim_top)] + [(x, y + 9) for x, y in brim_top[::-1]]
    p.fill(R(band), FRILL, line=hx('c9a9b6'), lw=LW * 0.8)
    for x, y in brim_top[1::2]:
        p.line(R([(x, y - 2), (x, y + 8)]), 0.7, FRILL_SH)
    p.fill(R([(CX - 7, 92), (CX, 86), (CX + 7, 92), (CX, 98)]), hx('ff8fb0'), line=PINK_LN, lw=0.8)   # tiny bow
    return p


def gown_collar():
    p = Part('睡衣領')
    xs = np.linspace(236, 2 * CX - 236, 21)
    top = [(x, 286 + 10 * ((x - CX) / 50) ** 2) for x in xs]
    band = [(x, y - (4 if i % 2 else 0)) for i, (x, y) in enumerate(top)] + [(x, y + 12) for x, y in top[::-1]]
    p.fill(R(band), FRILL, line=hx('c9a9b6'), lw=LW * 0.8)
    for x, y in top[1::2]:
        p.line(R([(x, y - 2), (x, y + 10)]), 0.7, FRILL_SH)
    return p


def build():
    out = []
    for name, items in WG.build():
        if name == '身體':
            new = []
            for it in items:
                if not isinstance(it, tuple) and it.name.startswith('背心'):
                    RH.recolor(it, GOWN_FROM_VEST)
                    flowers(it, (190, 290, 381, 545), 11 if it.name.endswith('R') else 12)
                new.append(it)
            new.append(gown_collar())
            items = new
        if name == '頭':
            ears = [it for it in items if not isinstance(it, tuple) and it.name.startswith('耳朵')]
            rest = [it for it in items if isinstance(it, tuple) or not it.name.startswith('耳朵')]
            items = rest + [nightcap()] + ears                      # ears poke out through the cap
        out.append((name, items))
    return out


landmarks, body_landmarks = W.landmarks, W.body_landmarks
RIG = copy.deepcopy(WG.RIG)
RIG['head3d']['layers']['睡帽'] = (1, 10)
