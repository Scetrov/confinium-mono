"""Isolated Grid Bold ASCII punctuation. Build compiles the editable UFO as-is."""
import argparse
import base64
from html import escape
import json
import math
import os
import re
import subprocess
import sys

from booleanOperations.booleanGlyph import BooleanGlyph
from fontTools.svgLib.path import parse_path
from ufoLib2 import Font

from study_reference import GRID_TTF, GRID_UFO
from chromium_proof import capture_chromium
from font_license import write_licensed_html
from grid_token_study import STUDY, ccw_poly, diag_bar, rect, reverse
from web import appearance_head, primary_nav

OUT = STUDY / 'punctuation'
BASE_UFO = GRID_UFO
STEM = 'ConfiniumMono-GridToken-Punctuation'
SOURCE = OUT / 'sources' / f'{STEM}.ufo'
BINARY = OUT / 'fonts' / f'{STEM}.ttf'
NAMES = dict(zip(
    '''!"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~''',
    '''exclam quotedbl numbersign dollar percent ampersand quotesingle
    parenleft parenright asterisk plus comma hyphen period slash colon
    semicolon less equal greater question at bracketleft backslash
    bracketright asciicircum underscore grave braceleft bar braceright
    asciitilde'''.split(), strict=True,
))
SAMPLES = (
    'IF (X != 0) { Y = A[1] + B_2; }',
    r'C:\TMP\BUILD-07.LOG',
    'NET = $120; TAX = 8%; TAG = "A&B";',
    'A@B.IO #42 | `CMD` ^ ~ / \\',
    "(0O) [1I] {2Z} <5S> .,:; !? '\" *",
)


CODE_SAMPLE = '''// BUILD AN INVOICE ROW
(({ ID, NET, TAX }) => ({
  TAG: "INV-" + ID,
  TOTAL: NET + (NET * TAX) / 100,
  STATUS: NET >= 1000 ? "REVIEW" : "OK",
  FLAGS: ["PAID", "EXPORT"],
}))({ ID: 42, NET: 1200, TAX: 8 });'''
# Tokenize only the constructs in this fixed sample, not arbitrary JavaScript.
CODE_TOKENS = re.compile(
    r'(?P<comment>//[^\n]*)|(?P<string>"[^"\n]*")|(?P<number>\b[0-9]+\b)'
    r'|(?P<property>\b[A-Z]+(?=:))|(?P<operator>=>|>=|[+*/?])'
)


def highlight_sample():
    parts = []
    end = 0
    for token in CODE_TOKENS.finditer(CODE_SAMPLE):
        parts.append(escape(CODE_SAMPLE[end:token.start()]))
        parts.append(f'<span class="tok-{token.lastgroup}">{escape(token[0])}</span>')
        end = token.end()
    parts.append(escape(CODE_SAMPLE[end:]))
    return ''.join(parts)


def stroke(x, y, dx, dy, thickness):
    """Normal-width segment with square (perpendicular) end cuts."""
    scale = thickness / (2 * math.hypot(dx, dy))
    a, b = -dy * scale, dx * scale
    return ccw_poly([(x-a, y-b), (x+dx-a, y+dy-b),
                     (x+dx+a, y+dy+b), (x+a, y+b)])


