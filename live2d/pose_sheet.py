# -*- coding: utf-8 -*-
"""3 x 3 nine-axis keyform sheet (Head:: Yaw-Pitch) for a puppet -- the check from the 九軸 tutorial.

    python live2d/pose_sheet.py 小紅帽/characters/red_hood/red_hood.inp out.png [--cy -560 --scale 0.9]
Rows: looking up / level / down; columns: left / front / right.
"""
import argparse, base64, io, os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_video import serve, ROOT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('model'); ap.add_argument('out')
    ap.add_argument('--cy', type=float, default=-560); ap.add_argument('--scale', type=float, default=0.9)
    ap.add_argument('--params', default='', help='comma list: one row per param at -1 / 0 / +1 instead of the 3x3 head sheet')
    a = ap.parse_args()
    from playwright.sync_api import sync_playwright
    httpd = serve(ROOT)
    rel = os.path.relpath(os.path.abspath(a.model), ROOT).replace(os.sep, "/")
    tiles = []
    with sync_playwright() as p:
        b = p.chromium.launch(channel=os.environ.get('RENDER_BROWSER', 'msedge'))
        pg = b.new_page(viewport={'width': 600, 'height': 600})
        pg.goto(f'http://127.0.0.1:{httpd.server_address[1]}/live2d/player/pose.html?model=/{rel}')
        pg.wait_for_function('window.ready === true', timeout=60000)
        if a.params:
            poses = [{pn: v} for pn in a.params.split(',') for v in (-1, 0, 1)]
        else:
            poses = [{'Head:: Yaw-Pitch': [kx, ky]} for ky in (1, 0, -1) for kx in (-1, 0, 1)]
        import json as _j
        for ps in poses:
            js = f"window.shot({_j.dumps(ps, ensure_ascii=False)}, {{cx: 0, cy: {a.cy}, scale: {a.scale}}})"
            tiles.append(Image.open(io.BytesIO(base64.b64decode(pg.evaluate(js).split(',', 1)[1]))))
        b.close()
    httpd.shutdown()
    rows = (len(tiles) + 2) // 3
    sheet = Image.new('RGB', (1800, 600 * rows), (230, 232, 240))
    d = ImageDraw.Draw(sheet)
    for i, t in enumerate(tiles):
        bg = Image.new('RGBA', t.size, (230, 232, 240, 255)); bg.alpha_composite(t.convert('RGBA'))
        sheet.paste(bg.convert('RGB'), ((i % 3) * 600, (i // 3) * 600))
    for k in (1, 2):
        d.line([(k * 600, 0), (k * 600, 600 * rows)], fill=(160, 160, 175), width=2)
    for k in range(1, rows):
        d.line([(0, k * 600), (1800, k * 600)], fill=(160, 160, 175), width=2)
    sheet.save(a.out)
    print('wrote', a.out)


if __name__ == '__main__':
    main()
