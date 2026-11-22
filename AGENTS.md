# AGENTS.md — Confinium Mono

Guidance for coding and design agents working in the Confinium Mono repository.

## Key design points

Confinium Mono is an original geometric monospace typeface built from blank UFO sources. **Never** use third-party font outlines or font images as drawing inputs.

The current 800-unit family builds on the Grid study. Its expanded static styles live in `studies/grid-token-bold/full-family/` and its variable build in `studies/variable-repertoire/`. `scripts/midline_promotion.py` applies the approved straight-join A/V/W/v/w outlines, including the fuller lowercase w, their accented forms, and Cyrillic А, without changing the archived Grid sources. The two outline tracks below are separate:

1. **Archived 9-glyph variable experiment** (`sources/`, `fonts/`, `specimen/`)
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
   - **Diagonal-to-stem joins**: Keep the outer bend on the intended grid line, but let the parallel inner diagonal meet the vertical wall directly wherever it intersects. Don’t force both joins to the same height or add a flare that reads as a notch. In the isolated [A/V midline-knee study](studies/grid-token-bold/av-knees/index.html), 152-unit diagonals meet the 160-unit stems 29 units below the midline on A and above on V; A’s crossbar moves down 40 units without thinning. Verify the join on the grid and at 14–18 px. The approved A/V construction is promoted in the full family only; these values are not universal thickness tokens.
   - **Geometry & winding rules** (`scripts/grid_token_study.py`):
     - **Winding matters for `BooleanGlyph.removeOverlap()`**: all solid outer contours must be **counter-clockwise** (`ccw_poly()`, `rect()`, `diag_bar()`) and all hole contours **clockwise** (`reverse(ccw_poly(...))`). Opposite-winding solids silently subtract from each other during overlap removal (causing stem/join cutaways).
     - **Double-lobe waists (`B`, `3`, `8`)**: drawn as single outer contours with a rounded `40`-unit waist indent (`28`-unit outer lobe curves + `10`-unit inner waist fillets), avoiding overlapping-arc corners and pinched walls.
     - **Single-stroke `Z` & architectural `2`, `1`, `4`, `K`**: `Z` is a single 10-vertex 45° stroke (`144` normal units, `181.82`-unit vertical outer lands); `2` uses a five-band form matching `S`; `1` uses a horizontal `140`-unit top-left flag; `4` uses an open-top architectural form; `K` anchors its arms across `y = low..high` on the vertical stem to avoid a narrow neck.
   - **Hollow Display study** (`studies/grid-token-bold/hollow/`, `scripts/hollow_study.py`): isolated `28`-unit wireframe display variant generated from `Grid` via `pyclipper.PyclipperOffset` (inverting `Execute(-28)` orientation so inset channels subtract cleanly from the solid). Intended for sci-fi display/HUD use (`24 px+`).

## Variable outline standards

- **Approved 0.2.0 spacing and weight:** `scripts/spacing_balance.py` rebalances `f–i` and matches `i`’s ink bounds to `n` across the axis (`x = 80…720` in Bold), without changing the 800-unit advance. `scripts/stroke_balance.py` matches all three `m` stems to capital `U` while preserving `m`’s outside walls. The [equal-width i](studies/variable-repertoire/i-width-study/index.html) and [equal-stroke m](studies/variable-repertoire/m-stroke-study/index.html) studies keep their pre-promotion controls under `reference/`.

