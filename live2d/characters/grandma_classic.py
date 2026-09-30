# -*- coding: utf-8 -*-
"""外婆 for the classic 小紅帽: the same grandma sitting up in bed under her quilt, but no phone --
her hands rest folded on the quilt."""
import grandma as G
import girl_v4 as G4
from girl import Part
from girl_v4 import R, Rell


def folded_hands():
    p = Part('雙手')
    for (hx0, hy0, flip) in ((270, 448, 1), (300, 446, -1)):
        hand = [(hx0 - 14 * flip, hy0 - 6), (hx0 + 8 * flip, hy0 - 10), (hx0 + 16 * flip, hy0 + 2),
                (hx0 + 10 * flip, hy0 + 12), (hx0 - 12 * flip, hy0 + 12)]
        cuff = [(hx0 - 26 * flip, hy0 - 4), (hx0 - 10 * flip, hy0 - 8), (hx0 - 8 * flip, hy0 + 14), (hx0 - 26 * flip, hy0 + 14)]
        p.fill(R(cuff), G.CARD, line=G.CARD_LN, lw=G4.LW * 0.8)
        p.fill(R(hand), G4.SKIN, line=G4.SKIN_LN, lw=G4.LW * 0.9)
        p.cfill(R([(hx0 - 14, hy0 + 4), (hx0 + 14, hy0 + 4), (hx0 + 14, hy0 + 14), (hx0 - 14, hy0 + 14)]), G4.SKIN_SH, blur=2)
    return p


def build():
    orig = G.phone_hands
    G.phone_hands = folded_hands
    try:
        return G.build()
    finally:
        G.phone_hands = orig


landmarks, body_landmarks = G.landmarks, G.body_landmarks
RIG = dict(G.RIG, breath_lift=['雙手', '上臂_R', '上臂_L'])
