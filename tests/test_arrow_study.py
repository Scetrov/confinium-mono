import base64
from io import BytesIO
from pathlib import Path
import re
import sys
import unittest

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
import uharfbuzz as hb

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import arrow_study as study


class ArrowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        page = (study.OUT / 'index.html').read_text()
        cls.data = base64.b64decode(re.search(r'data:font/ttf;base64,([^)]*)', page)[1])
        cls.font = TTFont(BytesIO(cls.data))

    def test_proof_is_current_ascii_only(self):
        self.assertEqual(self.data, study.build_font())
        self.assertEqual(set(self.font.getBestCmap()), set(range(32, 127)))

    def test_shaping_and_geometry(self):
        for weight in (100, 175, 400, 700):
            face = hb.Font(hb.Face(self.data))
            face.set_variations({'wght': weight})
            static = instantiateVariableFont(self.font, {'wght': weight})
            for text, (_, name) in zip(('->', '<-', '=>', '<=', '>=', '!=', '!==', '==', '===', '<->', '<=>'), study.RULES):
                glyph = static['glyf'][name]
                comparison = text in ('<=', '>=')
                count = {'<=>': 2, '!=': 3, '!==': 4, '==': 2, '===': 3}.get(text, 2 if comparison else 1)
                self.assertEqual(glyph.numberOfContours, count)
                if comparison:
                    points = glyph.coordinates
                    # At each terminal compare the rule with the lower edge of
                    # the chevron. Both edges of the rule must follow its slope.
                    ends = []
                    for x in (400, 1200):
                        arm = min(y for px, y in points[:7] if px == x)
                        low, high = sorted(y for px, y in points[7:] if px == x)
                        self.assertGreater(arm, high)
                        ends.append((arm, low, high))
                    rise = 200 if text == '>=' else -200
                    self.assertEqual([b-a for a, b in zip(*ends)], [rise]*3)
                bounds = {'!=': (340, 1260), '!==': (620, 1780), '==': (340, 1260), '===': (620, 1780),
                          '<->': (120, 2280), '<=>': (120, 2280)}
                self.assertEqual((glyph.xMin, glyph.xMax), bounds.get(text, (400, 1200) if comparison else (120, 1480)))
                if weight in (100, 400, 700):
                    self.assertEqual(list(glyph.coordinates), [point for path in study.contours(name, weight) for point in path])
                for feature in ({}, {'dlig': False}, {'dlig': True}):
                    buf = hb.Buffer()
                    buf.add_str('a' + text + 'b = c')
                    buf.guess_segment_properties()
                    hb.shape(face, buf, feature)
                    lig = feature.get('dlig')
                    names = ['a', *([name] if lig else [self.font.getBestCmap()[ord(c)] for c in text]), 'b', 'space', 'equal', 'space', 'c']
                    self.assertEqual([self.font.getGlyphName(g.codepoint) for g in buf.glyph_infos], names)
                    self.assertEqual([p.x_advance for p in buf.glyph_positions], [800, *([800 * len(text)] if lig else [800] * len(text)), *([800] * 5)])

            for plain, crossed in [('equalPair.alt', 'notEqual.alt'), ('equalTriple.alt', 'notStrictEqual.alt')]:
                regular = static['glyf'][plain]
                negated = static['glyf'][crossed]
                self.assertEqual(regular.coordinates[:], negated.coordinates[:-4])
                self.assertEqual(regular.endPtsOfContours, negated.endPtsOfContours[:-1])
