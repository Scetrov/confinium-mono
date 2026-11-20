"""Controlled normal-thickness study for the grid- and token-driven Q45 tail and Y arms.

Draw overwrites only this study's UFOs. Build never redraws editable sources.
Proof embeds the existing reference and three alternatives; no font fallback.
"""
import base64
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from booleanOperations.booleanGlyph import BooleanGlyph
from fontTools.svgLib.path import parse_path
from fontTools.pens.svgPathPen import SVGPathPen
from ufoLib2 import Font
from grid_token_study import STUDY, CONFIG, polygon, reverse, shapes
from font_license import apply_ufo_license, write_licensed_html
from web import NAV_CSS, primary_nav

OUT=STUDY/'diagonals'
PARAMS=OUT/'parameters.json'


def config(): return json.loads(PARAMS.read_text())
def source(t): return OUT/f'sources/ConfiniumMono-Diagonal{t}.ufo'
def binary(t): return OUT/f'fonts/ConfiniumMono-Diagonal{t}.ttf'


def outlines(t):
    p=config(); base=json.loads(CONFIG.read_text())
    assert p['angle_degrees']==45 and p['junction_taper']==0
    # x+y=constant for each long edge; their normal separation is t.
    half=t/math.sqrt(2); centre=p['q_centerline_x_plus_y']
    top,bottom=p['q_top'],p['q_bottom']
    tail=polygon([(centre-top-half,top),(centre-top+half,top),
                  (centre-bottom+half,bottom),(centre-bottom-half,bottom)])
    q=shapes(base)['O']+' '+reverse(tail)
    # Hold the Y's outside silhouette and its 160-unit stem fixed. Move only
    # the inside edges, parallel to the outside at true normal distance t.
    l,r=base['active_left'],base['active_right']; v=base['vertical_stem']
    mid=base['advance']/2; drop=p['y_outer_drop_y']; join=p['y_stem_join_y']
    inner_intercept=p['y_outer_left_intercept']+t*math.sqrt(2)
    inner_drop=inner_intercept-(l+v); notch=inner_intercept-mid
    y=polygon([(l,800),(l+v,800),(l+v,inner_drop),(mid,notch),
               (r-v,inner_drop),(r-v,800),(r,800),(r,drop),
               (mid+v/2,join),(mid+v/2,0),(mid-v/2,0),
               (mid-v/2,join),(l,drop)])
    return {'Q':q,'Y':y}


def draw():
    (OUT/'sources').mkdir(exist_ok=True)
    for t in config()['normal_thicknesses']:
        font=Font.open(STUDY/'sources/ConfiniumMono-GridToken-Grid.ufo')
        font.info.familyName='Confinium Mono'; font.info.styleName=f'Grid-Token Diagonal {t} Bold'
        font.info.openTypeNameDescription=f'Confinium Mono optical comparison: Q and Y diagonal normal thickness {t}, 45 degrees, no junction taper.'
        for name,path in outlines(t).items():
            glyph=font[name]; glyph.clearContours(); parse_path(path,glyph.getPen())
            union=BooleanGlyph(glyph).removeOverlap(); glyph.clearContours(); union.draw(glyph.getPen())
        apply_ufo_license(font.info)
        font.save(source(t),overwrite=True)
        svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1080"><title>Confinium Mono diagonal '+str(t)+' normal units</title><rect width="1600" height="1080" fill="#faf8f2"/>']
        for i,name in enumerate(['Q','Y']):
            pen=SVGPathPen(font); font[name].draw(pen)
            svg.append(f'<g transform="translate({i*800},880) scale(1,-1)"><path d="{pen.getCommands()}" fill="#172426"/>')
            for n in range(11):
                svg.append(f'<path d="M {n*80},-160 V 880 M 0,{n*80} H 800" fill="none" stroke="#398b8b" stroke-width="1.2" opacity=".5"/>')
            svg.append('<path d="M 80,0 H 720 V 800 H 80 Z" fill="none" stroke="#c76b3d" stroke-width="2" stroke-dasharray="8 8"/></g>')
        (OUT/f'grid-{t}.svg').write_text(''.join(svg)+'</svg>')
    print('Drew three isolated Q/Y variants; all reference fonts and sources unchanged.')


def build():
    (OUT/'fonts').mkdir(exist_ok=True)
    os.environ.setdefault('SOURCE_DATE_EPOCH','1795132800')
    for t in config()['normal_thicknesses']:
        subprocess.run([sys.executable,'-m','fontmake','-u',str(source(t)),'-o','ttf','--output-path',str(binary(t))],check=True)


