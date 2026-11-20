from pathlib import Path
import unittest

from fontTools.pens.areaPen import AreaPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[1]


class VariableRepertoireTests(unittest.TestCase):
    def test_coverage_metrics_and_weight_progression(self):
        path = ROOT/'studies/variable-repertoire/fonts/ConfiniumMono-VariableRepertoire[wght].ttf'
        with TTFont(path) as variable, TTFont(
                ROOT/'studies/grid-token-bold/full-family/fonts/ConfiniumMono-FullGrid.ttf') as grid:
            cmap = variable.getBestCmap()
            self.assertEqual(set(cmap),set(grid.getBestCmap()))
            self.assertEqual(variable['GSUB'].compile(variable),grid['GSUB'].compile(grid))
            previous = {}
            for weight in (100,250,400,550,700):
                face = instantiateVariableFont(variable,{'wght':weight},overlap=False)
                glyphs = face.getGlyphSet()
                for cp,n in cmap.items():
                    with self.subTest(cp=hex(cp),weight=weight):
                        self.assertEqual(glyphs[n].width,grid['hmtx'][grid.getBestCmap()[cp]][0])
                        if chr(cp).isspace(): continue
                        pen=AreaPen(glyphs); glyphs[n].draw(pen)
                        self.assertGreater(abs(pen.value),previous.get(cp,0)); previous[cp]=abs(pen.value)
                if weight == 700:
                    for n in grid.getGlyphOrder():
                        self.assertEqual(face['glyf'][n].getCoordinates(face['glyf']),
                                         grid['glyf'][n].getCoordinates(grid['glyf']),n)
                        self.assertEqual(face['hmtx'][n],grid['hmtx'][n],n)
