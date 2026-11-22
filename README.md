# Confinium Mono

Confinium Mono is an original upright geometric monospace under development.
No third-party font outlines or font images were used as drawing inputs.

## Current family: 800-unit Grid

Start with the **[typeface home page](index.html)** for a quick look at the family,
or open the **[Explorer](explorer.html)** to try it yourself. Grid, Open,
Dense, and Hollow each map 416 Unicode characters, including all printable
ASCII, broad European Latin coverage, and the modern Russian, Ukrainian,
and Belarusian alphabets. [Confinium Mono Variable](studies/variable-repertoire/)
covers the same repertoire from weight 100 to 700, with Book at 400. At 700,
its outlines and horizontal metrics match Full Grid. Thin and Book are
generated constructions, not individually optically refined masters.

See the [full-family fonts and proofs](studies/grid-token-bold/full-family/)
and the [design process archive](process.html). These are review builds,
not a production release.

## Install the font family

Download **ConfiniumMono-Family.zip** from the [Install page](https://scetrov.github.io/confinium-mono/install.html) or [GitHub Releases](https://github.com/Scetrov/confinium-mono/releases) and unzip it. Choose the font package, not GitHub’s source archive. Choose the variable font for Grid weights 100–700. For a fixed Bold, choose Full Grid; Full Open, Full Dense, and Full Hollow are alternative cuts, not weights on the slider. All five come as desktop TTFs and web WOFF2s. Older variable-only packages omit the static cuts. Remove any earlier copy of the same family before updating.

- **Windows 10/11:** Right-click the desired TTFs in `desktop/` and select **Install** (on Windows 11 you may need **Show more options**). **Install for all users** requires administrator access.
- **macOS:** Double-click each desired TTF, then click **Install** in Font Book.
- **Linux (Fontconfig):** Run these commands from the extracted folder:

  ```sh
  mkdir -p ~/.local/share/fonts/confinium-mono
  cp desktop/*.ttf ~/.local/share/fonts/confinium-mono/
  fc-cache -f ~/.local/share/fonts/confinium-mono
  ```

Reopen your editor or terminal, select **Confinium Mono Variable Repertoire**, and start at weight 400. Apps with variable-weight controls can also select intermediate weights such as 175.

### Self-host the webfont

Copy `web/ConfiniumMono-Variable.woff2` and `OFL.txt` into your site's `fonts/` directory. No desktop installation is needed. Adjust the URL for sites hosted under a subpath:

```css
@font-face {
  font-family: "Confinium Mono Web";
  src: url("/fonts/ConfiniumMono-Variable.woff2") format("woff2");
  font-weight: 100 700;
  font-style: normal;
  font-display: swap;
}
pre, code, kbd, samp { font-family: "Confinium Mono Web", monospace; }
```

For a static cut, use a separate CSS family name, its matching file (for example `ConfiniumMono-FullDense.woff2`), and `font-weight: 700` instead of a range.

Serve the file as `font/woff2`. For a separate font origin enable CORS. Check the request in the browser’s Network panel and inspect the rendered font at weights 400 and 700.

### 0.2.0 outline changes

The 800-unit family rebalances `f–i`, extends `i` to match `n`’s ink bounds, and matches the three `m` stems to capital `U`. The monospace advance is unchanged. The archived [equal-width `i`](studies/variable-repertoire/i-width-study/index.html) and [equal-stroke `m`](studies/variable-repertoire/m-stroke-study/index.html) studies retain their pre-promotion font inputs under `reference/`.

### Publishing (maintainers)

Push a numeric `MAJOR.MINOR.PATCH` tag on the reviewed commit (for example, `git tag 0.1.0` then `git push origin 0.1.0`). The release workflow tests the tagged tree, packages the variable and four static family TTFs and their WOFF2 equivalents, and publishes the ZIP and its SHA-256 checksum to GitHub Releases. The tag versions the distribution; it does not rewrite the font’s internal metadata.

## Archived experiment: 697-unit variable design

This separate nine-glyph experiment tested curves and weight interpolation in
a 697-unit cell. Its sources, fonts, and proofs are preserved below; it is
not the basis for the current family's outlines.

### Review the experiment

**Curve revision 02:** c/e/s/g have been reconstructed after review found
kinked curves and uneven bowl thickness. Compare the actual headless-Chromium
captures: [before](verification/curves-before.png) / [after](verification/curves-after.png).
The matching HTML files embed each version's font, so the comparison will not
silently change on rebuild. Reload the specimen to see the revised font.

Open **[specimen/index.html](specimen/index.html)** in a browser. It has a live
100–700 weight slider, size control, all three masters and seven-weight small-size
proofs. For a static first look, open **[specimen/overview.png](specimen/overview.png)**:
rows are Thin, Book, Bold. The glyph-only PNGs are rendered exclusively with the
new family, without fallback. HTML interface labels use the system UI font and
are explicitly separated from the font samples.

If your browser blocks local fonts, from this directory run:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Then visit `http://localhost:8000/specimen/`. Stop the server with Ctrl-C.

Use **Appearance** in the navigation to choose Auto (system), Light, or Dark.
The setting is shared across pages served from the same origin. When opening
HTML files directly, browsers may store the setting separately for each file.

Please review:

1. Is the broad, softly rectangular O the right starting character?
2. Is the narrow, faceted zero distinct enough without being over-emphasised?
3. Are the Q step, g hook and straight y descender convincing together?
4. Are the c/e/s lower cuts too assertive, especially at Bold?
5. Does Book have the right colour, and does Thin remain useful at display sizes?

### Experiment files

- `sources/ConfiniumMono-{Thin,Book,Bold}.ufo`: editable cubic-outline masters.
- `sources/ConfiniumMono.designspace`: weight axis and seven named instances.
- `sources/coverage.json`: exact experiment coverage and spacing classification.
- `fonts/ConfiniumMono[wght].ttf`: variable TrueType, default Book 400.
- `fonts/ConfiniumMono-*.ttf`: seven static TrueType weights, 100–700.
- `sketches/`: dated vector drawing sheet, Thin / Book / Bold.
- `DESIGN-LOG.md`: decisions, revisions and remaining optical questions.
- `scripts/`: original drawing construction, standard-tool build and proof rendering.
- `tests/test_pilot.py` and `tests/test_curves.py`: experiment metrics, shaping,
  outline matching, ink progression, and curve geometry checks.

All 12 exported glyphs (`.notdef`, space, no-break space, and nine drawn
characters) advance exactly 697 units. UPM is 1,000. Ascender / descender /
line gap are 885 / −242 / 0, with matching hhea, typo and Windows metrics.
Cap height metadata is 700; x-height metadata is 500. Curved glyphs overshoot.
The lowercase x is not drawn yet, so its height cannot yet be verified.

### Build and edit the experiment

Requires Python 3.11+ and `uv`. `uv.lock` pins direct and transitive dependencies
with artifact hashes; this cut was built with Python 3.13 on Linux. Package
versions were checked against PyPI on 2026-11-20. No custom font compiler is used:
fontmake/ufo2ft/fontTools compile the sources; HarfBuzz checks shaping; Pillow's
FreeType renderer produces the PNG proofs.

```sh
uv sync --locked
# Build directly from the editable UFO masters:
uv run python scripts/build.py
uv run python -m unittest discover -s tests -v
uv run python -m fontTools.varLib.interpolatable sources/ConfiniumMono.designspace
uv run python scripts/proof.py
```

**Optional regeneration:** `uv run python scripts/draw.py` redraws the original
construction and **overwrites all three UFO masters and the dated sketch**.
Do not run it after manual outline edits unless you intend to discard those
edits. The normal build never invokes it. UFOs can be edited in a UFO-capable
font editor; preserve contour and point correspondence across masters.

Build timestamps use `SOURCE_DATE_EPOCH`, defaulting to the experiment’s date.
Statics are instantiated from the same compiled variable font, with standard
TrueType coordinate rounding. Two consecutive builds were checked for identical
SHA-256 hashes in this environment; cross-platform binary identity is not claimed.

### Experiment verification

The automated suite exercises seven statics plus the variable font at all 13
coordinates 100, 150, …, 700. It checks exported coverage, every glyph advance,
fixed-pitch metadata, bounds, line metrics, axis/default/instances, static outline
matching, and shaping with kerning enabled and disabled. It checks every pen
position and run totals, including 80-character rows at 55,760 units, and increasing
raster ink across the seven named weights for each drawn character.

Geometry regressions also check c/e/s/g for zero handles, unintended cubic
inflections and tangent discontinuities, and check g's concentric bowl corners.
These run on all three UFO masters and linear point interpolation at every
remaining named weight and midpoint. They caught the original defects before
the fix. To refresh the Chromium evidence after an intentional revision:

```sh
uv run python scripts/review_curves.py after
```

This requires `chromium` on PATH. It verifies font loading and uses a fresh
browser profile; visual inspection of the PNG remains a separate human task.

These are **experiment checks**, not the complete brief's acceptance tests. All tests
use actual supported characters; missing letters are not silently substituted.
FontTools' interpolatability report is also checked. Passing it does not certify
optical quality or absence of every geometric defect.

### Outside the experiment’s scope

- Remaining Latin, Cyrillic, numerals, punctuation, symbols and box drawing.
- Combining marks, canonical equivalence, language-specific forms and controls.
- K/k, M and Ж/ж ink traps: those glyphs are not part of this nine-glyph experiment.
- Full words such as `gypsy`, `easy access` and `minimum` cannot yet be proofed.
- Full no-fallback acceptance matrix, wrapping and discretionary-hyphen tests.
- Human O/0 transcription tests; thin small-size rendering needs particular review.
- Hinting, exhaustive outline QA, FontBakery/OTS release checks and release metadata.
- Q and g have intentional same-winding bowl/tail overlaps in the sources;
  these render as unions, but should be resolved or explicitly validated for release.

## Project links

[Live specimen](https://scetrov.github.io/confinium-mono/) ·
[Issues](https://github.com/Scetrov/confinium-mono/issues) ·
[Contributing](CONTRIBUTING.md) · [Security policy](SECURITY.md)

## Licence status

Copyright 2026, Scetrov, All Rights Reserved, Licensed under the OFL 1.1.
The fonts, editable font sources and font-specific drawing and build sources
are licensed under the [SIL Open Font License 1.1](OFL.txt), with no Reserved
Font Name. The OFL does not license the surrounding site, documentation, tests
or proof images as separate works.

Include `OFL.txt` in every font or font-source download package. The active
HTML proofs that embed fonts include a copy of the licence. Do not publish
`verification/curves-before.html` or `verification/curves-after.html`: these
historical proofs still embed pre-licence binaries. Archived checksums describe
the historical builds, not the current fonts. The fonts remain review builds.

[Programming arrows study](studies/programming-arrows/index.html): an isolated comparison of `->`, `<-`, `=>`, `<=`, and `>=` at four weights. Rebuild with `uv run python scripts/arrow_study.py`.

For local site builds and GitHub Pages deployment, see the [Hugo site guide](site/README.md).
