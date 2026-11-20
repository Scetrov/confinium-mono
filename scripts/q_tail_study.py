"""Isolated Q-tail comparison on the grid- and token-driven Grid bowl; no baseline changes.
Run draw, build, proof separately to preserve manual UFO edits during builds.
"""
import base64
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from ufoLib2 import Font
from booleanOperations.booleanGlyph import BooleanGlyph
from fontTools.svgLib.path import parse_path
from grid_token_study import STUDY, CONFIG, shapes, polygon, reverse
from font_license import apply_ufo_license, write_licensed_html
from web import NAV_CSS, primary_nav
import json

OUT=STUDY/'q-tail'
SOURCE=OUT/'ConfiniumMono-GridToken-Q45.ufo'
FONT=OUT/'ConfiniumMono-GridToken-Q45.ttf'


def draw():
    OUT.mkdir(exist_ok=True)
    p=json.loads(CONFIG.read_text())
    font=Font.open(STUDY/'sources/ConfiniumMono-GridToken-Grid.ufo')
    font.info.styleName='Grid-Token Q45 Bold'
    font.info.openTypeNameDescription='Confinium Mono grid- and token-driven Q-tail direction study: descending right at 45 degrees.'
    q=font['Q']; q.clearContours()
    # Horizontal end cuts; the long edges have slope -1 exactly. The tail
    # starts within the bottom bar, below the counter, and ends at x=720.
    # Its 136-unit horizontal section gives 96.17 units normal thickness.
    width=p['tail_width']; depth=p['tail_depth']; top=120
    right=p['active_right']
    tail=polygon([(right-width-depth-top,top),(right-depth-top,top),
                  (right,-depth),(right-width,-depth)])
    parse_path(shapes(p)['O']+' '+reverse(tail),q.getPen())
    union=BooleanGlyph(q).removeOverlap(); q.clearContours(); union.draw(q.getPen())
    apply_ufo_license(font.info)
    font.save(SOURCE,overwrite=True)
    print('Drew isolated Q45 UFO; baseline Grid and original pilot untouched.')


def build():
    os.environ.setdefault('SOURCE_DATE_EPOCH','1795132800')
    subprocess.run([sys.executable,'-m','fontmake','-u',str(SOURCE),'-o','ttf','--output-path',str(FONT)],check=True)


def proof():
    css=''; rows=''
    for key,label,path in [('centred','Existing centred tail',STUDY/'fonts/ConfiniumMono-GridToken-Grid.ttf'),('diagonal','Right-descending 45° tail',FONT)]:
        data=base64.b64encode(path.read_bytes()).decode()
        css+=f'@font-face{{font-family:{key};src:url(data:font/ttf;base64,{data});font-weight:700}}'
        rows+=f'<section><h2>{label}</h2><div class="big" style="font-family:{key}">OQ0Q</div><div class="small" style="font-family:{key}">'+''.join(f'<div style="font-size:{size}px">QOQO 0Q0Q QQQQ</div>' for size in [14,18,32,64])+'</div></section>'
    nav=primary_nav('../../../','q-tail')
    page=OUT/'index.html'
    write_licensed_html(page, '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Confinium Mono / Q tail study</title><style>'''+css+NAV_CSS+'''body{margin:32px;background:#faf8f2;color:#172426;font:16px/1.5 system-ui}h1{font-size:30px}h2{font-size:16px;font-weight:500}section{border-top:1px solid #bbc9c0;margin-top:20px}.big{font-size:clamp(64px,20vw,300px);line-height:1.2}.big,.small{font-weight:700;font-synthesis:none;letter-spacing:0;font-kerning:none;white-space:pre}.small div{margin:8px 0}p{max-width:1050px}a{color:inherit}</style>'''+nav+'''<h1>Confinium Mono / Q tail direction</h1><p>Same Grid bowl, clear counter and 800-unit cell. Top: centred reference. Bottom: right-descending 45° alternative, with a horizontal end cut at −120. Tail stays within x=720. No other glyph changes.</p><p>The diagonal has a 136-unit horizontal section (96.17 units perpendicular to the stroke), intentionally lighter than the centred tail to avoid a heavy attachment. This is a direction comparison, not a controlled equal-ink comparison.</p><p><a href="../diagonals/">New: optical Q/Y thickness comparison</a> · <a href="../specimen/">Back to grid- and token-driven study</a></p><p id="status">Loading…</p>'''+rows+'''<script>Promise.all(['centred','diagonal'].map(f=>document.fonts.load('700 300px '+f,'OQ0Q'))).then(r=>document.querySelector('#status').textContent=r.every(f=>f.length)?'Both fonts loaded':'FONT FAILURE')</script></html>''')
    with tempfile.TemporaryDirectory(prefix='confinium-q45-') as profile:
        run=subprocess.run(['chromium','--headless','--disable-gpu','--no-first-run',f'--user-data-dir={profile}','--virtual-time-budget=3000','--window-size=1300,1600',f'--screenshot={OUT / "chromium.png"}','--dump-dom',page.as_uri()],check=True,capture_output=True,text=True)
        assert '<p id="status">Both fonts loaded</p>' in run.stdout
    print('Captured centred versus Q45 in Chromium; both font loads verified.')

if __name__=='__main__':
    if len(sys.argv)!=2 or sys.argv[1] not in ('draw','build','proof'): raise SystemExit('Usage: q_tail_study.py draw|build|proof')
    globals()[sys.argv[1]]()
