"""Check current-family TTFs with the reviewed Fontspector distribution."""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import zipfile

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
STATIC = Path('studies/grid-token-bold/full-family/fonts')
VARIABLE = Path('studies/variable-repertoire/fonts/ConfiniumMono-VariableRepertoire[wght].ttf')
FAMILIES = {STATIC / f'ConfiniumMono-Full{s}.ttf': f'Confinium Mono Full {s}'
            for s in ('Grid', 'Open', 'Dense', 'Hollow')}
FAMILIES[VARIABLE] = 'Confinium Mono VF'


def verified_cli(directory):
    archive = Path(os.environ['FONTSPECTOR_ARCHIVE'])
    pins = dict(line.split() for line in
                (ROOT / 'verification/fontspector/tool.sha256').read_text().splitlines())
    with archive.open('rb') as stream:
        if pins.get(hashlib.file_digest(stream, 'sha256').hexdigest()) != archive.name:
            raise ValueError('Fontspector archive does not match approved name and SHA-256')
        stream.seek(0)
        binary = 'fontspector.exe' if archive.suffix == '.zip' else 'fontspector'
        target = directory / binary
        if archive.suffix == '.zip':
            with zipfile.ZipFile(stream) as bundle:
                member, = [n for n in bundle.namelist() if Path(n).name == binary]
                with bundle.open(member) as src, target.open('wb') as dst:
                    shutil.copyfileobj(src, dst)
        else:
            with tarfile.open(fileobj=stream, mode='r:gz') as bundle:
                member, = [m for m in bundle if m.isfile() and Path(m.name).name == binary]
                with bundle.extractfile(member) as src, target.open('wb') as dst:
                    shutil.copyfileobj(src, dst)
    target.chmod(0o700)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--desktop', type=Path)
    parser.add_argument('files', nargs='*', type=Path)
    args = parser.parse_args()
    if args.desktop is not None:
        if args.files:
            parser.error('--desktop cannot be combined with files')
        inputs = {args.desktop / ('ConfiniumMono-Variable.ttf' if p == VARIABLE else p.name): family
                  for p, family in FAMILIES.items()}
        if set(args.desktop.glob('*.ttf')) != set(inputs):
            parser.error('expected exactly the five release TTFs')
    else:
        inputs = {p: FAMILIES[p] for p in args.files or FAMILIES}
    with tempfile.TemporaryDirectory() as temp:
        cli = verified_cli(Path(temp))
        for path, family in inputs.items():
            with TTFont(path) as font:
                name = font['name']
                style = 'Regular' if family == FAMILIES[VARIABLE] else 'Bold'
                if (name.getBestFamilyName(), name.getBestSubFamilyName()) != (family, style):
                    raise ValueError(f'{path}: expected {family} {style}')
            print(f'Checking {path}', flush=True)
            subprocess.run([cli, '--profile', 'universal', '--error-code-on', 'fail', path], check=True)


if __name__ == '__main__':
    main()
