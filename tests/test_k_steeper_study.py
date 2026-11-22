import sys
import unittest
from math import atan2, degrees, hypot
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from full_grid_family import OUT as FAMILY
from k_steeper_study import BASES, REFERENCE, WEIGHTS, apply_candidate
from variable_repertoire import BINARY


def edge_dist(a, b, p):
    dx, dy = b[0]-a[0], b[1]-a[1]
    return abs(dx*(p[1]-a[1])-dy*(p[0]-a[0])) / hypot(dx, dy)


def angle(a, b):
    return degrees(atan2(abs(b[1]-a[1]), abs(b[0]-a[0])))


class SteeperKTests(unittest.TestCase):
    def test_promoted_forks_match_the_proof(self):
        with TTFont(BINARY) as variable, TTFont(REFERENCE) as control:
            for weight in WEIGHTS:
                current = instantiateVariableFont(variable, {'wght': weight})
                reference = instantiateVariableFont(control, {'wght': weight})
                expected = apply_candidate(reference, weight, replace=False)
                for name, glyph in expected.items():
                    actual = current['glyf'][name]
                    self.assertEqual(actual.endPtsOfContours, glyph.endPtsOfContours)
                    self.assertEqual(current['hmtx'][name][0], 800)
                    for (a, b), (x, y) in zip(actual.coordinates, glyph.coordinates, strict=True):
                        self.assertAlmostEqual(a, x, delta=1 if weight == 175 else 0)
                        self.assertAlmostEqual(b, y, delta=1 if weight == 175 else 0)
                for name in 'AVY':
                    self.assertEqual(current['glyf'][name].coordinates, reference['glyf'][name].coordinates)
            for style in ('Grid', 'Open', 'Dense', 'Hollow'):
                with TTFont(FAMILY / f'ConfiniumMono-Full{style}.ttf') as static:
                    for name, glyph in expected.items():
                        actual = static['glyf'][name]
                        self.assertEqual(static['hmtx'][name][0], 800)
                        if style == 'Grid':
                            self.assertEqual(actual.coordinates, glyph.coordinates)
                        elif style == 'Hollow':
                            self.assertGreater(actual.numberOfContours, 1)
                        else:
                            self.assertEqual(actual.coordinates[7][0], glyph.coordinates[7][0])

    def test_candidate_arms_and_dependencies(self):
        with TTFont(REFERENCE) as variable:
            for weight in WEIGHTS:
                with self.subTest(weight=weight):
                    font = instantiateVariableFont(variable, {'wght': weight})
                    cmap, glyf = font.getBestCmap(), font['glyf']
                    old = {ch: (list(glyf[cmap[ord(ch)]].coordinates), glyf[cmap[ord(ch)]].endPtsOfContours[0]+1)
                           for ch in BASES}
                    controls = {ch: list(glyf[cmap[ord(ch)]].coordinates) for ch in 'AVXYÝŶŸỲ'}
                    apply_candidate(font, weight)
                    for ch, base in BASES.items():
                        name = cmap[ord(ch)]; g = glyf[name]; p = g.coordinates
                        before, cut = old[ch]
                        self.assertEqual(font['hmtx'][name][0], 800)
                        self.assertEqual(p[:13], glyf[cmap[ord(base)]].coordinates[:13])
                        self.assertEqual(list(p[13:]), [(round(x), round(y)) for x, y in before[cut:]])
                        self.assertAlmostEqual(edge_dist(p[6], p[7], p[4]), edge_dist(p[6], p[7], p[5]), delta=1.5)
                        self.assertAlmostEqual(edge_dist(p[7], p[8], p[9]), edge_dist(p[7], p[8], p[10]), delta=1.5)
                        self.assertGreater(p[7][0], before[6 if base == 'k' else 7][0])
                        if base != 'K':
                            for top, bottom in ((4, 10), (5, 9), (6, 8)):
                                self.assertEqual(p[top], (p[bottom][0], 560-p[bottom][1]))
                            self.assertAlmostEqual(edge_dist(p[6], p[7], p[5]),
                                                   56 + 88*(weight-100)/600, delta=1)
                            self.assertEqual(p[3][1]-p[11][1], 2*round(28 + 42*(weight-100)/600))
                        if weight == 700:
                            top = 5 if base == 'k' else 6
                            self.assertGreater(angle(p[6], p[7]), angle(before[top], before[top+1]))
                            self.assertGreater(angle(p[7], p[8]), angle(before[top+1], before[top+2]))
                    for ch, before in controls.items():
                        self.assertEqual(list(glyf[cmap[ord(ch)]].coordinates), before)
