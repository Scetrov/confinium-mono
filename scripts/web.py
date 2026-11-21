"""Static website generator for Confinium Mono: root explorer, design process, and shared primary nav."""
import base64
from html import escape
import json
import unicodedata
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from io import BytesIO
from pathlib import Path
from chromium_proof import capture_chromium
from font_license import write_licensed_html

ROOT = Path(__file__).resolve().parents[1]

def appearance_head(root_rel: str) -> str:
    """Load the shared theme before rendering any page content."""
    return (f'<script src="{root_rel}assets/appearance.js"></script>'
            f'<link rel="stylesheet" href="{root_rel}assets/appearance.css">')


def primary_nav(root_rel: str, active: str) -> str:
    """Return shared primary navigation HTML with relative links from root_rel."""
    links = [
        ('av-knees', 'Midline Knees', f'{root_rel}studies/grid-token-bold/av-knees/index.html'),
        ('reading-proof', 'Reading-Size Proof', f'{root_rel}studies/variable-repertoire/reading-proof.html'),
        ('cyrillic', 'Cyrillic', f'{root_rel}studies/grid-token-bold/cyrillic/index.html'),
        ('european', 'European Latin', f'{root_rel}studies/grid-token-bold/european-latin/index.html'),
        ('mixed-text', 'Mixed Text · ASCII', f'{root_rel}studies/grid-token-bold/mixed-text/index.html'),
        ('grid-token', 'Grid & Token Bold', f'{root_rel}studies/grid-token-bold/specimen/index.html'),
        ('hollow', 'Hollow Display', f'{root_rel}studies/grid-token-bold/hollow/index.html'),
        ('diagonals', 'Optical Diagonals', f'{root_rel}studies/grid-token-bold/diagonals/index.html'),
        ('q-tail', 'Q-Tail Direction', f'{root_rel}studies/grid-token-bold/q-tail/index.html'),
        ('alphabet', 'Lowercase Alphabet', f'{root_rel}studies/grid-token-bold/lowercase-alphabet/index.html'),
        ('lowercase', 'Lowercase Foundations', f'{root_rel}studies/grid-token-bold/lowercase/index.html'),
        ('punctuation', 'ASCII Punctuation', f'{root_rel}studies/grid-token-bold/punctuation/index.html'),
        ('pilot', '697-Unit Experiment', f'{root_rel}specimen/index.html'),
    ]
    def link(key, label, href):
        state = ' class="active" aria-current="page"' if active == key else ''
        return f'<a href="{href}"{state}>{label}</a>'

    explorer = link('explorer', 'Explorer', f'{root_rel}explorer.html')
    home_state = ' aria-current="page"' if active == 'home' else ''
    process = link('process', 'Design Process', f'{root_rel}process.html')
    install = link('install', 'Install', f'{root_rel}install.html')
    items = ''.join(link(*item) for item in links)
    section = ' class="active"' if any(key == active for key, _, _ in links) else ''
    return (
        '<nav class="site-nav" aria-label="Primary">'
        f'<a class="brand" href="{root_rel}index.html"{home_state}>Confinium <span class="brand-mono">Mono</span></a>'
        f'<div class="nav-center">{explorer}{process}{install}<details><summary{section}>Studies</summary>'
        f'<div class="study-links">{items}</div></details></div></nav>'
    )


def _b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


# Alphabet membership is deliberately many-to-many (Å is Latin, Nordic,
# Swedish, Finnish, Danish and Norwegian). These are letters, not locales.
ALPHABETS = {
    'Icelandic': 'aábdðeéfghiíjklmnoóprstuúvxyýþæö',
    'Faroese': 'aáb dð e f g h ií j k l m n oó p r s t uú v yý æ ø'.replace(' ', ''),
    'Danish': 'abcdefghijklmnopqrstuvwxyzæøå',
    'Norwegian': 'abcdefghijklmnopqrstuvwxyzæøå',
    'Swedish': 'abcdefghijklmnopqrstuvwxyzåäö',
    'Finnish': 'abcdefghijklmnopqrstuvwxyzåäöšž',
    'Northern Sámi': 'aábcčdđefghijklmnŋoprsštŧuvzž',
    'Russian': 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя',
    'Ukrainian': 'абвгґдеєжзиіїйклмнопрстуфхцчшщьюя',
    'Belarusian': 'абвгдеёжзійклмнопрстуўфхцчшыьэюя',
}
NORDIC = {'Icelandic', 'Faroese', 'Danish', 'Norwegian', 'Swedish', 'Finnish', 'Northern Sámi'}


def character_data(fonts):
    """Map each embedded face to its actual Unicode inventory (not glyph names)."""
    faces, entries = {}, {}
    for key, _, path, _ in fonts:
        with TTFont(path) as font:
            codes = sorted(font.getBestCmap())
        faces['exp_' + key] = codes
        for cp in codes:
            ch = chr(cp)
            kind = unicodedata.category(ch)[0]
            title = unicodedata.name(ch, 'UNNAMED')
            if kind == 'L':
                group = 'Cyrillic' if 'CYRILLIC' in title else ('Basic Latin' if cp < 128 else 'Extended Latin')
            else:
                group = {'N': 'Figures', 'M': 'Combining marks', 'Z': 'Spaces'}.get(kind, 'Punctuation & symbols')
            groups = [group]
            if group in ('Basic Latin', 'Extended Latin'):
                groups.append('Latin')
            if kind == 'L':
                groups.append('Uppercase' if ch.isupper() else 'Lowercase')
                languages = [lang for lang, alphabet in ALPHABETS.items()
                             if ch in alphabet or ch in alphabet.upper()]
                if NORDIC.intersection(languages):
                    groups.append('Nordic')
                groups.extend(languages)
            if kind == 'P':
                groups.append('Punctuation')
            if kind == 'S':
                groups.append('Symbols')
            if unicodedata.category(ch) == 'Sc':
                groups.append('Currency')
            entries[cp] = [title, groups]
    return {'faces': faces, 'entries': entries}


