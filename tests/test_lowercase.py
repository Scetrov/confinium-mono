from pathlib import Path
import unittest

from fontTools.ttLib import TTFont
from fontTools.pens.pointInsidePen import PointInsidePen

STUDY = Path(__file__).resolve().parents[1] / 'studies/grid-token-bold/lowercase'


class LowercaseTest(unittest.TestCase):
    def test_foundation_metrics_and_counters(self):
        with TTFont(STUDY / 'fonts/ConfiniumMono-GridToken-Lowercase.ttf') as font:
            glyphs = font.getGlyphSet()
            for char in 'nohpdbq':
                with self.subTest(char=char):
                    name = font.getBestCmap()[ord(char)]
                    outline = font['glyf'][name]
                    self.assertEqual(glyphs[name].width, 800)
                    self.assertEqual(outline.yMin, -200 if char in 'pq' else 0)
                    self.assertEqual(outline.yMax, 800 if char in 'hdb' else 560)
                    for x, expected in [(160, True), (400, False), (640, True)]:
                        pen = PointInsidePen(glyphs, (x, 280))
                        glyphs[name].draw(pen)
                        self.assertEqual(pen.getResult(), expected)
