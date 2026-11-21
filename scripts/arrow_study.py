"""Build the isolated ASCII proof font and page; never edit family sources."""
import base64
import hashlib
from html import escape
from io import BytesIO
from math import sqrt

from fontTools import subset
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.TupleVariation import TupleVariation

from web import ROOT, appearance_head, primary_nav, write_licensed_html

SOURCE = ROOT / 'studies/variable-repertoire/fonts/ConfiniumMono-VariableRepertoire[wght].ttf'
OUT = ROOT / 'studies/programming-arrows'
RULES = [('hyphen greater', 'arrowRight.alt'), ('less hyphen', 'arrowLeft.alt'),
         ('equal greater', 'arrowDouble.alt'), ('less equal', 'lessEqual.alt'),
         ('greater equal', 'greaterEqual.alt'), ('exclam equal', 'notEqual.alt'),
         ('exclam equal equal', 'notStrictEqual.alt'),
         ('equal equal', 'equalPair.alt'), ('equal equal equal', 'equalTriple.alt'),
         ('less hyphen greater', 'arrowBoth.alt'), ('less equal greater', 'arrowBothDouble.alt')]


def outline(name, weight):
    # 45° head with parallel edges. Intersect the inner edge directly with
    # each bar. For the double shaft, trace the open notch between bars.
    bar, normal = {100: (46, 52), 400: (84, 88), 700: (120, 120)}[weight]
    inset = round(normal * sqrt(2))
    double = name == 'arrowDouble.alt'
    half = bar // 2
    top = 100 + half if double else half
    left = 120
    def inner(y):
        return 1480 - inset - abs(y)
    points = [(left, top), (inner(top), top), (1180, 300-inset), (1180, 300),
              (1480, 0), (1180, -300), (1180, -300+inset), (inner(top), -top), (left, -top)]
    if double:
        gap = 100 - half
        points += [(left, -gap), (inner(gap), -gap), (inner(0), 0), (inner(gap), gap), (left, gap)]
    if name == 'arrowLeft.alt':
        points = [(1600-x, y) for x, y in reversed(points)]
    return [(x, y+400) for x, y in points]


def contours(name, weight):
    if name in ('arrowBoth.alt', 'arrowBothDouble.alt'):
        double = name == 'arrowBothDouble.alt'
        right = outline('arrowDouble.alt' if double else 'arrowRight.alt', weight)
        # Extend the existing head one cell and rotate it about the new centre.
        def turn(path):
            return [(2400-x, 800-y) for x, y in path]
        head = [(x+800, y) for x, y in right[1:8]]
        result = [head + turn(head)]
        if double:
            tip = [(x+800, y) for x, y in right[10:13]]
            result.append(tip + turn(tip))
        return result
    if name in ('notEqual.alt', 'notStrictEqual.alt', 'equalPair.alt', 'equalTriple.alt'):
        strict = name in ('notStrictEqual.alt', 'equalTriple.alt')
        center = 1200 if strict else 800
        bar = {100: 46, 400: 76, 700: 104}[weight]
        half = bar // 2
        width = 580 if strict else 460
        levels = (200, 400, 600) if strict else (280, 520)
        bars = [[(center-width, y+half), (center+width, y+half),
                 (center+width, y-half), (center-width, y-half)] for y in levels]
        if name in ('equalPair.alt', 'equalTriple.alt'):
            return bars
        # A common rising slash. X offset gives the same normal thickness
        # as the bars for a 1:2 run/rise (to within coordinate rounding).
        dx = round(half * sqrt(1.25))
        slash = [(center-170-dx, 60), (center+170-dx, 740),
                 (center+170+dx, 740), (center-170+dx, 60)]
        return bars + [slash]
    if name not in ('lessEqual.alt', 'greaterEqual.alt'):
        return [outline(name, weight)]
    # The chevron uses two parallel 1:4 slopes with vertical terminal cuts.
    # Translate the lower arm down 180 units; match its slope and normal thickness.
    bar = {100: 46, 400: 84, 700: 120}[weight]
    half = round(bar * sqrt(1 + 0.25**2) / 2)
    chevron = [(400, 680+half), (1200, 480+half), (1200, 480-half),
               (400, 280-half), (400, 280+half), (1200-4*half, 480),
               (400, 680-half)]
    rule = [(400, 100+half), (1200, 300+half),
            (1200, 300-half), (400, 100-half)]
    if name == 'lessEqual.alt':
        chevron, rule = [[(1600-x, y) for x, y in reversed(path)] for path in (chevron, rule)]
    return [chevron, rule]


