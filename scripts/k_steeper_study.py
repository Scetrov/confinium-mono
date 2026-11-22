"""Proof right-shifted K/k forks with steeper, parallel-edged diagonals."""
from math import hypot
from pathlib import Path

from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
from fontTools.varLib.instancer import instantiateVariableFont

from chromium_proof import capture_chromium
from font_license import write_licensed_html

OUT = Path(__file__).resolve().parents[1] / 'studies/k-steeper'
REFERENCE = OUT / 'reference/ConfiniumMono-VariableRepertoire[wght].ttf'
WEIGHTS = (100, 175, 400, 700)
BASES = {'K': 'K', 'k': 'k', 'Ķ': 'K', 'ķ': 'k', 'К': 'K', 'к': 'к'}
SAMPLES = ('K k · KAY · kayak', 'Ķ ķ · К к · КІК · клік', 'A V · X Y · Ý Ŷ Ÿ Ỳ')
STATUS = 'All eight comparison fonts loaded.'


def outline(char, weight):
    """Solve the fork from a shared outside vertex and normal offsets."""
    t = (weight - 100) / 600
    cap = char == 'K'
    height = 800 if cap else 560
    ascender = 560 if char == 'к' else 800
    left = round((129 if cap else 132) * (1-t) + 80*t)
    wall = 240 - (left-80)
    pivot = (475 if cap else 470, height // 2)
    px, py = pivot
    # The shorter fork reads unevenly with asymmetric angles and a lighter
    # bridge. Reflect the lowercase arms about the waist and give them more ink.
    top = round((640 if cap else 625) * (1-t) + (695 if cap else 688)*t)
    bottom = round(650*(1-t) + 700*t) if cap else top
    top_slope = (top-px) / (height-py)
    bottom_slope = (bottom-px) / py
    width = (54 if cap else 56)*(1-t) + 144*t
    upper_offset = width*hypot(1, top_slope)
    lower_offset = width*hypot(1, bottom_slope)
    # Meet the inner diagonal edges with horizontal lands. Keep the land
    # thickness independent of the diagonal angle and the outside fork.
    half_land = round((27 if cap else 28)*(1-t) + 70*t)
    hi, lo = py+half_land, py-half_land
    upper_join = px + top_slope*(hi-py) - upper_offset
    lower_join = px + bottom_slope*(py-lo) - lower_offset
    if min(upper_join, lower_join) <= wall:
        raise ValueError('Fork does not leave room for a straight bridge')
    return [(round(x), round(y)) for x, y in [
        (left, 0), (left, ascender), (wall, ascender), (wall, hi), (upper_join, hi),
        (top-upper_offset, height), (top, height), pivot,
        (bottom, 0), (bottom-lower_offset, 0), (lower_join, lo), (wall, lo), (wall, 0),
    ]]


def apply_candidate(font, weight, *, replace=True):
    cmap, g = font.getBestCmap(), font['glyf']
    changes = {}
    for char, base in BASES.items():
        name = cmap[ord(char)]
        old = g[name]
        cut = old.endPtsOfContours[0]+1
        points = outline(base, weight)
        pen = TTGlyphPen(None)
        pen.moveTo(points[0])
        for point in points[1:]:
            pen.lineTo(point)
        pen.closePath()
        glyph = pen.glyph()
        glyph.coordinates = GlyphCoordinates(list(glyph.coordinates) + [(round(x), round(y)) for x, y in old.coordinates[cut:]])
        glyph.flags.extend(old.flags[cut:])
        glyph.endPtsOfContours.extend(end+len(points)-cut for end in old.endPtsOfContours[1:])
        glyph.numberOfContours = len(glyph.endPtsOfContours)
        glyph.recalcBounds(g)
        changes[name] = glyph
        if replace:
            g[name] = glyph
            font['hmtx'][name] = (font['hmtx'][name][0], glyph.xMin)
    return changes


def build():
    from m_stroke_study import encode
    from web import appearance_head, primary_nav

    css, rows, names = [], [], []
    text = ' '.join(SAMPLES)
    with TTFont(REFERENCE, recalcTimestamp=False) as variable:
        for weight in WEIGHTS:
            cards = []
            for candidate in (False, True):
                face = f'k{weight}{int(candidate)}'
                names.append(face)
                font = instantiateVariableFont(variable, {'wght': weight})
                if candidate:
                    apply_candidate(font, weight)
                css.append(f'@font-face{{font-family:{face};src:url(data:font/ttf;base64,{encode(font, text)})}}')
                lines = ''.join(f'<div>{sample}</div>' for sample in SAMPLES)
                cards.append(f'<div class="samples" style="font-family:{face}"><div class="large">{lines}</div>{lines}</div>')
            rows.append(f'<section><h2>Weight {weight}</h2><div class="comparison">{"".join(cards)}</div></section>')
    write_licensed_html(OUT/'index.html', f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Confinium Mono · Steeper K and k</title>{appearance_head('../../')}
<style>{''.join(css)}
body{{font:16px/1.4 system-ui,sans-serif}} .comparison{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem}}
h2{{font-size:18px;margin:.35rem 0}} section{{border-top:1px solid var(--border);padding-bottom:.55rem}}
.samples{{overflow:auto;font-synthesis:none;white-space:nowrap}} .large{{font-size:29px}}
html:not([data-font-ready]) .samples{{visibility:hidden}}
</style></head><body>{primary_nav('../../', '')}
<main><h1>Steeper K and k</h1>
<p>The candidate moves the fork right and brings the diagonal terminals inward. Parallel edges keep each arm even from join to terminal. Lowercase k now has mirrored diagonals and a fuller bridge. A, V, and Y are unchanged in both columns.</p>
<p><a href="README.md">Geometry and Y review</a> · <a href="first-fork.html">First fork study</a> · <a href="../variable-repertoire/reading-proof.html">Reading-size proof</a></p>
<p id="status" role="status">Loading fonts…</p><div class="comparison"><h2>Current</h2><h2>Steeper fork</h2></div>{''.join(rows)}</main>
<script>Promise.all({names!r}.map(face => document.fonts.load('16px '+face, {text!r}))).then(results => {{
 if (!results.every(f => f.length && f.every(x => x.status === 'loaded'))) throw new Error();
 document.documentElement.dataset.fontReady = '';
 document.querySelector('#status').textContent = '{STATUS}';
}}).catch(() => {{ document.querySelector('#status').textContent = 'Proof font load failed.'; }});</script></body></html>''')
    capture_chromium(OUT/'index.html', OUT/'verification/chromium.png', '1200,1220', STATUS)


if __name__ == '__main__':
    build()
