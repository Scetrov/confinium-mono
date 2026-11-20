"""Regression gates for the pilot's formerly kinked c/e/s/g source outlines.
These geometric checks supplement, rather than certify, visual quality.
"""
import math
from pathlib import Path
import unittest
from fontTools.pens.recordingPen import RecordingPen, lerpRecordings
from ufoLib2 import Font

ROOT = Path(__file__).resolve().parents[1]


def segments(glyph):
    pen=RecordingPen(); glyph.draw(pen)
    contours=[]; current=[]; start=point=None
    for op,args in pen.value:
        if op=='moveTo': start=point=args[0]; current=[]
        elif op in ('lineTo','curveTo'):
            current.append((point,*args)); point=args[-1]
        elif op=='closePath':
            if point!=start: current.append((point,start))
            contours.append(current)
    return contours


def sub(a,b): return (a[0]-b[0],a[1]-b[1])
def cross(a,b): return a[0]*b[1]-a[1]*b[0]
def norm(v): return math.hypot(*v)


class CurveTests(unittest.TestCase):
    def masters(self):
        masters=[]
        for style,t in [('Thin',24),('Book',66),('Bold',108)]:
            font=Font.open(ROOT/f'sources/ConfiniumMono-{style}.ufo')
            masters.append((t,font))
            yield style,t,font
        # Exercise the actual linear point interpolation at every named weight
        # and midpoint, not a fresh evaluation of the construction formulas.
        for index,((t0,f0),(t1,f1)) in enumerate(zip(masters,masters[1:])):
            for step in range(1,6):
                factor=step/6; interpolated=Font()
                for name in 'cesg':
                    a=RecordingPen(); b=RecordingPen()
                    f0[name].draw(a); f1[name].draw(b)
                    recording=RecordingPen()
                    recording.value=list(lerpRecordings(a.value,b.value,factor))
                    recording.replay(interpolated.newGlyph(name).getPen())
                yield f'wght {100+index*300+step*50}',t0+(t1-t0)*factor,interpolated

    def test_corner_cubics_have_no_reversal_or_inflection(self):
        for style,_,font in self.masters():
            for name in 'cesg':
                for contour in segments(font[name]):
                    for seg in contour:
                        if len(seg)!=4: continue
                        with self.subTest(style=style,glyph=name,start=seg[0],end=seg[-1]):
                            p0,p1,p2,p3=seg
                            self.assertGreater(norm(sub(p1,p0)),1e-6,'zero start handle')
                            self.assertGreater(norm(sub(p3,p2)),1e-6,'zero end handle')
                            bends=[]
                            for i in range(1,100):
                                u=i/100; v=1-u
                                d=tuple(3*(v*v*(p1[j]-p0[j])+2*v*u*(p2[j]-p1[j])+u*u*(p3[j]-p2[j])) for j in (0,1))
                                dd=tuple(6*(v*(p2[j]-2*p1[j]+p0[j])+u*(p3[j]-2*p2[j]+p1[j])) for j in (0,1))
                                self.assertGreater(norm(d),1e-6,'cusp inside cubic')
                                bends.append(cross(d,dd))
                            self.assertFalse(min(bends)<-1e-4 and max(bends)>1e-4,'unintended corner inflection')

    def test_tangents_match_except_terminal_cuts(self):
        for style,t,font in self.masters():
            for name in 'cesg':
                for contour in segments(font[name]):
                    for a,b in zip(contour,contour[1:]+contour[:1]):
                        if len(a)==len(b)==2: continue  # intentional line corners
                        # End caps cross a stroke. They must remain sharp.
                        if any(len(s)==2 and norm(sub(s[-1],s[0]))<=t*1.02 for s in (a,b)): continue
                        incoming=sub(a[-1],a[-2]); outgoing=sub(b[1],b[0])
                        length=norm(incoming)*norm(outgoing)
                        with self.subTest(style=style,glyph=name,join=a[-1]):
                            self.assertGreater(length,1e-6)
                            self.assertLess(abs(cross(incoming,outgoing))/length,1e-5,'non-tangent curve join')
                            self.assertGreater(sum(x*y for x,y in zip(incoming,outgoing)),0,'reversed tangent')

    def test_g_bowl_corners_are_concentric(self):
        # Top-left bowl centre must stay (241,369) for both contours.
        for style,t,font in self.masters():
            contours=segments(font['g'])
            for index,radius in ((0,139),(1,139-t)):
                points=[p for seg in contours[index] for p in (seg[0],seg[-1])]
                with self.subTest(style=style,contour=index):
                    for expected in ((241,369+radius),(241-radius,369)):
                        self.assertTrue(any(math.dist(p,expected)<1e-5 for p in points),f'corner centre/radius drift at {expected}')
                    for seg in contours[index]:
                        if len(seg)!=4 or not all(p[0]<=241+1e-5 and p[1]>=369-1e-5 for p in (seg[0],seg[-1])): continue
                        for i in range(101):
                            u=i/100; v=1-u
                            p=tuple(v**3*seg[0][j]+3*v*v*u*seg[1][j]+3*v*u*u*seg[2][j]+u**3*seg[3][j] for j in (0,1))
                            self.assertAlmostEqual(math.dist(p,(241,369)),radius,delta=radius*.0003)

if __name__=='__main__': unittest.main()