def build_site_titles() -> None:
    font = ROOT / 'studies/grid-token-bold/full-family/fonts/ConfiniumMono-FullGrid.ttf'
    licence = (ROOT / 'OFL.txt').read_text(encoding='utf-8')
    variable = ROOT / 'studies/variable-repertoire/fonts/ConfiniumMono-VariableRepertoire[wght].ttf'
    light_data = BytesIO()
    with TTFont(variable, recalcTimestamp=False) as face:
        light = instantiateVariableFont(face, {'wght': 300}, inplace=True)
        wordmark = subset.Subsetter()
        wordmark.populate(text='Mono')
        wordmark.subset(light)
        light.save(light_data)
    wordmark_data = base64.b64encode(light_data.getvalue()).decode('ascii')
    (ROOT / 'assets/site-titles.css').write_text(
        f'/* Generated by scripts/web.py.\n{licence}\n*/\n'
        "@font-face{font-family:'Confinium Site Titles';font-style:normal;font-weight:700;"
        f"font-display:swap;src:url(data:font/ttf;base64,{_b64(font)}) format('truetype');}}\n"
        "@font-face{font-family:'Confinium Site Titles';font-style:normal;font-weight:300;"
        f"font-display:swap;src:url(data:font/ttf;base64,{wordmark_data}) format('truetype');}}\n",
        encoding='utf-8',
    )


