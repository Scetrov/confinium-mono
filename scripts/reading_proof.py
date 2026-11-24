"""Generate the reading-size proof from the compiled Full Grid variable font."""
from base64 import b64encode
from html import escape

from fontTools.ttLib import TTFont
import uharfbuzz as hb

from font_license import write_licensed_html
from web import ROOT, appearance_head, primary_nav

STUDY = ROOT / 'studies/variable-repertoire'
FONT = STUDY / 'fonts/ConfiniumMono-VariableRepertoire[wght].ttf'
SIZES = (12, 14, 16, 18)
WEIGHTS = ((100, 'Thin'), (175, 'Intermediate'), (400, 'Regular'), (700, 'Bold'))
SAMPLES = (
    ("Cleft alignment", "v w vv w · wave · weave"),
    ("Stem and curve balance", "i j y s e · ijij · sys\nsissy · jigs · easy"),
    ("Steeper forks and diagonals", "K k Ķ ķ · К к · КІК · клік\nk x y · kick · axis\ntext · key · sky"),
    ('Straight stems', 'h n ĥ · H Ĥ Н\nhigh · ninth'),
    ('Lower bowls and descenders', 'a b d z  g j\nbadge · jazz · adagio\njudge · zigzag'),
    ('Thin joins and counters', 'n m p q r u w X\nminimum · plump · quiet\nnew wave · XxX'),
    ('Structural capitals', 'X Y · N M · I J L · W V\nMIX · MINIMUM · WIND\nХ М І Ї · МІНІМУМ · ІНІЙ'),
    ('Accented Y', 'Y Ý Ŷ Ÿ Ỳ · ÝR · ŶN'),
    ('Inherited outlines', 'È c ç o ô D Ď S Š Z Ž\nÉCOLE · garçon · Blöße\nЕ Ё · У Ў · T Т'),
    ('Extended Latin strokes', 'ÑŃŅŇŊ ṀȚ Łł ḟ\nØø Ææ Þþ ð · Ægir · Þór'),
    ('Rounded capitals and ligatures', 'UÛÜ CÇ DÐ OÖ Œœ Юю\nÜBER · ÇA · ÖL · cœur · Юлия'),
    ('Lower corners', 'UÛÜ CÇ\nDÛ · LÜCKE · ÇA · ÜBER'),
    ('Cyrillic strokes', 'ИЙй ф ЮЭЬЫЪ\nЙОД · ЭФИР · ОБЪЁМ · Южный'),
    ('Code', 'if (O0o !== Il1) {\n  log(rows[1], "g_y.p");\n}'),
    ('Mixed text', 'HÚSAVÍK · Þór · Černý\nЖизнь · Київ · Мінск'),
    ('Lookalikes & joins', 'O0o  Il1  rn/m  g_y_p\n[] {} ()  -=+  ,.;:'),
)


def verify_samples(data):
    """Reject missing characters and unexpected cell advances before embedding."""
    with TTFont(FONT) as tt:
        cmap = tt.getBestCmap()
        cell = tt['hmtx'][cmap[ord(' ')]][0]
        axes = {axis.axisTag: axis for axis in tt['fvar'].axes}
        assert cell == 800 and all(axes['wght'].minValue <= w <= axes['wght'].maxValue for w, _ in WEIGHTS)
    font = hb.Font(hb.Face(data))
    for weight, _ in WEIGHTS:
        font.set_variations({'wght': weight})
        for _, text in SAMPLES:
            for line in text.splitlines():
                missing = set(map(ord, line)) - cmap.keys()
                if missing:
                    raise ValueError(f'Unmapped proof sample: {sorted(missing)}')
                buf = hb.Buffer()
                buf.add_str(line)
                buf.guess_segment_properties()
                hb.shape(font, buf)
                if (len(buf.glyph_infos) != len(line) or any(not g.codepoint for g in buf.glyph_infos)
                        or any(p.x_advance != cell for p in buf.glyph_positions)):
                    raise ValueError(f'Unexpected shaping at {weight}: {line!r}')


def build():
    data = FONT.read_bytes()
    verify_samples(data)
    blocks = ''.join(f'<div class="sample"><h4>{escape(label)}</h4><pre>{escape(text)}</pre></div>'
                     for label, text in SAMPLES)
    rows = []
    for size in SIZES:
        faces = ''.join(f'<article style="--weight:{w}"><h3>{name} · {w}</h3>{blocks}</article>'
                        for w, name in WEIGHTS)
        rows.append(f'<section style="--size:{size}px"><h2>{size} px</h2><div class="faces">{faces}</div></section>')
    write_licensed_html(STUDY / 'reading-proof.html', f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Confinium Mono · Reading-size proof</title>
{appearance_head('../../')}
<style>
@font-face{{font-family:ReadingProof;src:url(data:font/ttf;base64,{b64encode(data).decode('ascii')}) format('truetype');font-weight:100 700;font-display:block}}
body{{background:var(--paper);color:var(--text);font:16px/1.45 system-ui,sans-serif}}

main{{padding-bottom:1rem}}
h1{{margin-bottom:.25em}} p{{margin:.4em 0;color:var(--secondary)}}
a{{color:var(--accent)}}
section{{margin:1.2rem 0}} h2{{font-size:1.125rem;margin:0 0 .4rem}}
.faces{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}}
article{{min-width:0;border:1px solid var(--border);background:var(--panel);padding:10px}}
h3{{font-size:.9rem;margin:0}} h4{{font-size:.75rem;margin:0;color:var(--muted)}}
.sample{{margin-top:8px}}
pre{{font-family:ReadingProof,monospace;font-size:var(--size);font-weight:var(--weight);font-synthesis:none;line-height:1.35;letter-spacing:0;margin:3px 0 0;overflow:auto}}
html:not([data-font-ready]) pre{{visibility:hidden}}
@media(max-width:1400px){{.faces{{grid-template-columns:repeat(4,minmax(315px,1fr));overflow-x:auto}}}}
</style></head><body>
{primary_nav('../../', 'reading-proof')}
<main>
<h1>Reading-size proof</h1>
<p>Full Grid variable · 800-unit cell · 100% browser zoom · use Appearance to compare light and dark.</p>
<p><a href="m-stroke-study/">Archived equal-stroke m comparison</a> · <a href="i-width-study/">Archived equal-width i comparison</a> · <a href="../structural-capitals/">Structural capitals study</a> · <a href="../k-steeper/">Steeper K/k and Y review</a></p>
<p id="font-status" role="status">Loading proof font…</p>
{''.join(rows)}
</main>
<script>
const statusLine = document.getElementById('font-status');
Promise.all([100, 175, 400, 700].map(w => document.fonts.load(`${{w}} 16px ReadingProof`, 'O0o Il1 Ж ї Þ')))
  .then(faces => {{
    if (!faces.every(list => list.length && list.every(face => face.status === 'loaded'))) throw new Error('font load');
    document.documentElement.dataset.fontReady = '';
    statusLine.textContent = 'Proof font loaded at all four weights.';
  }})
  .catch(() => {{ statusLine.textContent = 'Proof font failed to load; samples hidden to avoid fallback.'; }});
</script></body></html>
''')


if __name__ == '__main__':
    build()