def build_font():
    font = TTFont(SOURCE, recalcTimestamp=False)
    options = subset.Options()
    options.glyph_names = True
    sub = subset.Subsetter(options=options)
    sub.populate(unicodes=range(32, 127))
    sub.subset(font)
    for key in (1, 3, 4, 6, 16):
        for record in font['name'].names:
            if record.nameID == key:
                record.string = ('ConfiniumMono-ArrowStudy' if key in (3, 6) else 'Confinium Mono Arrow Study').encode(record.getEncoding())
    order = list(font.getGlyphOrder())
    for seq, name in RULES:
        base = contours(name, 400)
        pen = TTGlyphPen(None)
        for path in base:
            pen.moveTo(path[0])
            for point in path[1:]:
                pen.lineTo(point)
            pen.closePath()
        font['glyf'][name] = pen.glyph()
        if name in ('notEqual.alt', 'notStrictEqual.alt'):
            font['glyf'][name].flags[0] |= 0x40  # OVERLAP_SIMPLE: crossed bars
        font['hmtx'][name] = (800 * len(seq.split()), min(x for path in base for x, _ in path))
        variations = []
        for weight, region in [(100, (-1, -1, 0)), (700, (0, 1, 1))]:
            deltas = [(x-a, y-b) for path, default in zip(contours(name, weight), base)
                      for (x,y),(a,b) in zip(path, default)]
            variations.append(TupleVariation({'wght': region}, deltas + [(0, 0)] * 4))
        font['gvar'].variations[name] = variations
        order.append(name)
    font.setGlyphOrder(order)
    rules = ' '.join(f'sub {seq} by {name};' for seq, name in sorted(RULES, key=lambda rule: -len(rule[0].split())))
    addOpenTypeFeaturesFromString(font, f'feature dlig {{ {rules} }} dlig;')
    output = BytesIO()
    font.save(output)
    return output.getvalue()


def build():
    data = base64.b64encode(build_font()).decode()
    samples = ['==  !=  ===  !==', 'a == b; a != b; a === b; a !== b',
               'left <-> right; x <=> y', 'if lo <= x && x >= hi', '->  <-  =>']
    rows = []
    for w in (100, 175, 400, 700):
        for enabled in (False, True):
            cells = ''.join(f'<div class="s{s}">{escape(sample)}</div>' for s, sample in zip((36, 14, 16, 16, 16), samples))
            rows.append(f'<section><h2>{w} · {"Ligatures" if enabled else "ASCII"}</h2><div class="sample" style="font-weight:{w};font-feature-settings:\'dlig\' {int(enabled)}">{cells}</div></section>')
    html = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Programming Operators · Confinium Mono</title>{appearance_head('../../')}
<style>@font-face{{font-family:Arrows;src:url(data:font/ttf;base64,{data});font-weight:100 700}}body{{background:var(--paper);color:var(--text);font:16px/1.5 system-ui,sans-serif}}article{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}}section{{padding:12px;background:var(--panel);overflow:auto}}h2{{font-size:16px;margin:0}}.sample{{font-family:Arrows,monospace;white-space:pre}}.s36{{font-size:36px}}.s14{{font-size:14px}}.s16{{font-size:16px}}@media(max-width:640px){{article{{grid-template-columns:1fr}}}}</style>
<body>{primary_nav('../../','programming-arrows')}<main><h1>Programming arrows and comparisons</h1>
<p>Compare plain ASCII with discretionary ligatures (<code>dlig</code>). Each operator spans its original two or three cells; selecting or copying it keeps the original characters. At 14–16 px, compare two-bar and three-bar forms. The slash is the only difference between each equality and its negation. Earlier proofs: <a href="inequalities-and-arrows.html">inequalities and arrows</a> · <a href="parallel-rule.html">sloped lower rule</a> · <a href="flat-rule.html">horizontal lower rule</a> · <a href="arrows-only.html">arrows only</a>.</p>
<article>{''.join(rows)}</article><p>Isolated ASCII proof, not a release font. Source TTF SHA-256: <code style="overflow-wrap:anywhere">{hashlib.sha256(SOURCE.read_bytes()).hexdigest()}</code>.</p></main>
<script>document.fonts.ready.then(()=>{{if(document.fonts.check('16px Arrows')) document.body.dataset.proof='loaded'}})</script></body></html>'''
    OUT.mkdir(exist_ok=True)
    write_licensed_html(OUT / 'index.html', html)


if __name__ == '__main__':
    build()
