import base64
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Links(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.links.append(dict(attrs))


class HomeTests(unittest.TestCase):
    def test_home_and_shared_navigation_links(self):
        home = ROOT / 'index.html'
        explorer = ROOT / 'explorer.html'
        study = ROOT / 'studies/programming-arrows/index.html'
        pages = [*ROOT.glob('*.html'), *ROOT.glob('studies/**/*.html'), ROOT / 'specimen/index.html']
        pages = [page for page in pages if 'verification' not in page.relative_to(ROOT).parts]
        for page in pages:
            with self.subTest(page=page.relative_to(ROOT)):
                html = page.read_text()
                nav = Links(re.search(r'<nav class="site-nav".*?</nav>', html, re.S)[0]).links
                self.assertEqual((page.parent / nav[0]['href']).resolve(), home)
                self.assertEqual((page.parent / nav[1]['href']).resolve(), explorer)
                ligature_links = [link for link in nav if (page.parent / link['href']).resolve() == study]
                self.assertEqual(len(ligature_links), 1)
                self.assertIn('>Programming Ligatures</a>', html)
                if page == home:
                    self.assertEqual(nav[0]['aria-current'], 'page')
                    for link in Links(html).links:
                        path = unquote(urlsplit(link['href']).path)
                        self.assertTrue((ROOT / path).is_file(), path)
                if page == explorer:
                    self.assertEqual(nav[1]['aria-current'], 'page')

    def test_specimens_use_current_font_binaries(self):
        html = (ROOT / 'index.html').read_text()
        faces = dict(re.findall(r'@font-face\{font-family:(Home\w+);font-weight:[\d ]+;'
                                r'src:url\(data:font/ttf;base64,([^)]*)\)', html))
        variable = ROOT / 'studies/variable-repertoire/fonts/ConfiniumMono-VariableRepertoire[wght].ttf'
        family = ROOT / 'studies/grid-token-bold/full-family/fonts'
        expected = {f'Home{cut}': family / f'ConfiniumMono-Full{cut}.ttf'
                    for cut in ('Grid', 'Open', 'Dense', 'Hollow')}
        expected['HomeVariable'] = variable
        self.assertEqual(faces.keys(), expected.keys())
        for name, path in expected.items():
            self.assertTrue(base64.b64decode(faces[name]) == path.read_bytes(), name)
