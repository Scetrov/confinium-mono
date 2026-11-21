"""Coverage, outline and shaping gates for the isolated Grid Bold expansion."""
import json
import string
import sys
import unittest
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPointPen
from fontTools.ttLib import TTFont
from ufoLib2 import Font

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import punctuation_study as study


class PunctuationTests(unittest.TestCase):
    def test_coverage_and_base_parity(self):
        baseline = study.GRID_TTF
        with TTFont(baseline) as base, TTFont(study.BINARY) as font:
            base_cmap = base.getBestCmap()
            added = {ord(c): n for c, n in study.NAMES.items()}
            self.assertEqual(set(added), set(map(ord, string.punctuation)))
            self.assertEqual(font.getBestCmap(), base_cmap | added)
            coverage = json.loads((study.OUT / 'coverage.json').read_text())
            self.assertEqual(coverage['codepoints'],
                             {f'U+{cp:04X}': name for cp, name in font.getBestCmap().items()})
            self.assertEqual(coverage['advance'], 800)
            self.assertEqual(font.getGlyphOrder(), base.getGlyphOrder() + list(study.NAMES.values()))
            self.assertEqual(font['head'].unitsPerEm, 1000)
            self.assertEqual(font['OS/2'].sCapHeight, 800)
            self.assertEqual(font['OS/2'].usWeightClass, 700)
            self.assertEqual(font['post'].isFixedPitch, 1)
            self.assertNotIn('fvar', font)
            self.assertEqual((font['hhea'].ascent, font['hhea'].descent, font['hhea'].lineGap),
                             (920, -200, 0))
            for name in base.getGlyphOrder():
                with self.subTest(base_glyph=name):
                    self.assertEqual(font['hmtx'][name], base['hmtx'][name])
                    self.assertEqual(font['glyf'][name].getCoordinates(font['glyf']),
                                     base['glyf'][name].getCoordinates(base['glyf']))

        with Font.open(study.BASE_UFO) as original, Font.open(study.SOURCE) as source:
            self.assertEqual(set(source.keys()), set(original.keys()) | set(added.values()))
            for name in original.keys():
                a, b = RecordingPointPen(), RecordingPointPen()
                original[name].drawPoints(a)
                source[name].drawPoints(b)
                self.assertEqual(a.value, b.value, name)
                self.assertEqual(source[name].unicodes, original[name].unicodes, name)
                self.assertEqual(source[name].width, original[name].width, name)
            for cp, name in added.items():
                self.assertEqual(source[name].unicodes, [cp])
                self.assertEqual(source[name].width, 800)
                self.assertTrue(len(source[name]), name)

    def test_outline_classes(self):
        with TTFont(study.BINARY) as font:
            glyphs = font.getGlyphSet()
            for char, name in study.NAMES.items():
                with self.subTest(char=char):
                    pen = BoundsPen(glyphs)
                    glyphs[name].draw(pen)
                    self.assertIsNotNone(pen.bounds)
                    l, b, r, t = pen.bounds
                    self.assertTrue(80 <= l < r <= 720, pen.bounds)
                    if char in ',;_':
                        self.assertEqual(b, -120)
                    elif char == '$':
                        self.assertEqual((b, t), (-80, 880))
                    else:
                        self.assertGreaterEqual(b, 0)
                    self.assertLessEqual(t, 880 if char == '$' else 800)
                    if char in '()[]{}|/\\':
                        self.assertEqual((b, t), (0, 800))
                    self.assertEqual(font['hmtx'][name][0], 800)
            # Distinct dots and enclosed counters survive overlap removal.
            for char, count in {'!': 2, '?': 2, ':': 2, ';': 2, '"': 2,
                                '%': 5, '&': 3, '@': 2}.items():
                self.assertEqual(font['glyf'][study.NAMES[char]].numberOfContours, count, char)

    def test_shaping(self):
        hbfont = hb.Font(hb.Face(study.BINARY.read_bytes()))
        hbfont.scale = (1000, 1000)
        with TTFont(study.BINARY) as font:
            cmap = font.getBestCmap()
            for text in (*study.NAMES, *study.SAMPLES, *study.CODE_SAMPLE.splitlines(),
                         ''.join(study.NAMES), 'A\u00a0B'):
                for kern in (False, True):
                    with self.subTest(text=text, kern=kern):
                        buf = hb.Buffer()
                        buf.add_str(text)
                        buf.guess_segment_properties()
                        hb.shape(hbfont, buf, {'kern': kern})
                        expected = [font.getGlyphID(cmap[ord(c)]) for c in text]
                        self.assertNotIn(0, expected)
                        self.assertEqual([g.codepoint for g in buf.glyph_infos], expected)
                        self.assertEqual([(p.x_advance, p.y_advance, p.x_offset, p.y_offset)
                                          for p in buf.glyph_positions], [(800, 0, 0, 0)] * len(text))
