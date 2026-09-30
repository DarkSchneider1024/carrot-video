# -*- coding: utf-8 -*-
"""Validate an Inochi2D .inp/.inx and recomposite it at default parameters.

    python src/inochi2d/validate_inp.py output/inochi2D/girl_v4.inp [--compare merged.png] [--out recomposite.png]

1. container: "TRNSRTS\\0", big-endian JSON length, JSON, "TEX_SECT", count, (len, enc, bytes)*, optional EXT_SECT
2. JSON: every key the Rust loader (inox2d formats/payload.rs) reads with a hard `?`, plus the D keys
3. references: unique uuids, bindings point at existing nodes / params, texture ids in range,
   binding value matrices match the axis points, deform offsets match the vertex count, indices in range
4. recomposite: evaluate the node tree at the default parameter values (translation/rotation/scale chain,
   zsort accumulated along the tree, drawn by descending zsort) and composite every Part; compare with
   the PSD's own composite (same layers, same scale).
"""
import argparse, io, json, math, struct, sys
import numpy as np
from PIL import Image

NO_TEX = 4294967295
ERR = []


def need(obj, keys, where):
    for k in keys:
        if k not in obj:
            ERR.append(f'{where}: missing "{k}"')


def read_inp(path):
    b = open(path, 'rb').read()
    assert b[:8] == b'TRNSRTS\0', 'bad magic'
    (n,) = struct.unpack('>I', b[8:12])
    js = json.loads(b[12:12 + n].decode('utf-8'))
    o = 12 + n
    assert b[o:o + 8] == b'TEX_SECT', 'no TEX_SECT'
    (cnt,) = struct.unpack('>I', b[o + 8:o + 12])
    o += 12
    texs = []
    for _ in range(cnt):
        (ln,) = struct.unpack('>I', b[o:o + 4]); enc = b[o + 4]; o += 5
        data = b[o:o + ln]; o += ln
        texs.append((enc, data))
    ext = b[o:o + 8] == b'EXT_SECT'
    return js, texs, len(b) - o, ext


def walk(n, fn, parent=None):
    fn(n, parent)
    for c in n.get('children', []):
        walk(c, fn, n)


