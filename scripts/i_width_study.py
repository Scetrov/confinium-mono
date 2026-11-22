"""Compare the current Bold i with a version matching n's ink bounds."""
from fontTools.ttLib import TTFont

from chromium_proof import capture_chromium
from font_license import write_licensed_html
from m_stroke_study import encode
from spacing_balance import I_CONTROL, wide_i
from variable_repertoire import OUT
from web import appearance_head, primary_nav

STUDY = OUT / 'i-width-study'
SAMPLES = ('Confinium', 'final file', 'minimum', 'fini · ini · iii')
STATUS = 'Both Bold comparison fonts loaded.'


def widen_i(font):
    glyf = font['glyf']
    i, n = glyf['i'], glyf['n']
    coords = i.coordinates
    # Existing squared flag and foot. Move only the free ends: the right
    # side of the flag is part of the stem and must stay where it is.
    if [coords[k][0] for k in (0, 9, 5, 6, 3, 4)] != [144, 144, 136, 136, 680, 680]:
        raise ValueError('Review equal-width proof after changing the reference i')
    coords[:] = wide_i(coords, n.xMin, n.xMax)
    i.recalcBounds(glyf)
    font['hmtx']['i'] = (font['hmtx']['i'][0], i.xMin)


def build():
    css, cards = [], []
    text = ' '.join(SAMPLES)
    for family, title, candidate in [('current', 'Current Bold', False), ('wide', 'Equal ink width', True)]:
        with TTFont(I_CONTROL, recalcTimestamp=False) as font:
            if candidate:
                widen_i(font)
            i, n = (font['glyf'][g] for g in 'in')
            measure = f'i: {i.xMax-i.xMin} units · n: {n.xMax-n.xMin} units'
            css.append(f'@font-face{{font-family:{family};src:url(data:font/ttf;base64,{encode(font, text)})}}')
        sizes = ''.join(f'<h3>{size} px</h3><div class="samples" style="font-family:{family};font-size:{size}px">'
                        + ''.join(f'<div>{sample}</div>' for sample in SAMPLES) + '</div>' for size in (16, 40))
        cards.append(f'<section><h2>{title}</h2><p>{measure}</p>{sizes}</section>')
    STUDY.mkdir(parents=True, exist_ok=True)
    write_licensed_html(STUDY / 'index.html', f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Confinium Mono · Equal-width i study</title>{appearance_head('../../../')}
<style>{''.join(css)}
body{{font:16px/1.5 system-ui,sans-serif}} .comparison{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem}}
section{{border-top:1px solid var(--border);padding-bottom:1rem}} h2,h3,p{{margin:.4rem 0}}
.samples{{white-space:nowrap;overflow:auto;font-synthesis:none}}
html:not([data-font-ready]) .samples{{visibility:hidden}}
@media(max-width:680px){{.comparison{{grid-template-columns:1fr}}}}
</style></head><body>{primary_nav('../../../', '')}
<main><h1>Equal-width i study</h1>
<p>Both Bold fonts advance 800 units. The candidate extends the left flag and both ends of the foot to match the ink bounds of <b>n</b> (x = 80…720). The stem, dot and every other letter are unchanged.</p>
<p><a href="../reading-proof.html">Back to the reading-size proof</a></p>
<p id="status" role="status">Loading fonts…</p><div class="comparison">{''.join(cards)}</div></main>
<script>Promise.all(['current','wide'].map(face => document.fonts.load('16px ' + face, {text!r}))).then(results => {{
 if (!results.every(f => f.length && f.every(x => x.status === 'loaded'))) throw new Error();
 document.documentElement.dataset.fontReady = '';
 document.querySelector('#status').textContent = '{STATUS}';
}}).catch(() => {{ document.querySelector('#status').textContent = 'Proof font load failed.'; }});</script>
</body></html>''')
    capture_chromium(STUDY / 'index.html', STUDY / 'verification/chromium.png', '1120,850', STATUS)


if __name__ == '__main__':
    build()
