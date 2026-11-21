"""Render proof screenshots without replacing existing verification evidence."""
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import tempfile


def archive_capture(source: Path, target: Path) -> Path:
    """Use the canonical filename once, then create dated sibling captures."""
    target.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    candidate = target
    sequence = 0
    while True:
        try:
            output = candidate.open('xb')
        except FileExistsError:
            sequence += 1
            suffix = '' if sequence == 1 else f'-{sequence}'
            candidate = target.with_name(f'{target.stem}-{stamp}{suffix}{target.suffix}')
            continue
        try:
            with output, source.open('rb') as screenshot:
                shutil.copyfileobj(screenshot, output)
        except BaseException:
            candidate.unlink()
            raise
        return candidate


def capture_chromium(page: Path, target: Path, size: str, expected: str) -> Path:
    """Publish a capture only after Chromium confirms the embedded fonts loaded."""
    with tempfile.TemporaryDirectory(prefix='confinium-proof-') as tmp:
        profile = Path(tmp) / 'profile'
        screenshot = Path(tmp) / 'proof.png'
        result = subprocess.run([
            'chromium', '--headless', '--disable-gpu', '--no-first-run',
            f'--user-data-dir={profile}', '--virtual-time-budget=3000',
            f'--window-size={size}', f'--screenshot={screenshot}', '--dump-dom',
            page.resolve().as_uri(),
        ], check=True, capture_output=True, text=True)
        if expected not in result.stdout or not screenshot.is_file():
            raise RuntimeError(f'Chromium proof did not verify: {page}')
        path = archive_capture(screenshot, target)
    print(f'Chromium proof: {path}')
    return path
