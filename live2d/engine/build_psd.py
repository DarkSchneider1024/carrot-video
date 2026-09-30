# -*- coding: utf-8 -*-
"""Render every part of a character module and write the Live2D PSD + previews.

    python live2d/engine/build_psd.py red_hood             # full 2400x4000 -> 小紅帽/characters/red_hood/
    GIRL_S=0.6 GIRL_SS=2 python live2d/engine/build_psd.py red_hood --quick
Character modules live in live2d/characters/ and expose build() -> [(group, [Part|(sub, [...])])].
"""
import os, sys, json
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'characters'))
import girl
import importlib

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
_args = [a for a in sys.argv[1:] if not a.startswith('--')]
PREFIX = os.environ.get('CHARACTER') or (_args[0] if _args else 'red_hood')
MODEL = importlib.import_module(PREFIX)
OUT = os.path.join(ROOT, os.environ.get('LIVE2D_OUT', os.path.join('小紅帽', 'characters')), PREFIX)


def flatten(groups):
    """-> list of (path tuple, Part) bottom->top."""
    out = []
    def walk(items, path):
        for it in items:
            if isinstance(it, tuple):
                walk(it[1], path + (it[0],))
            else:
                out.append((path, it))
    for g, items in groups:
        walk(items, (g,))
    return out


def _render(part):
    im, x, y = part.render()
    return part.name, im, x, y


def render_all(groups):
    flat = flatten(groups)
    names = [p.name for _, p in flat]
    dup = {n for n in names if names.count(n) > 1}
    assert not dup, f'duplicate layer names: {dup}'
    res = [_render(p) for _, p in flat]
    return [(path, name, im, x, y) for (path, _), (name, im, x, y) in zip(flat, res)]


def composite(rendered, bg=None):
    canvas = Image.new('RGBA', (girl.W, girl.H), bg or (0, 0, 0, 0))
    for _, _, im, x, y in rendered:
        canvas.alpha_composite(im, (x, y))
    return canvas


def write_psd(rendered, path, merged):
    from psd_tools import PSDImage
    from psd_tools.api.layers import PixelLayer, Group
    from psd_tools.constants import Tag
    # RGBA mode: layer alpha goes into each layer's transparency channel (RGB mode
    # would make psd-tools store it as a layer mask, which Live2D hand-off forbids)
    psd = PSDImage.new('RGBA', (girl.W, girl.H), color=(0, 0, 0, 0))
    counter = [0]

    def setname(layer, name):
        counter[0] += 1
        layer._record.name = f'L{counter[0]:03d}'          # legacy Pascal name (MacRoman)
        layer.tagged_blocks.set_data(Tag.UNICODE_LAYER_NAME, name)

    groups = {(): psd}
    for gpath, name, im, x, y in rendered:
        for i in range(1, len(gpath) + 1):
            key = gpath[:i]
            if key not in groups:
                g = Group.new(groups[key[:-1]], name='g')
                setname(g, key[-1])
                groups[key] = g
        lay = PixelLayer.frompil(im, groups[gpath], name='x', top=y, left=x)
        assert not lay.has_mask(), name
        setname(lay, name)
    # merged image (what thumbnails / quick viewers show)
    from psd_tools.constants import Compression
    rec = psd._record
    rec.image_data.compression = Compression.RLE
    flat = Image.new('RGBA', merged.size, (255, 255, 255, 255))   # thumbnail on white;
    flat.alpha_composite(merged)                                    # layers keep real alpha
    rec.image_data.set_data([flat.getchannel(c).tobytes() for c in 'RGBA'], rec.header)
    psd._updated = False     # keep our merged image; save() would re-composite it over the fill colour
    psd.save(path)
    return psd


def contact_sheet(rendered, path, cols=10, cell=220):
    font = None
    for f in ('C:/Windows/Fonts/msjh.ttc', 'C:/Windows/Fonts/msyh.ttc'):
        if os.path.exists(f):
            font = ImageFont.truetype(f, 18); break
    n = len(rendered); rows = (n + cols - 1) // cols
    sheet = Image.new('RGB', (cols * cell, rows * (cell + 26)), (236, 236, 240))
    d = ImageDraw.Draw(sheet)
    for i, (gpath, name, im, x, y) in enumerate(rendered):
        cx, cy = (i % cols) * cell, (i // cols) * (cell + 26)
        # checker
        for yy in range(0, cell, 16):
            for xx in range(0, cell, 16):
                if (xx // 16 + yy // 16) % 2:
                    d.rectangle([cx + xx, cy + yy, cx + xx + 15, cy + yy + 15], fill=(222, 222, 228))
        t = im.copy(); t.thumbnail((cell - 12, cell - 12), Image.LANCZOS)
        sheet.paste(t, (cx + (cell - t.width) // 2, cy + (cell - t.height) // 2), t)
        d.text((cx + 6, cy + cell + 2), f'{i + 1:02d} {name}', fill=(30, 30, 40), font=font)
    sheet.save(path)


def main():
    quick = '--quick' in sys.argv
    os.makedirs(OUT, exist_ok=True)
    groups = MODEL.build()
    rendered = render_all(groups)
    prev = composite(rendered, (214, 214, 222, 255))
    if quick:
        prev.save(os.path.join(OUT, '_quick.png'))
        print('quick preview', prev.size, len(rendered), 'layers')
        return
    merged = composite(rendered)
    merged.save(os.path.join(OUT, PREFIX + '_merged.png'))
    prev.save(os.path.join(OUT, PREFIX + '_preview.png'))
    contact_sheet(rendered, os.path.join(OUT, PREFIX + '_parts.png'))
    write_psd(rendered, os.path.join(OUT, PREFIX + '.psd'), merged)
    manifest = [{'group': '/'.join(g), 'name': n, 'x': int(x), 'y': int(y), 'w': im.width, 'h': im.height}
                for g, n, im, x, y in rendered]
    with open(os.path.join(OUT, PREFIX + '_layers.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print('done', len(rendered), 'layers')


if __name__ == '__main__':
    main()