def mat(t, r, s):
    c, si = math.cos(r), math.sin(r)
    return np.array([[c * s[0], -si * s[1], t[0]], [si * s[0], c * s[1], t[1]], [0, 0, 1]])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('inp')
    ap.add_argument('--compare')
    ap.add_argument('--out')
    a = ap.parse_args()
    js, texs, trailing, ext = read_inp(a.inp)
    print(f'container OK: {len(texs)} textures, EXT_SECT={ext}, trailing bytes after TEX_SECT={trailing}')

    need(js, ['meta', 'physics', 'nodes', 'param'], 'puppet')
    need(js['meta'], ['name', 'version', 'rigger', 'artist', 'copyright', 'licenseURL', 'contact', 'reference',
                      'preservePixels'], 'meta')
    need(js['physics'], ['pixelsPerMeter', 'gravity'], 'physics')

    nodes, uuids = {}, []

    def chk(n, parent):
        w = f"node {n.get('name')}"
        need(n, ['uuid', 'name', 'type', 'enabled', 'zsort', 'transform', 'lockToRoot'], w)
        need(n['transform'], ['trans', 'rot', 'scale'], w + '.transform')
        if len(n['transform']['trans']) != 3 or len(n['transform']['rot']) != 3 or len(n['transform']['scale']) != 2:
            ERR.append(w + ': transform vector sizes')
        uuids.append(n['uuid']); nodes[n['uuid']] = n
        if n['type'] == 'Part':
            need(n, ['mesh', 'textures', 'blend_mode'], w)
            m = n['mesh']
            need(m, ['verts', 'uvs', 'indices'], w + '.mesh')
            nv = len(m['verts']) // 2
            if len(m['verts']) % 2 or len(m['uvs']) != len(m['verts']):
                ERR.append(w + ': verts/uvs size')
            if max(m['indices']) >= nv or len(m['indices']) % 3:
                ERR.append(w + ': indices')
            if not (0 <= n['textures'][0] < len(texs)):
                ERR.append(w + ': albedo texture id')
        elif n['type'] == 'SimplePhysics':
            need(n, ['param', 'model_type', 'map_mode', 'gravity', 'length', 'frequency', 'angle_damping',
                     'length_damping', 'output_scale'], w)
    walk(js['nodes'], chk)
    if len(set(uuids)) != len(uuids):
        ERR.append('duplicate node uuids')

    puuids = set()
    for p in js['param']:
        w = f"param {p.get('name')}"
        need(p, ['uuid', 'name', 'is_vec2', 'min', 'max', 'defaults', 'axis_points', 'bindings'], w)
        puuids.add(p['uuid'])
        ax, ay = p['axis_points']
        if not all(0 <= v <= 1 for v in ax + ay):
            ERR.append(w + ': axis points must be normalised 0..1')
        for b in p['bindings']:
            need(b, ['node', 'param_name', 'values', 'isSet', 'interpolate_mode'], w + '.binding')
            if b['node'] not in nodes:
                ERR.append(w + ': binding to unknown node'); continue
            if len(b['values']) != len(ax) or any(len(v) != len(ay) for v in b['values']):
                ERR.append(f"{w}: {b['param_name']} values shape != axis points")
            if b['param_name'] == 'deform':
                nv = len(nodes[b['node']]['mesh']['verts']) // 2
                for row in b['values']:
                    for cell in row:
                        if len(cell) != nv:
                            ERR.append(f"{w}: deform offsets {len(cell)} != verts {nv}")
    for n in nodes.values():
        if n['type'] == 'SimplePhysics' and n['param'] not in puuids:
            ERR.append(f"physics {n['name']}: unknown param")
    for i, (enc, data) in enumerate(texs):
        if enc != 0:
            ERR.append(f'texture {i}: encoding {enc} (expected 0=PNG)')
        Image.open(io.BytesIO(data)).verify()
    parts_n = sum(1 for n in nodes.values() if n['type'] == 'Part')
    print(f'{len(nodes)} nodes ({parts_n} parts), {len(js["param"])} params, '
          f'{sum(len(p["bindings"]) for p in js["param"])} bindings')

    # ---------------------------------------------------------------- recomposite at defaults
    if a.compare or a.out:
        items = []

        def rec(n, M, z):
            t = n['transform']
            L = mat(t['trans'], t['rot'][2], t['scale'])
            W_ = M @ L
            zz = z + n['zsort']
            if n['type'] == 'Part':
                items.append((zz, n, W_))
            for c in n.get('children', []):
                rec(c, W_, zz)
        rec(js['nodes'], np.eye(3), 0.0)
        items.sort(key=lambda it: -it[0])                   # descending zsort = back to front
        ref = Image.open(a.compare).convert('RGBA') if a.compare else None
        Wc, Hc = ref.size if ref else (1200, 2000)
        canvas = Image.new('RGBA', (Wc, Hc), (0, 0, 0, 0))
        for z, n, Mw in items:
            v = np.array(n['mesh']['verts']).reshape(-1, 2)
            p = (Mw @ np.c_[v, np.ones(len(v))].T).T[:, :2] + (Wc / 2, Hc / 2)
            x0, y0 = p.min(0)
            im = Image.open(io.BytesIO(texs[n['textures'][0]][1])).convert('RGBA')
            canvas.alpha_composite(im, (int(round(x0)), int(round(y0))))
        if a.out:
            canvas.save(a.out)
        if ref is not None:
            A = np.asarray(canvas).astype(int); B = np.asarray(ref).astype(int)
            d = np.abs(A - B)
            print(f'recomposite vs PSD composite: max diff {d.max()}/255, mean {d.mean():.4f}')
            if d.max() > 3:
                ERR.append('recomposite differs from the PSD composite')

    for e in ERR[:40]:
        print('FAIL', e)
    print('RESULT', 'FAIL' if ERR else 'PASS')
    sys.exit(1 if ERR else 0)


if __name__ == '__main__':
    main()
