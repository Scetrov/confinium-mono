"""Isolated Latin-script accent study. Build reads editable UFOs, never writes them."""
import argparse
import base64
from html import escape
import os
from string import punctuation
import unicodedata as ud

from fontTools.pens.areaPen import AreaPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont
from ufo2ft import compileTTF
from ufoLib2 import Font

from mixed_text_study import ALPHABET, GRID, PUNCT
from font_license import write_licensed_html
from web import appearance_head, primary_nav

OUT = GRID / 'european-latin'
BINARY = OUT / 'fonts/ConfiniumMono-EuropeanLatin.ttf'
# Local accent space: center x=0, bottom y=0. Below marks attach at y=0.
MARKS = {
    '̀': 'M-152 148 H-16 L100 0 H-16 Z', '́': 'M16 148 H152 L16 0 H-100 Z',
    '̂': 'M-176 0 L-52 144 H52 L176 0 H48 L0 60 L-48 0 Z',
    '̌': 'M-176 144 H-48 L0 84 L48 144 H176 L52 0 H-52 Z',
    '̃': 'M-184 28 Q-118 160 -4 100 Q76 58 132 126 L180 66 Q104 -52 -16 6 Q-86 46 -138 -22 Z',
    '̈': 'M-168 0 H-56 V112 H-168 Z M56 0 H168 V112 H56 Z',
    '̄': 'M-180 16 H180 V104 H-180 Z', '̇': 'M-60 0 H60 V120 H-60 Z',
    '̆': 'M-176 140 H-76 Q-60 72 0 72 Q60 72 76 140 H176 Q146 -8 0 -8 Q-146 -8 -176 140 Z',
    '̊': 'M-104 76 Q-104 160 0 160 Q104 160 104 76 Q104 -8 0 -8 Q-104 -8 -104 76 Z M-44 76 Q-44 40 0 40 Q44 40 44 76 Q44 112 0 112 Q-44 112 -44 76 Z',
    '̋': 'M-88 152 H28 L-70 0 H-174 Z M90 152 H206 L108 0 H4 Z',
    '̧': 'M-36 12 H54 L32 -40 Q146 -44 114 -132 Q88 -196 -88 -184 V-120 Q26 -134 28 -98 Q30 -76 -62 -78 Z',
    '̨': 'M-28 8 H68 Q-66 -118 60 -102 V-180 Q-160 -194 -106 -74 Z',
    '̦': 'M-36 -40 H72 L12 -184 H-78 Z',
}
# Modern European Latin letters whose NFD consists of one ASCII base and one mark.
ACCENTS = {chr(cp): ud.normalize('NFD', chr(cp)) for cp in [*range(192,384), *range(0x218,0x21c),
            *range(0x1e80,0x1e86), 0x1ef2,0x1ef3,0x1e60,0x1e61,0x1e6a,0x1e6b,*range(0x1e02,0x1e04),
            0x1e0a,0x1e0b,0x1e1e,0x1e1f,0x1e40,0x1e41,0x1e56,0x1e57]}
ACCENTS = {c:d for c,d in ACCENTS.items() if len(d)==2 and d[0].isascii() and d[1] in MARKS}
SAMPLES = {'Icelandic': 'ÁÐÉÍÓÚÝÞÆÖ   áðéíóúýþæö\nÞjóðhátíð · Ísafjörður · íslensk tunga · HÚSAVÍK',
           'Faroese': 'Á Í Ó Ú Ý Æ Ð Ø · Føroyar · Tórshavn · Suðuroy',
           'Scandinavian': 'Æ Ø Å Ä Ö · København · blåbær · Malmö · Ålesund',
           'Northern Sámi': 'Á Č Đ Ŋ Š Ŧ Ž · á č đ ŋ š ŧ ž · Sápmi',
           'Continental Latin': 'Gdańsk · Łódź · Őrség · Timișoara · Dvořák · Ķīšezers\nLietuvà · Ħaż-Żebbuġ · Straße · cœur · naïve · garçon · ŷ · Ŵ'}


def name(c):
    return c if c.isascii() else 'uni%04X' % ord(c)