- Treat `100` and the under-200 range as design targets, not just interpolation endpoints. Independent insets can slant grid-aligned stems, lift one side of a terminal, or taper a diagonal. Prefer explicit compatible Thin masters when that happens; share stem/bar zones and construct opposing diagonal edges in parallel. Keep approved Bold exact for a light-end fix; don’t silently edit static styles.
- Check both sides of each terminal against baseline, x-height, cap, and descender zones. Measure comparable strokes normal to the stroke at multiple points, and inspect thickness and tangency through curved shoulders, bowls, and hooks. Match related strokes optically; intentional differences are allowed. Alignment and ink-area tests alone do not establish consistent widths.
- Use family relationships as checks: `h/n` shoulders; `i/j` stems, dots, and top bars; `g/j/y` hooks; `s` top/bottom bars; `k/x` terminals and diagonal balance; `M/N/W` diagonals. Align lowercase `v`’s cleft to both upper-facing valleys of lowercase `w` across the axis. Preserve the approved `w`’s fuller outer arms and narrower centre strokes.
- Verify dependents explicitly: accented and dotless forms, shared-script glyphs (e.g. `H/Ĥ/Н`), and existing transforms such as shortened accented ascenders. Preserve mark geometry and placement. Test equivalent precomposed/decomposed shaping and unchanged advances where applicable. Proof enlarged geometry and words at 14–16 px, including `100`, an under-200 instance such as `175`, `400`, and `700`.

## How to build the typeface

Use the locked `uv` environment (Python 3.11+, tested on 3.13; dependencies in `pyproject.toml` and `uv.lock`):

```sh
uv sync --locked

# Original variable experiment (compiles existing UFOs/designspace -> fonts/)
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

Standalone HTML proofs embed compiled `.ttf` fonts as base64 data URLs and use the navigation generated by `scripts/web.py`. Hugo serves its own navigation and imported page fragments:

```sh
# Home (index.html), Explorer (explorer.html), and Design Process (process.html)
uv run python scripts/web.py

# Study proof pages + Chromium screenshots (requires `chromium` on PATH)
uv run python scripts/grid_token_study.py proof
uv run python scripts/hollow_study.py proof
uv run python scripts/q_tail_study.py proof
uv run python scripts/diagonal_study.py proof

# Original experiment PNG proofs
uv run python scripts/proof.py
```

- Edit the Python generators, not just generated HTML. When a live font changes, regenerate the affected pages, then import each affected Hugo-managed page with `uv run --locked python scripts/import_proof.py <path-to-page.html>` (for example, `explorer.html`). Regeneration alone leaves Hugo’s fragments stale. Fetch the Hugo route and confirm its embedded font bytes match the rebuilt binaries; a browser refresh is not a substitute. Keep archived controls pinned.
- Keep the public site on the shared `assets/appearance.css` layout: nearly full-width with responsive gutters, centered at a 2000 px maximum. Oversized specimens scroll locally. Titles use Full Grid Bold; the shared wordmark uses Bold “Confinium” and Light (300) “Mono,” scaled together by nav container width. Keep study names and links synced in the Studies menu and Design Process; put new comparisons where readers can find them from the existing study URL.
- To preview locally:
  ```sh
  hugo server --source site --bind 127.0.0.1 --port 1313
  ```
  Then open `http://localhost:1313/`. Hugo and GitHub Pages setup: [site/README.md](site/README.md).

## Verification and repository guardrails

- **Run all tests** after any outline, script, or parameter change:
  ```sh
  uv run python -m unittest discover -s tests -v
  ```
- **Inspect rendered output**: Always visually check Chromium captures (`verification/site-explorer.png`, `studies/grid-token-bold/verification/chromium.png`, etc.)—geometry and shaping checks do not guarantee optical quality.
- **Preserve design history**: Do not delete or overwrite existing studies, UFOs, or verification archives without explicit approval. Use `scripts/chromium_proof.py` for new Chromium screenshot commands: it writes a dated sibling if the original exists. Keep the historical PNG and the exact embedded-font proof inputs (or hashes and a Git revision that contains them); do not use a live font as a historical control. Label reconstructions as such. See [the archive guide](verification/README.md).
- **Approval and promotion**: Keep experiments isolated until explicitly approved. Promote only the selected forms through the full-family builders, verify derived glyphs and Grid/Open/Dense/Hollow style treatment, and confirm variable Bold matches Full Grid. Audit earlier accepted decisions against their pinned references (e.g. Q128 and Y144); unselected controls and the 697-unit experiment remain historical.
- **Scope & licensing**: Do not invent an OFL rights-holder or label current binaries as production-ready.
