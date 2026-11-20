from pathlib import Path
import unittest

from fontTools.pens.areaPen import AreaPen
from fontTools.ttLib import TTFont

GRID = Path(__file__).resolve().parents[1] / 'studies/grid-token-bold'


class FullGridTests(unittest.TestCase):
    def test_full_faces(self):
        with TTFont(GRID/'cyrillic/fonts/ConfiniumMono-Cyrillic.ttf') as master:
            expected = master.getBestCmap()
            for style in ('Grid','Open','Dense','Hollow'):
                with self.subTest(style=style), TTFont(GRID/f'full-family/fonts/ConfiniumMono-Full{style}.ttf') as f:
                    self.assertEqual(f.getBestCmap(),expected)
                    self.assertEqual(f['GSUB'].compile(f),master['GSUB'].compile(master))
                    for cp,n in expected.items():
                        self.assertEqual(f['hmtx'][n][0],master['hmtx'][n][0])
                        if not chr(cp).isspace(): self.assertGreater(f['glyf'][n].numberOfContours,0,n)
                    for c in 'öЖ':
                        def area(font):
                            gs=font.getGlyphSet(); pen=AreaPen(gs); gs[expected[ord(c)]].draw(pen); return abs(pen.value)
                        ratio=area(f)/area(master)
                        if style=='Hollow': self.assertLess(ratio,.85)
                        elif style=='Open': self.assertLess(ratio,1)
                        elif style=='Dense': self.assertGreater(ratio,1)
                        else: self.assertEqual(ratio,1)
