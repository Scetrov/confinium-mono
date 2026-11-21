"""Isolated, original grid- and token-driven Bold study. Does not alter the nine-glyph experiment.

Draw: regenerate editable UFOs + grid SVGs. Build: compile existing UFOs only.
Proof: capture embedded-font study in Chromium. See study README.
"""
import base64
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from fontTools.svgLib.path import parse_path
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from ufoLib2 import Font
from booleanOperations.booleanGlyph import BooleanGlyph
from chromium_proof import capture_chromium
from font_license import apply_ufo_license, write_licensed_html
from web import appearance_head, primary_nav

ROOT=Path(__file__).resolve().parents[1]
STUDY=ROOT/'studies/grid-token-bold'
CONFIG=STUDY/'parameters.json'


def polygon(points, radii=None):
    """Tangent circular fillets on orthogonal polygon vertices; sharp diagonals.

    Radius is explicit per corner. A cap stays a cap, not an implicit fillet.
    """
    radii=radii or {}
    corners=[]
    for i,p in enumerate(points):
        prev,nxt=points[i-1],points[(i+1)%len(points)]
        a=(prev[0]-p[0],prev[1]-p[1]); b=(nxt[0]-p[0],nxt[1]-p[1])
        la,lb=math.hypot(*a),math.hypot(*b); r=radii.get(i,0)
        assert r<=min(la,lb), (i,r,la,lb)
        a=tuple(v/la for v in a); b=tuple(v/lb for v in b)
        if r: assert abs(sum(x*y for x,y in zip(a,b)))<1e-9
        enter=tuple(p[j]+a[j]*r for j in (0,1)); leave=tuple(p[j]+b[j]*r for j in (0,1))
        corners.append((enter,leave,p,r,a,b))
    fmt=lambda p:f'{p[0]:.6f},{p[1]:.6f}'
    result='M '+fmt(corners[0][0])+' '
    for i,(enter,leave,p,r,a,b) in enumerate(corners):
        if i: result+='L '+fmt(enter)+' '
        if r:
            k=.5522847498307936
            c1=tuple(enter[j]-a[j]*r*k for j in (0,1))
            c2=tuple(leave[j]-b[j]*r*k for j in (0,1))
            result+=f'C {fmt(c1)} {fmt(c2)} {fmt(leave)} '
    return result+'Z'


def reverse(path):
    rec=RecordingPen(); parse_path(path,rec); pen=SVGPathPen(None)
    rec.replay(ReverseContourPen(pen)); return pen.getCommands()


def rect(x,y,w,h,r=0):
    return polygon([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],{i:r for i in range(4)})


def ccw_poly(points,radii=None):
    """Ensure counter-clockwise (solid) winding regardless of vertex listing order."""
    area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1]))
    if area<0:
        n=len(points)
        points=list(reversed(points))
        radii={n-1-k:v for k,v in (radii or {}).items()}
    return polygon(points,radii)


def diag_bar(x0,y0,x1,y1,w,y_lo,y_hi,align='center'):
    """Diagonal stroke of exact perpendicular width w, cut horizontally at y_lo and y_hi."""
    dx,dy=x1-x0,y1-y0
    hx=(w/2)*math.hypot(dx,dy)/abs(dy)
    x_at=lambda y: x0+dx*(y-y0)/dy
    shift=0 if align=='center' else hx if align=='left' else -hx
    return polygon([(x_at(y_lo)+shift-hx,y_lo),(x_at(y_lo)+shift+hx,y_lo),
                    (x_at(y_hi)+shift+hx,y_hi),(x_at(y_hi)+shift-hx,y_hi)])


