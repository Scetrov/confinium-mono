# Full Grid family study

The four static [fonts](fonts/) each contain 416 mapped Unicode characters.
They retain the European Latin and East Slavic Cyrillic study's 1040/−200
line metrics, zero-width combining marks and composition substitutions.
The 697-unit variable pilot and all previous study binaries remain separate.

[Compare the styles](verification/styles.png), top to bottom: Grid, Open,
Dense, Hollow. Use the [Explorer](../../../index.html) for arbitrary text.

The builder takes the cumulative Cyrillic study as its repertoire master and
keeps each style's original Grid-study glyphs from its archived TTF. New
Open/Dense forms use a piecewise vertical mapping to thin/thicken horizontal
bars by four units without changing the cell, baseline, cap or x-height.
New Hollow forms trace a 28-unit boundary band on a two-unit lattice after
combining intersecting strokes. Features narrower than two walls remain solid.
Hollow is a display design; evaluate at 24 px or larger.

```
uv run python scripts/full_grid_family.py
uv run python scripts/web.py
```
