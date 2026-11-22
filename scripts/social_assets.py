"""Render the site's favicon and Open Graph banner from our own outlines."""
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

from variable_repertoire import BINARY, GRID

ASSETS = Path(__file__).resolve().parents[1] / 'assets'
PAPER = '#1a1b26'
INK = '#c0caf5'
ACCENT = '#7aa2f7'


def favicon():
    with TTFont(GRID) as font:
        glyphs = font.getGlyphSet()
        pen = SVGPathPen(glyphs)
        glyphs[font.getBestCmap()[ord('C')]].draw(pen)
    (ASSETS / 'favicon.svg').write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="13" fill="{PAPER}"/>
  <path d="{pen.getCommands()}" transform="translate(10 54) scale(.055 -.055)" fill="{INK}"/>
</svg>
''', encoding='utf-8')


def banner():
    image = Image.new('RGB', (1200, 630), PAPER)
    draw = ImageDraw.Draw(image)
    panel = (48, 48, 1151, 581)
    draw.rectangle(panel, fill='#1f2335')
    for x in range(76, 1151, 32):
        draw.line((x, 48, x, 581), fill='#292e42')
    for y in range(64, 581, 32):
        draw.line((48, y, 1151, y), fill='#292e42')
    draw.rectangle(panel, outline='#555e80')
    draw.line((76, 147, 198, 147), fill=ACCENT, width=3)

    bold = ImageFont.truetype(str(GRID), 88)
    mono = ImageFont.truetype(str(BINARY), 88)
    mono.set_variation_by_axes([300])
    info = ImageFont.truetype(str(BINARY), 28)
    title = 'Confinium '
    draw.text((76, 338), title, font=bold, anchor='ls', fill=INK)
    draw.text((76 + draw.textlength(title, font=bold), 338), 'Mono', font=mono, anchor='ls', fill=ACCENT)
    draw.text((76, 412), 'An original geometric monospace.', font=info, anchor='ls', fill=INK)
    draw.text((76, 520), 'VARIABLE WEIGHTS   /   800-UNIT CELL', font=info, anchor='ls', fill=ACCENT)
    image.save(ASSETS / 'social-banner.png', optimize=True)


if __name__ == '__main__':
    favicon()
    banner()