def build():
    os.environ.setdefault('SOURCE_DATE_EPOCH', '1795132800')
    font = Font.open(ALPHABET)
    with Font.open(PUNCT) as symbols:
        for glyph in symbols:
            if glyph.unicode and chr(glyph.unicode) in punctuation:
                font.addGlyph(glyph.copy())
    # 800 cap + 48 clearance + up to 160 mark height, with headroom.
    font.info.ascender = font.info.openTypeHheaAscender = 1040
    font.info.openTypeOS2TypoAscender = font.info.openTypeOS2WinAscent = 1040
    font.info.familyName = 'Confinium Mono European Latin Study'
    font.info.openTypeNameDescription = 'Icelandic and European Latin accent study.'

    def new(c):
        g = font.newGlyph(name(c)); g.unicode = ord(c); g.width = 800
        return g

    def copy(g, c, sx=1, sy=1, x=0, y=0):
        source = font[name(c)]
        area = AreaPen(font); source.draw(area)
        pen = g.getPen() if area.value > 0 else ReverseContourPen(g.getPen())
        source.draw(TransformPen(pen, (sx,0,0,sy,x,y)))

    def path(g, d, x=0, y=0, sx=1, sy=1):
        area = AreaPen(None); parse_path(d, area)
        pen = g.getPen() if area.value > 0 else ReverseContourPen(g.getPen())
        parse_path(d, TransformPen(pen, (sx,0,0,sy,x,y)))

    # Dotless base for acute i etc.; the existing i has its dot in contour 2.
    dotless = new('ı'); copy(dotless, 'i'); del dotless.contours[1]
    jbase=font.newGlyph('j.dotless'); copy(jbase, 'j'); del jbase.contours[1]; jbase.width=800
    for c in 'Þþ':
        g = new(c); copy(g, 'P' if c=='Þ' else 'p', 1,.67 if c=='Þ' else 1,0,124 if c=='Þ' else 0)
        path(g, 'M80 0 H240 V800 H80 Z')
    for c, base in zip('ÐĐđĦħŦŧŁłØø','DDdHhTtLlOo'):
        g = new(c); copy(g,base)
        if c in 'Øø':
            path(g,'M66 0 H180 L734 800 H620 Z',sy=1 if c=='Ø' else .70)
        elif c in 'Łł': path(g,'M70 276 L520 530 V416 L70 162 Z')
        else:
            x = 468 if c=='đ' else 44
            path(g,'M0 0 H300 V96 H0 Z',x,604 if c in 'đħĦ' else (364 if c!='ŧ' else 200))
    g=new('ð'); copy(g,'o',sy=.91)
    path(g,'M540 396 Q554 596 224 762 L346 806 Q676 644 702 400 Z')
    path(g,'M268 576 L586 792 L664 752 L348 532 Z')
    for c, left, right in [('Æ','A','E'),('æ','a','e'),('Œ','O','E'),('œ','o','e')]:
        g=new(c); copy(g,left,.61,1,30); copy(g,right,.59,1,302)
    for c,base in [('Ŋ','N'),('ŋ','n')]:
        g=new(c); copy(g,base); path(g,'M560 40 H720 V-40 Q720 -200 560 -200 H352 V-60 H528 Q560 -60 560 -28 Z')
    g=new('ß'); path(g,'M80 0 V594 Q80 800 296 800 H464 Q672 800 672 628 Q672 524 538 430 Q716 376 716 222 Q716 0 500 0 H320 V138 H472 Q556 138 556 228 Q556 320 354 352 V454 Q524 562 516 612 Q516 662 450 662 H312 Q240 662 240 580 V0 Z')
    # Historical Greenlandic kra, long s and the legacy apostrophe-n.
    g=new('ĸ'); path(g,'M80 0 V560 H240 V326 L480 560 H688 L420 296 L720 0 H504 L292 212 L240 160 V0 Z')
    g=new('ſ'); path(g,'M224 0 V640 Q224 800 384 800 H616 V660 H416 Q384 660 384 628 V0 Z')
    g=new('ŉ'); copy(g,'n',.82,1,116); path(g,'M64 604 H166 L112 444 H48 Z')
    for c, base in [('Ŀ','L'), ('ŀ','l')]:
        g=new(c); copy(g,base); path(g,'M540 370 H660 V490 H540 Z')
    for c,left,right in [('Ĳ','I','J'), ('ĳ','i','j')]:
        g=new(c); copy(g,left,.52,1,24); copy(g,right,.53,1,356)
    g=new('ẞ'); path(g,'M80 0 V660 L224 800 H516 L692 628 L524 440 Q720 372 720 208 Q720 0 516 0 H322 V142 H486 Q560 142 560 214 Q560 300 342 358 V448 L492 610 L440 660 H290 L240 610 V0 Z')
    # Frequent non-letter signs for European prices, temperatures and quotations.
    for c, d in {
        '·':'M332 220 H468 V356 H332 Z', '–':'M120 254 H680 V362 H120 Z',
        '—':'M32 254 H768 V362 H32 Z', '−':'M112 280 H688 V400 H112 Z',
        '‘':'M350 560 H472 V676 H416 L476 800 H390 L310 658 Z',
        '’':'M328 800 H464 V674 L390 560 H306 L366 682 H328 Z',
        '«':'M300 128 L100 320 L300 512 H446 L246 320 L446 128 Z M552 128 L352 320 L552 512 H698 L498 320 L698 128 Z',
        '»':'M102 128 L302 320 L102 512 H248 L448 320 L248 128 Z M354 128 L554 320 L354 512 H500 L700 320 L500 128 Z',
    }.items(): path(new(c),d)
    for c,base in [('“','‘'),('”','’'),('„','’')]:
        g=new(c); copy(g,base,x=-118,y=-554 if c=='„' else 0); copy(g,base,x=118,y=-554 if c=='„' else 0)
    path(new('°'),MARKS['̊'],400,602,1.28,1.2)
    g=new('€'); copy(g,'C',.88,1,68); path(g,'M72 326 H488 V402 H72 Z M72 466 H520 V542 H72 Z')
    for m,d in MARKS.items():
        g=new(m); g.width=0; path(g,d,-400,600 if ud.combining(m)==230 else 0)
    subs=[]
    for c,(base,m) in ACCENTS.items():
        g=new(c); above=ud.combining(m)==230
        source={'i':'ı','j':'j.dotless'}.get(base,base) if above else base
        # Use a side caron on ascenders rather than stacking on the stem.
        side = m=='̌' and base in 'dltL'
        high = (base.isupper() or base in 'bhklt') and above and not side
        copy(g,source,sy=.90 if high and not base.isupper() else 1)
        x=440 if source=='ı' else 400
        if m=='̨': x=570 if base not in 'Ii' else 456
        if side: path(g,'M0 0 H100 L48 -154 H-32 Z', 740 if base=='d' else 560,790)
        elif base=='g' and m=='̧': path(g,'M0 0 H100 L148 144 H54 Z',360,598)
        elif base in 'GKkLlNnRr' and m=='̧': path(g, MARKS['̦'],x,0)
        else:
            mark_y = 756 if high else 606
            if above and base.isupper():
                # The tilde dips below its local origin; give it extra clearance.
                mark_y = 872 if m == '̃' else 848
            path(g, MARKS[m], x, mark_y if above else 0)
        subs.append(f'sub {name(base)} {name(m)} by {name(c)};')
    font.features.text += '\nfeature ccmp {\n'+'\n'.join(subs)+'\n} ccmp;\n'
    BINARY.parent.mkdir(parents=True,exist_ok=True)
    compileTTF(font,removeOverlaps=False,useProductionNames=False).save(BINARY)


