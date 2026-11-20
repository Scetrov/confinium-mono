from contextlib import ExitStack
from pathlib import Path
from string import punctuation
import unittest

from fontTools.ttLib import TTFont

GRID = Path(__file__).resolve().parents[1] / 'studies/grid-token-bold'


class MixedTextTests(unittest.TestCase):
    def test_printable_ascii_matches_parents(self):
        with ExitStack() as stack:
            mixed, alpha, punct = (stack.enter_context(TTFont(next((GRID / name / 'fonts').glob('*.ttf'))))
                                   for name in ('mixed-text', 'lowercase-alphabet', 'punctuation'))
            for cp in range(32, 127):
                with self.subTest(character=chr(cp)):
                    parent = punct if chr(cp) in punctuation else alpha
                    g, source = (font['glyf'][font.getBestCmap()[cp]] for font in (mixed, parent))
                    self.assertNotEqual(mixed.getBestCmap()[cp], '.notdef')
                    self.assertEqual(mixed['hmtx'][mixed.getBestCmap()[cp]][0], 800)
                    self.assertEqual(g.getCoordinates(mixed['glyf']), source.getCoordinates(parent['glyf']))
