from math import hypot
from pathlib import Path
from string import ascii_lowercase
import unittest

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

FONT = (Path(__file__).resolve().parents[1] / 'studies/variable-repertoire/fonts/'
        'ConfiniumMono-VariableRepertoire[wght].ttf')


def stroke_widths(points, a, b, c, d):
    """Measure an opposing edge at both ends against the same line."""
    x, y = points[a]
    u, v = points[b]
    dx, dy = u - x, v - y
    return [abs(dx * (points[i][1] - y) - dy * (points[i][0] - x)) / hypot(dx, dy)
            for i in (c, d)]


class VariableDiagonalTests(unittest.TestCase):
    def test_lowercase_i_j_s_y_stroke_balance(self):
        with TTFont(FONT) as font:
            for weight in (100, 175, 250, 400, 550, 700):
                g = instantiateVariableFont(font, {'wght': weight}, overlap=False)['glyf']
                i, j, s, y = (g[n].coordinates for n in 'ijsy')
                self.assertEqual(i[2][0]-i[7][0], j[2][0]-j[10][0])
                self.assertEqual(i[10][0], i[7][0])
                self.assertEqual(j[12][0], j[10][0])
                self.assertEqual(i[12][0]-i[10][0], j[14][0]-j[12][0])
                self.assertEqual(i[10][1], j[12][1])
                self.assertEqual(i[0][1]-i[9][1], j[0][1]-j[11][1])
                self.assertEqual(s[0][1]-s[1][1], s[15][1]-s[14][1])
                self.assertEqual(y[7][1], y[8][1])
                self.assertEqual(y[9][1], y[10][1])
                self.assertEqual(g['uni0131'].coordinates[:], i[:10])
                self.assertEqual(g['uni045E'].coordinates[:14], y[:])
                if weight == 100:
                    self.assertEqual(s[7][1]-s[21][1], 52)
                    self.assertEqual(y[9][1]-y[8][1], 52)
                    for z in [*stroke_widths(y, 4, 5, 3, 12), *stroke_widths(y, 0, 13, 1, 2)]:
                        self.assertAlmostEqual(z, 54, delta=1)

    def test_lowercase_alignment_and_k_x_stroke_balance(self):
        with TTFont(FONT) as font:
            bold = instantiateVariableFont(font, {'wght': 700}, overlap=False)['glyf']
            for weight in (100, 150, 175, 200, 400, 550, 700):
                glyphs = instantiateVariableFont(font, {'wght': weight}, overlap=False)['glyf']
                for name in ascii_lowercase:
                    high, low = bold[name].yMax, bold[name].yMin
                    for old, new in zip(bold[name].coordinates, glyphs[name].coordinates):
                        if old[1] in (low, high):
                            self.assertEqual(new[1], old[1], (name, weight))
                self.assertEqual(glyphs['x'].coordinates, glyphs['uni0445'].coordinates)
                k = glyphs['k'].coordinates
                self.assertEqual(k[:], glyphs['uni0137'].coordinates[:len(k)])
                self.assertEqual(k[0][1], k[8][1])
                self.assertEqual(k[8][1], k[9][1])
                self.assertEqual(k[5][1], k[6][1])
                if weight == 100:
                    for width in (*stroke_widths(k, 6, 7, 4, 5), *stroke_widths(k, 7, 8, 9, 10)):
                        self.assertAlmostEqual(width, 56, delta=1)
                    x = glyphs['x'].coordinates
                    for width in (*stroke_widths(x, 0, 11, 1, 2), *stroke_widths(x, 3, 2, 4, 5)):
                        self.assertAlmostEqual(width, 54, delta=1)

    def test_lowercase_h_shares_n_geometry_below_the_ascender(self):
        with TTFont(FONT) as font:
            for weight in (100, 175, 250, 400, 550, 700):
                glyphs = instantiateVariableFont(font, {'wght': weight}, overlap=False)['glyf']
                h, n, marked = (glyphs[name].coordinates for name in ('h', 'n', 'uni0125'))
                self.assertEqual(h[3:], n[3:])
                self.assertEqual(h[1][1], 800)
                self.assertEqual(marked[1][1], 720)
                self.assertEqual([x for x, _ in h], [x for x, _ in marked[:len(h)]])
                for points in (h, marked):
                    self.assertEqual(points[8][0], points[9][0])
                    self.assertEqual(points[10][0], points[11][0])
                    self.assertEqual(points[2][0], points[3][0])

    def test_h_stems_are_vertical_in_plain_cyrillic_and_accented_forms(self):
        with TTFont(FONT) as font:
            for weight in (100, 175, 400, 550, 700):
                face = instantiateVariableFont(font, {'wght': weight}, overlap=False)
                glyphs = face['glyf']
                points = glyphs['H'].coordinates
                self.assertEqual(points, glyphs['uni041D'].coordinates)
                self.assertEqual(points[:], glyphs['uni0124'].coordinates[:len(points)])
                for a, b, c in [(0, 1, 1), (2, 3, 11), (4, 5, 8), (6, 7, 7)]:
                    self.assertEqual(points[a][0], points[b][0])
                    self.assertEqual(points[a][0], points[c][0])
                self.assertEqual(points[3][1], points[4][1])
                self.assertEqual(points[9][1], points[10][1])

    def test_light_lowercase_walls_and_balanced_w_and_x(self):
        # Each listed edge is a vertical or horizontal land in the Bold source.
        lands = {'n': ([(0, 1), (9, 8), (16, 17)], [(5, 6), (13, 14)]),
                 'm': ([(0, 1), (14, 13), (22, 21), (23, 24)], [(5, 6), (18, 19)]),
                 'p': ([(0, 1), (17, 18), (23, 24)], [(14, 15), (20, 21)]),
                 'q': ([(0, 13), (16, 17), (22, 23)], [(19, 20), (25, 14)]),
                 'r': ([(0, 1), (8, 9), (16, 17)], [(5, 6), (13, 14)]),
                 'u': ([(1, 2), (7, 8), (9, 10)], [(4, 5), (14, 15)])}
        with TTFont(FONT) as font:
            for weight in (100, 150, 175, 200, 400, 700):
                face = instantiateVariableFont(font, {'wght': weight}, overlap=False)
                glyf = face['glyf']
                for name, axes in lands.items():
                    glyph = glyf[name]
                    for axis, edges in enumerate(axes):
                        for a, b in edges:
                            self.assertEqual(glyph.coordinates[a][axis], glyph.coordinates[b][axis], (name, weight))
                    self.assertEqual(glyph.yMax, 560)
                    self.assertEqual(glyph.yMin, -200 if name in 'pq' else 0)
                for name, edges in {'w': [(15, 16, 2, 3), (4, 3, 13, 14)],
                                    'X': [(1, 2, 5, 6)]}.items():
                    for edge in edges:
                        self.assertAlmostEqual(*stroke_widths(glyf[name].coordinates, *edge), delta=2.5,
                                               msg=f'{name} at {weight}')
                for a, b in [('X', 'uni0425'), ('p', 'uni0440')]:
                    self.assertEqual(glyf[a].coordinates, glyf[b].coordinates)

    def test_lower_bowls_bars_and_hooks_keep_their_grid(self):
        x_edges = {'a': [(3, 4), (22, 23)], 'b': [(0, 1), (17, 18)],
                   'd': [(0, 13), (16, 17)], 'g': [(0, 1), (7, 8)], 'j': [(1, 2), (8, 9)]}
        y_edges = {'a': [(8, 9), (20, 21)], 'b': [(11, 12), (14, 15)],
                   'd': [(2, 3), (19, 20)], 'z': [(0, 1), (3, 4), (5, 6), (8, 9)],
                   'g': [(3, 4), (5, 6)], 'j': [(4, 5), (6, 7)]}
        with TTFont(FONT) as font:
            for weight in (100, 175, 250, 400, 550, 700):
                face = instantiateVariableFont(font, {'wght': weight}, overlap=False)
                glyf = face['glyf']
                for axis, rules in enumerate((x_edges, y_edges)):
                    for name, edges in rules.items():
                        points = glyf[name].coordinates
                        for a, b in edges:
                            self.assertEqual(points[a][axis], points[b][axis], (name, weight, a, b))
                        self.assertEqual(face['hmtx'][name][0], 800)
                for name, (a, b) in {'g': (4, 5), 'j': (5, 6)}.items():
                    points = glyf[name].coordinates
                    self.assertEqual(points[a][1], -200)
                    self.assertGreater(points[b][1], points[a][1])
                self.assertEqual(glyf['a'].coordinates, glyf['uni0430'].coordinates)
                self.assertEqual(glyf['j'].coordinates[:12], glyf['uni0135'].coordinates[:12])
                self.assertAlmostEqual(*stroke_widths(glyf['z'].coordinates, 2, 3, 7, 8),
                                       delta=1.5 if weight <= 400 else 3)

    def test_diagonals_thin_evenly_between_baseline_and_cap(self):
        strokes = {'M': [(3, 4, 12, 13)], 'N': [(2, 3, 8, 9)],
                   'W': [(15, 16, 2, 3), (4, 3, 13, 14)]}
        with TTFont(FONT) as font:
            previous = {}
            for weight in (100, 250, 400, 550, 700):
                face = instantiateVariableFont(font, {'wght': weight}, overlap=False)
                glyf = face['glyf']
                self.assertEqual(glyf['M'].coordinates, glyf['uni041C'].coordinates)
                for name, edges in strokes.items():
                    glyph = glyf[name]
                    self.assertEqual((glyph.yMin, glyph.yMax), (0, 800))
                    self.assertEqual(face['hmtx'][name][0], 800)
                    for j, edge in enumerate(edges):
                        widths = stroke_widths(glyph.coordinates, *edge)
                        self.assertAlmostEqual(*widths, delta=2.5, msg=f'{name} at {weight}')
                        mean = sum(widths) / 2
                        self.assertGreater(mean, previous.get((name, j), 0))
                        previous[name, j] = mean
                w = glyf['W'].coordinates
                for cp in map(ord, 'ŴẀẂẄ'):
                    name = face.getBestCmap()[cp]
                    self.assertEqual(glyf[name].coordinates[:len(w)], w[:])
