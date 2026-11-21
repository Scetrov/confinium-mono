"""Isolated Grid Bold A/V comparison: draw, build, and proof are separate."""
import argparse
from base64 import b64encode
from math import hypot
import os
import subprocess
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont
from ufoLib2 import Font

from study_reference import GRID_TTF, GRID_UFO
from font_license import apply_ufo_license, write_licensed_html
from chromium_proof import capture_chromium
from grid_token_study import STUDY, ccw_poly, reverse
from web import appearance_head, primary_nav

OUT = STUDY / 'av-knees'
NAME = 'ConfiniumMono-GridToken-AVKnees'
BASE = GRID_TTF
TRIAL = OUT / f'{NAME}.ttf'
FULLER = OUT / f'{NAME}152.ttf'
STRAIGHT = OUT / f'{NAME}152Straight.ttf'
STRAIGHT_BOTH = OUT / f'{NAME}152StraightBoth.ttf'
STRAIGHT_AVW = OUT / f'{NAME}152StraightAVW.ttf'
STRAIGHT_FACES = {'v': STRAIGHT, 'both': STRAIGHT_BOTH, 'avw': STRAIGHT_AVW}
VARIANTS = {144: TRIAL, 152: FULLER}
TEXT = 'AV VA AVALON WAVE'
LOWER_BASE = STUDY / 'lowercase-alphabet/fonts/ConfiniumMono-GridToken-LowercaseAlphabet.ttf'
LOWER_TRIAL = OUT / 'ConfiniumMono-GridToken-LowercaseVWKnees.ttf'
LOWER_WIDE = OUT / 'ConfiniumMono-GridToken-LowercaseVWKnees144W.ttf'
LOWER_SAMPLES = ('Vv Ww   vv w', 'wave weave', 'review view')


def outlines(thickness, straight=None):
    # Shift 3u in 5u from the midline to a 2u-wide flat apex.
    # Offset the shoulder in parallel until it meets the 160-unit stem.
    slope = 240 / 400
    offset = thickness * hypot(1, slope)
    inner_knee = 400 + (offset - 160) / slope
    tip = 400 + (320 - offset) / slope
    roof = [(80, 0), (80, 400), (320, 800), (480, 800), (720, 400), (720, 0)]
    bar_top, bar_bottom = (360, 220) if straight in ('both', 'avw') else (400, 260)
    if thickness == 144:
        # Historical control; preserve the original, slightly nonparallel join.
        inner = [(560, inner_knee), (400, tip), (240, inner_knee)]
        v_opening = [(560, 0), *inner, (240, 0)]
        counter = [(240, 400), (560, 400), *inner]
    else:
        # A higher inside knee cannot land on the original stem wall with a
        # parallel inset this wide. Flare locally, leaving the main stem fixed.
        left = 80 + slope * (inner_knee - 400) + offset
        inner = [(800 - left, inner_knee), (400, tip), (left, inner_knee)]
        counter = [(240, 400), (560, 400), *inner]
        v_opening = [(560, 0), (560, 400), *inner, (240, 400), (240, 0)]
    if straight:
        # Intersect the same parallel inset with x=240/560 directly. In V
        # coordinates this lands above the midline, with no intermediate vertex.
        meet = 400 + (160 - offset) / slope
        v_opening = [(560, 0), (560, meet), (400, tip), (240, meet), (240, 0)]
        if straight in ('both', 'avw'):
            counter = [(240, bar_top), (560, bar_top), (560, meet), (400, tip), (240, meet)]
    a = ccw_poly(roof + [(560, 0), (560, bar_bottom), (240, bar_bottom), (240, 0)])
    a += ' ' + reverse(ccw_poly(counter))
    v = ccw_poly([(x, 800 - y) for x, y in roof + v_opening])
    return {'A': a, 'V': v, 'W': w_outline()} if straight == 'avw' else {'A': a, 'V': v}


