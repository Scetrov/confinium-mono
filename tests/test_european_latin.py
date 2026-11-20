import unittest
import unicodedata as ud
from pathlib import Path
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1] / 'studies/grid-token-bold'


class EuropeanLatinTests(unittest.TestCase):
    def test_coverage_metrics_and_decomposition(self):
        with TTFont(next((ROOT/'european-latin/fonts').glob('*.ttf'))) as f:
            cmap = f.getBestCmap()
            letters = [chr(cp) for cp in range(192,384) if ud.category(chr(cp)).startswith('L')]
            for c in letters + list('ÁÐÉÍÓÚÝÞÆÖáðéíóúýþæöÅØŊŦȘțẞ€°'):
                with self.subTest(c=c):
                    name = cmap[ord(c)]
                    self.assertEqual(f['hmtx'][name][0], 800)
                    g = f['glyf'][name]
                    self.assertGreater(g.numberOfContours, 0)
                    self.assertLessEqual(g.yMax,f['hhea'].ascent)
                    self.assertGreaterEqual(g.yMin,-200)
            rules = {(first,*lig.Component):lig.LigGlyph for lookup in f['GSUB'].table.LookupList.Lookup
                     for sub in lookup.SubTable for first,items in getattr(sub,'ligatures',{}).items() for lig in items}
            for cp,name in cmap.items():
                decomposition = ud.normalize('NFD',chr(cp))
                if len(decomposition)==2:
                    self.assertEqual(rules[tuple(cmap[ord(c)] for c in decomposition)],name)
                if ud.combining(chr(cp)):
                    self.assertEqual(f['hmtx'][name][0],0)

    def test_accented_cap_bodies(self):
        with TTFont(next((ROOT/'european-latin/fonts').glob('*.ttf'))) as font:
            cmap, glyf = font.getBestCmap(), font['glyf']
            self.assertEqual(font['OS/2'].sCapHeight, 800)
            for limit in (font['hhea'].ascent, font['OS/2'].sTypoAscender, font['OS/2'].usWinAscent):
                self.assertGreaterEqual(limit, font['head'].yMax)
            for cp, name in cmap.items():
                d = ud.normalize('NFD',chr(cp))
                if len(d) != 2 or not d[0].isupper() or ud.combining(d[1]) != 230:
                    continue
                with self.subTest(letter=chr(cp)):
                    body = glyf[cmap[ord(d[0])]].getCoordinates(glyf)[0]
                    coords = glyf[name].getCoordinates(glyf)[0]
                    self.assertEqual(list(coords[:len(body)]), list(body))
                    if chr(cp) != 'Ľ':  # Side caron, not an above accent.
                        self.assertGreater(min(y for x,y in coords[len(body):]), 800)

    def test_ascii_is_unchanged(self):
        with TTFont(next((ROOT/'european-latin/fonts').glob('*.ttf'))) as f, \
             TTFont(next((ROOT/'mixed-text/fonts').glob('*.ttf'))) as parent:
            for cp in range(32,127):
                self.assertEqual(*(face['glyf'][face.getBestCmap()[cp]].getCoordinates(face['glyf'])
                                   for face in (f,parent)))