def proof():
    variants=[('reference','Current reference',STUDY/'q-tail/ConfiniumMono-GridToken-Q45.ttf','Q ≈96 / Y ≈113 normal units')]
    variants += [(f'diag{t}',str(t)+' normal units',binary(t),'Q and Y: same measured diagonal thickness') for t in config()['normal_thicknesses']]
    css=''; cards=''; detail=''
    for key,label,path,note in variants:
        data=base64.b64encode(path.read_bytes()).decode()
        css+=f'@font-face{{font-family:{key};src:url(data:font/ttf;base64,{data});font-weight:700}}'
        samples=''.join(f'<div class="sample" style="font-family:{key};font-size:{size}px">QYQY HY</div>' for size in [14,18,32,64])
        grid='' if key=='reference' else f'<p><a href="grid-{key[4:]}.svg">Grid overlay</a></p>'
        cards+=f'<article><h2>{label}</h2><p class="note">{note}</p><div class="sample hero" style="font-family:{key}">QY</div><div class="sample" style="font-family:{key};font-size:64px">HOQY</div>{samples}{grid}</article>'
        detail+=f'<section><h2>{label}</h2><div class="sample" style="font-family:{key};font-size:320px">OQHY</div></section>'
    nav=primary_nav('../../../','diagonals')
    style=css+NAV_CSS+'''body{margin:30px;background:#faf8f2;color:#172426;font:16px/1.5 system-ui}h1{font-size:30px}h2{font-size:17px;font-weight:600}.intro{max-width:1100px}.cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:20px}.cards article,section{border-top:1px solid #bbc9c0;padding-top:12px}.sample{font-weight:700;white-space:pre;letter-spacing:0;font-kerning:none;font-synthesis:none;line-height:1.4;margin:14px 0;overflow:auto}.hero{font-size:180px}.note{min-height:48px;font-size:13px;color:#586d67}a{color:inherit}#status{color:#23695c}@media(max-width:1100px){.cards{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:550px){.cards{grid-template-columns:1fr}}'''
    intro=nav+'''<h1>Confinium Mono / optical diagonal thickness</h1><p class="intro">Reference versus 128 / 144 / 160 units, measured perpendicular to the diagonal. Q tails and Y arms remain at 45°. The Q bowl, counter, other glyphs and 800-unit advances are unchanged. Grid stems remain 160 units.</p><p class="intro">Q keeps its tail centreline, −120 depth and horizontal cut. Added width extends right of the active box but stays inside the cell. Y keeps its outer silhouette and lower stem; its inner edges move to change thickness. No junction taper yet: compare thickness before tuning the join.</p><p><a href="detail.html">Enlarged O/Q/H/Y proofs</a> · <a href="../q-tail/">Previous tail comparison</a> · <a href="../specimen/">Grid- and token-driven study</a></p>'''
    loader='''<script>Promise.all(['reference','diag128','diag144','diag160'].map(f=>document.fonts.load('700 180px '+f,'OQHY'))).then(r=>document.querySelector('#status').textContent=r.every(f=>f.length)?'All four comparison fonts loaded':'FONT FAILURE')</script>'''
    for filename,body in [('index.html','<div class="cards">'+cards+'</div>'),('detail.html',detail)]:
        write_licensed_html(OUT/filename, '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Confinium Mono / optical diagonal study</title><style>'+style+'</style>'+intro+'<p id="status">Loading…</p>'+body+loader+'</html>')
    with tempfile.TemporaryDirectory(prefix='confinium-diagonals-') as profile:
        for page,size in [('index','1600,1100'),('detail','1400,2500')]:
            run=subprocess.run(['chromium','--headless','--disable-gpu','--no-first-run',f'--user-data-dir={profile}','--virtual-time-budget=3000',f'--window-size={size}',f'--screenshot={OUT / (page+".png")}', '--dump-dom',(OUT/(page+'.html')).as_uri()],check=True,capture_output=True,text=True)
            assert '<p id="status">All four comparison fonts loaded</p>' in run.stdout
    print('Rendered reference and three thicknesses in Chromium; all font loads verified.')

if __name__=='__main__':
    if len(sys.argv)!=2 or sys.argv[1] not in ('draw','build','proof'): raise SystemExit('Usage: diagonal_study.py draw|build|proof')
    globals()[sys.argv[1]]()
