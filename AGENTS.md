# AGENTS.md — Confinium Mono

Guidance for coding and design agents working in the Confinium Mono repository.

## Key design points

Confinium Mono is an original geometric monospace typeface built from blank UFO sources. **Never** use third-party font outlines or font images as drawing inputs.

Two parallel tracks are maintained in this repository:

1. **Original 9-glyph variable pilot** (`sources/`, `fonts/`, `specimen/`)
   - 1,000 UPM, **697-unit advance**, 700 cap height, 500 x-height, line metrics `885 / −242 / 0`.
   - Variable `wght` axis `100–700` with `Thin`, `Book`, and `Bold` masters and seven static weights.
   - Coverage: `H O 0 Q g y c e s`, `space`, `nbspace`, `.notdef`.
   - Narrow faceted `0`, stepped `Q` tail, open-hook `g`, diagonal `y`, and analytic tangent curves on `c/e/s/g`.

2. **Grid- and token-driven Bold study** (`studies/grid-token-bold/`, `studies/grid-token-bold/parameters.json`)
   - 1,000 UPM, **800-unit advance and cap height** (`1u = 80`), active drawing bounds `x = 80…720`, line metrics `920 / −200 / 0`, no overshoot.
   - Coverage: `A–Z` (26 uppercase), `0–9` (10 figures), `space`, `nbspace`, `.notdef` (39 glyphs total).
   - Shared tokens: `vertical_stem = 160` (`2u`), `outer_radius = 160` (`2u`), non-concentric tight inner fillets.
   - Three coupled treatments: **Grid** (bar `140`, fillet `32`), **Open** (bar `136`, fillet `40`), **Dense** (bar `144`, fillet `24`).
   - Promoted optical 45° diagonals (overriding raw `2u` grid thickness):
     - **Q tail**: **128** normal units, 45° right-descending (`x + y = 532`, `y = 120…−120`, horizontal cut). Extends to `x ≈ 742.51`, intentionally past `x = 720` but inside the 800-unit cell.
     - **Y arms**: **144** normal units, 45° inner/outer diagonals with fixed outer silhouette and 160-unit lower stem. No junction taper applied yet.
     - **Other primary diagonals** (`A, K, M, N, R, V, W, X, Z, 4, 7`): built via `diag_bar()` at exact normal thickness (`144` or `128` for `W`/`1`).
   - **Geometry & winding rules** (`scripts/grid_token_study.py`):
     - **Winding matters for `BooleanGlyph.removeOverlap()`**: all solid outer contours must be **counter-clockwise** (`ccw_poly()`, `rect()`, `diag_bar()`) and all hole contours **clockwise** (`reverse(ccw_poly(...))`). Opposite-winding solids silently subtract from each other during overlap removal (causing stem/join cutaways).
     - **Double-lobe waists (`B`, `3`, `8`)**: drawn as single outer contours with a rounded `40`-unit waist indent (`28`-unit outer lobe curves + `10`-unit inner waist fillets), avoiding overlapping-arc corners and pinched walls.
     - **Single-stroke `Z` & architectural `2`, `1`, `4`, `K`**: `Z` is a single 10-vertex 45° stroke (`144` normal units, `181.82`-unit vertical outer lands); `2` uses a five-band form matching `S`; `1` uses a horizontal `140`-unit top-left flag; `4` uses an open-top architectural form; `K` anchors its arms across `y = low..high` on the vertical stem to avoid a narrow neck.
   - **Hollow Display study** (`studies/grid-token-bold/hollow/`, `scripts/hollow_study.py`): isolated `28`-unit wireframe display variant generated from `Grid` via `pyclipper.PyclipperOffset` (inverting `Execute(-28)` orientation so inset channels subtract cleanly from the solid). Intended for sci-fi display/HUD use (`24 px+`).

## How to build the typeface

Use the locked `uv` environment (Python 3.11+, tested on 3.13; dependencies in `pyproject.toml` and `uv.lock`):

```sh
uv sync --locked

# Original variable pilot (compiles existing UFOs/designspace -> fonts/)
uv run python scripts/build.py

# Grid- and token-driven Bold baseline (Grid, Open, Dense)
uv run python scripts/grid_token_study.py build

# Preserved isolated comparisons
uv run python scripts/hollow_study.py build
uv run python scripts/q_tail_study.py build
uv run python scripts/diagonal_study.py build
```

**Important build rules:**
- `build` compiles existing editable UFOs without modifying them.
- `draw` commands (`scripts/draw.py`, `grid_token_study.py draw`, `q_tail_study.py draw`, `diagonal_study.py draw`) **overwrite UFOs and SVG grid overlays**. Only run `draw` when changing programmatic geometry/tokens, and inspect UFOs first so manual edits are never silently discarded.
- Preserve deterministic `SOURCE_DATE_EPOCH` defaults when building binaries.

## How to build the static website

HTML pages embed compiled `.ttf` fonts as base64 data URLs so they work both over HTTP and directly as local files, and share the primary navigation bar defined in `scripts/web.py`:

```sh
# Root explorer (index.html) and design process archive (process.html)
uv run python scripts/web.py

# Study proof pages + Chromium screenshots (requires `chromium` on PATH)
uv run python scripts/grid_token_study.py proof
uv run python scripts/hollow_study.py proof
uv run python scripts/q_tail_study.py proof
uv run python scripts/diagonal_study.py proof

# Original pilot PNG proofs
uv run python scripts/proof.py
```

- Edit the Python generators (`scripts/web.py` and the `proof()` functions in the study scripts), not only the generated HTML files.
- To preview locally:
  ```sh
  python3 -m http.server 8000 --bind 127.0.0.1
  ```
  Then open `http://localhost:8000/`.

## Verification and repository guardrails

- **Run all tests** after any outline, script, or parameter change:
  ```sh
  uv run python -m unittest discover -s tests -v
  ```
- **Inspect rendered output**: Always visually check Chromium captures (`verification/site-explorer.png`, `studies/grid-token-bold/verification/chromium.png`, etc.)—geometry and shaping checks do not guarantee optical quality.
- **Preserve design history**: Do not delete or overwrite existing studies, UFOs, or verification archives without explicit approval.
- **Scope & licensing**: Do not promote unapproved variants, invent an OFL rights-holder, or label current binaries as production-ready.
