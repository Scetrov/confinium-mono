"""Render glyph-only proofs with FreeType through Pillow; no fallback fonts."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from draw import WEIGHTS
ROOT=Path(__file__).resolve().parents[1]

def main():
    out=ROOT/'specimen'; out.mkdir(exist_ok=True)
    image=Image.new('RGB',(1500,690),'#faf8f2'); draw=ImageDraw.Draw(image)
    for row,style in enumerate(['Thin','Book','Bold']):
        font=ImageFont.truetype(str(ROOT/f'fonts/ConfiniumMono-{style}.ttf'),200)
        draw.text((110,180+row*220),'HO0Qgyces',font=font,fill='#172426',anchor='ls')
    image.save(out/'overview.png')
    for weight,style in WEIGHTS.items():
        im=Image.new('RGB',(1600,1000),'#faf8f2'); d=ImageDraw.Draw(im)
        y=55
        for size in [14,18,32,96,180]:
            font=ImageFont.truetype(str(ROOT/f'fonts/ConfiniumMono-{style}.ttf'),size)
            for text in (['O0O0 00OO OQ0Q','gygy cyc egg','ce s es cec ses'] if size<180 else ['HO0Qgyces']):
                d.text((40,y),text,font=font,fill='#172426',anchor='ls')
                y+=round(size*1.127)+18
            y+=20
        im.save(out/f'{style}.png')
    print('Rendered overview and seven size proofs using only Confinium Mono.')

if __name__=='__main__': main()
