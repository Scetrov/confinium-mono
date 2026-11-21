"""Compile the mixed-text study directly from the editable parent UFOs."""
import argparse
import base64
from html import escape
import os
from pathlib import Path
from string import punctuation

from fontTools.ttLib import TTFont
from ufo2ft import compileTTF
from ufoLib2 import Font

from font_license import write_licensed_html
from web import appearance_head, primary_nav

GRID = Path(__file__).resolve().parents[1] / 'studies/grid-token-bold'
OUT = GRID / 'mixed-text'
ALPHABET = GRID / 'lowercase-alphabet/sources/ConfiniumMono-GridToken-LowercaseAlphabet.ufo'
PUNCT = GRID / 'punctuation/sources/ConfiniumMono-GridToken-Punctuation.ufo'
BINARY = OUT / 'fonts/ConfiniumMono-GridToken-MixedText.ttf'
ASCII = ''.join(chr(cp) for cp in range(32, 127))
LINES = ('minimum rhythm; wide windows.', 'Il1| O0o rn/m cl/d bdpq []{} () <>',
         'if (glyph_id != 0) return faces[i];', 'g_j p_q y_g [j] {q} (p)')


def build():
    os.environ.setdefault('SOURCE_DATE_EPOCH', '1795132800')
    with Font.open(ALPHABET) as font, Font.open(PUNCT) as symbols:
        names = {cp: glyph.name for glyph in symbols for cp in glyph.unicodes}
        order = font.glyphOrder.copy()
        for ch in punctuation:
            name = names[ord(ch)]
            font.addGlyph(symbols[name].copy())
            order.append(name)
        font.glyphOrder = order
        font.info.familyName = 'Confinium Mono Mixed Text Study'
        font.info.openTypeNameDescription = 'Isolated Grid Bold mixed-text study; printable ASCII.'
        binary = compileTTF(font, removeOverlaps=False, useProductionNames=False)
        BINARY.parent.mkdir(parents=True, exist_ok=True)
        binary.save(BINARY)


def proof():
    with TTFont(BINARY) as font:
        cmap = font.getBestCmap()
        for ch in ASCII:
            if cmap.get(ord(ch), '.notdef') == '.notdef' or font['hmtx'][cmap[ord(ch)]][0] != 800:
                raise ValueError(f'Missing or non-monospace glyph: {ch!r}')
    data = base64.b64encode(BINARY.read_bytes()).decode()
    lines = escape('\n'.join(LINES))
    sections = ''.join(f'<section><h2>{px} px</h2><pre style="font-size:{px}px">{lines}</pre></section>'
                       for px in (12, 16, 24))
    chart = escape('\n'.join(ASCII[i:i+32] for i in range(0, len(ASCII), 32)))
    write_licensed_html(OUT / 'index.html', f'''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Grid Bold · Mixed Text</title>
{appearance_head('../../../')}<style>@font-face{{font-family:mixed;src:url(data:font/ttf;base64,{data});font-weight:700}}
body{{font:1rem/1.5 system-ui}}pre{{font:700 20px/1.5 mixed;overflow-x:auto;padding:.8rem;background:var(--panel)}}
</style><body>{primary_nav('../../../', 'mixed-text')}<main><h1>Mixed text · Grid Bold</h1>
<p>95 printable ASCII characters in one face · 800-unit advance. Compare rhythm, ambiguous forms, and punctuation clearance.</p>
{sections}<h2>Complete printable ASCII</h2><pre>{chart}</pre></main></body></html>''')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('build', 'proof'))
    globals()[parser.parse_args().action]()