def proof():
    with TTFont(BINARY) as font:
        cmap=font.getBestCmap()
        groups={**SAMPLES,'Cap-line comparison': 'A Á Å · O Ó Ö · U Ú Ü · Y Ý\nHÚSAVÍK · ÅLESUND · ÖREBRO','Canonical pairs (precomposed / decomposed)': 'Á Á · Ý Ý · ö ö · í í · Å Å · ș ș',
                'European signs': '„5 €“ · «20 °C» · – — −',
                'Letter inventory': ' '.join(chr(cp) for cp in sorted(cmap) if cp>127 and chr(cp).isalpha())}
        for sample in groups.values():
            missing={c for c in sample if c!='\n' and ord(c) not in cmap }
            if missing: raise ValueError(missing)
    data=base64.b64encode(BINARY.read_bytes()).decode()
    sections=''.join(f'<section><h2>{title}</h2><p class="sample">{escape(sample)}</p></section>' for title,sample in groups.items())
    write_licensed_html(OUT/'index.html',f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>European Latin · Confinium Mono</title>{appearance_head('../../../')}
<style>@font-face{{font-family:accent;src:url(data:font/ttf;base64,{data});font-weight:700}}body{{font:1rem/1.5 system-ui}}.sample{{white-space:pre-wrap;font:700 clamp(20px,3vw,34px)/1.5 accent}}</style><body>{primary_nav('../../../','european')}<main><h1>European Latin · Icelandic first</h1>{sections}</main></body></html>''')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('action',choices=('build','proof')); globals()[parser.parse_args().action]()
