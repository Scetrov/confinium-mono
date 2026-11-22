from base64 import b64decode
from pathlib import Path
import re
import unittest
from unicodedata import normalize

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[1]
GRID = ROOT / 'studies/grid-token-bold'
FAMILY = GRID / 'full-family/fonts'
STUDY = GRID / 'av-knees'
VARIABLE = ROOT / 'studies/variable-repertoire/fonts/ConfiniumMono-VariableRepertoire[wght].ttf'


def coords(font, name):
    return font['glyf'][name].getCoordinates(font['glyf'])


class MidlinePromotionTests(unittest.TestCase):
    def test_lowercase_v_cleft_matches_both_w_valleys(self):
        def check(font):
            v, w = (coords(font, name)[0] for name in 'vw')
            self.assertEqual((v[3][1], v[3][1]), (w[3][1], w[6][1]))
            self.assertEqual(v[3][0], 400)
            self.assertEqual(v[2][1], v[4][1])
        for style in ('Grid', 'Open', 'Dense'):
            with TTFont(FAMILY / f'ConfiniumMono-Full{style}.ttf') as font:
                check(font)
        with TTFont(VARIABLE) as font:
            for weight in (100, 125, 175, 250, 400, 550, 700):
                with self.subTest(weight=weight):
                    check(instantiateVariableFont(font, {'wght': weight}, overlap=False))

    def test_grid_matches_approved_study_outlines(self):
        with (TTFont(FAMILY / 'ConfiniumMono-FullGrid.ttf') as full,
              TTFont(STUDY / 'ConfiniumMono-GridToken-AVKnees152StraightAVW.ttf') as upper,
              TTFont(STUDY / 'ConfiniumMono-GridToken-LowercaseVWKnees144W.ttf') as lower):
            for glyph in 'AVw':
                self.assertEqual(coords(full, glyph), coords(upper if glyph.isupper() else lower, glyph))
            v, old_v = coords(full, 'v')[0], coords(lower, 'v')[0]
            self.assertEqual(list(v[:2]) + list(v[5:]), list(old_v[:2]) + list(old_v[5:]))
            for glyph, thickness in [('Q', 128), ('Y', 144)]:
                with TTFont(GRID / f'diagonals/fonts/ConfiniumMono-Diagonal{thickness}.ttf') as approved:
                    self.assertEqual(coords(full, glyph), coords(approved, glyph))

    def test_all_static_styles_keep_qy_and_inherit_approved_bases(self):
        for style in ('Grid', 'Open', 'Dense', 'Hollow'):
            history = (GRID / f'fonts/ConfiniumMono-GridToken-{style}.ttf' if style != 'Hollow'
                       else GRID / 'hollow/ConfiniumMono-GridToken-Hollow.ttf')
            with (self.subTest(style=style), TTFont(history) as archived,
                  TTFont(FAMILY / f'ConfiniumMono-Full{style}.ttf') as full):
                self.assertEqual(coords(full, 'uni0410'), coords(full, 'A'))
                for glyph in 'QY':
                    self.assertEqual(coords(full, glyph), coords(archived, glyph))
                for glyph in 'AVW':
                    self.assertNotEqual(coords(full, glyph), coords(archived, glyph))
                if style == 'Hollow':
                    for glyph in 'AVWvw':
                        self.assertGreater(full['glyf'][glyph].numberOfContours, 1)
                    continue  # Shells are traced as complete silhouettes, not point-for-point copies.
                for cp, name in full.getBestCmap().items():
                    text = normalize('NFD', chr(cp))
                    if len(text) == 2 and text[0] in 'AWw':
                        base_points = coords(full, text[0])[0]
                        self.assertEqual(coords(full, name)[0][:len(base_points)], base_points[:])

    def test_variable_matches_approved_book_candidate(self):
        with (TTFont(VARIABLE) as variable,
              TTFont(STUDY / 'ConfiniumMono-MidlineKneesW144-Variable.ttf') as approved):
            for weight in (100, 400, 700):
                current = instantiateVariableFont(variable, {'wght': weight}, overlap=False)
                control = instantiateVariableFont(approved, {'wght': weight}, overlap=False)
                for cp, name in current.getBestCmap().items():
                    base = normalize('NFD', chr(cp))[0]
                    if base in 'AV' or (base == 'w' and weight == 700):
                        self.assertEqual(coords(current, name), coords(control, name), (weight, name))
                self.assertEqual(coords(current, 'uni0410'), coords(current, 'A'))

    def test_site_title_face_is_the_current_grid_font(self):
        css = (ROOT / 'assets/site-titles.css').read_text()
        data = re.search(r'data:font/ttf;base64,([A-Za-z0-9+/=]+)', css)[1]
        self.assertEqual(b64decode(data), (FAMILY / 'ConfiniumMono-FullGrid.ttf').read_bytes())
