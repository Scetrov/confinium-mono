import sys
import unittest
from pathlib import Path

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from i_width_study import widen_i
from m_stroke_study import WEIGHTS, equal_stems, stem_zones
from spacing_balance import I_CONTROL
from stroke_balance import M_CONTROL
from variable_repertoire import BINARY, GRID


class SpacingBalanceTests(unittest.TestCase):
    def test_spacing_and_dependent_forms(self):
        shaping = hb.Font(hb.Face(BINARY.read_bytes()))

        def shape(text):
            buffer = hb.Buffer()
            buffer.add_str(text)
            buffer.guess_segment_properties()
            hb.shape(shaping, buffer)
            self.assertTrue(all(p.x_advance == 800 and p.x_offset == 0 for p in buffer.glyph_positions))
            return [info.codepoint for info in buffer.glyph_infos]

        with TTFont(BINARY) as variable:
            for weight in WEIGHTS:
                with self.subTest(weight=weight):
                    shaping.set_variations({'wght': weight})
                    shape('Confinium fil і ı')
                    for pre, decomposed in [('í', 'i\u0301'), ('į', 'i\u0328'), ('ḟ', 'f\u0307'), ('ṁ', 'm\u0307')]:
                        self.assertEqual(shape(pre), shape(decomposed))
                    glyf = instantiateVariableFont(variable, {'wght': weight})['glyf']
                    i = glyf['i'].coordinates
                    self.assertEqual(i[:], glyf['uni0456'].coordinates[:])
                    self.assertEqual(i[:10], glyf['uni0131'].coordinates[:])
                    self.assertEqual(i[:14], glyf['uni012F'].coordinates[:14])
                    self.assertEqual(i[7][0], i[10][0])  # Stem and dot aligned.
                    gap = 800 + i[7][0] - glyf['f'].coordinates[17][0]
                    self.assertEqual(gap, {100: 781, 175: 768.75, 400: 732, 700: 680}[weight])
                    n = glyf['n'].coordinates
                    self.assertEqual((min(x for x, y in i), max(x for x, y in i)),
                                     (min(x for x, y in n), max(x for x, y in n)))
                    m = glyf['m'].coordinates
                    stem = glyf['U'].coordinates[2][0] - glyf['U'].coordinates[1][0]
                    for a, b in [(0, 30), (23, 22), (15, 14)]:
                        self.assertAlmostEqual(m[b][0] - m[a][0], stem, delta=1)
                    self.assertEqual(m[:], glyf['uni1E41'].coordinates[:len(m)])
        with TTFont(BINARY) as variable, TTFont(GRID) as static:
            bold = instantiateVariableFont(variable, {'wght': 700})
            for name in ('f', 'i', 'm', 'uni0131', 'uni0456', 'uni012F', 'uni1E1F', 'uni1E41'):
                self.assertEqual(bold['glyf'][name].coordinates, static['glyf'][name].coordinates)

    def test_equal_width_i_changes_only_flag_and_foot_ends(self):
        with TTFont(I_CONTROL) as font:
            i, n = (font['glyf'][g] for g in 'in')
            before = list(i.coordinates)
            self.assertEqual(i.xMax - i.xMin, 544)
            widen_i(font)
            self.assertEqual((i.xMin, i.xMax), (n.xMin, n.xMax))
            self.assertEqual(font['hmtx']['i'], (800, n.xMin))
            changed = {k for k, pair in enumerate(zip(before, i.coordinates)) if pair[0] != pair[1]}
            self.assertEqual(changed, {0, 3, 4, 5, 6, 9})
            self.assertEqual([y for x, y in before], [y for x, y in i.coordinates])

    def test_equal_stroke_variant_preserves_advance_and_outer_walls(self):
        with TTFont(M_CONTROL) as variable:
            for weight in WEIGHTS:
                with self.subTest(weight=weight):
                    font = instantiateVariableFont(variable, {'wght': weight})
                    before, capital = stem_zones(font)
                    self.assertLess(before[1] - before[0], capital)
                    equal_stems(font)
                    (a, b, c, d, e, f), _ = stem_zones(font)
                    self.assertEqual((b-a, d-c, f-e), (capital,) * 3)
                    self.assertEqual((a, f), (before[0], before[-1]))
                    self.assertGreater(min(c-b, e-d), 0)
                    self.assertEqual(font['hmtx']['m'][0], 800)
