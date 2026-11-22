from math import hypot
from pathlib import Path
import unittest
from unicodedata import normalize

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

FONT = (Path(__file__).resolve().parents[1] / 'studies/variable-repertoire/fonts'
        / 'ConfiniumMono-VariableRepertoire[wght].ttf')


class ExtendedThinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with TTFont(FONT) as font:
            cls.faces = {w: instantiateVariableFont(font, {'wght': w}, overlap=False)
                         for w in (100, 175, 400, 700)}

    def points(self, c, weight=100):
        face = self.faces[weight]
        return list(face['glyf'][face.getBestCmap()[ord(c)]].coordinates)

    def test_accents_inherit_the_corrected_bases_and_shape_equivalently(self):
        font = hb.Font(hb.Face(FONT.read_bytes()))

        def shape(text):
            buf = hb.Buffer()
            buf.add_str(text)
            buf.guess_segment_properties()
            hb.shape(font, buf)
            return [(g.codepoint, p.x_advance) for g, p in zip(buf.glyph_infos, buf.glyph_positions)]

        for weight in self.faces:
            font.set_variations({'wght': weight})
            for c in 'ÑŃŅŇȚṀḟЙйÛÜÇÖÝŶŸỲ':
                with self.subTest(c=c, weight=weight):
                    nfd = normalize('NFD', c)
                    base = self.points(nfd[0], weight)
                    self.assertEqual(self.points(c, weight)[:len(base)], base)
                    expected = shape(c)
                    self.assertEqual(expected, shape(nfd))
                    self.assertEqual([advance for _, advance in expected], [800])

    def test_y_fix_preserves_accents_and_plain_y(self):
        root = FONT.parents[3]
        with TTFont(root / 'studies/k-steeper/reference' / FONT.name) as control:
            for weight in self.faces:
                old = instantiateVariableFont(control, {'wght': weight}, overlap=False)['glyf']
                base = self.points('Y', weight)
                self.assertEqual(base, list(old['Y'].coordinates))
                for char in 'ÝŶŸỲ':
                    with self.subTest(char=char, weight=weight):
                        name = self.faces[weight].getBestCmap()[ord(char)]
                        actual = self.points(char, weight)
                        self.assertEqual(actual[len(base):], list(old[name].coordinates[len(base):]))
                        if weight == 700:
                            self.assertEqual(actual, list(old[name].coordinates))

    def test_parallel_diagonals(self):
        # Measure normal to the first edge at both ends of the opposing edge.
        for c, a, b, d, e, width in (
            ('Ø',36,37,39,38,54), ('ø',24,25,27,26,54),
            ('Ł',6,7,9,8,52), ('ł',12,13,15,14,52),
            ('И',3,4,9,8,54), ('и',3,4,9,8,54),
            ('Æ',0,1,7,6,56),
        ):
            with self.subTest(c=c):
                p = self.points(c)
                x, y = p[a]
                dx, dy = p[b][0]-x, p[b][1]-y
                for i in (d,e):
                    u, v = p[i]
                    normal = abs(dx*(v-y)-dy*(u-x))/hypot(dx,dy)
                    self.assertAlmostEqual(normal, width, delta=1.1)

    def test_matched_bowl_walls_and_bars(self):
        for c, pairs in {
            # Each pair measures two corresponding walls or two bars.
            'Þ': ((0,12,6,17,0), (2,23,11,14,1)),
            'þ': ((0,13,8,17,0), (1,19,11,14,1)),
            'ø': ((1,20,7,14,0), (0,12,5,17,1)),
            'ð': ((1,20,7,14,0), (0,12,5,17,1)),
            'ф': ((1,20,7,14,0), (0,12,5,17,1)),
            'Ь': ((1,2,6,13,0), (4,16,9,11,1)),
            'Ы': ((1,2,6,13,0), (4,16,9,11,1)),
            'Ъ': ((1,2,6,13,0), (4,16,9,11,1)),
        }.items():
            p = self.points(c)
            for a,b,d,e,axis in pairs:
                with self.subTest(c=c, axis=axis):
                    one, two = abs(p[a][axis]-p[b][axis]), abs(p[d][axis]-p[e][axis])
                    self.assertTrue(52 <= one <= 62, one)
                    self.assertAlmostEqual(one, two, delta=1)

    def test_rounded_bodies_and_ligature_joins(self):
        # Sample straight walls and bars where they leave the rounded corners.
        for c, widths in {
            'Û': ((1,2,0,62), (12,11,0,62), (6,17,1,54)),
            'Ü': ((1,2,0,62), (12,11,0,62), (6,17,1,54)),
            'Ç': ((29,10,0,62), (0,1,0,62), (34,6,1,54), (25,14,1,54)),
            'Ö': ((0,20,0,62), (10,27,0,62), (5,32,1,54), (15,23,1,54)),
            'Ð': ((0,12,0,62), (6,16,0,62), (2,19,1,54), (11,13,1,54), (23,22,1,52)),
            'Œ': ((0,20,0,60), (10,27,0,60), (5,32,1,54), (15,23,1,54),
                  (36,27,0,0), (40,10,0,0), (42,43,1,54)),
            'œ': ((1,20,0,56), (7,14,0,56), (5,17,1,54), (0,12,1,54),
                  (32,14,0,0), (31,7,0,0), (24,40,1,52)),
            'ю': ((0,20,0,60), (10,27,0,60), (5,32,1,54), (15,23,1,54),
                  (36,43,0,60), (39,42,1,52)),
        }.items():
            points = self.points(c)
            for a,b,axis,width in widths:
                with self.subTest(c=c, a=a, b=b):
                    self.assertEqual(abs(points[a][axis]-points[b][axis]), width)
        for weight in self.faces:
            self.assertEqual(self.points('C', weight), self.points('С', weight))
            self.assertEqual(self.points('O', weight), self.points('О', weight))

    def test_lower_u_and_c_corners_round_without_a_thin_spot(self):
        def sample(points):
            # Consecutive off-curve controls imply on-curve midpoints.
            midpoints = [tuple((a+b)/2 for a,b in zip(p,q))
                         for p,q in zip(points[1:-2], points[2:-1])]
            on = [points[0], *midpoints, points[-1]]
            for a,b,c in zip(on, points[1:-1], on[1:]):
                for step in range(41):
                    t = step / 40
                    yield tuple((1-t)**2*x + 2*t*(1-t)*y + t*t*z for x,y,z in zip(a,b,c))

        for c, inner, outer in (
            ('Û', (3,4,5,6), (0,21,20,19,18)),
            ('Ü', (3,4,5,6), (0,21,20,19,18)),
            ('Ç', (10,11,12,13), (29,28,27,26,25)),
        ):
            with self.subTest(c=c):
                p = self.points(c)
                self.assertEqual(p[inner[0]][1], p[outer[0]][1])
                self.assertGreaterEqual(p[inner[-1]][0] - p[inner[0]][0], 140)
                outside = list(sample([p[i] for i in outer]))
                for x,y in sample([p[i] for i in inner]):
                    width = min(hypot(x-a, y-b) for a,b in outside)
                    self.assertGreaterEqual(width, 53)
                    self.assertLessEqual(width, 63)
