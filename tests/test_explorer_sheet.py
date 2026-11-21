import base64
import io
import json
from pathlib import Path
import re
import unittest

from fontTools.ttLib import TTFont


class ExplorerSheetTests(unittest.TestCase):
    def test_inventory_matches_embedded_fonts(self):
        html = (Path(__file__).resolve().parents[1] / 'explorer.html').read_text()
        data = json.loads(re.search(r'const inventory = (.*?);\n', html)[1])
        faces = dict(re.findall(r'@font-face\{font-family:(exp_\w+);src:url\(data:font/ttf;base64,([^)]*)\)', html))
        self.assertEqual(set(faces), set(data['faces']))
        for key, encoded in faces.items():
            with TTFont(io.BytesIO(base64.b64decode(encoded))) as font:
                self.assertEqual(data['faces'][key], sorted(font.getBestCmap()))
        default = re.search(r'<option value="(exp_\w+)" selected', html)[1]
        self.assertEqual(set(data['faces'][default]), set(map(int, data['entries'])))
        for ch, group in [('Þ','Extended Latin'),('ґ','Cyrillic'),('5','Figures'),('€','Punctuation & symbols'),
                          ('\u0301','Combining marks'),('\xa0','Spaces'),('a','Basic Latin')]:
            self.assertIn(group, data['entries'][str(ord(ch))][1])

        for ch, groups in [('Þ', {'Nordic', 'Latin', 'Icelandic', 'Uppercase'}),
                           ('ø', {'Nordic', 'Faroese', 'Danish', 'Norwegian'}),
                           ('ї', {'Cyrillic', 'Ukrainian'}), ('ў', {'Cyrillic', 'Belarusian'}),
                           ('Ж', {'Cyrillic', 'Russian', 'Ukrainian', 'Belarusian'})]:
            self.assertTrue(groups.issubset(data['entries'][str(ord(ch))][1]))
        from html import unescape
        selector = re.search(r'<select id="sheetCategory">(.*?)</select>', html)[1]
        options = {unescape(s) for s in re.findall(r'<option>(.*?)</option>', selector)}
        self.assertEqual(options, {'All characters'} | {g for _, groups in data['entries'].values() for g in groups})
