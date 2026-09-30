# -*- coding: utf-8 -*-
"""小紅帽 profile (《半夜三點的牛肉麵》 version): red_hood_side with the take-out noodle bag instead of the basket."""
import copy

import red_hood_side as RS
from red_noodle import noodle_bag, phone
from girl_v4 import CX

SIDE_RIG = copy.deepcopy(RS.SIDE_RIG)
SIDE_RIG['parts']['手機'] = 'Forearm B'          # phone in the far hand; the stage lifts that arm forward


def build():
    out = []
    for name, items in RS.build():
        new = []
        for it in items:
            if not isinstance(it, tuple) and it.name == '籃子':
                it = noodle_bag(CX, 568)
            new.append(it)
            if not isinstance(it, tuple) and it.name == '下臂_後':
                new.append(phone(CX + 2, 566, tilt=-0.2))
        out.append((name, new))
    return out