def w_outline(*, cap=800, mid=400, bottom=200, ridge=560, ridge_left=336, centre_slope=.25, outer_weight=128):
    # Outer stems and narrower diagonals reuse W's 128-unit optical weight.
    # Equations are x as a function of y for the left half; mirror at x=400.
    outer_slope = (bottom - 80) / mid
    outer_offset = outer_weight * hypot(1, outer_slope)
    centre_offset = 128 * hypot(1, centre_slope)
    stem_x = 80 + outer_weight
    centre_edge_at_zero = ridge_left - centre_slope * ridge
    centre_inner_bottom = centre_edge_at_zero + centre_offset
    centre_cleft = (400 - centre_inner_bottom) / centre_slope
    knee = mid + (80 + outer_offset - stem_x) / outer_slope
    valley = (bottom + outer_offset - centre_edge_at_zero) / (outer_slope + centre_slope)
    apparent_valley = (centre_edge_at_zero + centre_slope * valley, valley)
    # The inner wall hits its parallel diagonal directly; no flare vertex.
    flank = [(80, cap), (80, mid), (bottom, 0), (centre_inner_bottom, 0)]
    opening = [(stem_x, cap), (stem_x, knee), apparent_valley, (ridge_left, ridge)]
    mirror = lambda points: [(800 - x, y) for x, y in reversed(points)]
    return ccw_poly(flank + [(400, centre_cleft)] + mirror(flank) + mirror(opening)[::-1] + opening[::-1])


def draw(thickness=152, straight=None):
    OUT.mkdir(exist_ok=True)
    ufo = Font.open(GRID_UFO)
    face = STRAIGHT_FACES[straight] if straight else VARIANTS[thickness]
    ufo.info.styleName = ('Grid-Token AV Knees Bold' + (' 152' if thickness == 152 else '')
                          + {None: '', 'v': ' Straight V', 'both': ' Straight AV', 'avw': ' Straight AVW'}[straight])
    apply_ufo_license(ufo.info)
    for name, path in outlines(thickness, straight).items():
        glyph = ufo[name]
        glyph.clearContours()
        parse_path(path, glyph.getPen())
    ufo.save(face.with_suffix('.ufo'), overwrite=True)


def build(thickness=152, straight=None):
    face = STRAIGHT_FACES[straight] if straight else VARIANTS[thickness]
    os.environ.setdefault('SOURCE_DATE_EPOCH', '1795132800')
    subprocess.run([sys.executable, '-m', 'fontmake', '-u', str(face.with_suffix('.ufo')), '-o', 'ttf',
                    '--output-path', str(face)], check=True)


def detail(path, names="AVW", mid=400, height=800):
    grid = ''.join(f'M{x} 0V{height} ' for x in range(0, 801, 80))
    grid += ''.join(f'M0 {y}H800 ' for y in range(0, height + 1, 80))
    cells = []
    with TTFont(path) as font:
        glyphs = font.getGlyphSet()
        for name in names:
            pen = SVGPathPen(glyphs)
            glyphs[name].draw(pen)
            cells.append(f'''<svg viewBox="-8 -8 816 {height + 16}" role="img" aria-label="{name} on an 80-unit grid">
<g transform="translate(0 {height}) scale(1 -1)"><path d="{grid}" class="grid"/>
<path d="{pen.getCommands()}" class="outline"/><path d="M0 {mid}H800" class="mid"/></g></svg>''')
    return ''.join(cells)


def lowercase_panels():
    faces, columns = [], []
    for key, label, path in [('vwBase', 'Lowercase alphabet reference', LOWER_BASE),
                             ('vwTrial', 'Straight joins · 128 w', LOWER_TRIAL),
                             ('vwWide', 'Fuller outer arms · 144 w', LOWER_WIDE)]:
        data = b64encode(path.read_bytes()).decode('ascii')
        faces.append(f'@font-face{{font-family:{key};src:url(data:font/ttf;base64,{data});font-weight:700;font-display:block}}')
        rows = ''.join(f'<div><small>{size} px</small> <span style="font-size:{size}px">{LOWER_SAMPLES[0]}</span></div>'
                       for size in (14, 18, 24))
        rows += ''.join(f'<div><small>18 px</small> <span style="font-size:18px">{text}</span></div>'
                        for text in LOWER_SAMPLES[1:])
        columns.append(f'<section><h2>{label}</h2><div class="cells">{detail(path, "vw", 280, 560)}</div>'
                       f'<div class="sample" style="--face:{key}">{rows}</div></section>')
    return ''.join(faces), ''.join(columns)


