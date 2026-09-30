# -*- coding: utf-8 -*-
"""紫髮小公主 without the golden ball (青蛙王子: after the ball falls into the well, before the frog brings it back)."""
import princess as P
from princess import *  # noqa: F401,F403
import copy


def build():
    out = []
    for name, items in P.build():
        out.append((name, [it for it in items if isinstance(it, tuple) or it.name != '道具_金球']))
    return out


RIG = copy.deepcopy(P.RIG)
RIG['arm_parts']['R'] = [n for n in RIG['arm_parts']['R'] if n != '道具_金球']
