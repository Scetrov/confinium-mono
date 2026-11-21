# Verification archive

Keep historical Chromium PNGs. The first capture may use the canonical name;
any later capture must get a new name. `scripts/chromium_proof.py` publishes
a UTC-dated sibling when the target already exists, and only after Chromium
confirms the fonts loaded. Keep links to older captures pointed at those exact
files, not at the newest render.

For a design milestone, commit the PNG together with its exact embedded-font
HTML and source/binaries, or record the Git revision and SHA-256 hashes that
identify those inputs. Record the Chromium version, viewport, zoom and theme
when relevant. Pin the reference font before starting a new historical
comparison; a redraw must not depend on the evolving live baseline.

## Known legacy gaps

The legacy `SHA256SUMS` files are historical records. Sixteen listed TTF hashes
have no matching binary in available Git history: eight from the 697-unit
experiment, three from Grid/Open/Dense, three from Optical Diagonals, one from
Hollow, and one from Q45. Keep those manifests and PNGs as evidence; do not
rewrite their hashes or claim those exact builds have been recovered. The new
[Grid reference snapshot](../studies/grid-token-bold/reference/README.md) has
its own manifest. The original centred-Q binary is also unavailable; the
[restored proof](../studies/grid-token-bold/q-tail/index.html) labels its
centred row as a reconstruction and preserves the original PNG separately.

The original curve before/after captures are preserved here. The current
curve review script can render the revised font but cannot regenerate the
historical before capture from it.
