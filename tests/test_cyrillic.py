from pathlib import Path
import unittest

from fontTools.ttLib import TTFont

GRID = Path(__file__).resolve().parents[1] / 'studies/grid-token-bold'


class CyrillicTests(unittest.TestCase):
    def test_east_slavic_letters_and_metrics(self):
        letters = ''.join(map(chr, range(0x410, 0x450))) + 'ЁёҐґЄєІіЇїЎў'
        with TTFont(GRID/'cyrillic/fonts/ConfiniumMono-Cyrillic.ttf') as font:
            cmap = font.getBestCmap()
            for c in letters:
                with self.subTest(char=c):
                    name = cmap[ord(c)]
                    self.assertEqual(font['hmtx'][name][0], 800)
                    g = font['glyf'][name]
                    self.assertGreater(g.numberOfContours, 0)
                    self.assertTrue(0 <= g.xMin < g.xMax <= 800)
                    self.assertTrue(-200 <= g.yMin < g.yMax <= 1040)
            for base, accented in [('И','Й'),('У','Ў'),('Е','Ё'),('І','Ї')]:
                original, marked = [font['glyf'][cmap[ord(c)]].getCoordinates(font['glyf'])[0] for c in (base,accented)]
                self.assertEqual(list(original),list(marked[:len(original)]))
                self.assertGreater(min(y for x,y in marked[len(original):]),800)

    def test_parent_preserved(self):
        with TTFont(GRID/'european-latin/fonts/ConfiniumMono-EuropeanLatin.ttf') as parent, \
             TTFont(GRID/'cyrillic/fonts/ConfiniumMono-Cyrillic.ttf') as font:
            for cp,n in parent.getBestCmap().items():
                new = font.getBestCmap()[cp]
                self.assertEqual(font['hmtx'][new],parent['hmtx'][n])
                self.assertEqual(font['glyf'][new].getCoordinates(font['glyf']),
                                 parent['glyf'][n].getCoordinates(parent['glyf']))
