# Confinium Mono — grid- and token-driven Bold direction study

A separate original design experiment, **not a replacement or rescaling of the
existing mixed-case variable experiment**. Family name remains Confinium Mono;
`Grid-Token Grid Bold`, `Grid-Token Open Bold`, and `Grid-Token Dense Bold` are distinct
study styles. They are not three weights and are not interpolation masters.

## Review

With the repository's local HTTP server running, visit:

**http://localhost:8000/studies/grid-token-bold/specimen/**

Or open `specimen/index.html` directly; its fonts are embedded to avoid local
font-loading restrictions and cache confusion. Re-run `proof` after changing
fonts: these HTML pages deliberately snapshot a build rather than hot-load it.

- `specimen/index.html`: equal-cap-height comparison with the previous experiment,
  three grid- and token-driven variants, repeated groups and 14 / 18 / 32 px samples.
- `specimen/detail.html`: enlarged C/E/S/G for inspecting joins and fillets.
- [Punctuation study](punctuation/index.html): isolated Grid Bold expansion with
  all 32 ASCII punctuation and operator characters.
- `specimen/grid-{Grid,Open,Dense}.svg`: all nine drawings on the 80-unit grid.
  Cyan lines are 1u; orange outlines mark the active box and centre axis.
- `verification/chromium.png`, `verification/detail.png`: captured browser proofs.
- `sources/*.ufo`: editable cubic-outline sources with overlaps resolved.
- `fonts/*.ttf`: three static Bold fonts. No installation is needed to review.
- `parameters.json`: explicit construction tokens in 1,000-UPM coordinates.
- `coverage.json`: exact mapping; all 12 exported glyphs occupy one cell.

All glyph samples use only the study fonts (or the existing Confinium Mono experiment
in the labelled comparison). Descriptive interface text uses the system font.
The SVG diagrams contain outlines, not substitute fonts.

## Optical diagonal thickness comparison

**[Q/Y: reference versus 128 / 144 / 160 normal units](diagonals/index.html)**
compares optically heavier 45° diagonals while retaining the Q bowl, Y outer
silhouette and 800-unit advances. It includes enlarged proofs, grid diagrams,
editable sources and three separate fonts. The previous versions remain intact.
See [the comparison notes](diagonals/README.md) for fixed constraints and the
intentional Q-tail extension beyond the active drawing box, within the cell.

## Q-tail alternative

**[Centred versus right-descending 45° Q](q-tail/index.html)** is a separate
comparison using the Grid bowl. The diagonal ends at y=−120 and x=720, with a
horizontal cut, leaving the counter and 800-unit advance unchanged. Its normal
stroke thickness is approximately 96 units (136 horizontally), intentionally
lighter than the reference tail to avoid a dense join. Other glyphs are unchanged.

The angled outline is editable in `q-tail/ConfiniumMono-GridToken-Q45.ufo`, with
its compiled TTF, Chromium PNG and test report alongside it. The original
centred binary is not present in Git history. The page embeds a labelled
160-unit centred-tail reconstruction on the archived bowl instead of using
current Grid, whose Q is already diagonal. The original capture is preserved;
see the [restored comparison capture](q-tail/chromium-restored.png).

To regenerate the reconstruction and proof without editing the archive:
```sh
uv run python scripts/q_tail_study.py reconstruct
uv run python scripts/q_tail_study.py proof
uv run python scripts/q_tail_study.py capture
uv run python -m unittest discover -s tests -v
```
The comparison snapshots both fonts inside the HTML. Tests check the two sloping
edges at exactly 45°, unchanged non-Q outlines, bowl attachment without ink
cancellation, a clear counter, an off-centre tail and fixed shaping advances.

## Reference grid

The local drawing box x=0…8u is translated into cell coordinates x=1u…9u.
This makes the active bounds **80…720** inside an **800** advance. Baseline is
0, cap height is 800. There is no overshoot, and baseline-to-cap extrema are flat.
Ordinary letters have 80-unit sidebearings; the narrower zero has 120 each.

| Token | Grid | Open | Dense |
|---|---:|---:|---:|
| Unit | 80 | 80 | 80 |
| Advance / cap height | 800 / 800 | 800 / 800 | 800 / 800 |
| Active width | 640 | 640 | 640 |
| Vertical stem | 160 | 160 | 160 |
| Horizontal bar | 140 | 136 | 144 |
| Outer radius | 160 | 160 | 160 |
| Inner fillet | 32 | 40 | 24 |
| Three-bar counter gaps | 190 | 196 | 184 |
| Q tail normal thickness / depth | 128 (45° right) / 120 | 128 (45° right) / 120 | 128 (45° right) / 120 |
| Y arm normal thickness | 144 (45°) | 144 (45°) | 144 (45°) |

Open and Dense are **coupled treatments**: two tokens change together. This
comparison can select an overall treatment but cannot isolate which token caused
a preference. Once a direction is chosen, vary each token independently if needed.

