"""Refresh Hugo fragments from a standalone proof; never used by Hugo builds."""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
NAV = re.compile(r'<nav class="site-nav"[^>]*>.*?</nav>', re.S)
CURRENT = re.compile(r'<a\b[^>]*href="([^"]+)"[^>]*aria-current="page"')


def import_proof(page):
    page = page.resolve()
    route = page.relative_to(ROOT)
    if route.suffix != '.html' or 'verification' in route.parts:
        raise ValueError(f'{route}: expected a public HTML proof')
    payload = page.read_bytes().decode('utf-8')
    match = NAV.search(payload)
    if not match:
        raise ValueError(f'{route}: missing shared navigation boundary')
    nav = json.loads((SITE / 'data/navigation.json').read_text())
    keys = {href: key for key, _, href in nav['primary'] + nav['studies']}
    keys['index.html'] = 'home'
    active = keys.get(route.as_posix(), '')
    current = CURRENT.search(match[0])
    if current:
        target = (page.parent / current[1]).resolve().relative_to(ROOT)
        active = keys.get(target.as_posix(), active)
    fragment = route.with_suffix('')
    content = SITE / 'content'/ route.with_suffix('.md')
    if content.name == "index.md":
        content = content.with_name("page-index.md")
    metadata = {'url': f'/{route.as_posix()}', 'proof': f'proofs/{fragment.as_posix()}',
                'depth': len(route.parts) - 1, 'active': active}
    # Updating generated specimen content must not overwrite Hugo-owned routes.
    if not content.exists():
        content.parent.mkdir(parents=True, exist_ok=True)
        content.write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    else:
        metadata = json.loads(content.read_text(encoding='utf-8'))
    for suffix, value in [('before', payload[:match.start()]), ('after', payload[match.end():])]:
        path = SITE / 'assets' / f"{metadata['proof']}.{suffix}.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value.encode('utf-8'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pages', nargs='+', type=Path)
    for path in parser.parse_args().pages:
        import_proof(path)
