"""Isolated Grid Bold lowercase foundations: draw, build, or proof."""
import argparse
import base64
import os
from pathlib import Path

from fontTools.svgLib.path import parse_path
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from ufoLib2 import Font
from ufo2ft import compileTTF
from study_reference import GRID_UFO
from font_license import write_licensed_html
from web import appearance_head, primary_nav

GRID = Path(__file__).resolve().parents[1] / 'studies/grid-token-bold'
OUT = GRID / 'lowercase'
NAME = 'ConfiniumMono-GridToken-Lowercase'
SOURCE = OUT / 'sources' / (NAME + '.ufo')
BINARY = OUT / 'fonts' / (NAME + '.ttf')
# Outer and counter have opposite winding. Flat lands keep the Grid character.
COUNTER = 'M272 140 H528 Q560 140 560 172 V388 Q560 420 528 420 H272 Q240 420 240 388 V172 Q240 140 272 140 Z'
ROUND = 'M240 0 Q80 0 80 160 V400 Q80 560 240 560 H560 Q720 560 720 400 V160 Q720 0 560 0 Z'


def draw():
    font = Font.open(GRID_UFO)
    font.info.familyName = 'Confinium Mono Lowercase Study'
    font.info.styleName = 'Bold'
    font.info.xHeight = 560
    for name in 'nohpdbq':
        glyph = font.newGlyph(name)
        glyph.unicode, glyph.width = ord(name), 800
        pen = ReverseContourPen(glyph.getPen())
        if name in 'nh':
            top = 800 if name == 'h' else 560
            path = f'M80 0 V{top} H240 V504 Q280 560 360 560 H560 Q720 560 720 400 V0 H560 V388 Q560 420 528 420 H304 Q240 420 240 356 V0 Z'
        elif name == 'o':
            path = ROUND + COUNTER
        else:
            if name in 'dq':
                pen = TransformPen(ReverseContourPen(pen), (-1, 0, 0, 1, 800, 0))
            bottom, top = (-200, 560) if name in 'pq' else (0, 800)
            path = f'M80 {bottom} V{top} H240 V512 Q288 560 360 560 H560 Q720 560 720 400 V160 Q720 0 560 0 H240 V{bottom} Z' + COUNTER
        parse_path(path, pen)
    font.glyphOrder += list('nohpdbq')
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    font.save(SOURCE, overwrite=True)


def build():
    os.environ.setdefault('SOURCE_DATE_EPOCH', '1795132800')
    BINARY.parent.mkdir(parents=True, exist_ok=True)
    compileTTF(Font.open(SOURCE), removeOverlaps=False, useProductionNames=False).save(BINARY)


def proof():
    data = base64.b64encode(BINARY.read_bytes()).decode()
    write_licensed_html(OUT / 'index.html', f'''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Lowercase Foundations · Confinium Mono</title>
{appearance_head('../../../')}<style>@font-face{{font-family:study;src:url(data:font/ttf;base64,{data})}}
body{{font:1rem/1.5 system-ui}}.sample{{font-family:study,monospace;overflow-wrap:anywhere}}</style><body>
{primary_nav('../../../', 'lowercase')}<main><h1>Lowercase foundations</h1><p>Grid Bold · 800-unit cell · 560 x-height · 160 stem · 140 bar · −200 descender</p>
<p class="sample" style="font-size:clamp(36px,8vw,96px)">n o h p d b q</p>
<h2>Shoulders and counters</h2><p class="sample" style="font-size:36px">non noon hoop bond pod<br>Hh Oo Bbd Ppq</p>
<h2>Text sizes</h2><p class="sample">noon bond hoop pod bob</p><p class="sample" style="font-size:12px">noon bond hoop pod bob</p></main></body></html>''')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('draw', 'build', 'proof'))
    globals()[parser.parse_args().action]()