def punctuation():
    # Dots share one cut; arithmetic bars share the 400-unit axis.
    dot = lambda y: rect(320, y, 160, 144, 18)
    comma = ccw_poly([(320, 144), (480, 144), (480, 18), (386, -120),
                      (284, -120), (320, 14)])
    hyphen = rect(180, 340, 440, 120)
    slash = diag_bar(190, 0, 610, 800, 128, 0, 800)
    backslash = diag_bar(610, 0, 190, 800, 128, 0, 800)
    # Enclosures span the capitals; paired shapes mirror in the cell.
    bracket = [(524, 0), (252, 0), (252, 800), (524, 800), (524, 680),
               (380, 680), (380, 120), (524, 120)]
    brace = [(575, 0), (442, 0), (304, 112), (304, 275), (188, 336),
             (188, 464), (304, 525), (304, 688), (442, 800), (575, 800),
             (575, 680), (477, 680), (432, 640), (432, 474), (326, 400),
             (432, 326), (432, 160), (477, 120), (575, 120)]
    chevron = [(580, 133), (176, 344), (176, 456), (580, 667),
               (580, 529), (324, 400), (580, 271)]
    mirror = lambda points: ccw_poly([(800-x, y) for x, y in points])
    paren = ('M 530,0 H 398 C 290,110 228,244 228,400 '
             'C 228,556 290,690 398,800 H 530 C 429,679 356,553 356,400 '
             'C 356,247 429,121 530,0 Z')
    # Explicit mirrored Béziers; path direction compensates for reflection.
    paren_right = ('M 270,0 H 402 C 510,110 572,244 572,400 '
                   'C 572,556 510,690 402,800 H 270 C 371,679 444,553 444,400 '
                   'C 444,247 371,121 270,0 Z')
    # The hook has a deliberately open throat and ends above the shared dot.
    question = ccw_poly([(154, 560), (154, 644), (154, 800), (646, 800),
                         (646, 462), (476, 366), (476, 240), (324, 240),
                         (324, 440), (494, 536), (494, 668), (306, 668),
                         (306, 560)], {2: 136, 3: 136, 11: 28})
    ring = lambda x, y: (rect(x, y, 242, 268, 78) +
                         reverse(rect(x+75, y+74, 92, 120, 18)))
    # S-based dollar with a shortened body and a narrow through-stem.
    dollar = ccw_poly([(132, 196), (280, 196), (280, 176), (520, 176),
                        (520, 336), (132, 336), (132, 752), (668, 752),
                        (668, 604), (520, 604), (520, 624), (280, 624),
                        (280, 464), (668, 464), (668, 48), (132, 48)],
                       {5: 110, 6: 110, 7: 110, 12: 28, 13: 110, 14: 110, 15: 110})
    # Two enclosed counters and an open diagonal exit at the lower right.
    amp = ccw_poly([(120, 0), (120, 350), (258, 454), (192, 548),
                     (192, 800), (580, 800), (580, 540), (428, 429),
                     (523, 293), (611, 418), (720, 345), (604, 178),
                     (720, 0), (552, 0), (514, 55), (455, 0)],
                    {0: 114, 4: 100, 5: 100})
    amp += reverse(ccw_poly([(316, 674), (456, 674), (456, 596),
                             (350, 516), (316, 565)], {0: 22, 1: 22}))
    amp += reverse(ccw_poly([(254, 274), (332, 333), (438, 182),
                             (378, 124), (254, 124)], {4: 26}))
    at = ccw_poly([(80, 0), (80, 800), (720, 800), (720, 218),
                    (468, 218), (468, 560), (560, 560), (560, 316),
                    (612, 316), (612, 690), (188, 690), (188, 110),
                    (652, 110), (652, 0)],
                   {0: 154, 1: 154, 2: 154, 3: 68, 4: 54,
                    8: 14, 9: 52, 10: 52, 11: 52})
    # Use one connected inner bowl and stem; its hole is not crossed by the stem.
    at += rect(240, 218, 320, 342, 98) + reverse(rect(335, 312, 131, 154, 23))
    return {
        '!': dot(0) + ccw_poly([(339, 240), (461, 240), (482, 800), (318, 800)]),
        '"': rect(230, 556, 128, 244) + rect(442, 556, 128, 244),
        '#': (diag_bar(208, 80, 347, 720, 100, 80, 720) +
              diag_bar(453, 80, 592, 720, 100, 80, 720) +
              rect(95, 222, 610, 104) + rect(95, 474, 610, 104)),
        '$': dollar + rect(352, -80, 96, 960),
        '%': ring(92, 532) + ring(466, 0) + diag_bar(161, 0, 639, 800, 112, 0, 800),
        '&': amp,
        "'": rect(336, 556, 128, 244),
        '(': reverse(paren), ')': paren_right,
        '*': rect(348, 350, 104, 450) + stroke(205, 462, 390, 225, 104) +
             stroke(205, 687, 390, -225, 104),
        '+': hyphen + rect(336, 180, 128, 440),
        ',': comma, '-': hyphen, '.': dot(0), '/': slash,
        ':': dot(0) + dot(356), ';': comma + dot(356),
        '<': ccw_poly(chevron), '=': rect(180, 240, 440, 120) + rect(180, 440, 440, 120),
        '>': mirror(chevron), '?': question + dot(0), '@': at,
        '[': ccw_poly(bracket), '\\': backslash, ']': mirror(bracket),
        '^': ccw_poly([(160, 536), (344, 800), (456, 800), (640, 536),
                       (489, 536), (400, 675), (311, 536)]),
        '_': rect(80, -120, 640, 96),
        '`': ccw_poly([(251, 800), (407, 800), (543, 600), (413, 600)]),
        '{': ccw_poly(brace), '|': rect(336, 0, 128, 800), '}': mirror(brace),
        '~': ccw_poly([(125, 313), (125, 435), (257, 506), (523, 414),
                       (675, 487), (675, 365), (543, 294), (277, 386)]),
    }


