from pathlib import Path
from string import ascii_lowercase
import unittest

from fontTools.ttLib import TTFont

GRID = Path(__file__).resolve().parents[1] / 'studies/grid-token-bold'


class AlphabetTests(unittest.TestCase):
    def test_alphabet_and_foundations(self):
        with TTFont(next((GRID / 'lowercase-alphabet/fonts').glob('*.ttf'))) as font, \
             TTFont(next((GRID / 'lowercase/fonts').glob('*.ttf'))) as base:
            for c in ascii_lowercase:
                with self.subTest(c=c):
                    name = font.getBestCmap()[ord(c)]
                    shape = font['glyf'][name]
                    self.assertEqual(font['hmtx'][name][0], 800)
                    self.assertGreater(shape.numberOfContours, 0)
                    self.assertEqual(shape.yMin, -200 if c in 'gjpqy' else 0)
                    self.assertGreaterEqual(shape.xMin, 80)
                    self.assertLessEqual(shape.xMax, 720)
                    if c in 'nohpdbq':
                        self.assertEqual(shape.getCoordinates(font['glyf']),
                                         base['glyf'][c].getCoordinates(base['glyf']))
