# -*- coding: utf-8 -*-
"""Rig a side-view (profile) character as an Inochi2D puppet with a real joint hierarchy.

    python live2d/engine/rig_side.py red_hood_side     -> 小紅帽/characters/red_hood_side/red_hood_side.inp ...

The character module exposes SIDE_RIG:
  bones      [(name, parent or None, pivot ref px)]  -- plain Nodes; each rotates about its pivot
  parts      {part name: bone}  (unlisted parts: head group -> 'Head', others -> 'Body')
  rotations  [(param, bone, sign)]  param value = angle in radians (-1..1), sign turns "+ = forward" into
             the screen rotation (y is down, so a forward swing of a hanging limb is a negative angle)
  eye / eye_parts / lash_parts / blink_drop, breath=[parts]
  mouth=(part, pivot, closed scale-y)  or  mouth_rot=(bone, angle)
Walk cycles are driven by the stage (live2d/player/stage.js), which knows the joint angles it wants.
Z order: parts keep the PSD order; because Inochi2D accumulates zsort down the tree, each part's zsort
is stored relative to its bone so the absolute order is unchanged.
"""
import io, json, os, random, struct, sys

os.environ.setdefault('GIRL_S', '1.2')
os.environ.setdefault('GIRL_SS', '2')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_psd as build   # noqa: E402
import girl                 # noqa: E402
import girl_v4 as G4        # noqa: E402

NAME, MODEL, OUT = build.PREFIX, build.MODEL, build.OUT
RIG = MODEL.SIDE_RIG
NO_TEX = 4294967295
S = girl.S
W, H = girl.W, girl.H
ORIGIN = (W / 2.0, H / 2.0)
U = S * G4.K

rnd = random.Random(20260924)
_used = set()


def new_uuid():
    while True:
        u = rnd.randrange(1, 2 ** 31)
        if u not in _used:
            _used.add(u)
            return u


def P(xr, yr):
    x, y = G4.RP(xr, yr)
    return (x * S - ORIGIN[0], y * S - ORIGIN[1])


def node(name, wx, wy, parent, typ='Node', zsort=0.0):
    px, py = parent['_world'] if parent else (0.0, 0.0)
    n = {'uuid': new_uuid(), 'name': name, 'type': typ, 'enabled': True, 'zsort': zsort,
         'transform': {'trans': [wx - px, wy - py, 0.0], 'rot': [0.0, 0.0, 0.0], 'scale': [1.0, 1.0]},
         'lockToRoot': False, 'children': [], '_world': (wx, wy), '_zabs': (parent or {}).get('_zabs', 0.0) + zsort}
    if parent is not None:
        parent['children'].append(n)
    return n


