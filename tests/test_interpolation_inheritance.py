"""Discover inherited outlines independently of the variable build rules."""
import unittest
from pathlib import Path
from unicodedata import normalize

from fontTools.pens.areaPen import AreaPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[1]
GRID = ROOT / 'studies/grid-token-bold/full-family/fonts/ConfiniumMono-FullGrid.ttf'
VARIABLE = ROOT / 'studies/variable-repertoire/fonts/ConfiniumMono-VariableRepertoire[wght].ttf'
WEIGHTS = (100, 175, 250, 400, 550, 700)
SHORT_ASCENDERS = {'ḃ', 'ĥ'}


def topology(glyph):
    return glyph.coordinates[:], glyph.endPtsOfContours, list(glyph.flags)


class InterpolationInheritanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with TTFont(GRID) as grid, TTFont(VARIABLE) as variable:
            cls.cmap = grid.getBestCmap()
            cls.bold = grid['glyf']
            cls.samples = {w: instantiateVariableFont(variable, {'wght': w}, overlap=False)
                           for w in WEIGHTS}

    def test_matching_bold_bases_stay_aligned(self):
        pairs = []
        for cp, name in self.cmap.items():
            char = chr(cp)
            nfd = normalize('NFD', char)
            if len(nfd) < 2 or ord(nfd[0]) not in self.cmap:
                continue
            base_name = self.cmap[ord(nfd[0])]
            base = self.bold[base_name]
            glyph = self.bold[name]
            scale = .9 if char in SHORT_ASCENDERS else 1
            if (nfd[0] in 'ij' and char != 'į'):
                count = base.endPtsOfContours[0] + 1
            else:
                count = len(base.coordinates)
            expected = [(x, round(y*scale)) for x, y in base.coordinates[:count]]
            if list(glyph.coordinates[:count]) == expected:
                pairs.append((char, name, base_name, count, scale))
        self.assertGreaterEqual(len(pairs), 186)
        for char, name, base_name, count, scale in pairs:
            for weight, font in self.samples.items():
                with self.subTest(char=char, weight=weight):
                    g = font['glyf']
                    for actual, base in zip(g[name].coordinates[:count], g[base_name].coordinates[:count], strict=True):
                        self.assertEqual(actual[0], base[0])
                        self.assertAlmostEqual(actual[1], base[1]*scale, delta=1 if scale != 1 else 0)
                    self.assertEqual(font['hmtx'][name][0], 800)

    def test_identical_latin_and_cyrillic_bold_outlines_stay_identical(self):
        latin = {chr(cp): name for cp, name in self.cmap.items()
                 if cp < 128 and chr(cp).isalpha()}
        pairs = []
        for cp, name in self.cmap.items():
            if 0x400 <= cp <= 0x52F:
                for char, base in latin.items():
                    if topology(self.bold[name]) == topology(self.bold[base]):
                        pairs.append((char, chr(cp), base, name))
        self.assertGreaterEqual(len(pairs), 20)
        self.assertIn(('T', 'Т', 'T', 'uni0422'), pairs)
        for latin_char, cyrillic_char, base, name in pairs:
            for weight, font in self.samples.items():
                with self.subTest(pair=latin_char+cyrillic_char, weight=weight):
                    g = font['glyf']
                    self.assertEqual(topology(g[name]), topology(g[base]))

    def test_visible_glyphs_keep_ink_and_exact_bold(self):
        glyphsets = {weight: font.getGlyphSet() for weight, font in self.samples.items()}
        for char, name in self.cmap.items():
            bold = self.bold[name]
            if not bold.numberOfContours:
                continue
            for weight, font in self.samples.items():
                with self.subTest(codepoint=f'U+{char:04X}', weight=weight):
                    glyph = font['glyf'][name]
                    self.assertEqual(glyph.endPtsOfContours, bold.endPtsOfContours)
                    glyphset = glyphsets[weight]
                    path = RecordingPen()
                    glyphset[name].draw(path)
                    pen = AreaPen(glyphset)
                    for operation, args in path.value:
                        getattr(pen, operation)(*args)
                        if operation == 'closePath':
                            self.assertNotEqual(pen.value, 0, 'collapsed contour')
                            pen = AreaPen(glyphset)
                    if weight == 700:
                        self.assertEqual(topology(glyph), topology(bold))
