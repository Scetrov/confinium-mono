"""Shared OFL metadata for editable fonts and standalone HTML proofs."""
from html import escape
from pathlib import Path

OFL_PATH = Path(__file__).resolve().parents[1] / 'OFL.txt'
LICENSE_NAME = 'SIL Open Font License, Version 1.1'
LICENSE_URL = 'https://openfontlicense.org/'


def apply_ufo_license(info):
    info.copyright = OFL_PATH.read_text(encoding='utf-8').splitlines()[0]
    info.openTypeNameLicense = LICENSE_NAME
    info.openTypeNameLicenseURL = LICENSE_URL
    info.openTypeOS2Type = []  # fsType 0: installable embedding


def write_licensed_html(path, html):
    licence = escape(OFL_PATH.read_text(encoding='utf-8'))
    notice = (
        '<details style="margin:2rem 5vw;font:14px/1.5 system-ui,sans-serif">'
        '<summary>Font licence — SIL Open Font License 1.1</summary>'
        f'<pre style="white-space:pre-wrap">{licence}</pre></details>\n'
    )
    for closing_tag in ('</body>', '</html>'):
        if closing_tag in html:
            html = html.replace(closing_tag, notice + closing_tag, 1)
            break
    else:
        html += '\n' + notice
    path.write_text(html, encoding='utf-8')
