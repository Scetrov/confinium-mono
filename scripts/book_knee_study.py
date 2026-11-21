"""Isolated variable Midline Knees candidates, derived from the study's Bold outlines."""
import argparse
from base64 import b64encode
from html import escape
from unicodedata import normalize

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.TupleVariation import TupleVariation
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
from fontTools.varLib.instancer import instantiateVariableFont

from av_knee_study import OUT, STRAIGHT_AVW, LOWER_TRIAL, LOWER_WIDE
from chromium_proof import capture_chromium
from font_license import write_licensed_html
from midline_promotion import REFERENCE_VARIABLE as BINARY, REFERENCE_GRID as GRID
from variable_repertoire import masters
from web import appearance_head, primary_nav

LABELS = {128: 'Straight joins · 128 w', 144: 'Straight joins · 144 w'}
SAMPLES = ('vv w   vv w   w vv', 'wave weave review', 'vvave wave   vvw wvv')
ACCENT_SAMPLES = ('À Á Â Ã Ä Å Ā Ă Ą', 'Ŵ ŵ Ẁ ẁ Ẃ ẃ Ẅ ẅ', 'Á Ŵ ẅ   Á Ŵ ẅ')


def candidate(weight):
    return OUT / f'ConfiniumMono-MidlineKneesW{weight}-Variable.ttf'


def build():
    for width, lower in ((128, LOWER_TRIAL), (144, LOWER_WIDE)):
        with (TTFont(BINARY, recalcTimestamp=False) as face, TTFont(GRID) as grid,
              TTFont(STRAIGHT_AVW) as upper, TTFont(lower) as lowercase):
            # Capture existing marks before changing any outlines. The same base
            # master goes into the plain and every accented form at each weight.
            original = [instantiateVariableFont(face, {'wght': w}, overlap=False)['glyf']
                        for w in (100, 400, 700)]
            glyf = face['glyf']
            changes = {n: upper['glyf'][n] for n in 'AVW'} | {n: lowercase['glyf'][n] for n in 'vw'}
            shapes = {name: masters(glyph) for name, glyph in changes.items()}

            def install(name, coords, ends, flags):
                light, book, bold = coords
                glyph = glyf[name]
                glyph.coordinates = GlyphCoordinates(book)
                glyph.endPtsOfContours = ends
                glyph.numberOfContours = len(ends)
                glyph.flags = flags
                glyph.recalcBounds(glyf)
                face['hmtx'][name] = (face['hmtx'][name][0], glyph.xMin)
                face['gvar'].variations[name] = [
                    TupleVariation({'wght': support},
                                   [(x-u, y-v) for (x, y), (u, v) in zip(points, book)] + [(0, 0)]*4)
                    for points, support in [(light, (-1., -1., 0.)), (bold, (0., 1., 1.))]
                ]

            for name, outline in changes.items():
                install(name, shapes[name], outline.endPtsOfContours, outline.flags)
            for cp, name in face.getBestCmap().items():
                decomp = normalize('NFD', chr(cp))
                if len(decomp) != 2 or decomp[0] not in changes:
                    continue
                base = decomp[0]
                prefix = grid['glyf'][base]
                marked = grid['glyf'][name]
                count = len(prefix.coordinates)
                if (marked.coordinates[:count] != prefix.coordinates[:]
                        or marked.endPtsOfContours[:prefix.numberOfContours] != prefix.endPtsOfContours):
                    raise ValueError(f'Unexpected accent contour layout: {name}')
                outline = changes[base]
                delta = len(outline.coordinates) - count
                ends = outline.endPtsOfContours + [e + delta for e in marked.endPtsOfContours[prefix.numberOfContours:]]
                flags = outline.flags + marked.flags[count:]
                coords = [list(points) + list(table[name].coordinates[count:])
                          for points, table in zip(shapes[base], original)]
                install(name, coords, ends, flags)
            names = face['name']
            for rec in names.names:
                if rec.nameID in (1, 3, 4, 6, 10, 16):
                    text = f'Confinium Mono Midline Knees W{width} Study'
                    rec.string = (text.replace(' ', '') if rec.nameID == 6 else text).encode(rec.getEncoding())
            face.save(candidate(width))


def proof():
    faces, columns = [], []
    for key, label, path in [('bookGrid', 'Pre-promotion Full Grid', BINARY),
                             *((f'book{w}', LABELS[w], candidate(w)) for w in LABELS)]:
        data = b64encode(path.read_bytes()).decode('ascii')
        faces.append(f'@font-face{{font-family:{key};src:url(data:font/ttf;base64,{data});font-weight:100 700;font-display:block}}')
        rows = ''.join(f'<h3>{size} px</h3><pre style="font-size:{size}px">{escape(chr(10).join(SAMPLES))}</pre>'
                       for size in (14, 16))
        accent_rows = escape('\n'.join(ACCENT_SAMPLES))
        columns.append(f'<section style="--face:{key}"><h2>{label}</h2>{rows}'
                       f'<h3>Accents · 16 px</h3><pre>{accent_rows}</pre></section>')
    write_licensed_html(OUT / 'book.html', f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Confinium Mono · Midline Knees in Book</title>{appearance_head('../../../')}
<style>
{''.join(faces)}
body{{background:var(--paper);color:var(--text);font:16px/1.5 system-ui,sans-serif}}

a{{color:var(--accent)}}
.compare{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,325px),1fr));gap:16px}}
section{{min-width:0;background:var(--panel);border:1px solid var(--border);padding:16px}}
h2{{margin-top:0;font-size:20px}} h3{{margin:.8rem 0 .3rem;font-size:14px}}
pre{{font-family:var(--face),monospace;font-size:16px;font-weight:400;font-synthesis:none;line-height:1.45;margin:0;overflow:auto}}
html:not([data-font-ready]) pre{{visibility:hidden}}
</style></head><body>{primary_nav('../../../', 'av-knees')}
<main><h1>Midline Knees in Book</h1>
<p><a href="index.html">Back to the Bold study</a></p>
<p>Compare lowercase w against vv at 14 and 16 px. Only w’s outer-arm weight differs between the two candidates. The last accent row repeats the same three letters in precomposed and decomposed form.</p>
<p id="status" role="status">Loading proof fonts…</p><div class="compare">{''.join(columns)}</div></main>
<script>
const statusLine = document.getElementById('status');
Promise.all(['bookGrid','book128','book144'].map(f=>document.fonts.load(`400 16px ${{f}}`,'vv w Á ŵ')))
 .then(faces=>{{
    if (!faces.every(list=>list.length && list.every(f=>f.status==='loaded'))) throw new Error();
    document.documentElement.dataset.fontReady='';
    statusLine.textContent='All three Book proof fonts loaded.';
 }})
 .catch(()=>{{statusLine.textContent='Font load failed; samples hidden to avoid fallback.';}});
</script></body></html>''')


def capture():
    capture_chromium(OUT / 'book.html', OUT / 'chromium-book.png', '1280,850',
                     'All three Book proof fonts loaded.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('build', 'proof', 'capture'))
    globals()[parser.parse_args().command]()
