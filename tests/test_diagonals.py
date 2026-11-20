"""Normal-thickness regression checks for the optical Q/Y comparison."""
import importlib.util
import math
import sys
from pathlib import Path
import unittest
from PIL import Image,ImageDraw,ImageFont
from ufoLib2 import Font
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
import uharfbuzz as hb
from test_curves import segments,sub,norm

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
try:
    spec=importlib.util.spec_from_file_location('diagonal_study',ROOT/'scripts/diagonal_study.py')
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
finally:
    sys.path.pop(0)


def sloping_edges(glyph):
    edges=[]
    for contour in segments(glyph):
        for s in contour:
            if len(s)!=2: continue
            a,b=s; dx,dy=sub(b,a)
            if abs(dx)>1e-4 and abs(dy)>1e-4: edges.append((a,b))
    return edges


class DiagonalTests(unittest.TestCase):
    def test_normal_thickness_angles_and_fixed_alignment(self):
        for t in module.config()['normal_thicknesses']:
            font=Font.open(module.source(t))
            q=sloping_edges(font['Q']); y=sloping_edges(font['Y'])
            self.assertEqual(len(q),2); self.assertEqual(len(y),4)
            for name,edges in [('Q',q),('Y',y)]:
                for a,b in edges:
                    with self.subTest(t=t,glyph=name):
                        self.assertAlmostEqual(abs((b[1]-a[1])/(b[0]-a[0])),1,places=5)
            intercepts=sorted(a[0]+a[1] for a,_ in q)
            self.assertAlmostEqual((intercepts[1]-intercepts[0])/math.sqrt(2),t,places=4)
            self.assertAlmostEqual(sum(intercepts)/2,532,places=4)
            left=[a[0]+a[1] for a,b in y if max(a[0],b[0])<=400.001]
            right=[a[1]-a[0] for a,b in y if min(a[0],b[0])>=399.999]
            self.assertEqual(len(left),2); self.assertEqual(len(right),2)
            for values in (left,right):
                self.assertAlmostEqual((max(values)-min(values))/math.sqrt(2),t,places=4)
            self.assertAlmostEqual(min(left),660,places=4)
            self.assertEqual(len(font['Q'].contours),2)
            self.assertEqual(len(font['Y'].contours),1)
            for name in ('Q','Y'):
                pen=BoundsPen(font); font[name].draw(pen)
                x0,y0,x1,y1=pen.bounds
                self.assertGreaterEqual(x0,0); self.assertLessEqual(x1,800)
                self.assertEqual(y1,800); self.assertEqual(y0,-120 if name=='Q' else 0)
            # True 160-unit stem retained, from baseline through y=340.
            points=[s[0] for c in segments(font['Y']) for s in c]
            for p in [(320,0),(480,0),(320,340),(480,340)]: self.assertIn(p,points)

    def test_unrelated_outlines_metadata_and_shaping(self):
        base=TTFont(module.STUDY/'fonts/ConfiniumMono-GridToken-Grid.ttf')
        for t in module.config()['normal_thicknesses']:
            font=TTFont(module.binary(t))
            self.assertEqual(set(font.getBestCmap()),{ord(c) for c in 'HO0QCESGY '}|{160})
            self.assertTrue(set(font.getBestCmap()).issubset(set(base.getBestCmap())))
            self.assertEqual(font['name'].getDebugName(16),'Confinium Mono')
            self.assertEqual(font['OS/2'].usWeightClass,700)
            self.assertEqual(font['post'].isFixedPitch,1)
            self.assertEqual((font['hhea'].ascent,font['hhea'].descent,font['hhea'].lineGap),(920,-200,0))
            for name in font.getGlyphOrder():
                self.assertEqual(font['hmtx'][name][0],800)
                if name not in ('Q','Y'):
                    self.assertEqual(font['glyf'][name].getCoordinates(font['glyf'])[0],base['glyf'][name].getCoordinates(base['glyf'])[0])
            hbfont=hb.Font(hb.Face(module.binary(t).read_bytes())); hbfont.scale=(1000,1000)
            for text in ['OQHY','QYQY HY','Q\u00a0Y','Q'*80,'Y'*80,('HO0QCESGY '*8)]:
                for kern in [False,True]:
                    buf=hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
                    hb.shape(hbfont,buf,{'kern':kern})
                    self.assertTrue(all(g.codepoint!=0 for g in buf.glyph_infos))
                    self.assertEqual(len(buf.glyph_positions),len(text))
                    pen=0
                    for i,pos in enumerate(buf.glyph_positions):
                        self.assertEqual(pen,i*800)
                        self.assertEqual((pos.x_advance,pos.y_advance,pos.x_offset,pos.y_offset),(800,0,0,0))
                        pen+=pos.x_advance
                    self.assertEqual(pen,800*len(text))

    def test_clear_counter_attachment_and_progressive_ink(self):
        previous={}
        for t in module.config()['normal_thicknesses']:
            font=ImageFont.truetype(str(module.binary(t)),1000)
            for char in 'QY':
                im=Image.new('L',(800,1100)); ImageDraw.Draw(im).text((0,850),char,font=font,fill=255,anchor='ls')
                ink=sum(im.get_flattened_data())
                if char in previous: self.assertGreater(ink,previous[char])
                previous[char]=ink
                if char=='Q':
                    self.assertEqual(im.getpixel((400,450)),0,'counter must remain clear')
                    self.assertEqual(im.getpixel((500,790)),255,'no ink cancellation at tail attachment')
                    self.assertEqual(im.getpixel((650,930)),255,'visible right-descending tail')
                else:
                    self.assertEqual(im.getpixel((400,800)),255,'lower stem unchanged')

if __name__=='__main__': unittest.main()
