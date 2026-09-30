# -*- coding: utf-8 -*-
"""Rig any character module as an Inochi2D puppet (.inp + .inx), driven by the module's RIG dict.

    python live2d/engine/rig.py red_hood        -> 小紅帽/characters/red_hood/red_hood.inp / .inx / puppet.json
    python live2d/engine/rig.py wolf

Generalised from gimp-test/src/inochi2d/make_puppet.py (girl_v4). Format = Inochi2D 0.8 INP ("TRNSRTS\\0",
big-endian lengths, JSON payload, TEX_SECT with PNG blobs); see the inochi2d-puppet skill for the rules.

RIG keys (reference px of the girl_v4 grid; right-side points, the left side is mirrored):
  neck, waist            pivots of the Head / Body nodes
  eyes                   {'R': (cx, cy), 'L': (cx, cy)}, lower_lid_dy, blink_drop
  mouth_y, mouth_open    list of (part, key, value_when_open) -- missing parts are skipped
  head3d                 nine-axis head (Head:: Yaw-Pitch, 3 x 3 keyforms, +-30 deg / +-20 deg): the head parts
                         sit on an ellipsoid {'center', 'radii': (a, b, c) ref px, 'layers': {prefix: (side, dz)}}
                         side +1 = front surface, -1 = back surface (back hair / hood move the other way);
                         dz = extra depth in ref px (bangs float in front of the face, the nose sticks out)
  hair_deform            part names that sway with Hair:: Sway (hang from their top edge)
  arm_parts              {'R': [...], 'L': [...]} parts bent by the arm fields; arm_pivots (shoulder, elbow,
                         wrist) for the right arm; arm_warp: callable applied to the pivots (or None)
  breath_scale / breath_lift   parts that swell / rise with Body:: Breath
  extras                 [{'param', 'parts', 'pivot', 'angle', 'ramp': (y0, y1)}] extra swing parameters
  lifts                  [{'param', 'parts', 'dy'}] 0..1 parameters that raise parts (leg steps for walking)
  chest                  chest physics (Live2D Tips 04): {'centers': [(x, y) ref px], 'radius': (rx, ry), 'sway',
                         'attach_y' / 'free_y' (optional): anchored at the pectoral, free at the bottom (vrR2fITO-ZE),
                         'bounce' (ref px), 'squash' (fraction), 'parts'} -> Chest:: Sway X / Bounce Y / Squash, one
                         continuous warp field on skin + clothing so the garment never separates from the body
"""
import io, json, math, os, random, struct, sys

os.environ.setdefault('GIRL_S', '1.2')      # 1200 x 2000 puppet
os.environ.setdefault('GIRL_SS', '2')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_psd as build   # noqa: E402  (picks the character module from argv / CHARACTER)
import girl                 # noqa: E402
import girl_v4 as G4        # noqa: E402

NAME = build.PREFIX
MODEL = build.MODEL
RIG = MODEL.RIG
OUT = build.OUT
NO_TEX = 4294967295
S = girl.S
W, H = girl.W, girl.H
ORIGIN = (W / 2.0, H / 2.0)
U = S * G4.K                     # reference px -> puppet px

rnd = random.Random(20260923)
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


def mirror_x(x):
    return 2 * G4.CX - x


def tf(x=0.0, y=0.0):
    return {'trans': [x, y, 0.0], 'rot': [0.0, 0.0, 0.0], 'scale': [1.0, 1.0]}


def node(name, x=0.0, y=0.0, zsort=0.0, typ='Node'):
    return {'uuid': new_uuid(), 'name': name, 'type': typ, 'enabled': True, 'zsort': zsort,
            'transform': tf(x, y), 'lockToRoot': False, 'children': [], '_world': (x, y)}


