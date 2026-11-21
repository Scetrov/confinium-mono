from pathlib import Path
from unicodedata import normalize
import unittest

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
import uharfbuzz as hb

ROOT = Path(__file__).resolve().parents[1] / 'studies'
STUDY = ROOT / 'grid-token-bold/av-knees'
CURRENT = STUDY / 'reference/ConfiniumMono-VariableRepertoire[wght].ttf'


def shape(font, text):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf)
    return [(g.codepoint, p.x_advance, p.x_offset, p.y_offset)
            for g, p in zip(buf.glyph_infos, buf.glyph_positions)]


class BookKneeTests(unittest.TestCase):
    def test_variable_candidates_preserve_marks_and_shape_canonically(self):
        with TTFont(CURRENT) as current:
            cmap = current.getBestCmap()
            bases = set('AVWvw')
            accents = {chr(cp): normalize('NFD', chr(cp))[0] for cp in cmap
                       if len(normalize('NFD', chr(cp))) == 2 and normalize('NFD', chr(cp))[0] in bases}
            self.assertEqual(set(accents), set('ÀÁÂÃÄÅĀĂĄŴŵẀẁẂẃẄẅ'))
            current_faces = {w: instantiateVariableFont(current, {'wght': w}, overlap=False) for w in (100, 400, 700)}
            differences = []
            for width in (128, 144):
                path = STUDY / f'ConfiniumMono-MidlineKneesW{width}-Variable.ttf'
                hbfont = hb.Font(hb.Face(path.read_bytes()))
                changed = bases | {cmap[ord(c)] for c in accents}
                with TTFont(path) as variable:
                    self.assertEqual(variable.getBestCmap(), cmap)
                    self.assertEqual(variable['GSUB'].compile(variable), current['GSUB'].compile(current))
                    for weight, reference in current_faces.items():
                        hbfont.set_variations({'wght': weight})
                        face = instantiateVariableFont(variable, {'wght': weight}, overlap=False)
                        old, new = reference['glyf'], face['glyf']
                        self.assertEqual({n for n in current.getGlyphOrder()
                                          if old[n].getCoordinates(old) != new[n].getCoordinates(new)}, changed)
                        self.assertEqual([p[1] for p in shape(hbfont, 'vv w wave weave')], [800] * 15)
                        for char, base in accents.items():
                            name = cmap[ord(char)]
                            with self.subTest(width=width, weight=weight, char=char):
                                self.assertEqual(shape(hbfont, char), shape(hbfont, normalize('NFD', char)))
                                self.assertEqual(shape(hbfont, char), [(face.getGlyphID(name), 800, 0, 0)])
                                self.assertEqual(new[name].coordinates[:len(new[base].coordinates)], new[base].coordinates[:])
                                self.assertEqual(new[name].coordinates[len(new[base].coordinates):],
                                                 old[name].coordinates[len(old[base].coordinates):])
                        if weight == 400:
                            differences.append({n: list(new[n].getCoordinates(new)[0]) for n in changed})
            self.assertEqual({n for n in differences[0] if differences[0][n] != differences[1][n]},
                             {'w', *(cmap[ord(c)] for c in 'ŵẁẃẅ')})
