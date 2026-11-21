"""East Slavic upright Cyrillic extension of the European Latin study."""
import argparse
import base64
from html import escape
import os

from fontTools.pens.areaPen import AreaPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont

from european_study import BINARY as PARENT, MARKS, name
from mixed_text_study import GRID
from web import primary_nav, appearance_head
from font_license import write_licensed_html

OUT = GRID / 'cyrillic'
BINARY = OUT / 'fonts/ConfiniumMono-Cyrillic.ttf'
# Skeletons in 800-unit cap space. Single silhouettes wherever practical.
SHAPES = {
    'Г':'M80 0 V800 H720 V660 H240 V0 Z',
    'Ґ':'M80 0 V800 H560 V928 H720 V660 H240 V0 Z',
    'П':'M80 0 V800 H720 V0 H560 V660 H240 V0 Z',
    'Л':'M80 0 V144 Q164 144 182 260 L264 800 H720 V0 H560 V660 H400 L334 214 Q308 0 112 0 Z',
    'Д':'M56 -144 V140 H128 Q166 216 182 318 L252 800 H646 V140 H744 V-144 H608 V0 H192 V-144 Z M288 140 H494 V660 H380 L330 316 Q310 198 288 140 Z',
    'И':'M80 0 V800 H232 V292 L560 800 H720 V0 H568 V508 L240 0 Z',
    'Ч':'M80 800 H240 V508 Q240 464 288 464 H560 V800 H720 V0 H560 V324 H256 Q80 324 80 500 Z',
    'Ц':'M80 800 H232 V140 H528 V800 H680 V140 H744 V-144 H606 V0 H80 Z',
    'Ш':'M80 800 H216 V140 H332 V800 H468 V140 H584 V800 H720 V0 H80 Z',
    'Щ':'M64 800 H196 V140 H316 V800 H448 V140 H568 V800 H700 V140 H752 V-144 H620 V0 H64 Z',
    'Ж':'M48 800 H206 L334 496 V800 H466 V496 L594 800 H752 L568 414 L760 0 H602 L466 324 V0 H334 V324 L198 0 H40 L232 414 Z',
    'Б':'M80 0 V800 H680 V660 H240 V496 H548 Q720 496 720 328 V172 Q720 0 548 0 Z M240 140 H514 Q560 140 560 188 V310 Q560 356 514 356 H240 Z',
    'Ь':'M80 0 V800 H240 V494 H548 Q720 494 720 324 V170 Q720 0 548 0 Z M240 140 H516 Q560 140 560 186 V306 Q560 354 516 354 H240 Z',
    'б':'M80 176 V436 Q80 680 304 724 L536 766 Q588 778 606 810 L694 708 Q654 652 558 638 L332 598 Q242 580 234 482 Q292 528 370 528 H546 Q720 528 720 352 V176 Q720 0 544 0 H256 Q80 0 80 176 Z M240 180 Q240 140 280 140 H520 Q560 140 560 180 V352 Q560 390 520 390 H312 Q240 390 240 312 Z',
}
# Shared forms only where the upright design genuinely agrees with Latin.
SHARED = dict(zip('АВЕКМНОРСТХІаеорсухі', 'ABEKMHOPCTXIaeopcyxi', strict=True))
SAMPLES = {'ru':'Съешь ещё этих мягких французских булок.\nЖИЗНЬ · ОБЪЁМ · ЩУКА',
           'uk':'Ґанок і їжак · Київ · Європа · з’їзд',
           'be':'Беларусь · Мінск · воўк · жыццё'}