def smooth01(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def main():
    print(f'rendering {NAME} layers at', W, 'x', H, '...')
    rendered = build.render_all(MODEL.build())
    rendered = [r for r in rendered if r[1] != '背景色']
    N = len(rendered)
    os.makedirs(OUT, exist_ok=True)
    build.composite(rendered).save(os.path.join(OUT, 'psd_composite.png'))

    textures, parts = [], {}
    for i, (gpath, name, im, x, y) in enumerate(rendered):
        buf = io.BytesIO()
        im.save(buf, 'PNG', optimize=True)
        textures.append(buf.getvalue())
        parts[name] = dict(order=i, group=gpath, w=im.width, h=im.height, x0=x - ORIGIN[0], y0=y - ORIGIN[1],
                           tex=len(textures) - 1)

    HAIR = set(RIG.get('hair_deform', ()))
    ARM = {n for side in ('R', 'L') for n in RIG.get('arm_parts', {}).get(side, ())}
    EXTRA = {n for e in RIG.get('extras', ()) for n in e['parts']}
    CHEST = set(RIG.get('chest', {}).get('parts', ()))

    def grid_mesh(w, h, cols, rows, px, py, x0, y0):
        verts, uvs, idx = [], [], []
        for r in range(rows + 1):
            for c in range(cols + 1):
                u, v = c / cols, r / rows
                verts += [x0 + u * w - px, y0 + v * h - py]
                uvs += [u, v]
        for r in range(rows):
            for c in range(cols):
                a = r * (cols + 1) + c
                b, d, e = a + 1, a + cols + 1, a + cols + 2
                idx += [a, d, b, b, d, e]
        return verts, uvs, idx

    def make_part(name, parent, pivot=None, head=False):
        info = parts[name]
        cx, cy = info['x0'] + info['w'] / 2, info['y0'] + info['h'] / 2
        px, py = pivot if pivot else (cx, cy)
        if name in HAIR or name in EXTRA:
            cols, rows = (max(3, min(8, info['w'] // 60)), max(4, min(12, info['h'] // 60)))
        elif name in ARM:
            cols, rows = (max(3, min(5, info['w'] // 40)), max(4, min(12, info['h'] // 40)))
        elif name in CHEST:              # chest physics warp
            cols, rows = (max(4, min(12, info['w'] // 30)), max(4, min(12, info['h'] // 30)))
        elif head:                       # nine-axis warp needs a grid on every head part
            cols, rows = (max(3, min(10, info['w'] // 40)), max(3, min(12, info['h'] // 40)))
        else:
            cols, rows = 1, 1
        verts, uvs, idx = grid_mesh(info['w'], info['h'], cols, rows, px, py, info['x0'], info['y0'])
        wx, wy = parent['_world']
        n = node(name, px - wx, py - wy, zsort=(N - info['order']) * 0.01, typ='Part')
        n['zsort'] = round(n['zsort'] - parent.get('_zabs', 0.0), 4)
        n['_world'] = (px, py)
        n['_zabs'] = parent.get('_zabs', 0.0) + n['zsort']
        n.update({'mesh': {'verts': verts, 'uvs': uvs, 'indices': idx, 'origin': [0.0, 0.0]},
                  'textures': [info['tex'], NO_TEX, NO_TEX], 'blend_mode': 'Normal',
                  'tint': [1.0, 1.0, 1.0], 'screenTint': [0.0, 0.0, 0.0], 'emissionStrength': 1.0,
                  'mask_threshold': 0.5, 'opacity': 1.0})
        parent['children'].append(n)
        return n

    def child_node(parent, name, x, y):
        wx, wy = parent['_world']
        n = node(name, x - wx, y - wy)
        n['_world'] = (x, y)
        n['_zabs'] = parent.get('_zabs', 0.0)
        parent['children'].append(n)
        return n

    # ------------------------------------------------------------------ node tree
    root = node('Root')
    root['_world'] = (0.0, 0.0)
    by = {}
    body = child_node(root, 'Body', *P(*RIG['waist']))
    head = child_node(root, 'Head', *P(*RIG['neck']))
    eye_nodes, ball_nodes = {}, {}
    for side in ('R', 'L'):
        ex, ey = RIG['eyes'][side]
        eye_nodes[side] = child_node(head, f'Eye {side}', *P(ex, ey))
        ball_nodes[side] = child_node(eye_nodes[side], f'EyeBall {side}', *P(ex, ey + RIG['lower_lid_dy']))
    mouth = child_node(head, 'Mouth', *P(G4.CX, RIG['mouth_y']))

    HEAD_GROUPS = set(RIG.get('head_groups', ('頭', '後髮')))
    for gpath, name, im, x, y in rendered:
        info = parts[name]
        top_pivot = (info['x0'] + info['w'] / 2, info['y0'])
        top = gpath[0]
        if top == '背景':
            by[name] = make_part(name, root)
        elif top not in HEAD_GROUPS:
            by[name] = make_part(name, body, pivot=top_pivot if name in HAIR else None)
        else:
            sub = gpath[1] if len(gpath) > 1 else None
            if sub in ('眼_R', '眼_L'):
                side = sub[-1]
                if name.startswith(('眼白', '眼球', '高光')):
                    by[name] = make_part(name, ball_nodes[side], pivot=ball_nodes[side]['_world'], head=True)
                else:
                    by[name] = make_part(name, eye_nodes[side], head=True)
            elif sub == '嘴':
                by[name] = make_part(name, mouth, pivot=top_pivot if name in ('口腔', '舌頭') else None, head=True)
            else:
                by[name] = make_part(name, head, pivot=top_pivot if name in HAIR or top == '後髮' else None, head=True)

    phys = child_node(head, 'Hair Physics', *P(G4.CX, 120))
    phys['type'] = 'SimplePhysics'

    # ------------------------------------------------------------------ parameters
    def val_binding(n, key, values):
        return {'node': n['uuid'], 'param_name': key, 'values': values,
                'isSet': [[True] * len(v) for v in values], 'interpolate_mode': 'Linear'}

    def deform_binding(n, offs):
        return {'node': n['uuid'], 'param_name': 'deform', 'values': [[o] for o in offs],
                'isSet': [[True] for _ in offs], 'interpolate_mode': 'Linear'}

    def param(name, is_vec2, mn, mx, dflt, ax, ay, bindings):
        return {'uuid': new_uuid(), 'name': name, 'is_vec2': is_vec2, 'min': mn, 'max': mx, 'defaults': dflt,
                'axis_points': [ax, ay], 'merge_mode': 'Passthrough', 'bindings': bindings}

    def p01(name, binds):
        return param(name, False, [0.0, 0.0], [1.0, 1.0], [0.0, 0.0], [0.0, 1.0], [0.0], binds)

    def pm11(name, binds):
        return param(name, False, [-1.0, -1.0], [1.0, 1.0], [0.0, 0.0], [0.0, 0.5, 1.0], [0.0], binds)

    params = []

    # Head:: Yaw-Pitch -- nine-axis (九軸): 3 x 3 keyforms from rotating the head parts on an ellipsoid.
    # Edge keys = pure yaw / pure pitch; the four corners are the true combined rotation (= 四角合成 + 修正).
    H3 = RIG['head3d']
    hc = P(*H3['center'])
    ha, hb, hc_ = (r * U for r in H3['radii'])
    layers = sorted(H3['layers'].items(), key=lambda kv: -len(kv[0]))
    YAW, PITCH = math.radians(H3.get('yaw_deg', 30)), math.radians(H3.get('pitch_deg', 20))

    def layer_of(name):
        for pre, v in layers:
            if name.startswith(pre):
                return v
        return (1, 0.0)

    def rotate(x, y, side, dz, th, ph):
        dx, dy = x - hc[0], y - hc[1]
        u, v = dx / ha, dy / hb
        r = math.hypot(u, v)
        ex = ey = 0.0
        if r > 1:                                   # outside the ellipsoid rim: carry the excess rigidly
            ex, ey = dx * (1 - 1 / r), dy * (1 - 1 / r)
            u, v = u / r, v / r
        X, Y = u * ha, v * hb
        Z = side * math.sqrt(max(0.0, 1 - u * u - v * v)) * hc_ + dz * U * (1 if side > 0 else -1)
        x1 = X * math.cos(th) + Z * math.sin(th)
        z1 = -X * math.sin(th) + Z * math.cos(th)
        if z1 * side < 0:                           # never fold past the silhouette: stick to the limb
            x1 = math.copysign(math.hypot(X, Z), x1); z1 = 0.0
        y2 = Y * math.cos(ph) + z1 * math.sin(ph)
        z2 = -Y * math.sin(ph) + z1 * math.cos(ph)
        if z2 * side < 0:
            y2 = math.copysign(math.hypot(Y, z1), y2)
        return hc[0] + x1 + ex, hc[1] + y2 + ey

    yaw = []
    for gpath, name, im, x, y in rendered:
        if gpath[0] not in HEAD_GROUPS:
            continue
        n = by[name]
        side, dz = layer_of(name)
        wx, wy = n['_world']
        vs = n['mesh']['verts']
        keys = []
        for kx in (-1.0, 0.0, 1.0):                 # x keys
            col = []
            for ky in (-1.0, 0.0, 1.0):             # y keys (param y -1 = looking down)
                th, ph = kx * YAW, -ky * PITCH
                offs = []
                for i in range(0, len(vs), 2):
                    X0, Y0 = vs[i] + wx, vs[i + 1] + wy
                    bx, by_ = rotate(X0, Y0, side, dz, 0.0, 0.0)
                    nx, ny = rotate(X0, Y0, side, dz, th, ph)
                    offs.append([nx - bx, ny - by_])
                col.append(offs)
            keys.append(col)
        yaw.append({'node': n['uuid'], 'param_name': 'deform', 'values': keys,
                    'isSet': [[True] * 3 for _ in range(3)], 'interpolate_mode': 'Linear'})
    params.append(param('Head:: Yaw-Pitch', True, [-1.0, -1.0], [1.0, 1.0], [0.0, 0.0], [0.0, 0.5, 1.0],
                        [0.0, 0.5, 1.0], yaw))
    params.append(pm11('Head:: Roll', [val_binding(head, 'transform.r.z', [[-0.12], [0.0], [0.12]])]))

    # Eye blink (0 open, 1 closed)
    for side, pname in (('L', 'Eye:: Left:: Blink'), ('R', 'Eye:: Right:: Blink')):
        bl = [val_binding(ball_nodes[side], 'transform.s.y', [[1.0], [0.06]])]
        for nm in ('上眼線', '上睫毛'):
            if f'{nm}_{side}' in by:
                bl.append(val_binding(by[f'{nm}_{side}'], 'transform.t.y', [[0.0], [RIG['blink_drop'] * U]]))
        bl.append(val_binding(by[f'上眼線_{side}'], 'transform.s.y', [[1.0], [0.75]]))
        params.append(p01(pname, bl))

    # Mouth:: Open
    mo = []
    for nm, key, v in RIG['mouth_open']:
        if nm in by:
            base = 1.0 if key.startswith('transform.s') else 0.0
            mo.append(val_binding(by[nm], key, [[base], [v * (U if key.startswith('transform.t') else 1.0)]]))
    params.append(p01('Mouth:: Open', mo))

    # Body:: Breath
    br = [val_binding(head, 'transform.t.y', [[0.0], [-1.6 * U]])]
    for nm in RIG.get('breath_scale', ()):
        if nm in by:
            br.append(val_binding(by[nm], 'transform.s.y', [[1.0], [1.012]]))
    for nm in RIG.get('breath_lift', ()):
        if nm in by:
            br.append(val_binding(by[nm], 'transform.t.y', [[0.0], [-1.2 * U]]))
    params.append(p01('Body:: Breath', br))

    # rotation fields (arms, extras)
    def rot_field(n, centre, ang, y0, y1):
        wx, wy = n['_world']
        vs = n['mesh']['verts']
        out = []
        for k in range(0, len(vs), 2):
            px, py = vs[k] + wx, vs[k + 1] + wy
            a = ang * smooth01((py - y0) / (y1 - y0)) if y1 != y0 else ang
            dx, dy = px - centre[0], py - centre[1]
            c, s_ = math.cos(a), math.sin(a)
            out.append([dx * c - dy * s_ - dx, dx * s_ + dy * c - dy])
        return out

    warp = RIG.get('arm_warp')

    def arm_pt(side, x, y):
        if warp:
            x, y = warp(x, y)
        return P(mirror_x(x) if side == 'L' else x, y)

    if RIG.get('arm_parts'):
        sh, el, wr = RIG['arm_pivots']
        for side, sname, sgn in (('R', 'Right', 1.0), ('L', 'Left', -1.0)):
            S_, E_, W_ = arm_pt(side, *sh), arm_pt(side, *el), arm_pt(side, *wr)
            specs = [(f'Arm:: {sname}:: Swing', S_, 0.11 * sgn, S_[1] + 10 * U, E_[1], (-1.0, 0.0, 1.0)),
                     (f'Arm:: {sname}:: Bend', E_, -0.32 * sgn, E_[1] - 10 * U, E_[1] + 22 * U, (0.0, 1.0)),
                     (f'Hand:: {sname}:: Wrist', W_, 0.30 * sgn, W_[1] - 5 * U, W_[1] + 12 * U, (-1.0, 0.0, 1.0))]
            for pname, C_, amax, y0, y1, keys in specs:
                binds = [deform_binding(by[nm], [rot_field(by[nm], C_, amax * k, y0, y1) for k in keys])
                         for nm in RIG['arm_parts'][side] if nm in by]
                params.append(pm11(pname, binds) if len(keys) == 3 else p01(pname, binds))

    for e in RIG.get('extras', ()):
        C_ = P(*e['pivot'])
        y0, y1 = (P(0, e['ramp'][0])[1], P(0, e['ramp'][1])[1]) if e.get('ramp') else (C_[1], C_[1])
        binds = [deform_binding(by[nm], [rot_field(by[nm], C_, e['angle'] * k, y0, y1) for k in (-1.0, 0.0, 1.0)])
                 for nm in e['parts'] if nm in by]
        params.append(pm11(e['param'], binds))

    # lifts: simple translate-up parameters (e.g. Leg:: Right:: Step for the walk cycle)
    for lf in RIG.get('lifts', ()):
        binds = [val_binding(by[nm], 'transform.t.y', [[0.0], [lf['dy'] * U]]) for nm in lf['parts'] if nm in by]
        params.append(p01(lf['param'], binds))

    # Chest physics: Sway X (-1..1), Bounce Y (-1..1), Squash (-1..1) -- smooth falloff around each bust
    if RIG.get('chest'):
        C = RIG['chest']
        cen = [P(*c) for c in C['centers']]
        rx, ry = C['radius'][0] * U, C['radius'][1] * U

        def weight(x, y):
            w, near = 0.0, cen[0]
            for c in cen:
                d = math.hypot((x - c[0]) / rx, (y - c[1]) / ry)
                wi = smooth01(1.0 - d) if d < 1 else 0.0
                if wi > w:
                    near = c
                w += wi
            return min(1.0, w), near

        # anatomy: the breast hangs from its pectoral attachment -> no motion at the attachment line, full at the
        # free bottom (a mass on a hinge, not a disc sliding around)
        ay = P(0, C['attach_y'])[1] if 'attach_y' in C else None
        fy = P(0, C['free_y'])[1] if 'free_y' in C else None

        def chest_offsets(n, kind, k):
            wx, wy = n['_world']
            vs = n['mesh']['verts']
            out = []
            for i in range(0, len(vs), 2):
                x, y = vs[i] + wx, vs[i + 1] + wy
                w, c = weight(x, y)
                if ay is not None:
                    w *= smooth01((y - ay) / max(1e-6, fy - ay)) ** 0.8
                if kind == 'x':
                    out.append([k * C['sway'] * U * w, 0.0])
                elif kind == 'y':          # bounce: moves, and stretches a little below the centre
                    out.append([0.0, k * C['bounce'] * U * w * (1.0 + 0.25 * max(0.0, (y - c[1]) / ry))])
                else:                      # squash (+) = wider & shorter, (-) = narrower & taller
                    out.append([(x - c[0]) * C['squash'] * k * w, -(y - c[1]) * C['squash'] * 0.8 * k * w])
            return out

        for pname, kind in (('Chest:: Sway X', 'x'), ('Chest:: Bounce Y', 'y'), ('Chest:: Squash', 's')):
            binds = [deform_binding(by[nm], [chest_offsets(by[nm], kind, k) for k in (-1.0, 0.0, 1.0)])
                     for nm in C['parts'] if nm in by]
            params.append(pm11(pname, binds))

    # Hair:: Sway
    hs = []
    for nm in sorted(HAIR):
        if nm not in by:
            continue
        n = by[nm]
        vs = n['mesh']['verts']
        ys = vs[1::2]
        top, bot = min(ys), max(ys)
        amp = 0.07 * (bot - top) + 4
        offs = []
        for s_ in (-1.0, 0.0, 1.0):
            offs.append([[s_ * amp * ((vs[k + 1] - top) / max(1e-6, bot - top)) ** 1.6, 0.0]
                         for k in range(0, len(vs), 2)])
        hs.append(deform_binding(n, offs))
    hair_param = pm11('Hair:: Sway', hs)
    params.append(hair_param)
    phys.update({'param': hair_param['uuid'], 'model_type': 'Pendulum', 'map_mode': 'AngleLength',
                 'gravity': 1.0, 'length': 100.0, 'frequency': 1.0, 'angle_damping': 0.5, 'length_damping': 0.5,
                 'output_scale': [1.0, 1.0], 'local_only': False})

    # ------------------------------------------------------------------ write
    def strip(n):
        n = {k: v for k, v in n.items() if not k.startswith('_')}
        n['children'] = [strip(c) for c in n['children']]
        if not n['children']:
            del n['children']
        return n

    puppet = {
        'meta': {'name': NAME, 'version': '1.0-alpha', 'rigger': 'Claude (live2d/engine/rig.py)',
                 'artist': f'Claude ({NAME}.py, drawn in Python)', 'copyright': None, 'licenseURL': None,
                 'contact': None, 'reference': None, 'thumbnailId': NO_TEX, 'preservePixels': False},
        'physics': {'pixelsPerMeter': 1000.0, 'gravity': 9.8},
        'nodes': strip(root), 'param': params, 'automation': [], 'animations': {},
    }

    def write_inp(path):
        js = json.dumps(puppet, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        with open(path, 'wb') as f:
            f.write(b'TRNSRTS\0')
            f.write(struct.pack('>I', len(js)))
            f.write(js)
            f.write(b'TEX_SECT')
            f.write(struct.pack('>I', len(textures)))
            for t in textures:
                f.write(struct.pack('>I', len(t)))
                f.write(bytes([0]))
                f.write(t)

    write_inp(os.path.join(OUT, f'{NAME}.inp'))
    write_inp(os.path.join(OUT, f'{NAME}.inx'))
    with open(os.path.join(OUT, 'puppet.json'), 'w', encoding='utf-8') as f:
        json.dump(puppet, f, ensure_ascii=False, indent=1)
    print('parts', len(parts), 'params', [p['name'] for p in params])
    print('size', os.path.getsize(os.path.join(OUT, f'{NAME}.inp')) // 1024, 'KiB')


if __name__ == '__main__':
    main()
