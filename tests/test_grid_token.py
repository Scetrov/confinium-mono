"""Acceptance gates for the isolated grid- and token-driven Bold experiment, not the pilot."""
import importlib.util
from pathlib import Path
import unittest
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from ufoLib2 import Font
from test_curves import segments, sub, cross, norm

ROOT=Path(__file__).resolve().parents[1]
STUDY=ROOT/'studies/grid-token-bold'
spec=importlib.util.spec_from_file_location('grid_token',ROOT/'scripts/grid_token_study.py')
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)


def flattened(contour):
    points=[contour[0][0]]
    for seg in contour:
        if len(seg)==2: points.append(seg[-1]); continue
        for i in range(1,25):
            u=i/24; v=1-u
            points.append(tuple(v**3*seg[0][j]+3*v*v*u*seg[1][j]+3*v*u*u*seg[2][j]+u**3*seg[3][j] for j in (0,1)))
    return [(a,b) for a,b in zip(points,points[1:]) if norm(sub(b,a))>1e-6]


class GridTokenTests(unittest.TestCase):
    def test_grid_metrics_coverage_and_shaping(self):
        expected={ord(c) for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 '}|{160}
        for variant,p in module.parameters():
            path=STUDY/f'fonts/ConfiniumMono-GridToken-{variant}.ttf'
            font=TTFont(path)
            with self.subTest(variant=variant):
                self.assertEqual(set(font.getBestCmap()),expected)
                self.assertEqual(font['head'].unitsPerEm,1000)
                self.assertEqual(font['OS/2'].sCapHeight,800)
                self.assertEqual(font['OS/2'].usWeightClass,700)
                self.assertEqual(font['post'].isFixedPitch,1)
                self.assertEqual(font['name'].getDebugName(16) or font['name'].getDebugName(1),'Confinium Mono')
                self.assertEqual((font['hhea'].ascent,font['hhea'].descent,font['hhea'].lineGap),(920,-200,0))
                self.assertTrue(all(width==800 for width,_ in font['hmtx'].metrics.values()))
                self.assertNotIn('fvar',font)
                glyphs=font.getGlyphSet()
                for name in glyphs.keys():
                    pen=BoundsPen(glyphs); glyphs[name].draw(pen)
                    if pen.bounds:
                        left,bottom,right,top=pen.bounds
                        self.assertGreaterEqual(left,80)
                        self.assertLessEqual(right,800 if name=='Q' else 720)
                        self.assertEqual(top,800)
                        self.assertEqual(bottom,-120 if name=='Q' else 0)
                hbfont=hb.Font(hb.Face(path.read_bytes())); hbfont.scale=(1000,1000)
                for text in ['HO0QCESGY','ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789','O0O0 1I1I 2Z2Z 5S5S 8B8B','H H','H\u00a0H',' '*80,'O'*80,('HO0QCESGY '*8)]:
                    for kern in (False,True):
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

    def test_resolved_contours_and_tangent_fillets(self):
        for variant,p in module.parameters():
            font=Font.open(STUDY/f'sources/ConfiniumMono-GridToken-{variant}.ufo')
            for glyph in font:
                contours=segments(glyph)
                for contour in contours:
                    for a,b in zip(contour,contour[1:]+contour[:1]):
                        if len(a)==len(b)==2: continue
                        if glyph.name=='Q' and a[-1][1]<140 and (len(a)==2 or len(b)==2): continue
                        incoming=sub(a[-1],a[-2]); outgoing=sub(b[1],b[0])
                        length=norm(incoming)*norm(outgoing)
                        with self.subTest(variant=variant,glyph=glyph.name,join=a[-1]):
                            self.assertGreater(length,0)
                            self.assertLess(abs(cross(incoming,outgoing))/length,.0001)
                            self.assertGreater(sum(x*y for x,y in zip(incoming,outgoing)),0)
                # Flattened approximation catches crossed outlines, including
                # intersections across contours after boolean union.
                lines=[line for contour in contours for line in flattened(contour)]
                for i,(a,b) in enumerate(lines):
                    for c,d in lines[i+1:]:
                        ab=sub(b,a); cd=sub(d,c)
                        if max(a[0],b[0])<min(c[0],d[0]) or max(c[0],d[0])<min(a[0],b[0]): continue
                        if max(a[1],b[1])<min(c[1],d[1]) or max(c[1],d[1])<min(a[1],b[1]): continue
                        ca,da=sub(c,a),sub(d,a); ac,bc=sub(a,c),sub(b,c)
                        self.assertFalse(cross(ab,ca)*cross(ab,da)<-1e-8 and cross(cd,ac)*cross(cd,bc)<-1e-8,(variant,glyph.name,'crossed contours'))

    def test_q45_alternative(self):
        from PIL import Image,ImageDraw,ImageFont
        path=STUDY/'q-tail/ConfiniumMono-GridToken-Q45.ttf'
        base=TTFont(STUDY/'fonts/ConfiniumMono-GridToken-Grid.ttf'); alt=TTFont(path)
        for name in alt.getGlyphOrder():
            if name not in ('Q','Y'):
                self.assertEqual(base['glyf'][name].getCoordinates(base['glyf'])[0],alt['glyf'][name].getCoordinates(alt['glyf'])[0])
            self.assertEqual(alt['hmtx'][name][0],800)
        source=Font.open(STUDY/'q-tail/ConfiniumMono-GridToken-Q45.ufo')
        self.assertEqual(len(source['Q'].contours),2,'tail must form a union, not cut into bowl')
        edges=[seg for contour in segments(source['Q']) for seg in contour if len(seg)==2 and seg[0][1]<140 and seg[-1][1]<140]
        diagonals=[seg for seg in edges if abs(seg[0][0]-seg[-1][0])>1 and abs(seg[0][1]-seg[-1][1])>1]
        self.assertEqual(len(diagonals),2)
        for a,b in diagonals:
            self.assertAlmostEqual((b[1]-a[1])/(b[0]-a[0]),-1,places=5)
        font=ImageFont.truetype(str(path),1000)
        im=Image.new('L',(800,1000)); ImageDraw.Draw(im).text((0,800),'Q',font=font,fill=255,anchor='ls')
        self.assertEqual(im.getpixel((500,740)),255,'attachment must not subtract bowl ink')
        self.assertEqual(im.getpixel((400,400)),0,'counter remains clear')
        self.assertEqual(im.getpixel((650,880)),255,'tail extends down and right')
        self.assertEqual(im.getpixel((400,880)),0,'no centred tail')
        hbfont=hb.Font(hb.Face(path.read_bytes())); hbfont.scale=(1000,1000)
        for kern in (False,True):
            buf=hb.Buffer(); buf.add_str('OQ0Q'*20); buf.guess_segment_properties()
            hb.shape(hbfont,buf,{'kern':kern})
            self.assertTrue(all(pos.x_advance==800 and pos.x_offset==0 for pos in buf.glyph_positions))
            self.assertEqual(sum(pos.x_advance for pos in buf.glyph_positions),64000)

    def test_zero_counter_and_q_tail(self):
        import math
        from PIL import Image,ImageDraw,ImageFont
        for variant,p in module.parameters():
            font=ImageFont.truetype(str(STUDY/f'fonts/ConfiniumMono-GridToken-{variant}.ttf'),1000)
            for char in 'O0Q':
                image=Image.new('L',(800,1000)); ImageDraw.Draw(image).text((0,800),char,font=font,fill=255,anchor='ls')
                # A single white central void; no marker in either O or zero.
                self.assertEqual(image.getpixel((400,400)),0)
                self.assertEqual(image.getpixel((592,860)),255 if char=='Q' else 0)
                self.assertEqual(image.getpixel((400,860)),0)
                if char=='Q':
                    self.assertEqual(image.getpixel((500,740)),255,'attachment must not subtract bowl ink')
            ufo=Font.open(STUDY/f'sources/ConfiniumMono-GridToken-{variant}.ufo')
            expected_contours={
                **{g:1 for g in 'CEFGHIJKLMNSTUVWXYZ'},
                **{g:1 for g in ('one','two','three','four','five','seven')},
                **{g:2 for g in ('A','O','zero','Q','D','P','R','six','nine')},
                **{g:3 for g in ('B','eight')},
            }
            for gname,count in expected_contours.items():
                self.assertEqual(len(ufo[gname].contours),count,(variant,gname))
            q_edges=[s for c in segments(ufo['Q']) for s in c if len(s)==2 and abs(s[1][0]-s[0][0])>1 and abs(s[1][1]-s[0][1])>1]
            self.assertEqual(len(q_edges),2)
            q_intercepts=sorted(a[0]+a[1] for a,_ in q_edges)
            self.assertAlmostEqual((q_intercepts[1]-q_intercepts[0])/math.sqrt(2),128,places=4)
            self.assertAlmostEqual(sum(q_intercepts)/2,532,places=4)
            y_edges=[s for c in segments(ufo['Y']) for s in c if len(s)==2 and abs(s[1][0]-s[0][0])>1 and abs(s[1][1]-s[0][1])>1]
            self.assertEqual(len(y_edges),4)
            left=[a[0]+a[1] for a,b in y_edges if max(a[0],b[0])<=400.001]
            right=[a[1]-a[0] for a,b in y_edges if min(a[0],b[0])>=399.999]
            for values in (left,right):
                self.assertAlmostEqual((max(values)-min(values))/math.sqrt(2),144,places=4)
            # Single-stroke 45-degree Z at 144 normal units.
            z_edges=[s for c in segments(ufo['Z']) for s in c if len(s)==2 and abs(s[1][0]-s[0][0])>1 and abs(s[1][1]-s[0][1])>1]
            self.assertEqual(len(z_edges),2)
            for a,b in z_edges:
                self.assertAlmostEqual((b[1]-a[1])/(b[0]-a[0]),1,places=5)
            z_intercepts=sorted(a[1]-a[0] for a,_ in z_edges)
            self.assertAlmostEqual((z_intercepts[1]-z_intercepts[0])/math.sqrt(2),144,places=4)
            # Rounded 40-unit waist on B, 3, and 8 (right wall at x=680 across y=mid).
            for gname in ('B','three','eight'):
                pts=[s[0] for c in segments(ufo[gname]) for s in c]
                self.assertTrue(any(abs(pt[0]-680)<1e-3 and 330<=pt[1]<=470 for pt in pts),(variant,gname))
            # Raster regression checks against winding-mismatch cutaways and filled counters.
            for ch,px,py,val,msg in [
                ('B',400,235,0,'B upper counter clear'),
                ('B',400,565,0,'B lower counter clear'),
                ('8',400,235,0,'8 upper counter clear'),
                ('8',400,565,0,'8 lower counter clear'),
                ('R',420,400,255,'R middle-bar leg join solid'),
                ('5',160,400,255,'5 left stem solid'),
                ('2',640,400,255,'2 middle right turn solid'),
            ]:
                im=Image.new('L',(800,1000)); ImageDraw.Draw(im).text((0,800),ch,font=font,fill=255,anchor='ls')
                self.assertEqual(im.getpixel((px,py)),val,(variant,msg))

if __name__=='__main__': unittest.main()