def build_home() -> None:
    """Lead with live type specimens; leave controls and measurements to proofs."""
    full = 'studies/grid-token-bold/full-family'
    grid = 'studies/grid-token-bold'
    variable = 'studies/variable-repertoire'
    sources = [('HomeVariable', ROOT / variable / 'fonts/ConfiniumMono-VariableRepertoire[wght].ttf', '100 700')]
    sources += [(f'Home{style}', ROOT / full / f'fonts/ConfiniumMono-Full{style}.ttf', '700')
                for style in ('Grid', 'Open', 'Dense', 'Hollow')]
    faces = '\n'.join(f"@font-face{{font-family:{name};font-weight:{weight};"
                      f"src:url(data:font/ttf;base64,{_b64(path)}) format('truetype');font-display:swap}}"
                      for name, path, weight in sources)
    cards = ''.join(f'''<article class="cut">
      <h3>{style}</h3><p class="cut-type" style="--cut:Home{style}" data-specimen>Q0 Wy</p>
      <p>{copy}</p></article>''' for style, copy in (
        ('Grid', 'The baseline cut: square proportions, crisp joins and measured curves.'),
        ('Open', 'Thinner bars and rounder inner corners leave more room inside the letters.'),
        ('Dense', 'Thicker bars and tighter corners make for a more compact rhythm.'),
        ('Hollow', 'The Grid silhouette in outline, built for large display settings.')))
    weights = ''.join(f'''<div class="weight"><span>{label} / {value}</span>
      <p data-specimen style="font-weight:{value}">Signal</p></div>'''
                      for label, value in (('Thin', 100), ('Book', 400), ('Bold', 700)))
    write_licensed_html(ROOT / 'index.html', f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Confinium Mono is an original geometric monospace. Compare the variable weights, four static cuts, and Latin and Cyrillic lettering.">
<title>Confinium Mono — Geometric Monospace</title>
{appearance_head('')}
<link rel="stylesheet" href="assets/home.css">
<style>{faces}</style>
</head>
<body>
{primary_nav('', 'home')}
<main class="landing" id="main">
<section class="hero" aria-labelledby="hero-title">
  <p class="eyebrow">Geometric monospace · typeface in development</p>
  <h1 id="hero-title" data-specimen>Confinium<br><span data-specimen>Mono</span></h1>
  <div class="hero-foot">
    <p>One fixed-width grid, from hairline text to hollow display. Drawn from scratch for code, interfaces and lettering that needs a little edge.</p>
    <div class="actions"><a class="button" href="explorer.html">Try the Explorer →</a>
    <a href="process.html">See how it was drawn →</a></div>
  </div>
</section>
<section aria-labelledby="weights-title">
  <p class="eyebrow">01 / Variable weight</p>
  <h2 id="weights-title">Same width. Different weight.</h2>
  <p>From 100 to 700, the strokes change while the monospaced cells stay put.</p>
  <div class="weights">{weights}</div>
  <a href="{variable}/reading-proof.html">Compare at reading sizes →</a>
</section>
<section aria-labelledby="cuts-title">
  <p class="eyebrow">02 / Static cuts</p>
  <h2 id="cuts-title">Four ways to draw the grid.</h2>
  <p>The angled Q tail ties the cuts together; the corners, counters and fill set them apart.</p>
  <div class="cuts">{cards}</div>
  <div class="actions"><a href="{full}/index.html">Compare the full family →</a>
  <a href="{grid}/hollow/index.html">Inspect Hollow Display →</a></div>
</section>
<section aria-labelledby="details-title">
  <p class="eyebrow">03 / Characters and details</p>
  <h2 id="details-title">More than A to Z.</h2>
  <p>Extended Latin and Cyrillic share the same cell with figures and symbols. The studies put individual shapes and their joins under the microscope.</p>
  <div class="scripts">
    <article><p data-specimen>Æ Ø Þ Ŋ</p><a href="{grid}/european-latin/index.html">European Latin →</a></article>
    <article><p data-specimen>Ж Й Ю ф</p><a href="{grid}/cyrillic/index.html">Cyrillic →</a></article>
    <article><p data-specimen>Q A V w</p><a href="{grid}/av-knees/index.html">Diagonal joins →</a></article>
  </div>
</section>
</main>
<footer class="landing-footer"><a href="explorer.html">Open the Explorer →</a>
<a href="process.html">Browse the design studies →</a></footer>
<script>
Promise.all([...document.querySelectorAll('[data-specimen]')].map(sample => {{
  const style = getComputedStyle(sample);
  return document.fonts.load(`${{style.fontWeight}} 24px ${{style.fontFamily.split(',')[0]}}`, sample.textContent);
}})).then(results => {{
  if (results.every(faces => faces.length && faces.every(face => face.status === 'loaded'))) {{
    document.documentElement.dataset.fontReady = '';
  }}
}}).catch(console.error);
</script>
</body>
</html>
''')


def build_explorer() -> None:
    build_site_titles()
    """Generate the interactive explorer at explorer.html."""
    study = ROOT / 'studies/grid-token-bold'
    fonts = [
        (style.lower(), style + ' Bold', study / f'full-family/fonts/ConfiniumMono-Full{style}.ttf', '700')
        for style in ('Grid', 'Open', 'Dense', 'Hollow')
    ] + [
        ('variable', 'Confinium Mono Variable', ROOT / 'studies/variable-repertoire/fonts/ConfiniumMono-VariableRepertoire[wght].ttf', '100 700'),
    ]
    data = character_data(fonts)
    inventory = json.dumps(data, separators=(',', ':'))
    groups = sorted({group for _, memberships in data['entries'].values() for group in memberships})
    category_options = ''.join(f'<option>{escape(group)}</option>' for group in groups)
    css_fonts = ''.join(
        f'@font-face{{font-family:exp_{key};src:url(data:font/ttf;base64,{_b64(path)});font-weight:{wght}}}'
        for key, _, path, wght in fonts
    )
    nav = primary_nav('', 'explorer')
    html = f'''<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Confinium Mono — Type Explorer</title>
{appearance_head('')}
<style>
{css_fonts}
*{{box-sizing:border-box}}
body{{background:var(--paper);color:var(--text);font:16px/1.5 system-ui,sans-serif}}
h1{{margin:0 0 8px;font-size:34px;letter-spacing:-.01em}}
.lead{{max-width:860px;color:var(--secondary);margin:0 0 22px}}
.controls{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;padding:18px;border:1px solid var(--border);background:var(--panel);margin-bottom:24px}}
label{{display:block;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);margin-bottom:6px}}
select,input[type=search],input[type=text],input[type=range]{{width:100%;font:inherit;color:var(--text)}}
select,input[type=search],input[type=text]{{padding:7px 10px;border:1px solid var(--border);background:var(--paper)}}
.presets{{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}}
button.chip{{background:var(--paper);border:1px solid var(--border);padding:4px 10px;font:13px/1.3 system-ui,sans-serif;color:var(--text);cursor:pointer}}
button.chip:hover{{border-color:var(--accent)}}
.stage{{border-top:1px solid var(--border);padding:22px 0}}
.specimen{{font-family:exp_grid;font-weight:700;font-size:96px;line-height:1.25;letter-spacing:0;font-kerning:none;font-synthesis:none;white-space:pre-wrap;word-break:break-word;outline:none;min-height:1.3em}}
.meta{{display:flex;flex-wrap:wrap;gap:12px 24px;font-size:13px;color:var(--muted);margin-top:10px}}
.waterfall{{border-top:1px solid var(--border);padding:18px 0;display:grid;gap:10px}}
.wf-row{{display:grid;grid-template-columns:64px 1fr;align-items:baseline;gap:12px}}
.wf-size{{font-size:12px;color:var(--muted)}}
.wf-text{{font-family:exp_grid;font-weight:700;font-kerning:none;font-synthesis:none;letter-spacing:0;overflow:auto;white-space:pre}}
.character-sheet{{border-top:1px solid var(--border);padding:20px 0}}
.sheet-controls{{display:flex;flex-wrap:wrap;align-items:end;gap:12px}}
.glyph-bar{{display:grid;grid-template-columns:repeat(auto-fill,minmax(50px,1fr));gap:4px;max-height:24rem;overflow:auto;padding:3px}}
.glyph-btn{{font-family:exp_grid;font-weight:700;font-size:28px;width:100%;height:48px;border:1px solid var(--border);background:var(--paper);cursor:pointer;display:grid;place-items:center}}
.glyph-btn:hover{{border-color:var(--accent);background:var(--panel)}}
.timeline{{border-top:1px solid var(--border);padding-top:22px;margin-top:12px}}
.steps{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin-top:12px}}
.step{{border:1px solid var(--border);padding:14px;background:var(--panel)}}
.step h3{{margin:0 0 6px;font-size:15px}}
.step p{{margin:0 0 8px;font-size:13px;color:var(--secondary)}}
.step a{{font-size:13px;color:var(--accent);font-weight:600;text-decoration:none}}
.step a:hover{{text-decoration:underline}}
#status{{font-size:13px;color:var(--accent);margin:0 0 14px}}
:root{{--ink:var(--text, CanvasText)}}
/* Keep presets usable if the shared stylesheet is cached without the new tokens. */
:root[data-ink="red"]{{--ink:var(--red, #9e3046)}}
:root[data-ink="orange"]{{--ink:var(--orange, #904800)}}
:root[data-ink="yellow"]{{--ink:var(--yellow, #715019)}}
:root[data-ink="green"]{{--ink:var(--green, #435e2a)}}
:root[data-ink="blue"]{{--ink:var(--accent, #2c50a7)}}
:root[data-ink="purple"]{{--ink:var(--violet, #6935a0)}}
.specimen,.wf-text,.glyph-btn{{color:var(--ink)}}
.appearance{{display:flex;flex-wrap:wrap;align-items:end;gap:12px 20px;margin:0 0 24px}}
.appearance input[type=color]{{display:block;width:4rem;height:2.2rem;cursor:pointer}}
.specimen:focus-visible{{outline:2px solid var(--accent);outline-offset:3px}}
</style>
{nav}
<h1>Confinium Mono Explorer</h1>
<p class="lead">Original geometric monospace typeface under active development. Explore European Latin, Cyrillic, figures and symbols in Grid, Open, Dense and Hollow. Confinium Mono Variable covers the same characters at weights 100–700. All glyph previews use embedded Confinium Mono binaries.</p>
<p><a href="studies/variable-repertoire/reading-proof.html">Compare Thin, Book, and Bold at reading sizes</a> · <a href="studies/grid-token-bold/av-knees/index.html">Compare the Midline Knees study</a> · <a href="studies/grid-token-bold/full-family/index.html">Full Family Proof</a></p>
<p id="status">Loading fonts…</p>

<section class="controls" aria-label="Explorer controls">
  <div>
    <label for="familySel">Typeface</label>
    <select id="familySel">
      <option value="exp_grid" selected data-wght="700" data-meta="Advance 800 · Cap 800 · Stem 160 · Bar 140 · Fillet 32 · Q 128 / Y 144">Confinium Mono Grid Bold</option>
      <option value="exp_open" data-wght="700" data-meta="Advance 800 · Cap 800 · Stem 160 · Bar 136 · Fillet 40 · Q 128 / Y 144">Confinium Mono Open Bold</option>
      <option value="exp_dense" data-wght="700" data-meta="Advance 800 · Cap 800 · Stem 160 · Bar 144 · Fillet 24 · Q 128 / Y 144">Confinium Mono Dense Bold</option>
      <option value="exp_hollow" data-wght="700" data-meta="Advance 800 · Cap 800 · Display Wireframe · 28-unit wall inset from Grid">Confinium Mono Hollow Display</option>
      <option value="exp_variable" data-wght="700" data-meta="Advance 800 · Cap 800 · x-height 560 · Full Grid Bold master · Variable wght 100–700">Confinium Mono Variable</option>
    </select>
  </div>
  <div>
    <label for="sampleInput">Sample text (editable below too)</label>
    <input id="sampleInput" type="text" value="HO0QCESGY">
    <div class="presets">
      <button class="chip" type="button" data-text="HO0QCESGY">HO0QCESGY</button>
      <button class="chip" type="button" data-text="ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789">A–Z 0–9</button>
      <button class="chip" type="button" data-text="ABCDEFGHIJKLMNOPQRSTUVWXYZ">UPPERCASE</button>
      <button class="chip" type="button" data-text="abcdefghijklmnopqrstuvwxyz">lowercase</button>
      <button class="chip" type="button" data-text="0123456789">Numerals</button>
      <button class="chip" type="button" data-text="O0O0 1I1I 2Z2Z 5S5S 8B8B QO0Q">Pairs</button>
      <button class="chip" type="button" data-text="HO0Qgyces">9-glyph sample</button>
      <button class="chip" type="button" data-text="QYQY HY">Q/Y Focus</button>
    </div>
  </div>
  <div>
    <label for="sizeRange">Size: <span id="sizeVal">96</span> px</label>
    <input id="sizeRange" type="range" min="14" max="180" value="96">
    <div class="presets">
      <button class="chip size-chip" type="button" data-size="14">14</button>
      <button class="chip size-chip" type="button" data-size="18">18</button>
      <button class="chip size-chip" type="button" data-size="32">32</button>
      <button class="chip size-chip" type="button" data-size="64">64</button>
      <button class="chip size-chip" type="button" data-size="112">112</button>
    </div>
  </div>
  <div id="weightWrap">
    <label for="weightRange">Weight: <span id="weightVal">700</span></label>
    <input id="weightRange" type="range" min="100" max="700" step="10" value="700" disabled>
    <div class="meta" id="metaLine">Advance 800 · Cap 800 · Stem 160 · Bar 140 · Fillet 32 · Q 128 / Y 144</div>
  </div>
</section>

<section class="appearance" aria-label="Preview appearance">
  <div>
    <label for="inkSel">Typeface colour</label>
    <select id="inkSel">
      <option value="default">Default (neutral)</option>
      <option value="red">Red</option>
      <option value="orange">Orange</option>
      <option value="yellow">Yellow</option>
      <option value="green">Green</option>
      <option value="blue">Blue</option>
      <option value="purple">Purple</option>
      <option value="custom">Custom</option>
    </select>
  </div>
  <div>
    <label for="customInk">Custom colour</label>
    <input id="customInk" type="color" value="#007197">
  </div>
</section>

<section class="stage">
  <div id="specimen" class="specimen" contenteditable="true" spellcheck="false">HO0QCESGY</div>
</section>

<section class="character-sheet" aria-labelledby="sheetHeading">
  <h2 id="sheetHeading">Character sheet</h2>
  <p>Every typeface covers the entire sheet. Choose a character to append it to your sample.</p>
  <div class="sheet-controls">
    <label>Category <select id="sheetCategory"><option>All characters</option>{category_options}</select></label>
    <label>Filter characters <input type="search" id="sheetQuery" placeholder="e.g. Þ, breve, U+0416"></label>
  </div>
  <p id="sheetCount" role="status"></p>
  <div class="glyph-bar" id="glyphBar" role="group" aria-label="Insert character"></div>
</section>

<section class="waterfall" aria-label="Size waterfall">
  <div class="wf-row"><span class="wf-size">14 px</span><span class="wf-text" style="font-size:14px">HO0QCESGY O0O0 QO0Q</span></div>
  <div class="wf-row"><span class="wf-size">18 px</span><span class="wf-text" style="font-size:18px">HO0QCESGY O0O0 QO0Q</span></div>
  <div class="wf-row"><span class="wf-size">32 px</span><span class="wf-text" style="font-size:32px">HO0QCESGY O0O0 QO0Q</span></div>
  <div class="wf-row"><span class="wf-size">64 px</span><span class="wf-text" style="font-size:64px">HO0QCESGY</span></div>
</section>

<section class="timeline">
  <h2>Design Process</h2>
  <div class="steps">
    <article class="step">
      <h3>1. 697-Unit Variable Experiment</h3>
      <p>697-unit advance, 700 cap height, Thin/Book/Bold masters (100–700) for HO0Qgyces, plus analytic curve fixes.</p>
      <a href="specimen/index.html">Open the Experiment →</a>
    </article>
    <article class="step">
      <h3>2. Grid &amp; Token Bold</h3>
      <p>800-unit cell (1u = 80), 160-unit stems, Grid / Open / Dense treatments for HO0QCESGY.</p>
      <a href="studies/grid-token-bold/specimen/index.html">Open Grid &amp; Token Study →</a>
    </article>
    <article class="step">
      <h3>3. Q-Tail Direction</h3>
      <p>Evaluated centred tail versus 45° right-descending tail with horizontal end cut.</p>
      <a href="studies/grid-token-bold/q-tail/index.html">Open Q-Tail Study →</a>
    </article>
    <article class="step">
      <h3>4. Optical Diagonals</h3>
      <p>Tested 128 / 144 / 160 normal units; promoted Q = 128 and Y = 144 to the Grid-Token baseline.</p>
      <a href="studies/grid-token-bold/diagonals/index.html">Open Diagonals Study →</a>
    </article>
    <article class="step">
      <h3>5. ASCII Punctuation</h3>
      <p>All 32 ASCII punctuation and operator glyphs in an isolated Grid Bold study.</p>
      <a href="studies/grid-token-bold/punctuation/index.html">Open Punctuation Study →</a>
    </article>
  </div>
  <p style="margin-top:14px;font-size:14px"><a href="process.html" style="color:var(--accent);font-weight:600">Read full design process, curve corrections &amp; sketches →</a></p>
</section>

<script>
const familySel = document.getElementById('familySel');
const sampleInput = document.getElementById('sampleInput');
const specimen = document.getElementById('specimen');
const sizeRange = document.getElementById('sizeRange');
const sizeVal = document.getElementById('sizeVal');
const weightRange = document.getElementById('weightRange');
const weightVal = document.getElementById('weightVal');
const metaLine = document.getElementById('metaLine');
const glyphBar = document.getElementById('glyphBar');
const wfTexts = document.querySelectorAll('.wf-text');
const inkSel = document.getElementById('inkSel');
const customInk = document.getElementById('customInk');
const root = document.documentElement;

function applyInk() {{
  root.dataset.ink = inkSel.value;
  if (inkSel.value === 'custom') root.style.setProperty('--ink', customInk.value);
  else root.style.removeProperty('--ink');
}}

inkSel.addEventListener('change', applyInk);
customInk.addEventListener('input', () => {{
  inkSel.value = 'custom';
  applyInk();
}});
applyInk();

const inventory = {inventory};
const category = document.getElementById('sheetCategory');
const query = document.getElementById('sheetQuery');
function renderGlyphBar(fam, wght) {{
  const codes = inventory.faces[fam];
  const filter = query.value.trim().toUpperCase();
  const fragment = document.createDocumentFragment();
  for (const cp of codes) {{
    const ch = String.fromCodePoint(cp), [title, groups] = inventory.entries[cp];
    const code = 'U+' + cp.toString(16).toUpperCase().padStart(4, '0');
    if (category.value !== 'All characters' && !groups.includes(category.value)) continue;
    if ([...query.value].length === 1 ? ch !== query.value :
        filter && !title.includes(filter) && !code.startsWith(filter)) continue;
    const btn = document.createElement('button');
    btn.type = 'button'; btn.className = 'glyph-btn';
    btn.style.fontFamily = fam; btn.style.fontWeight = wght;
    btn.textContent = groups.includes('Spaces') ? (cp === 32 ? 'SP' : 'NB') : groups.includes('Combining marks') ? 'o' + ch : ch;
    btn.title = code + ' · ' + title;
    btn.setAttribute('aria-label', 'Insert ' + btn.title);
    btn.onclick = () => syncText(sampleInput.value + ch);
    fragment.appendChild(btn);
  }}
  const count = fragment.childElementCount;
  document.getElementById('sheetCount').textContent = count ? count + ' of ' + codes.length + ' characters' : 'No characters match this category and search. Try clearing the search.';
  glyphBar.replaceChildren(fragment);
  glyphBar.scrollTop = 0;
}}
category.addEventListener('change', applyStyle);
query.addEventListener('input', applyStyle);

function syncText(text) {{
  if (specimen.textContent !== text) specimen.textContent = text;
  if (sampleInput.value !== text) sampleInput.value = text;
  wfTexts.forEach(el => el.textContent = text || 'HO0QCESGY');
}}

function applyStyle() {{
  const opt = familySel.selectedOptions[0];
  const fam = opt.value;
  const isVar = fam === 'exp_variable';
  weightRange.disabled = !isVar;
  if (!isVar) {{
    weightRange.value = 700;
    weightVal.textContent = '700';
  }}
  const wght = weightRange.value;
  specimen.style.fontFamily = fam;
  specimen.style.fontWeight = wght;
  wfTexts.forEach(el => {{
    el.style.fontFamily = fam;
    el.style.fontWeight = wght;
  }});
  metaLine.textContent = opt.dataset.meta;
  renderGlyphBar(fam, wght);
}}

familySel.addEventListener('change', applyStyle);
sampleInput.addEventListener('input', e => syncText(e.target.value));
specimen.addEventListener('input', () => syncText(specimen.textContent));
sizeRange.addEventListener('input', e => {{
  sizeVal.textContent = e.target.value;
  specimen.style.fontSize = e.target.value + 'px';
}});
weightRange.addEventListener('input', e => {{
  weightVal.textContent = e.target.value;
  applyStyle();
}});
document.querySelectorAll('.chip[data-text]').forEach(b => b.onclick = () => syncText(b.dataset.text));
document.querySelectorAll('.size-chip').forEach(b => b.onclick = () => {{
  sizeRange.value = b.dataset.size;
  sizeVal.textContent = b.dataset.size;
  specimen.style.fontSize = b.dataset.size + 'px';
}});

applyStyle();
Promise.all(['exp_grid','exp_open','exp_dense','exp_hollow','exp_variable'].map(f => document.fonts.load('700 48px ' + f, 'HO0Q')))
  .then(r => document.getElementById('status').textContent = r.every(x => x.length) ? 'All explorer fonts loaded' : 'FONT LOAD FAILURE');
</script>
</html>
'''
    write_licensed_html(ROOT / 'explorer.html', html)


def build_install() -> None:
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Install · Confinium Mono</title>{appearance_head('')}
<style>body{{background:var(--paper);color:var(--text);font:1rem/1.55 system-ui,sans-serif}}main{{max-width:76ch}}pre{{overflow:auto}}</style>
<script defer src="assets/install.js"></script></head><body>{primary_nav('', 'install')}
<main><h1>Install Confinium Mono</h1>
<p id="release-status" aria-live="polite">Download the font package from GitHub Releases.</p>
<p><a href="https://github.com/Scetrov/confinium-mono/releases">Browse releases, notes and checksums</a>.</p>
<h2>Desktop</h2><p>Unzip <code>ConfiniumMono-Family.zip</code> and open the <code>desktop</code> folder. Choose the variable TTF for Grid weights 100–700, or Full Grid for a dedicated Bold. Full Open, Full Dense and Full Hollow are distinct static cuts, not slider settings. Older variable-only ZIPs omit these four cuts. Remove any older copy before updating.</p>
<ul><li><strong>Windows 10/11:</strong> Right-click the desired TTFs and select Install (under Show more options if needed). Install for all users requires administrator access.</li>
<li><strong>macOS:</strong> Double-click each desired TTF and choose Install in Font Book.</li>
<li><strong>Linux (Fontconfig):</strong> From the root of the extracted package, run:</li></ul>
<pre>mkdir -p ~/.local/share/fonts/confinium-mono
cp desktop/*.ttf ~/.local/share/fonts/confinium-mono/
fc-cache -f ~/.local/share/fonts/confinium-mono</pre>
<p>Reopen your editor or terminal. Select <strong>Confinium Mono Variable Repertoire</strong> and start at weight 400.</p>
<h2>Self-host on the web</h2><p>Copy the desired WOFF2 from <code>web/</code> and the included <code>OFL.txt</code> to your site's fonts folder. Adjust the URL for your deployment:</p>
<pre>@font-face {{
  font-family: "Confinium Mono Web";
  src: url("/fonts/ConfiniumMono-Variable.woff2") format("woff2");
  font-style: normal;
  font-weight: 100 700;
  font-display: swap;
}}
pre, code, kbd, samp {{ font-family: "Confinium Mono Web", monospace; }}</pre>
<p>For a static cut, declare a separate CSS family with its matching WOFF2 (for example <code>ConfiniumMono-FullDense.woff2</code>) and <code>font-weight: 700</code>.</p>
<p>Serve the file as <code>font/woff2</code> and enable CORS if hosting on a different origin. Inspect the rendered font at weights 400 and 700 in browser developer tools.</p>
</main></body></html>'''
    (ROOT / 'install.html').write_text(html, encoding='utf-8')


def build_process() -> None:
    """Generate process.html documenting the full design process and archive links."""
    nav = primary_nav('', 'process')
    html = f'''<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Confinium Mono — Design Process</title>
{appearance_head('')}
<style>
body{{background:var(--paper);color:var(--text);font:16px/1.6 system-ui,sans-serif}}
h1{{margin:0 0 8px;font-size:34px}}
h2{{margin:28px 0 8px;font-size:20px;border-top:1px solid var(--border);padding-top:16px}}
p,li{{max-width:820px;color:var(--secondary)}}
a{{color:var(--accent)}}
.tag{{display:inline-block;font-size:12px;font-weight:600;padding:2px 8px;border:1px solid var(--border);background:var(--panel);color:var(--muted);margin-left:8px;vertical-align:middle}}
</style>
{nav}
<h1>Design Process</h1>
<p>How Confinium Mono developed from an archived 697-unit experiment into the current 800-unit Grid family. The studies show what changed, what was adopted, and what is still under review.</p>
<p><strong>Latest experiment:</strong> <a href="#av-knees">Midline Knees</a> · <strong>Current family review:</strong> <a href="#reading-review">Reading-size proof</a></p>

<h2>1. 697-Unit Variable Experiment <span class="tag">697 advance · 100–700 wght</span></h2>
<p>Tested an upright geometric monospace with 1,000 UPM, 697-unit advance, 700 cap height, 500 x-height, and Thin / Book / Bold masters for <code>H O 0 Q g y c e s</code>.</p>
<ul>
  <li><a href="specimen/index.html">697-Unit Experiment Specimen</a></li>
  <li><a href="sketches/2026-11-20-nine-glyphs-v1.svg">Original v1 Nine-Glyph Sketch (SVG)</a> · <a href="sketches/2026-11-20-nine-glyphs.svg">Updated Nine-Glyph Sketch (SVG)</a></li>
</ul>

<h2>2. Analytic Curve Defect Corrections <span class="tag">c / e / s / g</span></h2>
<p>Visual inspection and curve-continuity checks caught degenerate handles and drifting inner corner centres in <code>c</code>, <code>e</code>, <code>s</code>, and <code>g</code>. Outlines were rebuilt using analytic tangent geometry and affine-compatible construction so tangency holds across interpolated weights.</p>
<ul>
  <li><a href="verification/curves-before.png">Curves Before Correction (PNG)</a> vs <a href="verification/curves-after.png">Curves After Correction (PNG)</a></li>
</ul>

<h2>3. Grid &amp; Token-Driven Bold Direction Study <span class="tag">800 advance · 1u = 80</span></h2>
<p>Explored an 800 × 800 cell with 160-unit vertical stems, 160-unit outer radii, and non-concentric tight inner fillets across three coupled treatments (<code>Grid</code>, <code>Open</code>, <code>Dense</code>) for <code>H O 0 Q C E S G Y</code>.</p>
<ul>
  <li><a href="studies/grid-token-bold/specimen/index.html">Grid / Open / Dense Specimen</a> · <a href="studies/grid-token-bold/specimen/detail.html">Enlarged C/E/S/G Detail</a></li>
  <li>Grid Overlays: <a href="studies/grid-token-bold/specimen/grid-Grid.svg">Grid</a> · <a href="studies/grid-token-bold/specimen/grid-Open.svg">Open</a> · <a href="studies/grid-token-bold/specimen/grid-Dense.svg">Dense</a></li>
</ul>

<h2>4. Right-Descending 45° Q-Tail Direction <span class="tag">Q45 comparison</span></h2>
<p>Evaluated replacing the centred vertical Q tail with a 45° right-descending tail ending at <code>y = −120</code> with a horizontal cut. The proof pairs the archived diagonal with a centred-tail reconstruction on the same bowl; the original centred binary is not in the repository’s history.</p>
<ul>
  <li><a href="studies/grid-token-bold/q-tail/index.html">Centred vs 45° Right-Descending Q-Tail</a></li>
</ul>

<h2>5. Optical Diagonal Thickness &amp; Baseline Promotion <span class="tag">Q = 128 · Y = 144</span></h2>
<p>Compared 128, 144, and 160 normal units for the 45° Q tail and Y arms against the lighter reference. Selected <strong>Q = 128</strong> and <strong>Y = 144</strong> independently and promoted both to the Grid &amp; Token-Driven Bold baseline.</p>
<ul>
  <li><a href="studies/grid-token-bold/diagonals/index.html">Optical Diagonals Comparison (128 / 144 / 160)</a> · <a href="studies/grid-token-bold/diagonals/detail.html">Enlarged O/Q/H/Y Detail</a></li>
  <li>Grid Overlays: <a href="studies/grid-token-bold/diagonals/grid-128.svg">128</a> · <a href="studies/grid-token-bold/diagonals/grid-144.svg">144</a> · <a href="studies/grid-token-bold/diagonals/grid-160.svg">160</a></li>
</ul>

<h2>6. ASCII Punctuation <span class="tag">Grid Bold · 32 additions</span></h2>
<p>Added all printable ASCII punctuation and operators in a separate Grid Bold build. The study proofs them in code and paths at 12, 16, and 28 px without changing the baseline.</p>
<ul>
  <li><a href="studies/grid-token-bold/punctuation/index.html">Open Punctuation Study</a></li>
</ul>
<h2>7. From Uppercase to Mixed Text <span class="tag">95 printable ASCII characters</span></h2>
<p>Built a lowercase alphabet with a 560-unit x-height, then combined it with the figures and punctuation to proof code and mixed-case text in the same 800-unit cell.</p>
<ul>
  <li><a href="studies/grid-token-bold/lowercase/index.html">Lowercase foundations</a> · <a href="studies/grid-token-bold/lowercase-alphabet/index.html">Full lowercase alphabet</a> · <a href="studies/grid-token-bold/mixed-text/index.html">Mixed-text proof</a></li>
</ul>
<h2>8. European Latin and East Slavic Cyrillic</h2>
<p>Extended coverage to European Latin and the modern Russian, Ukrainian, and Belarusian alphabets. Above-cap marks needed taller line metrics; supported combining marks keep zero advance.</p>
<ul>
  <li><a href="studies/grid-token-bold/european-latin/index.html">European Latin proof</a> · <a href="studies/grid-token-bold/cyrillic/index.html">East Slavic Cyrillic proof</a></li>
</ul>
<h2>9. Full Grid Family <span class="tag">416 mapped characters</span></h2>
<p>Grid, Open, Dense, and Hollow share the expanded repertoire. The 800-unit variable font covers weights 100–700 and matches Full Grid at Bold. Thin and Book are generated constructions, not independently refined masters.</p>
<ul>
  <li><a href="studies/grid-token-bold/full-family/verification/styles.png">Four static styles</a> · <a href="studies/variable-repertoire/verification/full-grid-weights.png">Variable weight comparison</a> · <a href="index.html">Try the current family</a></li>
</ul>
<h2 id="reading-review">10. Reading-Size Review <span class="tag">12–18 px · Thin / Book / Bold</span></h2>
<p>Compared code and mixed Latin/Cyrillic text in light and dark. The first priorities are distinguishing <code>O</code> from <code>0</code> in Book and making Thin punctuation read more evenly.</p>
<ul>
  <li><a href="studies/variable-repertoire/reading-proof.html">Reading-size proof</a></li>
</ul>
<h2 id="av-knees">11. Midline Knees <span class="tag">Isolated Grid Bold experiment</span></h2>
<p>Tested whether <code>A</code> and <code>V</code> would feel more at home on the grid if their diagonals started at the midline. A keeps vertical lower legs; V keeps vertical upper arms. The 800-unit advance and sidebearings are unchanged. The 152-unit follow-up replaces flared joins with parallel inner diagonals that meet the vertical walls directly: above the midline in V, below it in A. A’s crossbar moves down to clear the join. W adds the same direct join at a narrower 128-unit stroke to keep its two valleys open. The approved straight joins for A, V, W, v and the fuller-arm w are now in the full family, including accented forms and the shared Cyrillic А. Y retains its earlier approved construction.</p>
<ul>
  <li><a href="studies/grid-token-bold/av-knees/index.html">Compare Grid, straight A/V, and straight A/V/W</a> · <a href="studies/grid-token-bold/av-knees/chromium-fuller.png">Fuller-join capture</a> · <a href="studies/grid-token-bold/av-knees/chromium-straight-v.png">Straight V capture</a> · <a href="studies/grid-token-bold/av-knees/chromium-straight-av.png">Straight A/V capture</a> · <a href="studies/grid-token-bold/av-knees/chromium-straight-avw.png">Straight A/V/W capture</a> · <a href="studies/grid-token-bold/av-knees/chromium.png">Original capture</a></li>
  <li><a href="studies/grid-token-bold/av-knees/index.html#lowercase">Compare lowercase v and w</a> · <a href="studies/grid-token-bold/av-knees/chromium-straight-vw-lowercase.png">Lowercase capture</a></li>
  <li><a href="studies/grid-token-bold/av-knees/book.html">Archived Book comparison: w versus vv and accented forms</a> · <a href="studies/grid-token-bold/full-family/index.html">Promoted full-family proof</a></li>
</ul>
</html>
'''
    write_licensed_html(ROOT / 'process.html', html)


def verify() -> None:
    """Verify the home and explorer fonts load in headless Chromium."""
    capture_chromium(ROOT / 'index.html', ROOT / 'verification/site-home.png',
                     '1440,1500', 'data-font-ready=""')
    capture_chromium(ROOT / 'explorer.html', ROOT / 'verification/site-explorer.png',
                     '1440,1200', '<p id="status">All explorer fonts loaded</p>')
    print('Generated home, explorer and process pages; Chromium font loads verified.')


if __name__ == '__main__':
    build_home()
    build_explorer()
    build_process()
    build_install()
    verify()
