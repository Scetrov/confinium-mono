"""Isolated Q-tail comparison on the grid- and token-driven Grid bowl; no baseline changes.
Run draw, build, proof separately to preserve manual UFO edits during builds.
"""
import base64
import os
import subprocess
import sys
import tempfile
from ufoLib2 import Font
from booleanOperations.booleanGlyph import BooleanGlyph
from fontTools.svgLib.path import parse_path
from grid_token_study import STUDY, polygon, reverse
from chromium_proof import capture_chromium
from font_license import apply_ufo_license, write_licensed_html
from web import appearance_head, primary_nav

OUT=STUDY/'q-tail'
SOURCE=OUT/'ConfiniumMono-GridToken-Q45.ufo'
FONT=OUT/'ConfiniumMono-GridToken-Q45.ttf'


CENTRED = OUT/'ConfiniumMono-GridToken-QCentred.ttf'


def replace_tail(font, points):
    q = font['Q']
    q.clearContours()
    font['O'].draw(q.getPen())
    parse_path(reverse(polygon(points)), q.getPen())
    union = BooleanGlyph(q).removeOverlap()
    q.clearContours()
    union.draw(q.getPen())
    apply_ufo_license(font.info)


def draw():
    # Redraw only Q from the study's own archived bowl, not the expanded Grid.
    font = Font.open(SOURCE)
    replace_tail(font, [(344, 120), (480, 120), (720, -120), (584, -120)])
    font.save(SOURCE, overwrite=True)


def compile_source(source, target):
    os.environ.setdefault('SOURCE_DATE_EPOCH', '1795132800')
    subprocess.run([sys.executable, '-m', 'fontmake', '-u', str(source), '-o', 'ttf',
                    '--output-path', str(target)], check=True)


def build():
    compile_source(SOURCE, FONT)


def reconstruct():
    # No pre-promotion binary is in Git. Reconstruct a 2u centred tail on
    # the exact archived bowl, keeping all non-Q comparison glyphs intact.
    font = Font.open(SOURCE)
    font.info.styleName = 'Grid-Token Q Centred Reconstruction Bold'
    font.info.openTypeNameDescription = 'Reconstruction of the centred Grid Q for historical comparison.'
    replace_tail(font, [(320, 120), (480, 120), (480, -120), (320, -120)])
    with tempfile.TemporaryDirectory(prefix='confinium-centred-') as tmp:
        source = CENTRED.with_suffix('.ufo').name
        source = os.path.join(tmp, source)
        font.save(source)
        compile_source(source, CENTRED)


def proof():
    css=''; rows=''
    for key,label,path in [('centred','Centred tail (reconstructed)',CENTRED),('diagonal','Right-descending 45° tail',FONT)]:
        data=base64.b64encode(path.read_bytes()).decode()
        css+=f'@font-face{{font-family:{key};src:url(data:font/ttf;base64,{data});font-weight:700}}'
        rows+=f'<section><h2>{label}</h2><div class="big" style="font-family:{key}">OQ0Q</div><div class="small" style="font-family:{key}">'+''.join(f'<div style="font-size:{size}px">QOQO 0Q0Q QQQQ</div>' for size in [14,18,32,64])+'</div></section>'
    nav=primary_nav('../../../','q-tail')
    page=OUT/'index.html'
    write_licensed_html(page, '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Confinium Mono / Q tail study</title>'''+appearance_head('../../../')+'''<style>'''+css+'''body{background:var(--paper);color:var(--text);font:16px/1.5 system-ui}h1{font-size:30px}h2{font-size:16px;font-weight:500}section{border-top:1px solid var(--border);margin-top:20px}.big,.small{overflow-x:auto}.big{font-size:clamp(64px,20vw,300px);line-height:1.2}.big,.small{font-weight:700;font-synthesis:none;letter-spacing:0;font-kerning:none;white-space:pre}.small div{margin:8px 0}p{max-width:1050px}a{color:inherit}</style>'''+nav+'''<h1>Confinium Mono / Q tail direction</h1><p>Same Grid bowl, clear counter and 800-unit cell. Top: centred reference reconstructed on the archived bowl (original binary unavailable). Bottom: right-descending 45° alternative, with a horizontal end cut at −120. Tail stays within x=720. No other glyph changes.</p><p>The diagonal has a 136-unit horizontal section (96.17 units perpendicular to the stroke), intentionally lighter than the centred tail to avoid a heavy attachment. This is a direction comparison, not a controlled equal-ink comparison.</p><p><a href="../diagonals/">New: optical Q/Y thickness comparison</a> · <a href="../specimen/">Back to grid- and token-driven study</a></p><p id="status">Loading…</p>'''+rows+'''<script>Promise.all(['centred','diagonal'].map(f=>document.fonts.load('700 300px '+f,'OQ0Q'))).then(r=>document.querySelector('#status').textContent=r.every(f=>f.length)?'Both fonts loaded':'FONT FAILURE')</script></html>''')


def capture():
    page = OUT/'index.html'
    capture_chromium(page, OUT / 'chromium-restored.png', '1300,1700',
                     '<p id="status">Both fonts loaded</p>')
    print('Captured centred versus Q45 in Chromium; both font loads verified.')

if __name__=='__main__':
    if len(sys.argv)!=2 or sys.argv[1] not in ('draw','build','reconstruct','proof','capture'): raise SystemExit('Usage: q_tail_study.py draw|build|reconstruct|proof|capture')
    globals()[sys.argv[1]]()
