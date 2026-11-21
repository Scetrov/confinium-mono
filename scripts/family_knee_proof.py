"""Render the approved Midline Knees promotion across the current full family."""
import argparse
from html import escape

from chromium_proof import capture_chromium
from font_license import write_licensed_html
from full_grid_family import GRID, STYLES
from variable_repertoire import BINARY
from web import _b64, appearance_head, primary_nav

OUT = GRID / 'full-family'
SAMPLE = 'AVW ÁĄ Ŵ · Vv Ww ŵẅ · vv w wave weave · QY · А'
STATUS = 'All five family fonts and the site title font loaded.'


def proof():
    definitions, cards = [], []
    faces = [(style, OUT / f'fonts/ConfiniumMono-Full{style}.ttf', 700) for style in STYLES]
    faces.append(('Book', BINARY, 400))
    text = escape(SAMPLE)
    for name, path, weight in faces:
        definitions.append(f'@font-face{{font-family:proof{name};src:url(data:font/ttf;base64,{_b64(path)});font-weight:{weight}}}')
        cards.append(f'<section><h2>{"Variable · Book 400" if name == "Book" else name + " · Bold"}</h2>'
                     f'<div class="sample" style="font-family:proof{name};font-weight:{weight}">{text}</div></section>')
    loads = ','.join(f'document.fonts.load("{weight} 28px proof{name}", {SAMPLE!r})' for name, _, weight in faces)
    write_licensed_html(OUT / 'index.html', f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Confinium Mono · Full Family Proof</title>{appearance_head('../../../')}
<style>{''.join(definitions)}
body{{background:var(--paper);color:var(--text);font:16px/1.5 system-ui,sans-serif}}
h2{{font-size:17px;margin:.35rem 0}} a{{color:var(--accent)}}
section{{border-top:1px solid var(--border);padding:.45rem 0 .8rem}}
.sample{{font-size:28px;white-space:pre;overflow:auto;font-synthesis:none}}
html:not([data-font-ready]) .sample{{visibility:hidden}}
</style></head><body>{primary_nav('../../../', '')}
<main><h1>Full Family Proof</h1><p>The approved Midline Knees outlines, accented forms, Cyrillic А, and the earlier Q and Y decisions.</p>
<p><a href="../av-knees/book.html">Open the archived Book comparison</a></p>
<p id="status" role="status">Loading fonts…</p>{''.join(cards)}</main>
<script>
const heading = document.querySelector('h1');
const title = getComputedStyle(heading).fontFamily;
const fonts = [{loads}];
fonts.push(title.includes('Confinium Site Titles') ? document.fonts.load('700 28px "Confinium Site Titles"', heading.textContent) : Promise.resolve([]));
Promise.all(fonts).then(results => {{
 if (!results.every(f => f.length && f.every(x => x.status === 'loaded'))) throw new Error();
 document.documentElement.dataset.fontReady = '';
 document.querySelector('#status').textContent = '{STATUS}';
}}).catch(() => {{ document.querySelector('#status').textContent = 'Proof font load failed.'; }});
</script></body></html>''')


def capture():
    capture_chromium(OUT / 'index.html', OUT / 'verification/midline-knees-family.png', '1280,900', STATUS)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('proof', 'capture'))
    globals()[parser.parse_args().command]()
