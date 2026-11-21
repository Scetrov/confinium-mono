# Full Grid family study

The four static [fonts](fonts/) each contain 416 mapped Unicode characters.
They retain the European Latin and East Slavic Cyrillic study's 1040/−200
line metrics, zero-width combining marks and composition substitutions.
The 697-unit variable experiment and all previous study binaries remain separate.

[Current family proof](index.html) · [Archived pre-promotion styles](verification/styles.png).
Use the [Explorer](../../../index.html) for arbitrary text.

The builder takes the cumulative Cyrillic study as its repertoire master and
keeps each style's original Grid-study glyphs from its archived TTF unless
a later study has been approved and promoted. New
Open/Dense forms use a piecewise vertical mapping to thin/thicken horizontal
bars by four units without changing the cell, baseline, cap or x-height.
New Hollow forms trace a 28-unit boundary band on a two-unit lattice after
combining intersecting strokes. Features narrower than two walls remain solid.
Hollow is a display design; evaluate at 24 px or larger.

## Approved study audit

- **Q / Y:** Grid exactly matches the archived Q128 and Y144 outlines. Open,
  Dense, and Hollow retain their corresponding approved study outlines. The
  original centred Q and the lighter Q45 remain comparison controls only.
- **Midline Knees:** A, V, W, v, and the 144-unit outer-arm w are promoted.
  The 17 accented forms keep their marks and inherit the new base; Cyrillic А
  inherits Latin A as before. Grid uses the approved contours directly, Open
  and Dense use their existing style transforms, and Hollow derives a 28-unit
  shell. Variable Bold still matches Full Grid; Book matches the approved
  study shapes. Earlier variants remain archived.
- **Coverage:** The uppercase/figure, punctuation, lowercase, European Latin,
  and East Slavic Cyrillic studies are represented in the 416-character
  repertoire. No 697-unit outlines or unselected optical alternatives were
  promoted. The distinct Æ ligature was not part of the Midline Knees study.

```sh
uv run python scripts/full_grid_family.py
uv run python scripts/variable_repertoire.py
uv run python scripts/web.py
uv run python scripts/family_knee_proof.py proof
```
