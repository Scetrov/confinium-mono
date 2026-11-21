# Grid Bold punctuation study

[Open the embedded-font specimen](index.html). This isolated Bold build adds all
32 printable ASCII punctuation and operator characters to a copy of the Grid
UFO. Existing letters, figures, and spaces are unchanged. It is not promoted to
Grid, Open, Dense, Hollow, or the variable experiment, and does not add lowercase.
`coverage.json` records the exact Unicode-to-glyph mapping (71 glyphs total,
including unencoded `.notdef`).

- Dots share a 160 × 144 cut; the comma and semicolon descend 120 units.
- Arithmetic operators align to the 400-unit axis; slash and backslash use
  128-unit normal strokes. Bracket, brace, and parenthesis pairs mirror.
- The dollar stem straddles the caps, from −80 to 880. The underscore is fully
  below baseline (−120 to −24); global metrics and the 800-unit advance are unchanged.
- The specimen shows syntax-highlighted JavaScript at 17 px, all additions at
  60 px, and code, paths, and symbol pairs at 12, 16, and 28 px. See
  `verification/chromium-code.png` for the updated browser capture.

From the repository root:

```sh
# Only when updating programmatic outlines: overwrites this study's editable UFO.
uv run --locked python scripts/punctuation_study.py draw
# Build reads the existing UFO. Proof embeds the resulting TTF and needs Chromium.
uv run --locked python scripts/punctuation_study.py build
uv run --locked python scripts/punctuation_study.py proof
uv run --locked python -m unittest discover -s tests -v
```
