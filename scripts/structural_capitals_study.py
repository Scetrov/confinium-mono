"""Isolated Bold comparison of the structural X, N, M, I and W."""
from math import hypot, sqrt
from pathlib import Path
from unicodedata import normalize

from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates

from chromium_proof import capture_chromium
from font_license import write_licensed_html

OUT = Path(__file__).resolve().parents[1] / 'studies/structural-capitals'
REFERENCE = OUT / 'reference/ConfiniumMono-FullGrid.ttf'
BASES = 'XNMIW'
DERIVED = {'Х': 'X', 'М': 'M', 'І': 'I', 'Ї': 'I', 'Ŋ': 'N'}
SAMPLES = (
    ('Capitals and anchors', 'X Y   N M   I J L   W V'),
    ('Latin text', 'MIX · MINIMUM · WIND · WAX'),
    ('Latin extensions', 'Ñ Ń Ņ Ň Ŋ · Ṁ · Ì Í Î Ï Ĩ Ī Ĭ Į İ · Ŵ Ẁ Ẃ Ẅ'),
    ('Cyrillic', 'Х М І Ї · МІНІМУМ · ІНІЙ · И Й Ж Ш Щ'),
    ('Independent forms', 'Ĳ · x n m i w · х м і ї'),
)
STATUS = 'Both structural comparison fonts loaded.'


def balanced_w(points, width):
    """Keep the outside silhouette and offset the inner crown from the notch."""
    w = list(points)
    outer, knee = w[2], w[3]
    arm = (knee[0] - outer[0]) / (outer[1] - knee[1])
    foot, notch = w[14], w[13]
    slope = (notch[0] - foot[0]) / (notch[1] - foot[1])
    # x = intercept + slope*y. Its offset is measured normal to the stroke.
    intercept = foot[0] - slope * foot[1] - width * hypot(1, slope)
    y = (outer[0] + arm * outer[1] - intercept) / (arm + slope)
    x = round(intercept + slope * y)
    crown = round(intercept + slope * 400)
    w[3:7] = [(x, round(y)), (crown, 400), (800-crown, 400), (800-x, round(y))]
    return w


def alternatives(font, *, balance_crown=False):
    g = font['glyf']
    # X uses Y's upper land and arm cleft, then repeats them by reflection.
    y = g['Y'].coordinates
    cap, left, right = y[0][1], y[0][0], y[6][0]
    middle = cap // 2
    drop = y[7][1]
    notch_x = left + drop - middle
    x = [(left, middle * 2 - drop), (notch_x, middle), (left, drop), *y[:7],
         (right, drop), (left + right - notch_x, middle), (right, cap - drop),
         *((px, cap - py) for px, py in reversed(y[:7]))]
    # N's diagonal meets the right stem entirely above its baseline, with its
    # lower edge at midline. Solve upper/lower parallel edges at ~144 normal units.
    span = 320
    intercept = cap - middle
    thickness = 144
    slope = (intercept * span - thickness * sqrt(span**2 + intercept**2 - thickness**2)) / (span**2 - thickness**2)
    delta = round(thickness * sqrt(1 + slope**2))
    n = [(80, 0), (80, 800), (240, 800), (560, 400 + delta), (560, 800),
         (720, 800), (720, 0), (560, 0), (560, 400), (240, 800 - delta), (240, 0)]
    # M's brace ends on the midline. Parallel 136-unit diagonal edges meet
    # the original stem walls; the shoulders and flat central cut stay intact.
    slope = 1.55
    offset = round(136 * sqrt(1 + slope**2))
    land = round(400 + 88 * slope)
    m = [(80, 0), (80, 800), (240, 800), (240, land + offset),
         (400, land + offset - round(160 * slope)), (560, land + offset),
         (560, 800), (720, 800), (720, 0), (560, 0), (560, land),
         (472, 400), (328, 400), (240, land), (240, 0)]
    i = [(g['L'].xMin if px == g['I'].xMin else g['J'].xMax if px == g['I'].xMax else px, py)
         for px, py in g['I'].coordinates]
    # Lower only the inner crown and rebuild the two upper-facing knees along
    # the existing outer-arm lines. Keep the lower notch and baseline feet.
    w = list(g['W'].coordinates)
    a, b = w[2], w[3]
    arm = (b[0] - a[0]) / (a[1] - b[1])
    ridge = (w[4][1] - b[1]) / (w[4][0] - b[0])
    knee_x = (a[0] + arm * (a[1] - middle + ridge * w[4][0])) / (1 + arm * ridge)
    knee_y = round(middle + ridge * (knee_x - w[4][0]))
    w[3:7] = [(round(knee_x), knee_y), (w[4][0], middle), (w[5][0], middle),
              (800 - round(knee_x), knee_y)]
    if balance_crown:
        w = balanced_w(g['W'].coordinates, 128)
    return dict(zip(BASES, (x, n, m, i, w)))


def base_for(ch):
    return DERIVED.get(ch, normalize('NFD', ch)[0])