def main():
    print(f'rendering {NAME} layers at', W, 'x', H, '...')
    rendered = build.render_all(MODEL.build())
    N = len(rendered)
    os.makedirs(OUT, exist_ok=True)
    build.composite(rendered).save(os.path.join(OUT, 'psd_composite.png'))

    root = node('Root', 0.0, 0.0, None)
    bones = {}
    for name, parent, pivot in RIG['bones']:
        bones[name] = node(name, *P(*pivot), bones[parent] if parent else root)
    eye = node('Eye', *P(*RIG['eye']), bones['Head'])
    TURN = RIG.get('turn')
    far_eye = node('Eye Far', *P(*TURN['far_eye']['pivot']), bones['Head']) if TURN else None
    if 'mouth' in RIG:                      # (part, pivot, closed scale-y): the mouth part scales open
        mouth_part, mouth_pivot, mouth_closed = RIG['mouth'][:3]
        mouth_open = RIG['mouth'][3] if len(RIG['mouth']) > 3 else 1.0
        mouth = node('Mouth', *P(*mouth_pivot), bones['Head'])
    else:                                   # mouth_rot = (bone, angle): e.g. a jaw that swings open
        mouth_part = mouth = None

    textures, by = [], {}
    head_groups = set(RIG.get('head_groups', ('頭',)))
    for order, (gpath, name, im, x, y) in enumerate(rendered):
        buf = io.BytesIO()
        im.save(buf, 'PNG', optimize=True)
        textures.append(buf.getvalue())
        if name in RIG['eye_parts'] or name in RIG['lash_parts']:
            parent = eye
        elif TURN and name in TURN['far_eye']['parts']:
            parent = far_eye
        elif name == mouth_part:
            parent = mouth
        else:
            parent = bones[RIG['parts'].get(name, 'Head' if gpath[0] in head_groups else 'Body')]
        x0, y0 = x - ORIGIN[0], y - ORIGIN[1]
        px, py = parent['_world']
        # mesh in the parent's frame (Part node placed exactly at the parent pivot)
        cols = rows = 8 if TURN and name == TURN.get('face_part', '臉') else 2   # the face warps with Head:: Turn
        verts, uvs, idx = [], [], []
        for r in range(rows + 1):
            for c in range(cols + 1):
                u, v = c / cols, r / rows
                verts += [x0 + u * im.width - px, y0 + v * im.height - py]
                uvs += [u, v]
        for r in range(rows):
            for c in range(cols):
                a = r * (cols + 1) + c
                idx += [a, a + cols + 1, a + 1, a + 1, a + cols + 1, a + cols + 2]
        zabs = (N - order) * 0.01
        n = node(name, px, py, parent, typ='Part', zsort=round(zabs - parent['_zabs'], 4))
        n.update({'mesh': {'verts': verts, 'uvs': uvs, 'indices': idx, 'origin': [0.0, 0.0]},
                  'textures': [len(textures) - 1, NO_TEX, NO_TEX], 'blend_mode': 'Normal',
                  'tint': [1.0, 1.0, 1.0], 'screenTint': [0.0, 0.0, 0.0], 'emissionStrength': 1.0,
                  'mask_threshold': 0.5, 'opacity': 1.0})
        by[name] = n

    def vb(n, key, values):
        return {'node': n['uuid'], 'param_name': key, 'values': values,
                'isSet': [[True] * len(v) for v in values], 'interpolate_mode': 'Linear'}

    def param(name, mn, mx, ax, binds):
        return {'uuid': new_uuid(), 'name': name, 'is_vec2': False, 'min': [mn, mn], 'max': [mx, mx],
                'defaults': [0.0, 0.0], 'axis_points': [ax, [0.0]], 'merge_mode': 'Passthrough', 'bindings': binds}

    params = []
    for pname, bone, sign in RIG['rotations']:
        params.append(param(pname, -1.0, 1.0, [0.0, 1.0], [vb(bones[bone], 'transform.r.z', [[-sign], [sign]])]))
    blink = [vb(by[n], 'transform.s.y', [[1.0], [0.08]]) for n in RIG['eye_parts']]
    blink += [vb(by[n], 'transform.t.y', [[0.0], [RIG['blink_drop'] * U]]) for n in RIG['lash_parts']]
    params.append(param('Eye:: Blink', 0.0, 1.0, [0.0, 1.0], blink))
    if TURN:        # 90 deg profile (0) <-> 70 deg half-profile (1)
        fe = TURN['far_eye']
        tb = [vb(far_eye, 'transform.s.x', [[0.4], [1.0]]), vb(eye, 'transform.s.x', [[1.0], [TURN['near_eye_scale']]])]
        if 'dx' in fe:      # far eye hidden behind the face at rest: slide it out and bring it in front of the face
            tb += [vb(far_eye, 'transform.t.x', [[0.0], [fe['dx'] * U]]), vb(far_eye, 'zSort', [[0.0], [fe['dz']]])]
        for pre, (dx, dy) in TURN['shifts'].items():
            for nm, n in by.items():
                if nm.startswith(pre):
                    tb.append(vb(n, 'transform.t.x', [[0.0], [dx * U]]))
        n = by[TURN.get('face_part', '臉')]
        wx, wy = n['_world']
        vs = n['mesh']['verts']
        x_front = P(G4.CX + TURN['face_from'], 0)[0]
        xmax = max(vs[k] + wx for k in range(0, len(vs), 2))
        offs = []
        for k in range(0, len(vs), 2):
            x, y = vs[k] + wx, vs[k + 1] + wy
            yr = (y + ORIGIN[1]) / S / G4.K                        # back to reference px
            dx = 0.0
            for y0, y1, d in TURN['face']:
                if y0 <= yr < y1:
                    dx = d
            t = max(0.0, (x - x_front) / max(1e-6, xmax - x_front))
            offs.append([dx * U * t, 0.0])
        tb.append({'node': n['uuid'], 'param_name': 'deform', 'values': [[[[0.0, 0.0]] * len(offs)], [offs]],
                   'isSet': [[True], [True]], 'interpolate_mode': 'Linear'})
        params.append(param(TURN['param'], 0.0, 1.0, [0.0, 1.0], tb))
    if mouth:
        mo = [vb(mouth, 'transform.s.y', [[mouth_closed], [mouth_open]])]
    else:
        mo = [vb(bones[RIG['mouth_rot'][0]], 'transform.r.z', [[0.0], [RIG['mouth_rot'][1]]])]
    params.append(param('Mouth:: Open', 0.0, 1.0, [0.0, 1.0], mo))
    br = [vb(bones['Head'], 'transform.t.y', [[0.0], [-1.6 * U]])]
    br += [vb(by[n], 'transform.s.y', [[1.0], [1.012]]) for n in RIG.get('breath', []) if n in by]
    params.append(param('Body:: Breath', 0.0, 1.0, [0.0, 1.0], br))

    def strip(n):
        n = {k: v for k, v in n.items() if not k.startswith('_')}
        n['children'] = [strip(c) for c in n['children']]
        if not n['children']:
            del n['children']
        return n

    puppet = {
        'meta': {'name': NAME, 'version': '1.0-alpha', 'rigger': 'Claude (live2d/engine/rig_side.py)',
                 'artist': f'Claude ({NAME}.py, drawn in Python)', 'copyright': None, 'licenseURL': None,
                 'contact': None, 'reference': None, 'thumbnailId': NO_TEX, 'preservePixels': False},
        'physics': {'pixelsPerMeter': 1000.0, 'gravity': 9.8},
        'nodes': strip(root), 'param': params, 'automation': [], 'animations': {},
    }
    js = json.dumps(puppet, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    for ext in ('inp', 'inx'):
        with open(os.path.join(OUT, f'{NAME}.{ext}'), 'wb') as f:
            f.write(b'TRNSRTS\0' + struct.pack('>I', len(js)) + js + b'TEX_SECT' + struct.pack('>I', len(textures)))
            for t in textures:
                f.write(struct.pack('>I', len(t)) + bytes([0]) + t)
    with open(os.path.join(OUT, 'puppet.json'), 'w', encoding='utf-8') as f:
        json.dump(puppet, f, ensure_ascii=False, indent=1)
    # joint positions in puppet units, for the stage's walk solver
    joints = {name: P(*pivot) for name, _, pivot in RIG['bones']}
    with open(os.path.join(OUT, 'joints.json'), 'w', encoding='utf-8') as f:
        json.dump(joints, f, ensure_ascii=False, indent=1)
    print('parts', len(by), 'params', len(params), 'size', os.path.getsize(os.path.join(OUT, f'{NAME}.inp')) // 1024, 'KiB')


if __name__ == '__main__':
    main()