def proof():
    lower_faces, lower_columns = lowercase_panels()
    faces, panels = [], []
    for key, label, path in [('GridBase', 'Pinned Grid Bold', BASE), ('GridStraightBoth', 'Straight A/V · prior W', STRAIGHT_BOTH),
                             ('GridStraightAVW', 'Straight A/V/W', STRAIGHT_AVW)]:
        data = b64encode(path.read_bytes()).decode('ascii')
        faces.append(f'@font-face{{font-family:{key};src:url(data:font/ttf;base64,{data});font-weight:700;font-display:block}}')
        waterfall = ''.join(f'<div><small>{px} px</small> <span style="font-size:{px}px">{TEXT}</span></div>'
                            for px in (14, 18, 24))
        panels.append(f'''<section><h2>{label}</h2><div class="cells">{detail(path)}</div>
<div class="waterfall" style="--face:{key}">{waterfall}</div></section>''')
    write_licensed_html(OUT / 'index.html', f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Confinium Mono · Midline Knees</title>{appearance_head('../../../')}
<style>
{''.join(faces)}{lower_faces}
body{{background:var(--paper);color:var(--text);font:16px/1.5 system-ui,sans-serif}}

p,small{{color:var(--secondary)}}
.compare{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,365px),1fr));gap:16px}}
section{{min-width:0;background:var(--panel);border:1px solid var(--border);padding:16px}}
h2{{margin-top:0}} .cells{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px}}
.lower .cells{{grid-template-columns:1fr 1fr}}
a{{color:var(--accent)}}
svg{{display:block;width:100%}} .grid,.mid{{fill:none;stroke:var(--muted);stroke-width:2}}
.mid{{stroke:var(--accent);stroke-dasharray:14 9;stroke-width:4}}
.outline{{fill:var(--text);fill-opacity:.85}}
.waterfall,.sample{{margin-top:12px;overflow-x:auto}}
.waterfall span,.sample span{{font-family:var(--face),monospace;font-weight:700;font-synthesis:none;white-space:pre}}
html:not([data-font-ready]) :is(.waterfall,.sample) span{{visibility:hidden}}
</style></head><body>
{primary_nav('../../../', 'av-knees')}
<main><h1>Midline Knees</h1>
<p><a href="#lowercase">Lowercase v and w</a> · <a href="#uppercase">Uppercase A, V, and W</a> · <a href="book.html">Compare in Book at 14–16 px</a></p>
<p id="font-status" role="status">Loading proof fonts…</p>
<h2 id="lowercase">Lowercase v and w</h2>
<p>The new lowercase forms turn halfway down the x-height. Their inner diagonals meet the vertical walls directly, above the dashed midline. The last column widens only w’s outer arms from 128 to 144 units. The centre diagonals stay at 128, and v is identical in the last two columns.</p>
<div class="compare lower">{lower_columns}</div>
<h2 id="uppercase">Uppercase A, V, and W</h2>
<p>W uses the same direct join as V, with a 128-unit diagonal stroke to keep both valleys open. A and V are identical in the last two columns.</p>
<div class="compare">{''.join(panels)}</div></main>
<script>
const line = document.getElementById('font-status');
Promise.all(['GridBase','GridStraightBoth','GridStraightAVW','vwBase','vwTrial','vwWide'].map(f => document.fonts.load(`700 18px ${{f}}`, f.startsWith('vw') ? 'VvWw' : 'AVW')))
  .then(faces => {{
    if (!faces.every(list => list.length && list.every(f => f.status === 'loaded'))) throw new Error();
    document.documentElement.dataset.fontReady = '';
    line.textContent = 'All six proof fonts loaded.';
  }})
  .catch(() => {{ line.textContent = 'Font load failed; text samples hidden to avoid fallback.'; }});
</script></body></html>''')


def capture():
    capture_chromium(OUT / 'index.html', OUT / 'chromium-midline-knees-w144.png', '1280,1400',
                     'All six proof fonts loaded.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('draw', 'build', 'proof', 'capture'))
    parser.add_argument('--thickness', type=int, choices=tuple(VARIANTS), default=152)
    variants = parser.add_mutually_exclusive_group()
    variants.add_argument('--straight', dest='straight', action='store_const', const='v', help='straight joins on V')
    variants.add_argument('--straight-both', dest='straight', action='store_const', const='both', help='straight joins on A and V')
    variants.add_argument('--with-w', dest='straight', action='store_const', const='avw', help='straight joins on A, V and W')
    args = parser.parse_args()
    if args.straight and (args.thickness != 152 or args.command not in ('draw', 'build')):
        parser.error('straight joins are only for draw/build at 152 units')
    if args.command in ('draw', 'build'):
        globals()[args.command](args.thickness, args.straight)
    else:
        globals()[args.command]()
