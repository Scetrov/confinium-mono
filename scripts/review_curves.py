"""Capture the actual variable font in headless Chromium, without a font cache.
Usage: uv run python scripts/review_curves.py after
Render the revised font from a temporary embedded-font page. Never replace the
historical before/after captures.
"""
import base64
from pathlib import Path
import sys
import tempfile

from chromium_proof import capture_chromium

ROOT = Path(__file__).resolve().parents[1]

def main():
    if sys.argv[1:] != ['after']:
        raise SystemExit('Usage: review_curves.py after (the before font is not available)')
    phase = 'after'
    font = base64.b64encode((ROOT/'fonts/ConfiniumMono[wght].ttf').read_bytes()).decode()
    rows = ''.join(f'<section><label>{w}</label><div class="glyphs" style="font-weight:{w}">sceg</div></section>' for w in (100, 400, 700))
    small = ''.join(f'<div><label>{w}</label>'+''.join(f'<span class="small" style="font-size:{px}px;font-weight:{w}">sceg cese egg </span>' for px in (14, 18, 32))+'</div>' for w in range(100,701,100))
    html = f'''<!doctype html><meta charset="utf-8"><title>Confinium Mono curve review — {phase}</title>
<style>@font-face{{font-family:'Confinium Mono';src:url(data:font/ttf;base64,{font});font-weight:100 700}}body{{background:#faf8f2;color:#172426;margin:30px;font:14px system-ui}}section{{display:flex;align-items:center;border-bottom:1px solid #ddd}}label{{display:inline-block;width:65px;color:#65736c}}.glyphs,.small{{font-family:'Confinium Mono';font-synthesis:none;font-kerning:none;letter-spacing:0}}.glyphs{{font-size:360px;line-height:1.127}}.small{{display:inline-block;margin:12px 28px 12px 0}}#status{{font-size:12px}}</style>
<h1>Confinium Mono / curves / {phase}</h1>{rows}<h2>14 / 18 / 32 px</h2>{small}<p id="status">Loading</p>
<script>document.fonts.load('400 360px "Confinium Mono"','sceg').then(f=>document.getElementById('status').textContent=f.length?'FONT LOADED':'FONT FAILED')</script>'''
    out = ROOT/'verification'; out.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='confinium-curves-') as tmp:
        page = Path(tmp) / 'curves-after.html'
        page.write_text(html)
        capture_chromium(page, out / 'curves-after.png', '1200,1820',
                         '<p id="status">FONT LOADED</p>')
if __name__ == '__main__': main()
