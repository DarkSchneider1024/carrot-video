# -*- coding: utf-8 -*-
"""Smaller head for the hunter-based men (王子 / 國王): the hunter's head is drawn ~1/5 of his height, which
looks huge next to the anime princess (~1/7). Every head layer is drawn through girl_v4.WARP scaled about the
chin, so the neck joint stays where it is; rig landmarks are mapped with S()."""
import girl_v4 as G4
from girl_v4 import CX

HEAD_S = 0.8
CHIN_Y = 284.0


def S(x, y):
    return (CX + (x - CX) * HEAD_S, CHIN_Y + (y - CHIN_Y) * HEAD_S)


def scaled(fn):
    def w(*a, **k):
        old = G4.WARP
        G4.WARP = S
        try:
            return fn(*a, **k)
        finally:
            G4.WARP = old
    return w


HEAD_FUNCS = ('ears', 'back_hair', 'face', 'cheeks', 'beard', 'mouth_parts', 'mustache', 'nose', 'eye', 'brows',
              'front_hair', 'hat', 'feather')


def patch(H):
    for n in HEAD_FUNCS:
        setattr(H, n, scaled(getattr(H, n)))


def rig(RIG):
    RIG['eyes'] = {k: S(*v) for k, v in RIG['eyes'].items()}
    RIG['mouth_y'] = S(CX, RIG['mouth_y'])[1]
    h = RIG['head3d']
    h['center'] = S(*h['center'])
    h['radii'] = tuple(r * HEAD_S for r in h['radii'])
    RIG['lower_lid_dy'] *= HEAD_S
    RIG['blink_drop'] *= HEAD_S


BODY_SX = 0.8          # the hunter's torso / limbs are much broader than the princess -> slimmer build


def BX(x, y):
    return (CX + (x - CX) * BODY_SX, y)


def build_slim(H):
    """H.build() with the body drawn BODY_SX narrower (head layers keep their own uniform S warp)"""
    old = G4.WARP
    G4.WARP = BX
    try:
        return H.build()
    finally:
        G4.WARP = old


def rig_body(RIG):
    RIG['arm_pivots'] = tuple(BX(*p) for p in RIG['arm_pivots'])


def slim(fn):
    """body-layer helper drawn outside build_slim (e.g. trims added afterwards) -> same narrow warp"""
    def w(*a, **k):
        old = G4.WARP
        G4.WARP = BX
        try:
            return fn(*a, **k)
        finally:
            G4.WARP = old
    return w
