"""Isolated Hollow (outlined display) study built from the Grid-Token Grid baseline.

Draw overwrites only this study's UFO. Build compiles without redrawing.
Proof embeds Grid (solid) and Hollow (outlined) in Chromium.
"""
import base64
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import pyclipper
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.recordingPen import RecordingPen
from ufoLib2 import Font
from grid_token_study import STUDY
from font_license import apply_ufo_license, write_licensed_html
from web import appearance_head, primary_nav

OUT = STUDY / 'hollow'
SOURCE = OUT / 'ConfiniumMono-GridToken-Hollow.ufo'
FONT = OUT / 'ConfiniumMono-GridToken-Hollow.ttf'
WALL = 28
SCALE = 100


def _flatten_contour(contour, steps=20):
    """Flatten a UFO contour into integer-scaled (x, y) points for pyclipper."""
    rec = RecordingPen()
    contour.draw(rec)
    pts = []
    cur = None
    for op, args in rec.value:
        if op == 'moveTo':
            cur = args[0]
            pts.append((round(cur[0] * SCALE), round(cur[1] * SCALE)))
        elif op == 'lineTo':
            cur = args[0]
            pts.append((round(cur[0] * SCALE), round(cur[1] * SCALE)))
        elif op == 'curveTo':
            c1, c2, p3 = args
            for s in range(1, steps + 1):
                t = s / steps
                u = 1 - t
                x = u**3 * cur[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t**3 * p3[0]
                y = u**3 * cur[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t**3 * p3[1]
                pts.append((round(x * SCALE), round(y * SCALE)))
            cur = p3
    return pts


def _signed_area(pts):
    return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1]))


def draw():
    OUT.mkdir(exist_ok=True)
    font = Font.open(STUDY / 'sources/ConfiniumMono-GridToken-Grid.ufo')
    font.info.styleName = 'Grid-Token Hollow Bold'
    font.info.openTypeNameDescription = (
        f'Confinium Mono isolated Hollow display study: {WALL}-unit wall inset from Grid.'
    )
    for glyph in font:
        if not glyph.contours:
            continue
        # Keep original outer + counter contours; add inset hollow channels as CW holes.
        pco = pyclipper.PyclipperOffset(miter_limit=2.5)
        for contour in glyph.contours:
            pts = _flatten_contour(contour)
            if len(pts) >= 3:
                # Pyclipper expects CCW for outer, CW for holes (same as UFO).
                pco.AddPath(pts, pyclipper.JT_MITER, pyclipper.ET_CLOSEDPOLYGON)
        inset_paths = pco.Execute(-WALL * SCALE)
        for path in inset_paths:
            if len(path) < 3:
                continue
            # Invert Execute(-WALL) orientation so the inset solid is subtracted from the glyph.
            path = list(reversed(path))
            pen = glyph.getPen()
            pen.moveTo((path[0][0] / SCALE, path[0][1] / SCALE))
            for x, y in path[1:]:
                pen.lineTo((x / SCALE, y / SCALE))
            pen.closePath()
        # Verify outer contours remain positive area.
        ap = AreaPen()
        glyph.draw(ap)
        assert ap.value > 0, (glyph.name, ap.value)
    apply_ufo_license(font.info)
    font.save(SOURCE, overwrite=True)
    print(f'Drew isolated Hollow UFO ({WALL}-unit wall); Grid baseline untouched.')


def build():
    os.environ.setdefault('SOURCE_DATE_EPOCH', '1795132800')
    subprocess.run(
        [sys.executable, '-m', 'fontmake', '-u', str(SOURCE), '-o', 'ttf', '--output-path', str(FONT)],
        check=True,
    )


def proof():
    nav = primary_nav('../../../', 'hollow')
    variants = [
        ('solid', 'Grid Bold (Solid baseline)', STUDY / 'fonts/ConfiniumMono-GridToken-Grid.ttf'),
        ('hollow', f'Hollow Display ({WALL}-unit wall)', FONT),
    ]
    css = ''
    rows = ''
    for key, label, path in variants:
        data = base64.b64encode(path.read_bytes()).decode()
        css += f'@font-face{{font-family:{key};src:url(data:font/ttf;base64,{data});font-weight:700}}'
        rows += (
            f'<section><h2>{label}</h2>'
            f'<div class="hero" style="font-family:{key}">CONFINIUM 01</div>'
            f'<div class="sample" style="font-family:{key}">ABCDEFGHIJKLM\nNOPQRSTUVWXYZ\n0123456789</div>'
            f'<div class="sizes" style="font-family:{key}">'
            + ''.join(f'<div style="font-size:{px}px">SECTOR 09 // PROTOCOL A–Z 0–9</div>' for px in [24, 36, 56])
            + '</div></section>'
        )
    page = OUT / 'index.html'
    write_licensed_html(page,
        '<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Confinium Mono / Hollow Display Study</title>'
        f"{appearance_head('../../../')}<style>{css}"
        'body{margin:32px;background:var(--paper);color:var(--text);font:16px/1.5 system-ui}'
        'h1{font-size:30px;margin:0 0 8px}h2{font-size:16px;font-weight:600;color:var(--muted)}'
        'section{border-top:1px solid var(--border);padding:14px 0 24px}'
        '.hero{font-size:clamp(48px,8vw,112px);font-weight:700;font-synthesis:none;letter-spacing:0;font-kerning:none;white-space:pre;line-height:1.25;margin:10px 0}'
        '.sample{font-size:64px;font-weight:700;font-synthesis:none;letter-spacing:0;font-kerning:none;white-space:pre;line-height:1.35;margin:12px 0;overflow:auto}'
        '.sizes{font-weight:700;font-synthesis:none;letter-spacing:0;font-kerning:none;line-height:1.4}.sizes div{margin:6px 0}'
        '#status{color:var(--accent)}</style>'
        f'{nav}<h1>Confinium Mono / Hollow Display</h1>'
        f'<p>Isolated wireframe display study ({WALL}-unit wall inset from the 160-unit Grid baseline). Intended for sci-fi HUDs, headers, and display titling (24 px+).</p>'
        '<p id="status">Loading…</p>'
        f'{rows}'
        '<script>Promise.all(["solid","hollow"].map(f=>document.fonts.load("700 64px "+f,"HO0Q"))).'
        'then(r=>document.querySelector("#status").textContent=r.every(x=>x.length)?"Both fonts loaded":"FONT FAILURE")</script></html>'
    )
    with tempfile.TemporaryDirectory(prefix='confinium-hollow-') as profile:
        run = subprocess.run(
            [
                'chromium', '--headless', '--disable-gpu', '--no-first-run',
                f'--user-data-dir={profile}', '--virtual-time-budget=3000',
                '--window-size=1500,2200', f'--screenshot={OUT / "chromium.png"}',
                '--dump-dom', page.as_uri(),
            ],
            check=True, capture_output=True, text=True,
        )
        assert '<p id="status">Both fonts loaded</p>' in run.stdout
    print('Rendered Solid vs Hollow in Chromium; both font loads verified.')


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in ('draw', 'build', 'proof'):
        raise SystemExit('Usage: hollow_study.py draw|build|proof')
    globals()[sys.argv[1]]()
