"""Regression checks for the isolated Hollow display study."""
import importlib.util
import sys
from pathlib import Path
import unittest
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
import uharfbuzz as hb

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
try:
    spec = importlib.util.spec_from_file_location('hollow_study', ROOT / 'scripts/hollow_study.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
finally:
    sys.path.pop(0)


class HollowTests(unittest.TestCase):
    def test_hollow_cmap_advances_shaping_and_wireframe_ink(self):
        solid_path = module.STUDY / 'fonts/ConfiniumMono-GridToken-Grid.ttf'
        hollow_path = module.FONT
        solid = TTFont(solid_path)
        hollow = TTFont(hollow_path)
        self.assertEqual(set(hollow.getBestCmap()), set(solid.getBestCmap()))
        self.assertTrue(all(w == 800 for w, _ in hollow['hmtx'].metrics.values()))
        hbfont = hb.Font(hb.Face(hollow_path.read_bytes()))
        hbfont.scale = (1000, 1000)
        buf = hb.Buffer()
        buf.add_str('CONFINIUM 01')
        buf.guess_segment_properties()
        hb.shape(hbfont, buf, {'kern': False})
        self.assertEqual(len(buf.glyph_positions), 12)
        self.assertTrue(all(p.x_advance == 800 and p.x_offset == 0 for p in buf.glyph_positions))
        # Verify hollow interior on H stem (x=160, y_ufo=400 -> pil y=400) is white, while outer wall (x=94) is black.
        f_hollow = ImageFont.truetype(str(hollow_path), 1000)
        f_solid = ImageFont.truetype(str(solid_path), 1000)
        im_h = Image.new('L', (800, 1000))
        im_s = Image.new('L', (800, 1000))
        ImageDraw.Draw(im_h).text((0, 800), 'H', font=f_hollow, fill=255, anchor='ls')
        ImageDraw.Draw(im_s).text((0, 800), 'H', font=f_solid, fill=255, anchor='ls')
        self.assertEqual(im_h.getpixel((94, 400)), 255, 'outer wall solid')
        self.assertEqual(im_h.getpixel((160, 400)), 0, 'interior stem hollowed')
        self.assertLess(sum(im_h.get_flattened_data()), sum(im_s.get_flattened_data()))


if __name__ == '__main__':
    unittest.main()
