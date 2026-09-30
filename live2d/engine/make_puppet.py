# -*- coding: utf-8 -*-
"""Rig girl_v4 as an Inochi2D puppet and write it as .inp (puppet) and .inx (Inochi Creator project).

    python src/inochi2d/make_puppet.py            -> output/inochi2D/girl_v4.inp / .inx / puppet.json

Format follows Inochi2D 0.8 (INP "TRNSRTS\0" container, big-endian lengths, JSON payload, TEX_SECT with PNG
blobs), cross-checked against the reference D implementation (inochi2d v0.8.7) and the Rust one (inox2d):
  * node:  uuid, name, type, enabled, zsort, transform{trans[3], rot[3], scale[2]}, lockToRoot, children
  * Part:  + mesh{verts, uvs, indices, origin}, textures[3], blend_mode, tint, screenTint, emissionStrength,
           mask_threshold, opacity
  * param: uuid, name, is_vec2, min, max, defaults, axis_points (normalised 0..1), merge_mode, bindings
  * binding: node, param_name, values[x][y], isSet[x][y], interpolate_mode
  * drawn back-to-front by DESCENDING zsort (higher zsort = further back); zsort adds up along the tree
  * transform.s.* bindings multiply (default 1), t/r bindings add (default 0); y points down; rotation in radians
"""
import io, json, math, os, random, struct, sys

os.environ.setdefault('GIRL_S', '1.2')      # 1200 x 2000 puppet: light enough for the web demo
os.environ.setdefault('GIRL_SS', '2')
os.environ.setdefault('GIRL_VERSION', '4')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'src', 'claude5.5_live2d'))
import build            # noqa: E402  (renders every Part of the model)
import girl             # noqa: E402
import girl_v4 as G4    # noqa: E402

OUT = os.path.join(ROOT, 'output', 'inochi2D')
NO_TEX = 4294967295
S = girl.S
W, H = girl.W, girl.H
ORIGIN = (W / 2.0, H / 2.0)

rnd = random.Random(20260923)
_used = set()


def new_uuid():
    while True:
        u = rnd.randrange(1, 2 ** 31)
        if u not in _used:
            _used.add(u)
            return u


def P(xr, yr):
    """reference-image px -> puppet space (canvas px, origin at the canvas centre, y down)."""
    x, y = G4.RP(xr, yr)
    return (x * S - ORIGIN[0], y * S - ORIGIN[1])


def tf(x=0.0, y=0.0, rz=0.0, sx=1.0, sy=1.0):
    return {'trans': [x, y, 0.0], 'rot': [0.0, 0.0, rz], 'scale': [sx, sy]}


def node(name, x=0.0, y=0.0, zsort=0.0, typ='Node'):
    return {'uuid': new_uuid(), 'name': name, 'type': typ, 'enabled': True, 'zsort': zsort,
            'transform': tf(x, y), 'lockToRoot': False, 'children': [], '_world': (x, y)}


