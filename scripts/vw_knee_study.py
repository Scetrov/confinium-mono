"""Compare lowercase v/w straight joins without altering the alphabet study."""
import argparse
from math import hypot
import os

from fontTools.svgLib.path import parse_path
from ufo2ft import compileTTF
from ufoLib2 import Font

from av_knee_study import LOWER_TRIAL as TRIAL, LOWER_WIDE, OUT, lowercase_panels, w_outline
from chromium_proof import capture_chromium
from font_license import write_licensed_html
from grid_token_study import STUDY, ccw_poly
from web import appearance_head, primary_nav

ALPHABET = STUDY / 'lowercase-alphabet'
BASE_NAME = 'ConfiniumMono-GridToken-LowercaseAlphabet'
SOURCE = TRIAL.with_suffix('.ufo')


def draw(wider=False):
    font = Font.open(ALPHABET / 'sources' / f'{BASE_NAME}.ufo')
    font.info.familyName = 'Confinium Mono Lowercase VW Study' + (' Wider W' if wider else '')
    slope = 232 / 280
    offset = 152 * hypot(1, slope)
    meet = 280 + (80 + offset - 240) / slope
    tip = 280 + (80 + offset - 400) / slope
    v = ccw_poly([(80, 560), (80, 280), (312, 0), (488, 0), (720, 280), (720, 560),
                  (560, 560), (560, meet), (400, tip), (240, meet), (240, 560)])
    w = w_outline(cap=560, mid=280, bottom=192, ridge=420, ridge_left=344, centre_slope=.28,
                  outer_weight=144 if wider else 128)
    for name, outline in [('v', v), ('w', w)]:
        font[name].clearContours()
        parse_path(outline, font[name].getPen())
    font.save(LOWER_WIDE.with_suffix('.ufo') if wider else SOURCE, overwrite=True)


def build(wider=False):
    target = LOWER_WIDE if wider else TRIAL
    os.environ.setdefault('SOURCE_DATE_EPOCH', '1795132800')
    compileTTF(Font.open(target.with_suffix('.ufo')), removeOverlaps=False, useProductionNames=False).save(target)


def proof():
    faces, columns = lowercase_panels()
    write_licensed_html(OUT / 'lowercase.html', f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Confinium Mono · Lowercase v/w midline knees</title>{appearance_head('../../../')}
<style>
{faces}
body{{background:var(--paper);color:var(--text);font:16px/1.5 system-ui,sans-serif}}

.compare{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,365px),1fr));gap:16px}}
section{{min-width:0;background:var(--panel);border:1px solid var(--border);padding:16px}}
h2{{margin-top:0}} .cells{{display:grid;grid-template-columns:1fr 1fr;gap:8px}}
svg{{display:block;width:100%}} .grid,.mid{{fill:none;stroke:var(--muted);stroke-width:2}}
.mid{{stroke:var(--accent);stroke-dasharray:14 9;stroke-width:4}} .outline{{fill:var(--text);fill-opacity:.85}}
.sample{{margin-top:12px;overflow-x:auto}} .sample span{{font-family:var(--face),monospace;font-weight:700;font-synthesis:none;white-space:pre}}
html:not([data-font-ready]) .sample span{{visibility:hidden}}
a{{color:var(--accent)}}
</style></head><body>{primary_nav('../../../', 'av-knees')}
<main><h1>Lowercase v/w midline knees</h1>
<p><a href="index.html">Back to Midline Knees</a></p>
<p>Both lowercase outer bends sit at half the 560-unit x-height. The inner diagonals meet the vertical walls directly, just above the dashed line. The last column widens only w’s outer arms; v and the uppercase forms are unchanged.</p>
<p id="font-status" role="status">Loading proof fonts…</p><div class="compare">{columns}</div></main>
<script>
const statusLine = document.querySelector('#font-status');
Promise.all(['vwBase','vwTrial','vwWide'].map(f=>document.fonts.load(`700 18px ${{f}}`, 'VvWw')))
  .then(faces=>{{
    if (!faces.every(list=>list.length && list.every(f=>f.status==='loaded'))) throw new Error();
    document.documentElement.dataset.fontReady='';
    statusLine.textContent='All three lowercase proof fonts loaded.';
  }})
  .catch(()=>{{statusLine.textContent='Font load failed; samples hidden to avoid fallback.';}});
</script></body></html>''')


def capture():
    capture_chromium(OUT / 'lowercase.html', OUT / 'chromium-wider-w-lowercase.png', '1280,850',
                     'All three lowercase proof fonts loaded.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('draw', 'build', 'proof', 'capture'))
    parser.add_argument('--wider-w', action='store_true')
    args = parser.parse_args()
    if args.command in ('draw', 'build'):
        globals()[args.command](args.wider_w)
    else:
        globals()[args.command]()