def thin_alternatives(font):
    from variable_diagonals import thin_master

    g = font['glyf']
    # Match Y's Thin outer return; parallel inner edges keep the reflected
    # wedges separate above and below the middle.
    left, inner, drop = 129, 191, 628
    intercept = left + drop + 54 * sqrt(2)
    tip, join = round(intercept - 400), round(intercept - inner)
    arm = [(left, 800), (inner, 800), (inner, join), (400, tip),
           (800-inner, join), (800-inner, 800), (800-left, 800)]
    notch = left + drop - 400
    x = [(left, 800-drop), (notch, 400), (left, drop), *arm,
         (800-left, drop), (800-notch, 400), (800-left, 800-drop),
         *((px, 800-py) for px, py in reversed(arm))]
    span, rise, stem = 418, 400, 54
    slope = (rise * span - stem * sqrt(span**2 + rise**2 - stem**2)) / (span**2 - stem**2)
    delta = round(stem * hypot(1, slope))
    n = [(129, 0), (129, 800), (191, 800), (609, 400+delta), (609, 800),
         (671, 800), (671, 0), (609, 0), (609, 400), (191, 800-delta), (191, 0)]
    slope = 1.35
    land, offset = round(400 + 137*slope), round(54*hypot(1, slope))
    m = [(129, 0), (129, 800), (191, 800), (191, land+offset),
         (400, land+offset-round(209*slope)), (609, land+offset), (609, 800),
         (671, 800), (671, 0), (609, 0), (609, land), (472, 400), (328, 400),
         (191, land), (191, 0)]
    i = [(129, 0), (129, 54), (369, 54), (369, 746), (129, 746), (129, 800),
         (671, 800), (671, 746), (431, 746), (431, 54), (671, 54), (671, 0)]
    w = thin_master('W', list(g['W'].coordinates))
    w = balanced_w(w, 44)
    return dict(zip(BASES, (x, n, m, i, w)))


def candidates(font, reference=None, *, balance_crown=False):
    cmap, g = font.getBestCmap(), font['glyf']
    source_font = font if reference is None else reference
    points = alternatives(source_font, balance_crown=balance_crown)
    updated = {}
    for cp, name in cmap.items():
        ch = chr(cp)
        base = base_for(ch)
        if base not in points:
            continue
        source = source_font['glyf'][cmap[ord(base)]]
        glyph = source_font['glyf'][name]
        count = len(source.coordinates)
        if source.coordinates[:] != glyph.coordinates[:count]:
            raise ValueError(f'{ch} does not start with the expected {base} outline')
        pen = TTGlyphPen(None)
        pen.moveTo(points[base][0])
        for point in points[base][1:]:
            pen.lineTo(point)
        pen.closePath()
        new = pen.glyph()
        offset = len(new.coordinates) - count
        new.coordinates = GlyphCoordinates(list(new.coordinates) + list(glyph.coordinates[count:]))
        new.flags.extend(glyph.flags[count:])
        new.endPtsOfContours += [end + offset for end in glyph.endPtsOfContours[1:]]
        new.numberOfContours = len(new.endPtsOfContours)
        new.recalcBounds(g)
        updated[name] = new
    for name, new in updated.items():
        g[name] = new
        font['hmtx'][name] = (font['hmtx'][name][0], new.xMin)
    return updated


def build():
    from m_stroke_study import encode
    from web import appearance_head, primary_nav

    text = ' '.join(sample for _, sample in SAMPLES)
    faces = []
    for family in ('control', 'candidate'):
        with TTFont(REFERENCE, recalcTimestamp=False) as font:
            if family == 'candidate':
                candidates(font)
            faces.append(f'@font-face{{font-family:{family};src:url(data:font/ttf;base64,{encode(font, text)})}}')
    rows = []
    for label, sample in SAMPLES:
        cards = ''.join(f'<div class="samples" style="font-family:{face}"><div class="large">{sample}</div>'
                        f'<div>{sample}</div></div>' for face in ('control', 'candidate'))
        rows.append(f'<section><h2>{label}</h2><div class="comparison">{cards}</div></section>')
    write_licensed_html(OUT / 'index.html', f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Confinium Mono · Structural capitals</title>{appearance_head('../../')}
<style>{''.join(faces)}
body{{font:16px/1.45 system-ui,sans-serif}} .comparison{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem}}
h2{{font-size:18px;margin:.45rem 0}} section{{border-top:1px solid var(--border);padding-bottom:.8rem}}
.samples{{font-size:16px;overflow:auto;font-synthesis:none}} .large{{font-size:36px;letter-spacing:0}}
html:not([data-font-ready]) .samples{{visibility:hidden}}
</style></head><body>{primary_nav('../../', '')}
<main><h1>Structural capitals</h1>
<p>Bold only. X repeats Y’s outer vertical land above and below; N and M bring the low edge of the brace to the 400-unit midline;
I matches J and L’s ink width without thickening its bars or stem; W lowers the inner crown to the midline.</p>
<p>The variants keep the 800-unit advance. Accented and shared-script glyphs inherit the changes; independent shapes are shown as controls.
<a href="README.md">Read the inventory</a> (source notes).</p>
<p id="status" role="status">Loading fonts…</p><div class="comparison"><h2>Released 0.2.0 Bold</h2><h2>Structural candidate</h2></div>
{''.join(rows)}</main><script>
Promise.all(['control','candidate'].map(face => document.fonts.load('16px ' + face, {text!r}))).then(results => {{
 if (!results.every(f => f.length && f.every(x => x.status === 'loaded'))) throw new Error();
 document.documentElement.dataset.fontReady = '';
 document.querySelector('#status').textContent = '{STATUS}';
}}).catch(() => {{ document.querySelector('#status').textContent = 'Proof font load failed.'; }});
</script></body></html>''')
    capture_chromium(OUT / 'index.html', OUT / 'verification/chromium.png', '1360,1240', STATUS)


if __name__ == '__main__':
    build()
