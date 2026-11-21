from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
CHROMIUM = shutil.which('chromium')


@unittest.skipUnless(CHROMIUM, 'Chromium is required to check computed specimen colours')
class ExplorerColoursTests(unittest.TestCase):
    def test_presets_custom_and_reset(self):
        probe = '''<script>
        const picker = document.querySelector('#inkSel');
        const input = document.querySelector('#customInk');
        const targets = ['.specimen', '.wf-text', '.glyph-btn'].map(s => document.querySelector(s));
        function choose(value) {
          picker.value = value;
          picker.dispatchEvent(new Event('change'));
          const colors = targets.map(el => getComputedStyle(el).color);
          if (new Set(colors).size !== 1) throw new Error('Specimens disagree');
          return colors[0];
        }
        for (const theme of ['light', 'dark']) {
          document.documentElement.dataset.theme = theme;
          const colors = Array.from(picker.options, option => choose(option.value));
          if (new Set(colors).size !== colors.length) throw new Error('Duplicate ink');
          input.value = '#123456';
          input.dispatchEvent(new Event('input'));
          if (picker.value !== 'custom' || choose('custom') !== 'rgb(18, 52, 86)')
            throw new Error('Custom ink did not apply');
          if (choose('default') !== colors[0]) throw new Error('Default did not reset');
        }
        document.documentElement.dataset.colourTest = 'passed';
        </script>'''
        html = (ROOT / 'explorer.html').read_text().replace('</html>', probe + '</html>')
        with TemporaryDirectory() as directory:
            path = Path(directory)
            shutil.copytree(ROOT / 'assets', path / 'assets')
            page = path / 'explorer.html'
            for stale in (False, True):
                with self.subTest(stale_shared_css=stale):
                    # Emulate cached CSS without the newly introduced accent tokens.
                    css = path / 'assets/appearance.css'
                    if stale:
                        css.write_text('\n'.join(line for line in css.read_text().splitlines()
                                                if not line.startswith(('  --red:', '  --orange:',
                                                                        '  --yellow:', '  --green:',
                                                                        '  --violet:'))))
                    page.write_text(html)
                    result = subprocess.run(
                        [CHROMIUM, '--headless', '--no-sandbox', '--no-first-run',
                         f'--user-data-dir={path / "profile"}', '--dump-dom', page.as_uri()],
                        capture_output=True, text=True, check=True, timeout=25)
                    self.assertIn('data-colour-test="passed"', result.stdout[:500])
