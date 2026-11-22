import sys
import unittest
from base64 import b64decode
from pathlib import Path
from re import findall
from unicodedata import normalize

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from full_grid_family import OUT as FAMILY
from structural_capitals_study import BASES, OUT, REFERENCE, SAMPLES, base_for, candidates
from variable_repertoire import BINARY
from test_variable_diagonals import stroke_widths


class StructuralCapitalsTests(unittest.TestCase):
    def test_study_geometry_and_inheritance(self):
        with TTFont(REFERENCE) as control, TTFont(REFERENCE) as font:
            changes = candidates(font)
            cmap = font.getBestCmap()
            g, old = font['glyf'], control['glyf']
            expected = set('XNMIWХМІЇŊÑŃŅŇṀÌÍÎÏĨĪĬĮİŴẀẂẄ')
            self.assertEqual(set(changes), {cmap[ord(ch)] for ch in expected})
            for ch in expected:
                name = cmap[ord(ch)]
                base = {'Х': 'X', 'М': 'M', 'І': 'I', 'Ї': 'I', 'Ŋ': 'N'}.get(ch, normalize('NFD', ch)[0])
                current, previous = g[name], old[name]
                old_count = old[base].endPtsOfContours[0] + 1
                count = g[base].endPtsOfContours[0] + 1
                self.assertEqual(current.coordinates[:count], g[base].coordinates[:count])
                self.assertEqual(current.coordinates[count:], previous.coordinates[old_count:])
                self.assertEqual(current.flags[count:], previous.flags[old_count:])
                self.assertEqual(font['hmtx'][name][0], 800)
            x = g['X'].coordinates
            self.assertEqual(x[3:10], g['Y'].coordinates[:7])
            self.assertEqual(set(x), {(a, 800-b) for a, b in x})
            self.assertIn((560, 400), g['N'].coordinates)
            self.assertIn((328, 400), g['M'].coordinates)
            self.assertEqual((g['I'].xMin, g['I'].xMax), (g['L'].xMin, g['J'].xMax))
            self.assertEqual(g['I'].coordinates[2:4], old['I'].coordinates[2:4])
            self.assertEqual(g['W'].coordinates[4:6], [(336, 400), (464, 400)])
            for name in BASES:
                self.assertEqual((g[name].yMin, g[name].yMax), (0, 800))

    def test_family_promotion(self):
        with TTFont(REFERENCE) as proof, TTFont(BINARY) as variable:
            changed = candidates(proof, balance_crown=True)
            with TTFont(REFERENCE) as archive:
                original = archive['glyf']['W'].coordinates
                updated = changed['W'].coordinates
                self.assertEqual(original[:3] + original[7:], updated[:3] + updated[7:])
            cmap = proof.getBestCmap()
            for style in ('Grid', 'Open', 'Dense', 'Hollow'):
                with TTFont(FAMILY / f'ConfiniumMono-Full{style}.ttf') as static, self.subTest(style=style):
                    for cp, name in cmap.items():
                        if name not in changed:
                            continue
                        base = cmap[ord(base_for(chr(cp)))]; glyph = static['glyf'][name]
                        self.assertEqual(static['hmtx'][name][0], 800)
                        if style == 'Grid':
                            self.assertEqual(glyph.coordinates, changed[name].coordinates)
                        if style == 'Hollow':
                            self.assertGreater(glyph.numberOfContours, 1)
                        else:
                            points = static['glyf'][base].coordinates
                            self.assertEqual(glyph.coordinates[:len(points)], points[:])
            for weight in (100, 175, 400, 550, 700):
                with self.subTest(weight=weight):
                    face = instantiateVariableFont(variable, {'wght': weight}, overlap=False)
                    g = face['glyf']
                    for cp, name in cmap.items():
                        if name not in changed:
                            continue
                        base = cmap[ord(base_for(chr(cp)))]; points = g[base].coordinates
                        self.assertEqual(g[name].coordinates[:len(points)], points[:])
                        self.assertEqual(face['hmtx'][name][0], 800)
                        if weight == 700:
                            self.assertEqual(g[name].coordinates, changed[name].coordinates)
                    self.assertAlmostEqual(g['X'].coordinates[2][1], g['Y'].coordinates[7][1], delta=1)
                    for name, point in [('M', 12), ('N', 8), ('W', 4)]:
                        self.assertEqual(g[name].coordinates[point][1], 400)
                    w = g['W'].coordinates
                    outer = stroke_widths(w, 15, 16, 2, 3)
                    crown = stroke_widths(w, 4, 3, 13, 14)
                    for width in crown:
                        self.assertAlmostEqual(width, sum(outer) / 2, delta=2)
                    for name in 'JL':
                        self.assertEqual((g['I'].xMin, g['I'].xMax), (g[name].xMin, g[name].xMax))

    def test_embedded_fonts_shape_every_sample(self):
        html = (OUT / 'index.html').read_text()
        sources = findall(r'font/ttf;base64,([A-Za-z0-9+/=]+)', html)
        self.assertEqual(len(sources), 2)
        for source in sources:
            face = hb.Font(hb.Face(b64decode(source)))
            for _, sample in SAMPLES:
                buffer = hb.Buffer()
                buffer.add_str(sample)
                buffer.guess_segment_properties()
                hb.shape(face, buffer)
                self.assertTrue(all(info.codepoint for info in buffer.glyph_infos), sample)
                self.assertTrue(all(pos.x_advance == 800 for pos in buffer.glyph_positions), sample)