def draw():
    font = Font.open(BASE_UFO)
    info = font.info
    info.familyName = 'Confinium Mono Punctuation Study'
    info.styleName = 'Bold'
    info.openTypeNameDescription = 'Isolated Grid Bold ASCII punctuation study; no lowercase coverage.'
    outlines = punctuation()
    assert NAMES.keys() == outlines.keys()
    for char, name in NAMES.items():
        glyph = font.newGlyph(name)
        glyph.width = font['H'].width
        glyph.unicode = ord(char)
        parse_path(outlines[char], glyph.getPen())
        union = BooleanGlyph(glyph).removeOverlap()
        glyph.clearContours()
        union.draw(glyph.getPen())
        if not len(glyph):
            raise ValueError(f'Empty outline after union: {name}')
    font.glyphOrder = font.glyphOrder + list(NAMES.values())
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    font.save(SOURCE, overwrite=True)
    coverage = sorted((cp, glyph.name) for glyph in font for cp in glyph.unicodes)
    (OUT / 'coverage.json').write_text(json.dumps({
        'family': info.familyName, 'stage': 'isolated Grid Bold ASCII punctuation study',
        'advance': font['H'].width, 'codepoints': {f'U+{cp:04X}': name for cp, name in coverage},
    }, indent=2) + '\n')


def build():
    BINARY.parent.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault('SOURCE_DATE_EPOCH', '1795132800')
    subprocess.run([sys.executable, '-m', 'fontmake', '-u', str(SOURCE), '-o', 'ttf',
                    '--output-path', str(BINARY)], check=True)


def proof():
    data = base64.b64encode(BINARY.read_bytes()).decode()
    alphabet = ''.join(NAMES)
    rows = '\n'.join(' '.join(alphabet[i:i+8]) for i in range(0, len(alphabet), 8))
    specimens = ''.join(f'<section><h2>{px} px</h2><pre style="font-size:{px}px">'
                        f'{escape(chr(10).join(SAMPLES))}</pre></section>' for px in (12, 16, 28))
    html = f'''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Confinium Mono / Punctuation Study</title>
{appearance_head('../../../')}
<style>
@font-face{{font-family:punctuation;src:url(data:font/ttf;base64,{data}) format("truetype");font-weight:700}}
body{{background:var(--paper);color:var(--text);font:16px/1.45 system-ui}}
h1{{margin-bottom:0}} h2{{font-size:15px;color:var(--muted);margin:0}}
section{{border-top:1px solid var(--border);padding:12px 0}}
pre{{font:700 60px/1.32 punctuation;font-synthesis:none;margin:4px 0;overflow:auto}}
.code-sample{{font-size:17px;line-height:1.55;background:var(--panel);border:1px solid var(--border);
  border-radius:6px;padding:12px 16px;margin-top:10px;tab-size:2}}
.code-sample code{{font:inherit}}
.tok-comment{{color:var(--muted)}} .tok-string{{color:var(--green)}} .tok-number{{color:var(--orange)}}
.tok-property{{color:var(--cyan)}} .tok-operator{{color:var(--violet)}}
a{{color:inherit}}
</style>
{primary_nav('../../../', 'punctuation')}
<h1>Confinium Mono / Punctuation Study</h1>
<p>Grid Bold · 32 ASCII punctuation and operator glyphs · 800-unit advance. Lowercase is not included.</p>
<p><a href="../specimen/index.html">Grid Bold baseline</a> · <a href="fonts/{BINARY.name}">Study TTF</a> · <a href="coverage.json">Coverage</a></p>
<p id="status">Loading study font…</p>
<section><h2>JavaScript · 17 px</h2>
<pre class="code-sample"><code>{highlight_sample()}</code></pre></section>
<section><h2>All 32 additions · ASCII order</h2><pre>{escape(rows)}</pre></section>
{specimens}
<script>document.fonts.load('700 60px punctuation').then(fonts => {{
  document.querySelector('#status').textContent = fonts.length ? 'Study font loaded' : 'FONT LOAD FAILURE';
}});</script></html>
'''
    page = OUT / 'index.html'
    write_licensed_html(page, html)
    archive = OUT / 'verification'
    archive.mkdir(exist_ok=True)
    capture_chromium(page, archive / 'chromium-code.png', '1200,1560',
                     '<p id="status">Study font loaded</p>')
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('draw', 'build', 'proof'))
    globals()[parser.parse_args().command]()