def main():
    global N
    # =================================================================== render the layers
    print('rendering layers at', W, 'x', H, '...')
    groups = build.MODEL.build()
    rendered = build.render_all(groups)                   # [(group path, name, PIL image, x, y)] bottom -> top
    rendered = [r for r in rendered if r[1] != '背景色']   # the demo page draws its own background
    N = len(rendered)
    os.makedirs(OUT, exist_ok=True)
    build.composite(rendered).save(os.path.join(OUT, 'psd_composite.png'))   # reference for validate_inp.py

    textures = []                                         # PNG bytes, index = texture id
    parts = {}                                            # name -> dict(info)
    for i, (gpath, name, im, x, y) in enumerate(rendered):
        buf = io.BytesIO()
        im.save(buf, 'PNG', optimize=True)
        textures.append(buf.getvalue())
        parts[name] = dict(order=i, group=gpath, w=im.width, h=im.height,
                           x0=x - ORIGIN[0], y0=y - ORIGIN[1], tex=len(textures) - 1)

    HAIR_DEFORM = {'後髮_R', '後髮_L', '後髮內層_R', '後髮內層_L', '鬢角_R', '鬢角_L', '碎髮', '呆毛'}
    # arms bend as ONE continuous mesh field (no rigid per-segment rotation -> no "puppet" look)
    ARM_GRID = {'上臂': (4, 12), '下臂': (3, 10), '手掌': (3, 5), '手指': (4, 5)}


    def grid_mesh(w, h, cols, rows, px, py, x0, y0):
        """Grid mesh over the layer rect; verts are relative to the node position (px, py)."""
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


    def make_part(name, parent, pivot=None):
        info = parts[name]
        cx, cy = info['x0'] + info['w'] / 2, info['y0'] + info['h'] / 2
        px, py = pivot if pivot else (cx, cy)
        if name in HAIR_DEFORM:
            cols, rows = (3, max(4, min(12, info['h'] // 60)))
        elif name[:-2] in ARM_GRID:
            cols, rows = ARM_GRID[name[:-2]]
        else:
            cols, rows = 1, 1
        verts, uvs, idx = grid_mesh(info['w'], info['h'], cols, rows, px, py, info['x0'], info['y0'])
        wx, wy = parent['_world']
        n = node(name, px - wx, py - wy, zsort=(N - info['order']) * 0.01, typ='Part')   # front = lower zsort
        n['zsort'] = round(n['zsort'] - parent.get('_zabs', 0.0), 4)                  # zsort accumulates
        n['_world'] = (px, py)
        n['_zabs'] = parent.get('_zabs', 0.0) + n['zsort']
        n.update({'mesh': {'verts': verts, 'uvs': uvs, 'indices': idx, 'origin': [0.0, 0.0]},
                  'textures': [info['tex'], NO_TEX, NO_TEX], 'blend_mode': 'Normal',
                  'tint': [1.0, 1.0, 1.0], 'screenTint': [0.0, 0.0, 0.0], 'emissionStrength': 1.0,
                  'mask_threshold': 0.5, 'opacity': 1.0})
        n['_info'] = info
        parent['children'].append(n)
        return n


    def child_node(parent, name, x, y):
        wx, wy = parent['_world']
        n = node(name, x - wx, y - wy)
        n['_world'] = (x, y)
        n['_zabs'] = parent.get('_zabs', 0.0)
        parent['children'].append(n)
        return n


    # =================================================================== node tree
    root = node('Root')
    root['_world'] = (0.0, 0.0)
    by_name = {}

    body = child_node(root, 'Body', *P(G4.CX, G4.WAIST_Y))
    neck = P(G4.CX, 262)
    head = child_node(root, 'Head', *neck)                   # head pivot at the neck: Roll rotates around it
    eye_nodes, ball_nodes = {}, {}
    for side, cxr in (('R', G4.EYE_CX_R), ('L', G4.EYE_CX_L)):
        eye_nodes[side] = child_node(head, f'Eye {side}', *P(cxr, G4.EYE_Y))
        ball_nodes[side] = child_node(eye_nodes[side], f'EyeBall {side}', *P(cxr, G4.EYE_Y + 15))  # squash toward the lower lid
    mouth = child_node(head, 'Mouth', *P(G4.CX, G4.MOUTH_Y))

    for gpath, name, im, x, y in rendered:
        top = gpath[0]
        if top == '背景':
            by_name[name] = make_part(name, root)
        elif top == '身體':
            by_name[name] = make_part(name, body)
        elif top == '後髮':
            info = parts[name]
            by_name[name] = make_part(name, head, pivot=(info['x0'] + info['w'] / 2, info['y0']))     # hang from the top
        else:                                     # 頭 and its sub-groups
            sub = gpath[1] if len(gpath) > 1 else None
            info = parts[name]
            if sub in ('眼_R', '眼_L'):
                side = sub[-1]
                if name.startswith(('眼白', '眼球', '高光')):
                    by_name[name] = make_part(name, ball_nodes[side], pivot=ball_nodes[side]['_world'])
                else:
                    by_name[name] = make_part(name, eye_nodes[side])
            elif sub == '嘴':
                pv = (info['x0'] + info['w'] / 2, info['y0']) if name in ('口腔', '舌頭') else None
                by_name[name] = make_part(name, mouth, pivot=pv)
            elif name in HAIR_DEFORM:
                by_name[name] = make_part(name, head, pivot=(info['x0'] + info['w'] / 2, info['y0']))
            else:
                by_name[name] = make_part(name, head)

    # physics driver for the hair (Inochi2D SimplePhysics node, drives "Hair:: Sway")
    phys = child_node(head, 'Hair Physics', *P(G4.CX, 120))
    phys['type'] = 'SimplePhysics'


    # =================================================================== parameters
    def val_binding(n, key, values):
        """values: list over x axis points (each a list over y axis points)."""
        return {'node': n['uuid'], 'param_name': key, 'values': values,
                'isSet': [[True] * len(v) for v in values], 'interpolate_mode': 'Linear'}


    def deform_binding(n, offsets_by_x):
        """offsets_by_x: list over x axis points of [[dx, dy], ...] per vertex (y axis has 1 point)."""
        return {'node': n['uuid'], 'param_name': 'deform', 'values': [[o] for o in offsets_by_x],
                'isSet': [[True] for _ in offsets_by_x], 'interpolate_mode': 'Linear'}


    def param(name, is_vec2, mn, mx, dflt, ax, ay, bindings):
        return {'uuid': new_uuid(), 'name': name, 'is_vec2': is_vec2, 'min': mn, 'max': mx, 'defaults': dflt,
                'axis_points': [ax, ay], 'merge_mode': 'Passthrough', 'bindings': bindings}


    params = []
    U = S * G4.K                     # reference px -> puppet px

    # --- Head:: Yaw-Pitch (vec2): parallax, front layers move more than back ones
    DEPTH = {'瀏海': 1.25, '碎髮': 1.2, '呆毛': 1.1, '髮飾': 1.25, '眉毛': 1.0, '眼': 1.0, '鼻子': 1.1, '嘴': 1.0,
             '腮紅': 0.95, '髮陰影': 0.9, '臉線': 0.35, '臉陰影': 0.35, '臉': 0.3, '耳朵': -0.35, '鬢角': 0.55,
             '後髮': -0.7}


    def depth_of(name, gpath):
        if len(gpath) > 1 and gpath[1].startswith('眼'):
            return DEPTH['眼']
        if len(gpath) > 1 and gpath[1] == '嘴':
            return DEPTH['嘴']
        for k, v in sorted(DEPTH.items(), key=lambda kv: -len(kv[0])):
            if name.startswith(k):
                return v
        return 0.0


    yaw_b = []
    AMP_X, AMP_Y = 5.5 * U, 3.5 * U
    for gpath, name, im, x, y in rendered:
        if gpath[0] not in ('頭', '後髮'):
            continue
        d = depth_of(name, gpath)
        n = by_name[name]
        # sub-grouped parts sit under Eye/Mouth nodes: bind the part itself (offsets are local, still additive)
        yaw_b.append(val_binding(n, 'transform.t.x', [[-AMP_X * d] * 3, [0.0] * 3, [AMP_X * d] * 3]))
        yaw_b.append(val_binding(n, 'transform.t.y', [[-AMP_Y * d, 0.0, AMP_Y * d]] * 3))
    # 近大遠小: the eye on the far side narrows, the near one widens a little
    for side, sgn in (('R', 1.0), ('L', -1.0)):
        near, far = 1.04, 0.86
        row = lambda v: [v, v, v]
        vals = [row(near if sgn > 0 else far), row(1.0), row(far if sgn > 0 else near)]
        yaw_b.append(val_binding(eye_nodes[side], 'transform.s.x', vals))
    params.append(param('Head:: Yaw-Pitch', True, [-1.0, -1.0], [1.0, 1.0], [0.0, 0.0], [0.0, 0.5, 1.0], [0.0, 0.5, 1.0], yaw_b))

    # --- Head:: Roll
    params.append(param('Head:: Roll', False, [-1.0, -1.0], [1.0, 1.0], [0.0, 0.0], [0.0, 0.5, 1.0], [0.0],
                        [val_binding(head, 'transform.r.z', [[-0.12], [0.0], [0.12]])]))

    # --- Eye blink (0 = open, 1 = closed): eyeball squashes onto the lower lid, upper line slides down
    for side, pname in (('L', 'Eye:: Left:: Blink'), ('R', 'Eye:: Right:: Blink')):
        bl = [val_binding(ball_nodes[side], 'transform.s.y', [[1.0], [0.06]])]
        drop = 24 * U
        # only the line + lashes travel; the flat skin lid patch stays put (moving it exposes its edge
        # against the hair shadow on the face), the squashed eyeball reveals the face underneath
        for nm in ('上眼線', '上睫毛'):
            bl.append(val_binding(by_name[f'{nm}_{side}'], 'transform.t.y', [[0.0], [drop]]))
        bl.append(val_binding(by_name[f'上眼線_{side}'], 'transform.s.y', [[1.0], [0.75]]))
        params.append(param(pname, False, [0.0, 0.0], [1.0, 1.0], [0.0, 0.0], [0.0, 1.0], [0.0], bl))

    # --- Mouth:: Open: the cavity (a sliver inside the lip line) scales down from its top edge
    mo = [val_binding(by_name['口腔'], 'transform.s.y', [[1.0], [6.0]]),
          val_binding(by_name['口腔'], 'transform.s.x', [[1.0], [1.15]]),
          val_binding(by_name['舌頭'], 'transform.s.y', [[1.0], [4.0]]),
          val_binding(by_name['舌頭'], 'transform.t.y', [[0.0], [3.0 * U]]),
          val_binding(by_name['下排牙齒'], 'transform.t.y', [[0.0], [5.5 * U]]),
          val_binding(by_name['下唇陰影'], 'transform.t.y', [[0.0], [4.5 * U]])]
    params.append(param('Mouth:: Open', False, [0.0, 0.0], [1.0, 1.0], [0.0, 0.0], [0.0, 1.0], [0.0], mo))

    # --- Body:: Breath: chest rises, shoulders/head lift a little
    br = [val_binding(head, 'transform.t.y', [[0.0], [-1.6 * U]])]
    for nm in ('胸腔', '胸_R', '胸_L'):
        br.append(val_binding(by_name[nm], 'transform.s.y', [[1.0], [1.012]]))
    for nm in ('領子_R', '領子_L', '領巾_R', '領巾_L', '領巾結', '領巾尾_R', '領巾尾_L', '上臂_R', '上臂_L'):
        br.append(val_binding(by_name[nm], 'transform.t.y', [[0.0], [-1.2 * U]]))
    params.append(param('Body:: Breath', False, [0.0, 0.0], [1.0, 1.0], [0.0, 0.0], [0.0, 1.0], [0.0], br))

    # --- Arms: swing (shoulder), bend (elbow), wrist -- smooth rotation fields sampled per vertex
    def smooth01(t):
        t = min(1.0, max(0.0, t))
        return t * t * (3 - 2 * t)

    def arm_pt(side, x, y):             # reference px of the RIGHT arm -> puppet px for either side
        wx, wy = G4.shoulder_warp(x, y)
        if side == 'L':
            wx = 2 * G4.CX - wx
        return P(wx, wy)

    def rot_field_offsets(n, centre, ang, y0, y1):
        # offsets for every vertex: rotate about centre by ang * smoothstep(y0..y1) (world y)
        wx, wy = n['_world']
        vs = n['mesh']['verts']
        out = []
        for k in range(0, len(vs), 2):
            px, py = vs[k] + wx, vs[k + 1] + wy
            a = ang * smooth01((py - y0) / (y1 - y0))
            dx, dy = px - centre[0], py - centre[1]
            c, s_ = math.cos(a), math.sin(a)
            out.append([dx * c - dy * s_ - dx, dx * s_ + dy * c - dy])
        return out

    ARM_PARTS = ('上臂', '下臂', '手掌', '手指')
    for side, sname, sgn in (('R', 'Right', 1.0), ('L', 'Left', -1.0)):
        S_ = arm_pt(side, 205, 318)      # shoulder joint (under the sleeve cap)
        E_ = arm_pt(side, 193, 472)      # elbow
        W_ = arm_pt(side, 176, 556)      # wrist
        specs = [  # name, pivot, max angle (rad, + = hand swings outward for R), ramp start/end (world y), keys
            (f'Arm:: {sname}:: Swing', S_, 0.11 * sgn, S_[1] + 10 * U, E_[1], (-1.0, 0.0, 1.0)),
            (f'Arm:: {sname}:: Bend', E_, -0.32 * sgn, E_[1] - 10 * U, E_[1] + 22 * U, (0.0, 1.0)),
            (f'Hand:: {sname}:: Wrist', W_, 0.30 * sgn, W_[1] - 5 * U, W_[1] + 12 * U, (-1.0, 0.0, 1.0)),
        ]
        for pname, C_, amax, y0, y1, keys in specs:
            binds = []
            for pn in ARM_PARTS:
                n = by_name[f'{pn}_{side}']
                offs = [rot_field_offsets(n, C_, amax * k, y0, y1) for k in keys]
                binds.append(deform_binding(n, offs))
            if len(keys) == 3:
                params.append(param(pname, False, [-1.0, -1.0], [1.0, 1.0], [0.0, 0.0], [0.0, 0.5, 1.0], [0.0], binds))
            else:
                params.append(param(pname, False, [0.0, 0.0], [1.0, 1.0], [0.0, 0.0], [0.0, 1.0], [0.0], binds))

    # --- Hair:: Sway (driven by physics): hair bends more toward the tips
    hs = []
    for nm in sorted(HAIR_DEFORM):
        n = by_name[nm]
        vs = n['mesh']['verts']
        ys = vs[1::2]
        top, bot = min(ys), max(ys)
        amp = (0.05 if nm.startswith('後髮') else 0.07) * (bot - top) + 4
        offs = []
        for s_ in (-1.0, 0.0, 1.0):
            o = []
            for k in range(0, len(vs), 2):
                t = (vs[k + 1] - top) / max(1e-6, bot - top)
                o.append([s_ * amp * t ** 1.6, 0.0])
            offs.append(o)
        hs.append(deform_binding(n, offs))
    hair_param = param('Hair:: Sway', False, [-1.0, -1.0], [1.0, 1.0], [0.0, 0.0], [0.0, 0.5, 1.0], [0.0], hs)
    params.append(hair_param)

    phys.update({'param': hair_param['uuid'], 'model_type': 'Pendulum', 'map_mode': 'AngleLength',
                 'gravity': 1.0, 'length': 100.0, 'frequency': 1.0, 'angle_damping': 0.5, 'length_damping': 0.5,
                 'output_scale': [1.0, 1.0], 'local_only': False})


    # =================================================================== write
    def strip(n):
        n = {k: v for k, v in n.items() if not k.startswith('_')}
        n['children'] = [strip(c) for c in n['children']]
        if not n['children']:
            del n['children']
        return n


    puppet = {
        'meta': {'name': 'girl_v4', 'version': '1.0-alpha', 'rigger': 'Claude (make_puppet.py)',
                 'artist': 'Claude (girl_v4.py, drawn in Python)', 'copyright': None, 'licenseURL': None,
                 'contact': None, 'reference': None, 'thumbnailId': NO_TEX, 'preservePixels': False},
        'physics': {'pixelsPerMeter': 1000.0, 'gravity': 9.8},
        'nodes': strip(root),
        'param': params,
        'automation': [],
        'animations': {},
    }


    def write_inp(path, payload, texs):
        js = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        with open(path, 'wb') as f:
            f.write(b'TRNSRTS\0')
            f.write(struct.pack('>I', len(js)))
            f.write(js)
            f.write(b'TEX_SECT')
            f.write(struct.pack('>I', len(texs)))
            for t in texs:
                f.write(struct.pack('>I', len(t)))
                f.write(bytes([0]))                 # 0 = PNG
                f.write(t)


    os.makedirs(OUT, exist_ok=True)
    write_inp(os.path.join(OUT, 'girl_v4.inp'), puppet, textures)
    write_inp(os.path.join(OUT, 'girl_v4.inx'), puppet, textures)      # Creator project: same container, no EXT data
    with open(os.path.join(OUT, 'puppet.json'), 'w', encoding='utf-8') as f:
        json.dump(puppet, f, ensure_ascii=False, indent=1)
    print('parts', len(parts), 'textures', len(textures), 'params', [p['name'] for p in params])
    print('size', os.path.getsize(os.path.join(OUT, 'girl_v4.inp')) // 1024, 'KiB')


if __name__ == '__main__':
    main()