def build():
    os.environ.setdefault('SOURCE_DATE_EPOCH','1795132800')
    f = TTFont(PARENT, recalcTimestamp=False)
    order = list(f.getGlyphOrder()); cmap = f.getBestCmap().copy()
    def glyph(c, parts):
        pen = TTGlyphPen(None)
        for src,sx,sy,x,y in parts:
            dest = TransformPen(pen,(sx,0,0,sy,x,y))
            if len(src)==1:
                shape=f['glyf'][cmap[ord(src)]]
                shape.draw(ReverseContourPen(dest) if sx*sy<0 else dest, f['glyf'])
            else:
                area=AreaPen(None); parse_path(src,area)
                parse_path(src,ReverseContourPen(dest) if area.value*sx*sy>0 else dest)
        n=name(c); g=pen.glyph(); f['glyf'][n]=g; g.recalcBounds(f['glyf'])
        order.append(n); cmap[ord(c)]=n; f['hmtx'][n]=(800,g.xMin)

    for c,src in SHARED.items(): glyph(c,[(src,1,1,0,0)])
    for c,d in SHAPES.items(): glyph(c,[(d,1,1,0,0)])
    # Mirrored and narrowed parts come solely from this family's own outlines.
    for c,parts in {
        'З':[('3',1,1,0,0)], 'Я':[('R',-1,1,800,0)],
        'Э':[('C',-1,1,800,0),('M334 330 H614 V470 H334 Z',1,1,0,0)],
        'Є':[('C',1,1,0,0),('M196 330 H466 V470 H196 Z',1,1,0,0)],
        'Ю':[('О',.73,1,193,0),('M80 0 V800 H222 V472 H322 V332 H222 V0 Z',1,1,0,0)],
        'Ы':[('Ь',.72,1,22,0),('M564 0 H720 V800 H564 Z',1,1,0,0)],
        'Ъ':[('Ь',.82,1,128,0),('M80 660 V800 H324 V660 Z',1,1,0,0)],
        'Ф':[('О',1,.76,0,96),('M330 0 H470 V800 H330 Z',1,1,0,0)],
        'У':[('M72 800 H250 L422 420 L552 800 H724 L484 164 Q426 0 270 0 H136 V140 H238 Q316 140 346 230 Z',1,1,0,0)],
    }.items(): glyph(c,parts)
    for c in 'вгґджзиклмнптцчшщъыьэюяє': glyph(c,[(c.upper(),1,.70,0,0)])
    glyph('ф',[('о',1,1,0,0),('M330 -200 H470 V800 H330 Z',1,1,0,0)])
    for c,base,mark in [('Ё','Е','̈'),('ё','е','̈'),('Ї','І','̈'),('ї','ı','̈'),
                        ('Й','И','̆'),('й','и','̆'),('Ў','У','̆'),('ў','у','̆')]:
        glyph(c,[(base,1,1,0,0),(MARKS[mark],1,1,440 if c=='ї' else 400,848 if c.isupper() else 606)])
    f.setGlyphOrder(order)
    for table in f['cmap'].tables:
        if table.isUnicode(): table.cmap.update(cmap)
    family='Confinium Mono Cyrillic Study'
    for record in f['name'].names:
        text={1:family,3:'ConfiniumMono-Cyrillic-Bold-Study',4:family+' Bold',6:'ConfiniumMono-Cyrillic-Bold',10:'East Slavic Cyrillic and European Latin upright study.',16:family}.get(record.nameID)
        if text: record.string=text.encode(record.getEncoding())
    f['OS/2'].recalcUnicodeRanges(f); f['OS/2'].recalcCodePageRanges(f)
    BINARY.parent.mkdir(parents=True,exist_ok=True); f.save(BINARY); f.close()


def proof():
    data=base64.b64encode(BINARY.read_bytes()).decode()
    with TTFont(BINARY) as f:
        letters=''.join(chr(cp) for cp in sorted(f.getBestCmap()) if 0x400<=cp<0x500)
    sections=''.join(f'<section lang="{lang}"><h2>{label}</h2><p class="sample">{escape(SAMPLES[lang])}</p></section>' for lang,label in [('ru','Русский'),('uk','Українська'),('be','Беларуская')])
    write_licensed_html(OUT/'index.html',f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Cyrillic · Confinium Mono</title>{appearance_head('../../../')}
<style>@font-face{{font-family:study;src:url(data:font/ttf;base64,{data});font-weight:700}}body{{font:1rem/1.5 system-ui}}.sample{{font:700 clamp(20px,3vw,36px)/1.5 study;white-space:pre-wrap;overflow-wrap:anywhere}}</style><body>{primary_nav('../../../','cyrillic')}<main><h1>Cyrillic · East Slavic upright</h1><p>Russian, Ukrainian and Belarusian · 800-unit advance · built on European Latin</p>{sections}<h2>Mixed script</h2><p class="sample">Київ / Kyiv · Мінск / Minsk · Москва / Moskva</p><h2>Inventory</h2><p class="sample">{letters}</p></main></body></html>''')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('action',choices=('build','proof')); globals()[parser.parse_args().action]()