def shapes(p):
    l,r=p['active_left'],p['active_right']; cap=p['cap_height']
    v,h,ro,ri=(p[k] for k in ('vertical_stem','horizontal_bar','outer_radius','inner_radius'))
    il,ir=l+v,r-v; mid=cap/2; low=mid-h/2; high=mid+h/2
    ring=rect(l,0,r-l,cap,ro)+' '+reverse(rect(il,h,ir-il,cap-2*h,ri))
    d={'O':ring}
    d['H']=polygon([(l,0),(il,0),(il,low),(ir,low),(ir,0),(r,0),(r,cap),(ir,cap),(ir,high),(il,high),(il,cap),(l,cap)])
    # Zero remains unmarked; inset its drawing, never its advance.
    inset=p['unit']/2
    d['zero']=rect(l+inset,0,r-l-2*inset,cap,ro)+' '+reverse(rect(il+inset,h,ir-il-2*inset,cap-2*h,ri))
    # Full C path: flat horizontal cuts after 1u vertical returns.
    lo=h+p['aperture_extension']; hi=cap-lo
    pts=[(r,hi),(r,cap),(l,cap),(l,0),(r,0),(r,lo),(ir,lo),(ir,h),(il,h),(il,cap-h),(ir,cap-h),(ir,hi)]
    radii={1:ro,2:ro,3:ro,4:ro,7:ri,8:ri,9:ri,10:ri}
    d['C']=polygon(pts,radii)
    d['E']=polygon([(l,0),(r,0),(r,h),(il,h),(il,low),(r,low),(r,high),(il,high),(il,cap-h),(r,cap-h),(r,cap),(l,cap)])
    # Architectural S: five bands, two round outside turns per lobe, and
    # small inner fillets. All joins meet straight walls tangentially.
    s=[(r,hi),(r,cap),(l,cap),(l,low),(ir,low),(ir,h),(il,h),(il,lo),(l,lo),(l,0),(r,0),(r,high),(il,high),(il,cap-h),(ir,cap-h),(ir,hi)]
    d['S']=polygon(s,{**{i:ro for i in (1,2,3,9,10,11)},**{i:ri for i in (4,5,6,12,13,14)}})
    d['G']=d['C']+' '+rect(mid,low,r-mid,h)+' '+rect(ir,lo,v,low-lo)
    half=p['q_tail_normal_thickness']/math.sqrt(2)
    centre=p['q_centerline_x_plus_y']; top=p['q_top']; bottom=-p['tail_depth']
    tail=polygon([(centre-top-half,top),(centre-top+half,top),
                  (centre-bottom+half,bottom),(centre-bottom-half,bottom)])
    d['Q']=ring+' '+reverse(tail)
    # 45-degree arms with optical normal thickness; outer silhouette and 160-unit stem fixed.
    drop=p['y_outer_drop_y']; join=p['y_stem_join_y']; mid_x=p['advance']/2
    inner_intercept=p['y_outer_left_intercept']+p['y_arm_normal_thickness']*math.sqrt(2)
    inner_drop=inner_intercept-il; notch=inner_intercept-mid_x
    d['Y']=polygon([(l,cap),(il,cap),(il,inner_drop),(mid_x,notch),
                    (ir,inner_drop),(ir,cap),(r,cap),(r,drop),
                    (mid_x+v/2,join),(mid_x+v/2,0),(mid_x-v/2,0),
                    (mid_x-v/2,join),(l,drop)])
    # Remaining uppercase A–Z
    u=p['unit']
    d['I']=rect(mid_x-v/2,0,v,cap)+' '+rect(l+u,0,r-l-2*u,h)+' '+rect(l+u,cap-h,r-l-2*u,h)
    d['T']=rect(mid_x-v/2,0,v,cap)+' '+rect(l,cap-h,r-l,h)
    d['L']=rect(l,0,v,cap)+' '+rect(l,0,r-l,h)
    d['F']=rect(l,0,v,cap)+' '+rect(l,cap-h,r-l,h)+' '+rect(l,low,r-l-u,h)
    u_outer=ccw_poly([(l,cap),(r,cap),(r,0),(l,0)],{2:ro,3:ro})
    u_inner=ccw_poly([(il,cap),(ir,cap),(ir,h),(il,h)],{2:ri,3:ri})
    d['U']=u_outer+' '+reverse(u_inner)
    j_outer=ccw_poly([(ir,cap),(r,cap),(r,0),(l,0),(l,lo),(il,lo),(il,h),(ir,h)],{2:ro,3:ro,6:ri,7:ri})
    d['J']=j_outer
    d_outer=ccw_poly([(l,cap),(r,cap),(r,0),(l,0)],{1:ro,2:ro})
    d_inner=ccw_poly([(il,cap-h),(ir,cap-h),(ir,h),(il,h)],{1:ri,2:ri})
    d['D']=d_outer+' '+reverse(d_inner)
    p_outer=ccw_poly([(l,cap),(r,cap),(r,low),(il,low),(il,0),(l,0)],{1:ro,2:ro})
    p_inner=ccw_poly([(il,cap-h),(ir,cap-h),(ir,low+h),(il,low+h)],{1:ri,2:ri})
    d['P']=p_outer+' '+reverse(p_inner)
    b_outer=ccw_poly([(l,0),(r,0),(r,low),(r-40,low),(r-40,high),(r,high),(r,cap),(l,cap)],{1:ro,2:28,3:10,4:10,5:28,6:ro})
    b_top_in=ccw_poly([(il,cap-h),(ir,cap-h),(ir,low+h),(il,low+h)],{1:ri,2:ri})
    b_bot_in=ccw_poly([(il,low),(ir,low),(ir,h),(il,h)],{1:ri,2:ri})
    d['B']=b_outer+' '+reverse(b_top_in)+' '+reverse(b_bot_in)
    d['R']=d['P']+' '+diag_bar(mid_x-20,low+h/2,r,0,144,0,low+h/2,'right')
    d['V']=diag_bar(l,cap,mid_x-v/2,0,144,0,cap,'left')+' '+diag_bar(r,cap,mid_x+v/2,0,144,0,cap,'right')
    d['A']=diag_bar(l,0,mid_x-v/2,cap,144,0,cap,'left')+' '+diag_bar(r,0,mid_x+v/2,cap,144,0,cap,'right')+' '+rect(200,200,400,h)
    d['W']=(diag_bar(l,cap,210,0,128,0,cap,'left')+' '+diag_bar(278,0,mid_x,580,128,0,580,'center')+' '+
            diag_bar(522,0,mid_x,580,128,0,580,'center')+' '+diag_bar(r,cap,590,0,128,0,cap,'right'))
    d['X']=diag_bar(164,cap,636,0,144,0,cap,'center')+' '+diag_bar(636,cap,164,0,144,0,cap,'center')
    z_off=72*math.sqrt(2)
    z_pts=[(l,cap),(r,cap),(r,r-z_off),(h+z_off,h),(r,h),(r,0),(l,0),(l,l+z_off),(cap-h-z_off,cap-h),(l,cap-h)]
    d['Z']=ccw_poly(z_pts)
    d['N']=rect(l,0,v,cap)+' '+rect(ir,0,v,cap)+' '+diag_bar(l+90,cap,r-90,0,144,0,cap,'center')
    d['M']=rect(l,0,v,cap)+' '+rect(ir,0,v,cap)+' '+diag_bar(l+80,cap,mid_x,140,136,140,cap,'center')+' '+diag_bar(r-80,cap,mid_x,140,136,140,cap,'center')
    d['K']=rect(l,0,v,cap)+' '+diag_bar(il+100,low,r,cap,144,low,cap,'right')+' '+diag_bar(il+140,high,r,0,144,0,high,'right')
    # Figures 1–9 (zero already defined above)
    d['one']=rect(mid_x-v/2,0,v,cap)+' '+rect(l+u,0,r-l-2*u,h)+' '+rect(l+u,cap-h,mid_x+v/2-(l+u),h)
    two_pts=[(l,hi),(l,cap),(r,cap),(r,low),(il,low),(il,h),(r,h),(r,0),(l,0),(l,high),(ir,high),(ir,cap-h),(il,cap-h),(il,hi)]
    d['two']=ccw_poly(two_pts,{1:ro,2:ro,3:ro,4:ri,5:ri,9:ro,10:ri,11:ri,12:ri})
    three_pts=[(l,hi),(l,cap),(r,cap),(r,high),(r-40,high),(r-40,low),(r,low),(r,0),(l,0),(l,lo),
               (il,lo),(il,h),(ir,h),(ir,low),(mid_x-u,low),(mid_x-u,high),(ir,high),(ir,cap-h),(il,cap-h),(il,hi)]
    d['three']=ccw_poly(three_pts,{1:ro,2:ro,3:28,4:10,5:10,6:28,7:ro,8:ro,11:ri,12:ri,13:ri,16:ri,17:ri,18:ri})
    four_arm=ccw_poly([(l,cap),(il,cap),(il,200+h),(r,200+h),(r,200),(l,200)],{2:ri,5:ro})
    d['four']=four_arm+' '+rect(ir-40,0,v,cap)
    five_lo=h+40
    five_bot=ccw_poly([(l,five_lo),(il,five_lo),(il,h),(ir,h),(ir,low),(l,low),(l,high),(r,high),(r,0),(l,0)],{3:ri,4:ri,7:ro,8:ro,9:ro})
    d['five']=rect(l,cap-h,r-l,h)+' '+rect(l,low,v,cap-low)+' '+five_bot
    six_outer=ccw_poly([(l,0),(r,0),(r,high),(il,high),(il,cap-h),(ir,cap-h),(ir,hi),(r,hi),(r,cap),(l,cap)],{0:ro,1:ro,2:ro,4:ri,5:ri,8:ro,9:ro})
    d['six']=six_outer+' '+reverse(rect(il,h,ir-il,high-2*h,ri))
    d['seven']=rect(l,cap-h,r-l,h)+' '+diag_bar(r,cap-h+1,mid_x-40,0,144,0,cap-h+1,'right')
    eight_outer=ccw_poly([(l,0),(r,0),(r,low),(r-40,low),(r-40,high),(r,high),(r,cap),(l,cap),(l,high),(l+40,high),(l+40,low),(l,low)],{0:ro,1:ro,2:28,3:10,4:10,5:28,6:ro,7:ro,8:28,9:10,10:10,11:28})
    d['eight']=eight_outer+' '+reverse(rect(il,low+h,ir-il,cap-low-2*h,ri))+' '+reverse(rect(il,h,ir-il,high-2*h,ri))
    nine_outer=ccw_poly([(r,cap),(l,cap),(l,low),(ir,low),(ir,h),(il,h),(il,lo),(l,lo),(l,0),(r,0)],{0:ro,1:ro,2:ro,4:ri,5:ri,8:ro,9:ro})
    d['nine']=nine_outer+' '+reverse(rect(il,low+h,ir-il,cap-low-2*h,ri))
    d['.notdef']=rect(l,0,r-l,cap,0)+' '+reverse(rect(il,h,ir-il,cap-2*h,0))
    return d


