# Confinium Mono Variable · Full Grid

[Variable TTF](fonts/ConfiniumMono-VariableRepertoire%5Bwght%5D.ttf) · [Thin, Book, Bold comparison](verification/full-grid-weights.png) · [Explorer](../../index.html)

Full Grid is the outline source for **every** glyph, including Q. At weight
700 outlines and horizontal metrics match Full Grid exactly: 800-unit cell,
800 cap height, 560 x-height, zero-width combining marks, 1040/−200 line
metrics. Weights 100–700 interpolate through generated Thin and Book (400)
construction masters, not individually optically finished drawings.

The historical pilot supplies axis and naming conventions only. Its 697-unit
sources, fonts and proofs remain archived. The earlier adapted variable
study's [raster](verification/weights.png) is retained for comparison.

Run `uv run python scripts/variable_repertoire.py` after building Full Grid,
then regenerate the Explorer with `uv run python scripts/web.py`.
