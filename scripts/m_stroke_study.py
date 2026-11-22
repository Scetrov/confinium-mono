"""Proof equal U/m stem widths without changing the live weight axis."""
from base64 import b64encode
from io import BytesIO

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

from chromium_proof import capture_chromium
from font_license import write_licensed_html
from stroke_balance import M_CONTROL, equal_m, stem_positions, u_stem
from variable_repertoire import OUT
from web import appearance_head, primary_nav

STUDY = OUT / 'm-stroke-study'
WEIGHTS = (100, 175, 400, 700)
SAMPLE = 'U u m · Confinium · minimum · mum'
STATUS = 'All eight comparison fonts loaded.'


def stem_zones(font):
    m = font['glyf']['m'].coordinates
    u = font['glyf']['U'].coordinates
    return stem_positions(m), u_stem(u)


def equal_stems(font):
    m = font['glyf']['m']
    m.coordinates[:] = equal_m(m.coordinates, u_stem(font['glyf']['U'].coordinates))
    m.recalcBounds(font['glyf'])


def encode(font, text):
    options = subset.Options()
    options.name_IDs = ['*']  # Keep licensing and attribution in the proof fonts.
    sub = subset.Subsetter(options=options)
    sub.populate(text=text)
    sub.subset(font)
    stream = BytesIO()
    font.save(stream)
    return b64encode(stream.getvalue()).decode('ascii')


def build():
    css, rows, loads = [], [], []
    for weight in WEIGHTS:
        cards = []
        for equal, variant in ((False, 'Current m'), (True, 'Equal to U')):
            with TTFont(M_CONTROL, recalcTimestamp=False) as variable:
                font = instantiateVariableFont(variable, {'wght': weight})
                if equal:
                    equal_stems(font)
                (a, b, c, d, e, f), target = stem_zones(font)
                family = f'study{weight}{int(equal)}'
                css.append(f'@font-face{{font-family:{family};src:url(data:font/ttf;base64,{encode(font, SAMPLE)})}}')
            loads.append(f'document.fonts.load("16px {family}", {SAMPLE!r})')
            cards.append(f'<div><h3>{variant} · {b-a} units (U: {target})</h3>'
                         f'<p>Clear counters: {c-b} / {e-d} units</p>'
                         f'<div class="samples" style="font-family:{family}">'
                         f'<div class="large">U u m · mum</div><div>{SAMPLE}</div></div></div>')
        rows.append(f'<section><h2>Weight {weight}</h2><div class="comparison">{"".join(cards)}</div></section>')
    STUDY.mkdir(parents=True, exist_ok=True)
    write_licensed_html(STUDY / 'index.html', f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Confinium Mono · Equal-stroke m study</title>{appearance_head('../../../')}
<style>{''.join(css)}
body{{font:16px/1.4 system-ui,sans-serif}} .comparison{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem}}
section{{border-top:1px solid var(--border);padding-bottom:1rem}} h2,h3,p{{margin:.4rem 0}}
.samples{{font-size:16px;white-space:nowrap;overflow:auto;font-synthesis:none}} .large{{font-size:44px}}
html:not([data-font-ready]) .samples{{visibility:hidden}}
@media(max-width:750px){{.comparison{{grid-template-columns:1fr}}}}
</style></head><body>{primary_nav('../../../', '')}
<main><h1>Equal-stroke m study</h1>
<p>At each sampled weight, the candidate matches all three vertical stems of <b>m</b> to capital <b>U</b>.
The 800-unit advance, outside walls, and shoulder heights stay fixed. The candidate is not part of the live font.</p>
<p><a href="../reading-proof.html">Back to the reading-size proof</a></p>
<p id="status" role="status">Loading fonts…</p>{''.join(rows)}</main>
<script>Promise.all([{','.join(loads)}]).then(results => {{
 if (!results.every(f => f.length && f.every(x => x.status === 'loaded'))) throw new Error();
 document.documentElement.dataset.fontReady = '';
 document.querySelector('#status').textContent = '{STATUS}';
}}).catch(() => {{ document.querySelector('#status').textContent = 'Proof font load failed.'; }});</script>
</body></html>''')
    capture_chromium(STUDY / 'index.html', STUDY / 'verification/chromium.png', '1280,1250', STATUS)


if __name__ == '__main__':
    build()
