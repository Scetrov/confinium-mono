# Confinium Mono — optical diagonal comparison

Compare the existing Q/Y against **128, 144 and 160 units of thickness measured
perpendicular to the diagonal**. The angle remains 45 degrees. This is an
isolated experiment: no reference font, original experiment, Grid/Open/Dense source,
or previous Q-tail font is replaced.

## Review

**http://localhost:8000/studies/grid-token-bold/diagonals/**

- `index.html`: four side-by-side columns, display samples and 14/18/32/64 px checks.
- `detail.html`: enlarged O/Q/H/Y comparisons at a common size.
- `index.png`, `detail.png`: headless Chromium captures, with font loads verified.
- `grid-{128,144,160}.svg`: editable outline diagrams with grid and active box.
- `sources/`: three editable UFOs; family name Confinium Mono throughout.
- `fonts/`: three static Bold TTFs, not variable-font masters or additional weights.
- `parameters.json`: measured thickness targets and fixed construction constraints.

The HTML snapshots embed all four fonts; they can be opened directly without
font installation. Interface labels use the system UI font; all glyph samples
use only the embedded Confinium Mono fonts. Re-run `proof` to refresh snapshots
after editing sources and rebuilding. At 100% browser zoom, compare the small
sizes as well as the large drawings. Mobile layout stacks the columns.

## What changes and what stays fixed

| | Existing reference | Alternatives |
|---|---|---|
| Q tail normal thickness | 136 / √2 ≈ 96.17 | 128 / 144 / 160 |
| Y arm normal thickness | 160 / √2 ≈ 113.14 | 128 / 144 / 160 |
| Primary vertical stem | 160 | 160 |
| Q tail angle / Y diagonals | 45° | 45° |
| Advance / cap height | 800 / 800 | 800 / 800 |
| Q counter and bowl | Grid O | Unchanged |
| Q depth / end cut | −120 / horizontal | Unchanged |
| Y outer silhouette / lower stem | Grid Y | Unchanged |
| Additional junction taper | None | None |

### Q

Keep the tail centreline **x + y = 532** fixed. Its two long edges are offset by
`t / √2` in x+y coordinates, giving a perpendicular separation of t. The start
cut at y=120 lies inside the 140-unit bottom bar, so it does not intrude into the
counter. Resolve the tail/bowl union before saving sources.

The rightmost tail point becomes approximately **742.51 / 753.82 / 765.14**.
These points exceed the nominal x=720 active box but remain within the x=800
cell, with at least 34.86 units of clearance. The sidebearing exception is
intentional: clipping at 720 or shifting the tail would change the angle or
centreline and confound the thickness comparison. The bowl itself retains
its original 80-unit sidebearings.

### Y

Keep the outside diagonal edges, 160-unit vertical arm tops and 160-unit lower
stem unchanged. Move the inside diagonal edges parallel to the outside until
their normal separation reaches the target. Both diagonal directions remain
exactly 45°. This moves the inner fork and shortens its inner vertical runs;
those are geometric consequences of thickening within a fixed silhouette.

Do **not** interpret the absence of a junction taper as acceptance of the join.
Thickness and local join relief should be judged separately. Once a preferred
thickness is selected, a small, independent junction adjustment can be proofed
if it looks too dark. No ink trap or non-45° correction is introduced in this pass.

### Reading the results

The three columns pair Q and Y at the same target for convenience, not because
they must ultimately share it. It is valid to prefer, for example, a 128-unit Q
tail and 144-unit Y arms. No preferred version has been promoted to the baseline.
The previous reference is not an equal-thickness baseline: Q and Y started at
different thicknesses, so their visual changes are not expected to match exactly.

Judge the Q attachment against the bowl's lower-right corner, and the Y diagonals
against H's uprights and Y's lower stem. Check whether a weight that feels right
at display size becomes a knot or an indistinct tail at 14/18 px. The grid is a
construction aid, not the optical acceptance test.

## Build and verify

From the repository root, in the existing locked environment:

```sh
uv sync --locked
# Optional: overwrites this comparison's UFOs and grid SVGs only.
uv run python scripts/diagonal_study.py draw
# Compiles existing editable UFOs without regenerating them.
uv run python scripts/diagonal_study.py build
# Requires chromium on PATH; snapshots all four fonts and checks loading.
uv run python scripts/diagonal_study.py proof
uv run python -m unittest discover -s tests -v
```

The current Grid source and Q45 reference font must be present (both are included
in the repository). Drawing uses blank Q/Y grid- and token-driven geometry and the existing O
bowl construction; untouched glyphs are copied from this project's Grid source,
not from a third-party typeface.

Tests measure the actual source edges' normal separations and 45° slopes; check
the fixed Q centreline and Y lower stem; verify bounds, topology, clear counter,
solid tail attachment, increasing raster ink, fixed advances and shaping pen
positions; and compare every non-Q/Y compiled outline against Grid. TrueType
serialization rounds coordinates to integer units, so nominal construction
thicknesses should not be confused with sub-unit raster measurements.

The full test suite also covers the earlier experiment and study variants. Repeated
build hashes and existing-reference hashes are checked in the current environment.
These tests do not select a visual winner or establish human readability.
OFL rights-holder / public-release packaging remains pending, as for the other
local studies. No commits or publication are performed by these scripts.
