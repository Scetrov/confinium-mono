from base64 import b64decode
from pathlib import Path
import re
import unittest

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1] / 'studies/grid-token-bold'


def embedded(page):
    return {name: b64decode(data) for name, data in re.findall(
        r'@font-face\{font-family:([\w-]+);src:url\(data:font/ttf;base64,([\w+/=]+)\)',
        page.read_text())}


class ComparisonArchiveTests(unittest.TestCase):
    def test_q_tail_comparison_embeds_the_labelled_geometries(self):
        directory = ROOT / 'q-tail'
        centred = directory / 'ConfiniumMono-GridToken-QCentred.ttf'
        angled = directory / 'ConfiniumMono-GridToken-Q45.ttf'
        self.assertEqual(embedded(directory / 'index.html'),
                         {'centred': centred.read_bytes(), 'diagonal': angled.read_bytes()})
        with TTFont(centred) as before, TTFont(angled) as after:
            self.assertEqual(before.getBestCmap(), after.getBestCmap())
            self.assertEqual(before['hmtx'].metrics, after['hmtx'].metrics)
            a, b = before['glyf'], after['glyf']
            for name in before.getGlyphOrder():
                if name != 'Q':
                    self.assertEqual(a[name].getCoordinates(a), b[name].getCoordinates(b), name)
            below = lambda table: sorted((x, y) for x, y in table['Q'].getCoordinates(table)[0] if y < 0)
            self.assertEqual(below(a), [(320, -120), (480, -120)])
            self.assertEqual(below(b), [(584, -120), (720, -120)])

    def test_both_optical_diagonal_pages_embed_archived_fonts(self):
        directory = ROOT / 'diagonals'
        expected = {'reference': (ROOT / 'q-tail/ConfiniumMono-GridToken-Q45.ttf').read_bytes()}
        for t in (128, 144, 160):
            expected[f'diag{t}'] = (directory / f'fonts/ConfiniumMono-Diagonal{t}.ttf').read_bytes()
        for page in ('index.html', 'detail.html'):
            with self.subTest(page=page):
                self.assertEqual(embedded(directory / page), expected)
