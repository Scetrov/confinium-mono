"""Pilot gates only: absent repertoire is deliberately not claimed as tested."""
import json
from pathlib import Path
import unittest
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.boundsPen import BoundsPen

ROOT=Path(__file__).resolve().parents[1]
STYLES=['Thin','ExtraLight','Light','Book','Medium','SemiBold','Bold']

class PilotTests(unittest.TestCase):
    def configurations(self):
        for weight,style in zip(range(100,701,100),STYLES):
            yield ROOT/f'fonts/ConfiniumMono-{style}.ttf',None
        for weight in range(100,701,50):
            yield ROOT/'fonts/ConfiniumMono[wght].ttf',weight

    def test_coverage_metrics_and_bounds(self):
        manifest=json.loads((ROOT/'sources/coverage.json').read_text())
        expected={int(cp[2:],16):g['name'] for g in manifest['glyphs'] for cp in g['codepoints']}
        for path,weight in self.configurations():
            with self.subTest(font=path.name,weight=weight):
                font=TTFont(path)
                if weight is not None: font=instantiateVariableFont(font,{'wght':weight})
                self.assertEqual(font.getBestCmap(),expected)
                self.assertEqual(font['head'].unitsPerEm,1000)
                self.assertEqual(font['post'].isFixedPitch,1)
                self.assertEqual((font['hhea'].ascent,font['hhea'].descent,font['hhea'].lineGap),(885,-242,0))
                os2=font['OS/2']
                self.assertEqual((os2.sTypoAscender,os2.sTypoDescender,os2.sTypoLineGap),(885,-242,0))
                self.assertEqual((os2.usWinAscent,os2.usWinDescent,os2.sCapHeight,os2.sxHeight),(885,242,700,500))
                self.assertTrue(os2.fsSelection & 128)
                self.assertEqual(font['name'].getDebugName(16) or font['name'].getDebugName(1),'Confinium Mono')
                glyphset=font.getGlyphSet()
                for name in font.getGlyphOrder():
                    self.assertEqual(font['hmtx'][name][0],697)
                    pen=BoundsPen(glyphset); glyphset[name].draw(pen)
                    if pen.bounds:
                        left,bottom,right,top=pen.bounds
                        self.assertGreaterEqual(left,0); self.assertLessEqual(right,697)
                        self.assertGreaterEqual(bottom,-242); self.assertLessEqual(top,885)

    def test_shaping_and_intermediate_positions(self):
        strings=['HHH','OOO','O0Q','H H','H\u00a0H','gygy','ce s','H'*80,'O'*80,' '*80,('HO0Qgyces '*8)]
        for path,weight in self.configurations():
            font=hb.Font(hb.Face(path.read_bytes())); font.scale=(1000,1000)
            if weight is not None: font.set_variations({'wght':weight})
            for text in strings:
                for kern in [False,True]:
                    with self.subTest(font=path.name,weight=weight,text=text,kern=kern):
                        buf=hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
                        hb.shape(font,buf,{'kern':kern})
                        self.assertEqual(len(buf.glyph_infos),len(text))
                        self.assertTrue(all(i.codepoint!=0 for i in buf.glyph_infos))
                        pen=0
                        for i,pos in enumerate(buf.glyph_positions):
                            self.assertEqual(pen,i*697)
                            self.assertEqual((pos.x_advance,pos.y_advance,pos.x_offset,pos.y_offset),(697,0,0,0))
                            pen+=pos.x_advance
                        self.assertEqual(pen,len(text)*697)

    def test_axis_instances_and_static_match(self):
        var=TTFont(ROOT/'fonts/ConfiniumMono[wght].ttf')
        axis=var['fvar'].axes[0]
        self.assertEqual((axis.axisTag,axis.minValue,axis.defaultValue,axis.maxValue),('wght',100,400,700))
        self.assertEqual([i.coordinates['wght'] for i in var['fvar'].instances],list(range(100,701,100)))
        for weight,style in zip(range(100,701,100),STYLES):
            static=TTFont(ROOT/f'fonts/ConfiniumMono-{style}.ttf')
            instance=instantiateVariableFont(var,{'wght':weight},inplace=False)
            self.assertEqual(static['OS/2'].usWeightClass,weight)
            for glyph in static.getGlyphOrder():
                expected=instance['glyf'][glyph].getCoordinates(instance['glyf'])[0]
                expected.toInt()  # Serialized TrueType points are integer design units.
                self.assertEqual(static['glyf'][glyph].getCoordinates(static['glyf'])[0],expected)

    def test_progressive_ink(self):
        from PIL import Image,ImageFont,ImageDraw
        previous={}
        for style in STYLES:
            font=ImageFont.truetype(str(ROOT/f'fonts/ConfiniumMono-{style}.ttf'),200)
            for char in 'HO0Qgyces':
                image=Image.new('L',(200,250)); ImageDraw.Draw(image).text((0,190),char,font=font,fill=255,anchor='ls')
                ink=sum(image.get_flattened_data())
                if char in previous: self.assertGreater(ink,previous[char],(style,char))
                previous[char]=ink

if __name__=='__main__': unittest.main()