The file is a compact parameter table for this reference system, not a new generic
font engine. Arbitrary changes to cell dimensions or extreme radii are not claimed
safe. Keep the tested reference grid while reviewing these optical tokens.

### Architectural corners, not constant offsets

The outside radius and inside fillet are deliberately not concentric. For the
Grid top-left O corner, outside centre is (240,640), inside centre is (272,628).
This follows the proposed sharp-inside / soft-outside treatment. Vertical strokes
are 160 and horizontals 140 on their flat parts; corner mass transitions between
them. It must not be mistaken for an exact constant-width circular stroke.
Cubic handles use the standard quarter-circle factor 0.5522847498, with tangent
entry and exit, not independent hand-positioned handles. Both source and rendered
outlines need review; mathematically valid curves alone do not establish quality.

## Glyph decisions

- **H:** two 2u stems; centred 140-unit crossbar in the central band. The nominal
  4u…6u band contains the thinner centred bar rather than forcing a full 2u bar.
- **O:** rounded rectangle with 4u-wide central counter on its straight sides.
- **0:** 1u narrower overall inside its full cell; one uninterrupted counter.
  No dot, square marker, slash or alternate. This experiment uses rounded-rectangle
  corners rather than the original opposing facets. Whether to restore facets is
  a design decision, not a silent claim that the original zero brief is met.
- **Q:** O plus a 45° right-descending tail (128 normal units, centreline `x + y = 532`,
  descending to `y = −120` with a horizontal cut; extends right of `x = 720` to `≈ 742.51`
  inside the 800-unit cell). Tail union is resolved in the saved UFO; the counter remains untouched.
- **C:** vertical terminal returns extend 1u beyond the inside bar edges; flat cuts.
- **E:** square-ended rectilinear bars and a full left stem. Three horizontal bands
  are equal thickness; the two internal gaps are equal.
- **S:** five-band architectural zigzag, with softened outside turns and small
  inside fillets. Both mouths have flat returns, unlike the 697-unit experiment’s inclined cuts.
- **G:** C plus a half-active-width central spur and lower right closure. Its
  central bar spans cell x=400…720 (local x=4u…8u). Union is resolved before export.
- **Y:** 2.75u outer vertical arm drops, 45-degree diagonals at 144 normal units,
  centred 2u lower stem. Exact mitres are retained; no additional interior optical taper yet.

There are no lowercase mappings; unsupported lowercase must not masquerade as
uppercase. There are no marker alternates. The missing-glyph box, ordinary space
and no-break space also advance 800 units. No pair kerning or ligatures are added.

## Metrics and scope changes

This study uses 800-unit cap height and advance, rather than the earlier experiment’s 700 / 697.
Its trial line metrics are 920 / −200 / 0 (hhea and typo; Windows 920 / 200),
leaving headroom above capitals and below the Q tail. These are study metrics,
not a proposal that the full multilingual family has passed accent-clearance tests.
The comparison page renders the old experiment at 128 px and this study at 112 px,
giving both an 89.6 px cap height so raw size does not bias the comparison.

The original grid, inclined cuts, three distinctive tails and 100–700 range
remain untouched in the original files. Extending this direction to lowercase,
Thin/Book, Cyrillic and marks requires new design work and renewed acceptance
criteria. The original 697-unit test matrix does not apply to these study fonts.

## Reproduce

From the repository root, using the existing locked environment:

```sh
uv sync --locked
# Optional: regeneration OVERWRITES the three study UFOs and grid SVGs.
uv run python scripts/grid_token_study.py draw
# Build from the existing editable UFOs; does not redraw them.
uv run python scripts/grid_token_study.py build
# Snapshot both study fonts and the 697-unit experiment in HTML; capture Chromium PNGs.
uv run python scripts/grid_token_study.py proof
uv run python -m unittest discover -s tests -v
```

`proof` requires `chromium` on PATH. It checks that all three fonts load and uses
a fresh temporary profile. Overlap resolution uses the maintained
booleanOperations library already present in the build stack, now explicitly
pinned as a direct dependency. No new custom boolean geometry engine was added.

## Verification and review questions

Tests check mapping, all advances, every pen position, 80-cell rows (64,000 units),
zero offsets with kerning on/off, fixed-pitch metadata, cap bounds without overshoot,
resolved Q/G topology, a clear zero counter, tail visibility, tangent fillets and
sampled contour crossings. The full suite also rechecks the previous experiment.
Repeated study builds are checked for identical hashes in this environment.
These are not release certification or human readability tests.

Please judge:

1. Does the architectural S feel coherent, or too much like a segmented symbol?
2. Do C/G retain enough opening at 14 and 18 px?
3. Are the tight inner fillets appropriate, or is Open more convincing?
4. Is the centred Q tail recognisable without crowding below a line?
5. Does the narrow unmarked zero separate sufficiently from O without facets?
6. Does Y's junction become too dark compared with H?
7. Is this direction worth developing beyond Bold capitals?

This is private review material, with the same pending rights-holder / OFL release
packaging status as the original experiment. No public release is claimed.
