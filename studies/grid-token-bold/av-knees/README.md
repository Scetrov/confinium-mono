# Midline Knees · isolated Grid Bold experiment

[Side-by-side proof](index.html) · [A/V/W capture](chromium-straight-avw.png) · [Straight A/V capture](chromium-straight-av.png) · [Straight V capture](chromium-straight-v.png) · [Fuller-join capture](chromium-fuller.png) · [Original capture](chromium.png)

The same 800-unit cell and 80-unit sidebearings carry through. Instead of
running diagonally over the entire cap height, A's lower legs and V's upper
arms are 160-unit vertical stems up to the 400-unit midline. The outer
shoulders then move three grid squares horizontally over five vertically,
meeting a two-square flat apex. The diagonals retain the 144-unit normal
stroke, so their inner knees land just off the midline. A's 140-unit crossbar
ends at the midline and retains a closed counter above it.

The 152-unit revision keeps the outer diagonals, 160-unit stems, and A's
crossbar fixed. A short flare connects each stem to the parallel inner
diagonal about 16 units farther toward the point: up on A, down on V. This
keeps the extra ink local at the join. The proof shows the revision next to
the original 144-unit experiment and pinned Grid Bold.

The straight-cleft variant removes the flare on V only. Its 152-unit inner
shoulder runs directly to the 160-unit vertical wall at about y=429, while
the outer bend stays at y=400. This keeps the inner diagonal parallel to the
outer one without a notch. A is unchanged from the fuller-join version.

The straight A/V follow-up mirrors that join in A: the inner wall meets the
diagonal at about y=371. A's crossbar moves down 40 units without thinning,
so the counter shows the join instead of cutting it off at the midline. V is
identical to the straight-V-only variant.

W extends the straight-join approach without touching A or V. Its outer
bends stay at y=400; the parallel inner diagonals intersect the vertical
walls at about y=419. W uses 128-unit outer stems and normal diagonal
thickness to keep room for two valleys. The centre ridge lands at y=560.

Only U+0041, U+0056, and U+0057 differ from the Grid Bold reference. These comparison fonts remain unchanged; the accepted versions are now in the
[current full family](../full-family/index.html).

```sh
# --with-w selects the latest variant; skip draw to keep manual edits.
uv run python scripts/av_knee_study.py draw --with-w
uv run python scripts/av_knee_study.py build --with-w
uv run python scripts/av_knee_study.py proof
uv run python scripts/av_knee_study.py capture
```

## Lowercase v and w

[Lowercase comparison on the main page](index.html#lowercase) · [Chromium capture](chromium-straight-vw-lowercase.png)

This separate font starts from the archived lowercase alphabet. Only v and w
change. Outer bends sit at y=280 (half x-height); the inner shoulders meet
the stem walls directly, at about y=325 for v and y=305 for w. The 800-unit
advance and 560-unit x-height stay fixed. v uses 152-unit diagonals; w keeps
128 units for both valleys. Y is not part of this pass.

```sh
uv run python scripts/vw_knee_study.py draw  # overwrites only the new experimental UFO
uv run python scripts/vw_knee_study.py build
uv run python scripts/vw_knee_study.py proof
uv run python scripts/vw_knee_study.py capture
```

The wider-w comparison increases its outer stems and parallel outer diagonal
strokes from 128 to 144 units. The centre diagonals remain 128 units; the
midline, advance, and v are unchanged. The original variant and capture
are retained. Use `draw --wider-w` and `build --wider-w` for this variant.
[Combined Chromium proof](chromium-midline-knees-w144.png).

## Archived Book review

[Book proof](book.html) · [Chromium capture](chromium-book.png)

Two isolated 100–700 variable candidates carry the straight-join Bold
outlines into generated masters. The proof compares them and pre-promotion Full
Grid at Book 400. Accented A/W/w inherit the exact corresponding base in
each master while retaining the existing marks and composition substitutions.
The 128/144 labels describe the Bold source dimensions, not Book stroke widths.

In Chromium at 14–16 px, 144 gives w a little more presence next to the
pair vv without losing the two valleys. The difference is modest; keep 144
as the stronger candidate; it was subsequently approved for the full family. The straight v
also reads more like a small u than the current v, worth checking in text.

```sh
uv run python scripts/book_knee_study.py build
uv run python scripts/book_knee_study.py proof
uv run python scripts/book_knee_study.py capture
```
