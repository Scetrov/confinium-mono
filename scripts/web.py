"""Static website generator for Confinium Mono: root explorer, design process, and shared primary nav."""
import base64
from html import escape
import json
import unicodedata
from fontTools.ttLib import TTFont
from pathlib import Path
from font_license import write_licensed_html
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def appearance_head(root_rel: str) -> str:
    """Load the shared theme before rendering any page content."""
    return (f'<script src="{root_rel}assets/appearance.js"></script>'
            f'<link rel="stylesheet" href="{root_rel}assets/appearance.css">')


def primary_nav(root_rel: str, active: str) -> str:
    """Return shared primary navigation HTML with relative links from root_rel."""
    links = [
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
        ('pilot', 'Variable Pilot', f'{root_rel}specimen/index.html'),
        ('process', 'Design Process', f'{root_rel}process.html'),
    ]
    def link(key, label, href):
        state = ' class="active" aria-current="page"' if active == key else ''
        return f'<a href="{href}"{state}>{label}</a>'

    explorer = link('explorer', 'Explorer', f'{root_rel}index.html')
    items = ''.join(link(*item) for item in links)
    section = ' class="active"' if active != 'explorer' else ''
    return (
        '<nav class="site-nav" aria-label="Primary">'
        f'<a class="brand" href="{root_rel}index.html">Confinium Mono</a>'
        f'<div class="nav-center">{explorer}<details><summary{section}>Studies</summary>'
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


def build_explorer() -> None:
    """Generate root index.html interactive explorer."""
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
body{{margin:32px auto;max-width:1240px;padding:0 24px;background:var(--paper);color:var(--text);font:16px/1.5 system-ui,sans-serif}}
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
:root{{--ink:var(--text)}}
[data-ink="red"]{{--ink:light-dark(#a52736,#ff8f98)}}
[data-ink="orange"]{{--ink:light-dark(#9a4114,#ffad79)}}
[data-ink="yellow"]{{--ink:light-dark(#775900,#f8d66c)}}
[data-ink="green"]{{--ink:light-dark(#21633c,#8dd8a5)}}
[data-ink="blue"]{{--ink:light-dark(#2059a0,#92bfff)}}
[data-ink="purple"]{{--ink:light-dark(#703f9e,#caa7fa)}}
.specimen,.wf-text,.glyph-btn{{color:var(--ink)}}
.appearance{{display:flex;flex-wrap:wrap;align-items:end;gap:12px 20px;margin:0 0 24px}}
.appearance input[type=color]{{display:block;width:4rem;height:2.2rem;cursor:pointer}}
.specimen:focus-visible{{outline:2px solid var(--accent);outline-offset:3px}}
</style>
{nav}
<h1>Confinium Mono Explorer</h1>
<p class="lead">Original geometric monospace typeface under active development. Explore European Latin, Cyrillic, figures and symbols in Grid, Open, Dense and Hollow. Confinium Mono Variable covers the same characters at weights 100–700. All glyph previews use embedded Confinium Mono binaries.</p>
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
      <button class="chip" type="button" data-text="O0O0 1I1I 2Z2Z 5S5S 8B8B QO0Q">Pairs</button>
      <button class="chip" type="button" data-text="HO0Qgyces">Pilot 9</button>
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
    <input id="customInk" type="color" value="#23695c">
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
      <h3>1. Variable Pilot (9 glyphs)</h3>
      <p>697-unit advance, 700 cap height, Thin/Book/Bold masters (100–700) for HO0Qgyces, plus analytic curve fixes.</p>
      <a href="specimen/index.html">Open Variable Pilot →</a>
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
    write_licensed_html(ROOT / 'index.html', html)


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
body{{margin:32px auto;max-width:980px;padding:0 24px;background:var(--paper);color:var(--text);font:16px/1.6 system-ui,sans-serif}}
h1{{margin:0 0 8px;font-size:34px}}
h2{{margin:28px 0 8px;font-size:20px;border-top:1px solid var(--border);padding-top:16px}}
p,li{{max-width:820px;color:var(--secondary)}}
a{{color:var(--accent)}}
.tag{{display:inline-block;font-size:12px;font-weight:600;padding:2px 8px;border:1px solid var(--border);background:var(--panel);color:var(--muted);margin-left:8px;vertical-align:middle}}
</style>
{nav}
<h1>Design Process</h1>
<p>Chronological record of Confinium Mono’s original outline studies, curve-geometry corrections, and optical parameter decisions. All studies remain preserved and reproducible from blank-source UFOs.</p>

<h2>1. Variable Pilot (9 Glyphs) <span class="tag">697 advance · 100–700 wght</span></h2>
<p>Established an upright geometric monospace with 1,000 UPM, 697-unit advance, 700 cap height, 500 x-height, and Thin / Book / Bold masters for <code>H O 0 Q g y c e s</code>.</p>
<ul>
  <li><a href="specimen/index.html">Variable Pilot Specimen</a></li>
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
<p>Evaluated replacing the centred vertical Q tail with a 45° right-descending tail ending at <code>y = −120</code> with a horizontal cut, resolving a boolean winding cancellation at the bowl attachment.</p>
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
</html>
'''
    write_licensed_html(ROOT / 'process.html', html)


def verify() -> None:
    """Verify root explorer fonts load in headless Chromium."""
    with tempfile.TemporaryDirectory(prefix='confinium-site-') as profile:
        run = subprocess.run(
            [
                'chromium', '--headless', '--disable-gpu', '--no-first-run',
                f'--user-data-dir={profile}', '--virtual-time-budget=3000',
                '--window-size=1440,1200',
                f'--screenshot={ROOT / "verification/site-explorer.png"}',
                '--dump-dom', (ROOT / 'index.html').as_uri(),
            ],
            check=True, capture_output=True, text=True,
        )
        assert '<p id="status">All explorer fonts loaded</p>' in run.stdout
    print('Generated root index.html and process.html; Chromium font load verified.')


if __name__ == '__main__':
    build_explorer()
    build_process()
    verify()
