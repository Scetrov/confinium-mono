"""Full lowercase Grid Bold study, derived from the accepted foundation UFO."""
import argparse
import base64
import os
from string import ascii_lowercase

from fontTools.pens.areaPen import AreaPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.svgLib.path import parse_path
from ufo2ft import compileTTF
from ufoLib2 import Font

import lowercase_study as foundations
from font_license import write_licensed_html
from web import appearance_head, primary_nav

OUT = foundations.GRID / 'lowercase-alphabet'
NAME = 'ConfiniumMono-GridToken-LowercaseAlphabet'
SOURCE = OUT / 'sources' / (NAME + '.ufo')
BINARY = OUT / 'fonts' / (NAME + '.ttf')
# Separate contours per glyph; counter indices are declared explicitly below.
DOT = 'M360 640 H520 V800 H360 Z'
PATHS = {
    'a': ('M112 560 H560 Q720 560 720 400 V0 H560 V44 Q520 0 448 0 H224 Q80 0 80 144 V200 Q80 336 224 336 H560 V388 Q560 420 528 420 H112 Z',
          'M264 128 H512 Q560 128 560 176 V212 H264 Q236 212 236 184 V156 Q236 128 264 128 Z'),
    'c': ('M720 360 H560 V388 Q560 420 528 420 H272 Q240 420 240 388 V172 Q240 140 272 140 H528 Q560 140 560 172 V200 H720 V160 Q720 0 560 0 H240 Q80 0 80 160 V400 Q80 560 240 560 H560 Q720 560 720 400 Z',),
    'e': ('M720 226 H240 V168 Q240 136 272 136 H680 V0 H240 Q80 0 80 160 V400 Q80 560 240 560 H560 Q720 560 720 400 Z',
          'M240 348 H560 V396 Q560 428 528 428 H272 Q240 428 240 396 Z'),
    'f': ('M232 0 V420 H96 V560 H232 V640 Q232 800 392 800 H688 V660 H424 Q392 660 392 628 V560 H640 V420 H392 V0 Z',),
    'g': ('M720 560 V-40 Q720 -200 560 -200 H144 V-60 H528 Q560 -60 560 -28 V44 Q512 0 440 0 H240 Q80 0 80 160 V400 Q80 560 240 560 H448 Q520 560 560 516 V560 Z', foundations.COUNTER),
    'i': ('M168 560 H520 V140 H680 V0 H136 V140 H360 V420 H168 Z', DOT),
    'j': ('M176 560 H520 V-40 Q520 -200 360 -200 H96 V-60 H328 Q360 -60 360 -28 V420 H176 Z', DOT),
    'k': ('M80 0 V800 H240 V326 L480 560 H688 L420 296 L720 0 H504 L292 212 L240 160 V0 Z',),
    'l': ('M144 800 H464 V184 Q464 140 508 140 H672 V0 H456 Q304 0 304 160 V660 H144 Z',),
    # Optical exception: three 128-unit stems leave two usable apertures.
    'm': ('M80 0 V560 H208 V516 Q242 560 300 560 H352 Q408 560 448 508 Q484 560 548 560 H584 Q720 560 720 424 V0 H592 V388 Q592 420 560 420 H520 Q464 420 464 360 V0 H336 V388 Q336 420 304 420 H264 Q208 420 208 360 V0 Z',),
    'r': ('M112 0 V560 H272 V496 Q324 560 408 560 H544 Q688 560 688 416 V320 H528 V388 Q528 420 496 420 H368 Q272 420 272 316 V0 Z',),
    's': ('M680 560 V428 H268 Q236 428 236 396 V376 Q236 344 268 344 H548 Q716 344 716 196 V152 Q716 0 556 0 H100 V132 H528 Q560 132 560 164 V182 Q560 214 528 214 H248 Q84 214 84 364 V404 Q84 560 244 560 Z',),
    't': ('M224 720 H384 V560 H656 V420 H384 V180 Q384 140 424 140 H680 V0 H384 Q224 0 224 160 V420 H88 V560 H224 Z',),
    'u': ('M80 560 H240 V172 Q240 140 272 140 H496 Q560 140 560 204 V560 H720 V0 H560 V56 Q520 0 440 0 H240 Q80 0 80 160 Z',),
    'v': ('M80 560 H248 L400 172 L552 560 H720 L488 0 H312 Z',),
    'w': ('M80 560 H216 L266 230 L346 480 H454 L534 230 L584 560 H720 L620 0 H488 L400 256 L312 0 H180 Z',),
    'x': ('M80 560 H276 L400 390 L524 560 H720 L498 282 L720 0 H524 L400 174 L276 0 H80 L302 282 Z',),
    'y': ('M80 560 H254 L414 214 L550 560 H720 L456 -78 Q408 -200 276 -200 H144 V-60 H248 Q300 -60 320 -14 L336 24 Z',),
    'z': ('M100 560 H700 V438 L336 140 H704 V0 H96 V122 L464 420 H100 Z',),
}


def draw():
    font = Font.open(foundations.SOURCE)
    font.info.familyName = 'Confinium Mono Lowercase Alphabet Study'
    for name, contours in PATHS.items():
        glyph = font.newGlyph(name)
        glyph.width, glyph.unicode = 800, ord(name)
        for i, path in enumerate(contours):
            area = AreaPen(None)
            parse_path(path, area)
            hole = i == 1 and name in 'aeg'
            pen = glyph.getPen()
            parse_path(path, ReverseContourPen(pen) if (area.value < 0) != hole else pen)
    font.glyphOrder += list(PATHS)
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    font.save(SOURCE, overwrite=True)


def build():
    os.environ.setdefault('SOURCE_DATE_EPOCH', '1795132800')
    BINARY.parent.mkdir(parents=True, exist_ok=True)
    compileTTF(Font.open(SOURCE), removeOverlaps=False, useProductionNames=False).save(BINARY)


def proof():
    data = base64.b64encode(BINARY.read_bytes()).decode()
    write_licensed_html(OUT / 'index.html', f'''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Lowercase Alphabet · Confinium Mono</title>
{appearance_head('../../../')}<style>@font-face{{font-family:study;src:url(data:font/ttf;base64,{data})}}
body{{margin:3vw auto;padding:0 4vw;max-width:70rem;font:1rem/1.5 system-ui}}.sample{{font-family:study,monospace;overflow-wrap:anywhere}}</style><body>
{primary_nav('../../../', 'alphabet')}<main><h1>Lowercase alphabet</h1><p>Grid Bold · 560 x-height · 800 advance. Extends the <a href="../lowercase/index.html">seven foundation glyphs</a>.</p>
<p class="sample" style="font-size:clamp(36px,6vw,80px)">{ascii_lowercase}</p>
<h2>Rhythm and recognition</h2><p class="sample" style="font-size:32px">minimum summer velvet<br>agape giggle sizzle<br>Il1 O0o rn m ij ft ky</p>
<h2>Reading sizes</h2><p class="sample" style="font-size:24px">the quick brown fox jumps over the lazy dog</p><p class="sample">pack my box with five dozen liquor jugs</p>
<p class="sample" style="font-size:12px">the quick brown fox jumps over the lazy dog</p></main></body></html>''')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('draw', 'build', 'proof'))
    globals()[parser.parse_args().action]()