def parameters():
    base=json.loads(CONFIG.read_text())
    return [(name,base|override) for name,override in base['variants'].items()]


def draw():
    (STUDY/'sources').mkdir(exist_ok=True); (STUDY/'specimen').mkdir(exist_ok=True)
    for variant,p in parameters():
        font=Font(); info=font.info
        info.familyName=p['family']; info.styleName=f'Grid-Token {variant} Bold'
        info.unitsPerEm=p['units_per_em']; info.ascender=p['ascender']; info.descender=p['descender']
        info.capHeight=p['cap_height']; info.xHeight=500; info.versionMajor=0; info.versionMinor=2
        info.openTypeOS2WeightClass=700; info.openTypeOS2WidthClass=5
        info.postscriptIsFixedPitch=True; info.openTypeOS2Selection=[7]
        for prefix in ['openTypeHhea','openTypeOS2Typo']:
            setattr(info,prefix+'Ascender',p['ascender']); setattr(info,prefix+'Descender',p['descender']); setattr(info,prefix+'LineGap',0)
        info.openTypeOS2WinAscent=p['ascender']; info.openTypeOS2WinDescent=-p['descender']
        info.openTypeNameDescription='Confinium Mono isolated grid- and token-driven Bold direction study; incomplete repertoire.'
        glyph_names=list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')+['zero','one','two','three','four','five','six','seven','eight','nine']
        digit_codes={'zero':48,'one':49,'two':50,'three':51,'four':52,'five':53,'six':54,'seven':55,'eight':56,'nine':57}
        all_names=['.notdef','space','nbspace']+glyph_names
        for name in all_names:
            glyph=font.newGlyph(name); glyph.width=p['advance']
            glyph.unicodes=[] if name=='.notdef' else [32 if name=='space' else 160 if name=='nbspace' else digit_codes[name] if name in digit_codes else ord(name)]
            if name in shapes(p):
                parse_path(shapes(p)[name],glyph.getPen())
                # Resolve overlaps before saving editable sources.
                union=BooleanGlyph(glyph).removeOverlap(); glyph.clearContours(); union.draw(glyph.getPen())
        font.glyphOrder=all_names
        apply_ufo_license(info)
        font.save(STUDY/f'sources/ConfiniumMono-GridToken-{variant}.ufo',overwrite=True)
        svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 4800 6800"><title>Confinium Mono grid- and token-driven '+variant+' grid</title><rect width="4800" height="6800" fill="#faf8f2"/>']
        for i,name in enumerate(glyph_names):
            x=(i%6)*800; y=120+(i//6)*1120+800
            svg.append(f'<g transform="translate({x},{y}) scale(1,-1)">')
            pen=SVGPathPen(font); font[name].draw(pen)
            svg.append(f'<path d="{pen.getCommands()}" fill="#172426"/>')
            for n in range(11):
                svg.append(f'<path d="M {n*80},-120 V 880 M 0,{n*80} H 800" fill="none" stroke="#4a9b9b" stroke-width="1.3" opacity=".55"/>')
            svg.append('<path d="M 80,0 H 720 V 800 H 80 Z M 400,-120 V 880" fill="none" stroke="#c76b3d" stroke-width="2" stroke-dasharray="8 8"/></g>')
        (STUDY/f'specimen/grid-{variant}.svg').write_text(''.join(svg)+'</svg>')
    (STUDY/'coverage.json').write_text(json.dumps({'family':'Confinium Mono','stage':'isolated grid- and token-driven Bold study','advance':800,'spacing':'all exported glyphs single-cell','codepoints':{f'U+{cp:04X}':g.name for g in font for cp in g.unicodes}},indent=2)+'\n')
    print('Drew three editable grid- and token-driven UFOs and grid overlays; original experiment untouched.')


def build():
    (STUDY/'fonts').mkdir(exist_ok=True)
    os.environ.setdefault('SOURCE_DATE_EPOCH','1795132800')
    for variant,_ in parameters():
        subprocess.run([sys.executable,'-m','fontmake','-u',str(STUDY/f'sources/ConfiniumMono-GridToken-{variant}.ufo'),'-o','ttf','--output-path',str(STUDY/f'fonts/ConfiniumMono-GridToken-{variant}.ttf')],check=True)


def proof():
    (STUDY/'verification').mkdir(exist_ok=True)
    css=''; rows=''; details=''
    for variant,p in parameters():
        data=base64.b64encode((STUDY/f'fonts/ConfiniumMono-GridToken-{variant}.ttf').read_bytes()).decode()
        css+=f'@font-face{{font-family:study{variant};src:url(data:font/ttf;base64,{data});font-weight:700}}'
        details+=f'<section><h2>{variant}</h2><div style="font:700 320px/1.3 study{variant};white-space:pre;font-synthesis:none">CESG</div></section>'
        rows+=f'<section><h2>{variant} / bar {p["horizontal_bar"]} / inner radius {p["inner_radius"]}</h2><div class="sample" style="font-family:study{variant};font-size:64px">ABCDEFGHIJKLM\nNOPQRSTUVWXYZ\n0123456789</div><div class="sample" style="font-family:study{variant};font-size:52px">O0O0 1I1I 2Z2Z 5S5S 8B8B QO0Q</div><div class="sizes" style="font-family:study{variant}">'+''.join(f'<div style="font-size:{px}px">ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789</div>' for px in [14,18,32])+'</div><p><a href="grid-'+variant+'.svg">Open grid overlay</a></p></section>'
    original=base64.b64encode((ROOT/'fonts/ConfiniumMono-Bold.ttf').read_bytes()).decode()
    css+=f'@font-face{{font-family:pilot;src:url(data:font/ttf;base64,{original});font-weight:700}}'
    comparison='''<section><h2>697-unit experiment versus Grid / equal cap height (89.6 px)</h2><div class="sample" style="font-family:pilot;font-size:128px">HO0Q</div><div class="sample" style="font-family:studyGrid;font-size:112px">HO0Q</div><p>Top: existing 697-advance Bold. Bottom: proposed 800-advance Grid. Both rows have the same rendered cap height; differences in width and spacing are intentional. This is not a weight-axis interpolation.</p></section>'''
    nav=primary_nav('../../../','grid-token')
    html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Confinium Mono — grid- and token-driven Bold study</title>'''+appearance_head('../../../')+'''<style>'''+css+'''body{background:var(--paper);color:var(--text);font:16px/1.5 system-ui}h1{margin:0;font-size:38px}h2{font-size:16px;font-weight:500;color:var(--muted)}section{border-top:1px solid var(--border);padding:10px 0 24px}.sample{font-size:clamp(40px,7.8vw,112px);font-weight:700;line-height:1.4;white-space:pre;letter-spacing:0;font-synthesis:none;overflow:auto}.sizes{font-weight:700;line-height:1.4;font-synthesis:none;overflow-x:auto}.sizes div{margin:8px 0}p{max-width:1000px}a{color:inherit}#status{color:var(--accent)}</style>'''+nav+'''<h1>Confinium Mono / grid- and token-driven Bold</h1><p>Direction study: 800 advance · 800 cap height · 160 vertical stems · 160 outer radius. Three controlled variants; not a weight range. All glyph samples use only the new family. Interface labels use the system font.</p><p>Grid is the proposed baseline. Open and Dense vary only horizontal bar thickness and inner fillets. Zero remains unmarked and 80 units narrower; Q uses a 45° right-descending tail (128 normal units) and Y uses 144-normal-unit 45° arms. Coverage: uppercase A–Z and figures 0–9.</p><p><a href="../punctuation/index.html">ASCII punctuation study</a> · <a href="../diagonals/index.html">Optical Q/Y diagonal thickness: 128 / 144 / 160</a> · <a href="../q-tail/index.html">Q tail: centred versus 45° right</a> · <a href="detail.html">Enlarged C/E/S/G review</a> · <a href="../../../specimen/index.html">697-unit experiment</a></p><p id="status">Loading study fonts…</p>'''+comparison+rows+'''<script>Promise.all(['Grid','Open','Dense'].map(v=>document.fonts.load('700 112px study'+v,'HO0QCESGY'))).then(results=>document.querySelector('#status').textContent=results.every(r=>r.length)?'All three study fonts loaded':'FONT LOAD FAILURE')</script></html>'''
    page=STUDY/'specimen/index.html'; write_licensed_html(page, html)
    detail=STUDY/'specimen/detail.html'
    write_licensed_html(detail, '<!doctype html><meta charset="utf-8"><title>Confinium Mono / enlarged grid- and token-driven curves</title>'+appearance_head('../../../')+'<style>'+css+'body{background:var(--paper);color:var(--text);font:16px system-ui}section{border-top:1px solid var(--border);overflow-x:auto}h1{font-size:28px}h2{font-size:16px;font-weight:500}</style>'+nav+'<h1>Confinium Mono / enlarged grid- and token-driven C E S G</h1>'+details+'''<p id="status">Loading…</p>
<script>Promise.all(['Grid','Open','Dense'].map(v=>document.fonts.load('700 320px study'+v,'CESG')))
.then(faces=>document.getElementById('status').textContent=faces.every(f=>f.length)?'All detail fonts loaded':'FONT LOAD FAILURE');</script>''')
    expected = '<p id="status">All three study fonts loaded</p>'
    capture_chromium(page, STUDY / 'verification/chromium.png', '1600,2500', expected)
    capture_chromium(detail, STUDY / 'verification/detail.png', '1300,1700',
                     '<p id="status">All detail fonts loaded</p>')
if __name__=='__main__':
    if len(sys.argv)!=2 or sys.argv[1] not in ('draw','build','proof'): raise SystemExit('Usage: grid_token_study.py draw|build|proof')
    globals()[sys.argv[1]]()
