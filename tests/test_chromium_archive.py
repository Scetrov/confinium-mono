import hashlib
from pathlib import Path
import tempfile
import unittest

from scripts.chromium_proof import archive_capture
from scripts.study_reference import GRID_REFERENCE


class ChromiumArchiveTests(unittest.TestCase):
    def test_recapture_keeps_original_and_earlier_recaptures(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            generated = root / 'generated.png'
            target = root / 'verification' / 'chromium.png'
            captures = []
            for content in (b'original', b'revision one', b'revision two'):
                generated.write_bytes(content)
                captures.append((archive_capture(generated, target), content))
            self.assertEqual(captures[0][0], target)
            self.assertEqual(len({path for path, _ in captures}), 3)
            for path, content in captures:
                self.assertEqual(path.read_bytes(), content)

    def test_grid_reference_matches_its_manifest(self):
        root = GRID_REFERENCE.parents[2]
        for line in (GRID_REFERENCE / 'SHA256SUMS').read_text().splitlines():
            expected, relative = line.split(maxsplit=1)
            with self.subTest(path=relative):
                self.assertEqual(hashlib.sha256((root / relative).read_bytes()).hexdigest(), expected)
