from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


def luminance(hex_color):
    rgb = [int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4)]
    return sum(w * (x / 12.92 if x <= .04045 else ((x + .055) / 1.055)**2.4)
               for x, w in zip(rgb, (.2126, .7152, .0722)))


class SiteAppearanceTests(unittest.TestCase):
    def test_text_contrast_in_day_and_night(self):
        css = (ROOT / 'assets/appearance.css').read_text()
        palette = {key: (day, night) for key, day, night in re.findall(
            r'--(\w+): light-dark\(#([\da-f]{6}), #([\da-f]{6})\)', css)}
        for mode in (0, 1):
            for ink in ('text', 'secondary', 'muted', 'accent', 'violet',
                        'red', 'orange', 'yellow', 'green', 'cyan'):
                for surface in ('paper', 'panel', 'surface'):
                    with self.subTest(mode=('day', 'night')[mode], ink=ink, surface=surface):
                        lo, hi = sorted(luminance(palette[key][mode]) for key in (ink, surface))
                        self.assertGreaterEqual((hi + .05) / (lo + .05), 4.5)

    def test_pages_use_shared_palette(self):
        pages = [*ROOT.glob('*.html'), *ROOT.glob('studies/**/*.html'),
                 ROOT / 'specimen/index.html']
        for page in pages:
            with self.subTest(page=page.relative_to(ROOT)):
                html = page.read_text()
                match = re.search(r'<link rel="stylesheet" href="([^"]*assets/appearance\.css)">', html)
                self.assertIsNotNone(match)
                self.assertEqual((page.parent / match[1]).resolve(), ROOT / 'assets/appearance.css')
                self.assertNotIn('light-dark(', html)
