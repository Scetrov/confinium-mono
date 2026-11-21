from pathlib import Path
import unittest

from fontTools.ttLib import TTFont
import uharfbuzz as hb

STUDY = Path(__file__).resolve().parents[1] / 'studies/grid-token-bold'
BASE = STUDY / 'reference/ConfiniumMono-GridToken-Grid.ttf'
TRIAL = STUDY / 'av-knees/ConfiniumMono-GridToken-AVKnees.ttf'


class AVKneeTests(unittest.TestCase):
    def test_only_av_outlines_change(self):
        with TTFont(BASE) as base, TTFont(TRIAL) as trial:
            self.assertEqual(trial.getBestCmap(), base.getBestCmap())
            self.assertEqual(trial.getGlyphOrder(), base.getGlyphOrder())
            self.assertEqual(trial['hmtx'].metrics, base['hmtx'].metrics)
            self.assertEqual(trial['head'].unitsPerEm, base['head'].unitsPerEm)
            for metric in ('ascent', 'descent', 'lineGap'):
                self.assertEqual(getattr(trial['hhea'], metric), getattr(base['hhea'], metric))
            old, new = base['glyf'], trial['glyf']
            for name in base.getGlyphOrder():
                with self.subTest(glyph=name):
                    if name not in ('A', 'V'):
                        self.assertEqual(new[name].getCoordinates(new), old[name].getCoordinates(old))
                        continue
                    g = new[name]
                    self.assertEqual((g.xMin, g.yMin, g.xMax, g.yMax), (80, 0, 720, 800))
                    self.assertEqual(g.numberOfContours, 2 if name == 'A' else 1)
                    self.assertNotEqual(g.getCoordinates(new), old[name].getCoordinates(old))
                    y_end = 0 if name == 'A' else 800
                    coords = set(g.getCoordinates(new)[0])
                    for x in (80, 720):
                        self.assertTrue({(x, y_end), (x, 400)} <= coords)

    def test_fuller_knees_keep_outer_silhouette_and_parallel_diagonals(self):
        fuller = TRIAL.with_name(f'{TRIAL.stem}152.ttf')
        with TTFont(TRIAL) as first, TTFont(fuller) as revised:
            self.assertEqual(first.getBestCmap(), revised.getBestCmap())
            self.assertEqual(first['hmtx'].metrics, revised['hmtx'].metrics)
            old, new = first['glyf'], revised['glyf']
            for name in first.getGlyphOrder():
                before, ends, flags = old[name].getCoordinates(old)
                after, new_ends, new_flags = new[name].getCoordinates(new)
                if name not in ('A', 'V'):
                    self.assertEqual((before, ends, flags), (after, new_ends, new_flags), name)
                    continue
                def upright(points):
                    return {(x, y if name == 'A' else 800 - y) for x, y in points}
                removed = {(240, 413), (560, 413), (400, 653)}
                added = {(275, 429), (525, 429), (400, 638)}
                if name == 'V':
                    added |= {(240, 400), (560, 400)}
                self.assertEqual(upright(after), (upright(before) - removed) | added)
                self.assertAlmostEqual(125 / 209, 240 / 400, delta=.005)
                self.assertAlmostEqual((275 - (80 + .6 * 29)) / (1 + .6**2)**.5,
                                       152, delta=.5)

    def test_straight_v_cleft_has_no_midline_notch(self):
        fuller = TRIAL.with_name(f'{TRIAL.stem}152.ttf')
        straight = TRIAL.with_name(f'{TRIAL.stem}152Straight.ttf')
        with TTFont(fuller) as before, TTFont(straight) as after:
            self.assertEqual(before.getBestCmap(), after.getBestCmap())
            self.assertEqual(before['hmtx'].metrics, after['hmtx'].metrics)
            old, new = before['glyf'], after['glyf']
            for name in before.getGlyphOrder():
                if name != 'V':
                    self.assertEqual(old[name].getCoordinates(old), new[name].getCoordinates(new), name)
            points, ends, _ = new['V'].getCoordinates(new)
            self.assertEqual(len(ends), 1)
            # Cyclic neighbors must be the inner tip and the cap. No third leg
            # of the cleft, no midline step, and no change to the outer bend.
            for x in (240, 560):
                i = list(points).index((x, 429))
                self.assertEqual({points[i - 1], points[(i + 1) % len(points)]},
                                 {(400, 162), (x, 800)})
                self.assertNotIn((x, 400), points)
            self.assertTrue({(80, 400), (720, 400)} <= set(points))
            self.assertAlmostEqual((400 - 240) / (429 - 162), .6, delta=.002)

    def test_straight_a_mirrors_v_and_clears_the_crossbar(self):
        v_only = TRIAL.with_name(f'{TRIAL.stem}152Straight.ttf')
        both = TRIAL.with_name(f'{TRIAL.stem}152StraightBoth.ttf')
        with TTFont(v_only) as before, TTFont(both) as after:
            self.assertEqual(before.getBestCmap(), after.getBestCmap())
            self.assertEqual(before['hmtx'].metrics, after['hmtx'].metrics)
            old, new = before['glyf'], after['glyf']
            for name in before.getGlyphOrder():
                if name != 'A':
                    self.assertEqual(old[name].getCoordinates(old), new[name].getCoordinates(new), name)
            points, ends, _ = new['A'].getCoordinates(new)
            self.assertEqual(len(ends), 2)
            counter = list(points[ends[0] + 1:])
            self.assertEqual(set(counter), {(240, 360), (560, 360), (400, 638), (240, 371), (560, 371)})
            for x in (240, 560):
                i = counter.index((x, 371))
                self.assertEqual({counter[i - 1], counter[(i + 1) % len(counter)]}, {(400, 638), (x, 360)})
                self.assertIn((x, 220), points)
            self.assertTrue({(80, 400), (720, 400), (320, 800), (480, 800)} <= set(points))

    def test_straight_w_changes_only_w_and_keeps_the_two_valleys_open(self):
        control = TRIAL.with_name(f'{TRIAL.stem}152StraightBoth.ttf')
        avw = TRIAL.with_name(f'{TRIAL.stem}152StraightAVW.ttf')
        with TTFont(control) as before, TTFont(avw) as after:
            self.assertEqual(before.getBestCmap(), after.getBestCmap())
            self.assertEqual(before['hmtx'].metrics, after['hmtx'].metrics)
            old, new = before['glyf'], after['glyf']
            for name in before.getGlyphOrder():
                if name != 'W':
                    self.assertEqual(old[name].getCoordinates(old), new[name].getCoordinates(new), name)
            w = new['W']
            self.assertEqual((w.xMin, w.yMin, w.xMax, w.yMax), (80, 0, 720, 800))
            points, ends, _ = w.getCoordinates(new)
            self.assertEqual(len(ends), 1)
            self.assertEqual({(800 - x, y) for x, y in points}, set(points))
            for wall, valley in ((208, 259), (592, 541)):
                i = list(points).index((wall, 419))
                self.assertEqual({points[i - 1], points[(i + 1) % len(points)]},
                                 {(wall, 800), (valley, 250)})
                self.assertAlmostEqual(abs(valley - wall) / (419 - 250), .30, delta=.005)
            self.assertTrue({(80, 400), (720, 400), (336, 560), (464, 560)} <= set(points))

    def test_lowercase_direct_joins_and_reference_parity(self):
        baseline = STUDY / 'lowercase-alphabet/fonts/ConfiniumMono-GridToken-LowercaseAlphabet.ttf'
        trial = TRIAL.with_name('ConfiniumMono-GridToken-LowercaseVWKnees.ttf')
        with TTFont(baseline) as before, TTFont(trial) as after:
            self.assertEqual(before.getBestCmap(), after.getBestCmap())
            self.assertEqual(before['hmtx'].metrics, after['hmtx'].metrics)
            old, new = before['glyf'], after['glyf']
            for name in before.getGlyphOrder():
                if name not in ('v', 'w'):
                    self.assertEqual(old[name].getCoordinates(old), new[name].getCoordinates(new), name)
            for name, wall, join, lower in [('v', 240, 325, (400, 132)), ('w', 208, 305, (269, 152))]:
                glyph = new[name]
                self.assertEqual((glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax), (80, 0, 720, 560))
                points, ends, _ = glyph.getCoordinates(new)
                self.assertEqual(len(ends), 1)
                self.assertEqual(set(points), {(800 - x, y) for x, y in points})
                self.assertTrue({(80, 280), (720, 280)} <= set(points))
                i = list(points).index((wall, join))
                self.assertEqual({points[i - 1], points[(i + 1) % len(points)]}, {(wall, 560), lower})
        for font in (baseline, trial):
            self.assert_shaping(font, 'Vv Ww vv w wave weave review view')

    def test_wider_lowercase_w_changes_only_outer_arms(self):
        control = TRIAL.with_name('ConfiniumMono-GridToken-LowercaseVWKnees.ttf')
        wider = control.with_name(f'{control.stem}144W.ttf')
        with TTFont(control) as before, TTFont(wider) as after:
            self.assertEqual(before.getBestCmap(), after.getBestCmap())
            self.assertEqual(before['hmtx'].metrics, after['hmtx'].metrics)
            old, new = before['glyf'], after['glyf']
            for name in before.getGlyphOrder():
                if name != 'w':
                    self.assertEqual(old[name].getCoordinates(old), new[name].getCoordinates(new), name)
            old_points = set(old['w'].getCoordinates(old)[0])
            points, ends, _ = new['w'].getCoordinates(new)
            self.assertEqual(len(ends), 1)
            self.assertEqual(set(points), {(800 - x, y) for x, y in points})
            replaced = {(208, 560), (208, 305), (269, 152), (592, 560), (592, 305), (531, 152)}
            added = {(224, 560), (224, 308), (276, 177), (576, 560), (576, 308), (524, 177)}
            self.assertEqual(set(points), old_points - replaced | added)
            i = list(points).index((224, 308))
            self.assertEqual({points[i - 1], points[i + 1]}, {(224, 560), (276, 177)})
        self.assert_shaping(wider, 'Vv Ww vv w wave weave review view')

    def test_proof_text_shapes_to_expected_cells(self):
        text = 'AV VA AVALON WAVE'
        variants = ('152', '152Straight', '152StraightBoth', '152StraightAVW')
        for path in (BASE, TRIAL, *(TRIAL.with_name(f'{TRIAL.stem}{s}.ttf') for s in variants)):
            with self.subTest(path=path.name):
                self.assert_shaping(path, text)

    def assert_shaping(self, path, text):
        font = hb.Font(hb.Face(path.read_bytes()))
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(font, buf)
        with TTFont(path) as trial:
            cmap = trial.getBestCmap()
            self.assertEqual([g.codepoint for g in buf.glyph_infos],
                             [trial.getGlyphID(cmap[ord(c)]) for c in text])
        self.assertEqual([p.x_advance for p in buf.glyph_positions], [800] * len(text))
