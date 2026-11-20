# Confinium Mono — design log

## 2026-11-20 / first review cut

### Scope and provenance

Started from an empty directory and blank outlines. Inputs were the supplied
brief and general-purpose font tools, not installed fonts or extracted outlines.
The nine-glyph gate is H O 0 Q g y c e s. Three original masters use nominal
straight-stroke widths of 24, 66 and 108 units. Book is drawn directly, not chosen
from an endpoint-only interpolation. This deliberately regular first pass is a
baseline for optical revision, not a claim that mathematical spacing is sufficient.

### Drawing decisions

- H: 513-unit outside width, level crossbar at 365, equal horizontal and vertical
  stroke thickness. Its 92-unit sidebearings establish the initial cell rhythm.
- O: 531-unit outside width, 716-unit height including 8-unit overshoots, long
  straight walls and eased cubic turns. Inner corner radius decreases with mass.
- 0: 419-unit width, gaining 56 units of sidebearing on each side relative to O.
  Short opposing facets at upper right and lower left are carried into the one
  uninterrupted counter. No centre mark and no alternate feature design.
- Q: O bowl with a short descending step and rightward foot. The tail ends at
  x=647, leaving 50 units to the cell edge. Its counter is untouched.
- g: single-storey bowl and connected right stem; open left-returning hook ends
  at y=−222. At Bold, there remains substantial daylight below the bowl.
- y: junction in the lower half of the x-height, with a straight right diagonal
  continuing to a level cut at y=−220. No hook.
- c/e/s: related shallow lower cuts with slope +0.15 in design coordinates.
  The e has a level crossbar and a separate closed eye. The s uses distinct upper
  and lower mouths; its optical colour still needs review against c and e.
- Traps: intentionally deferred until K/k, M and Ж/ж are drawn, rather than adding
  gratuitous wedges to smooth bowls in this pilot.

### Revisions made during this cut

1. Raised the Bold g-hook floor to stay within the declared descender.
2. Moved the e crossbar down to avoid a coincident closing point in Bold that
   broke contour compatibility. Rebuilt all masters with matching topology.
3. First raster inspection revealed opposite-winding cancellation at Q's tail
   attachment. Reversed the tail contour, preserving same-winding overlap.
4. Corrected y's inner junction to follow the actual right-arm diagonal; the
   first Thin outline had an unintended taper.
5. Replaced steep/reversed lower cuts on c/e/s with a shared shallow rising cut.
6. Reduced the Thin s spine mass by making its two boundaries follow the weight
   parameter instead of retaining a fixed large separation.

The dated SVG records the resulting first-cut outlines, not an invented history
of earlier hand sketches. The generator captures the construction decisions;
UFOs remain independently editable.

### Review concerns / not yet accepted

- Thin at 14 px is very pale without hinting. This is a display design, but the
  required smallest-size O/0 reader test is still outstanding.
- Bold c/e terminals and the s spine may need further optical balancing.
- The faceted zero is deliberately assertive in this cut; judge its width and
  corner character beside the softer O before expanding the alphabet.
- Q's foot and g's hook may need length/weight adjustments in running words.
- Future traps, stacked marks, language proofs and box-drawing joins are untested.

### Verification

Pilot metrics and HarfBuzz tests cover seven static fonts and thirteen variable
coordinates, both kerning settings, intermediate positions and 80-cell rows.
Static outlines match their variable instances after TrueType rounding. Raster
ink increases through all seven weights. FontTools reports no interpolation
issues for the three UFO masters. The HTML specimen was loaded and visually
inspected in headless Chromium; glyph-only PNGs were inspected separately.
This evidence does not replace human readability testing or release validation.

## 2026-11-20 / curve revision 02

User review correctly identified corrupted-looking s/c/e curves and mismatched
inner/outer g radii. The first pass's width and interpolation gates did not test
these defects, and the initial visual review was inadequate.

### Reproduction and cause

Captured the actual variable TTF in headless Chromium at 360 px (Thin, Book,
Bold) and at 14/18/32 px (all seven weights). The original screenshot is retained
as `verification/curves-before.png`; its HTML embeds the original font. The v1
vector drawing is retained in `sketches/2026-11-20-nine-glyphs-v1.svg`.

The defects exist in the source geometry, not just the renderer: independent
handle placement produced reversed/degenerate handles, non-tangent joins and
corner inflections. The g inner radius was reduced by only 0.65 times the stroke
width, moving the inner corner centres instead of keeping concentric curves.
Three regression tests reproduced 43 failing subcases before reconstruction;
the red baseline was saved in a local verification log.

### Corrections

- c/e use shared circular-cubic corners with common centres, and inner radius
  equal to outer radius minus stroke width. Their lower terminal cuts are radial
  cuts at atan(0.15), preserving the requested shallow rising angle without a
  last-minute hook or notch. The e crossbar sits at 230.
- s uses circular-cubic shoulders and a common internal tangent for its diagonal.
  Both boundaries meet that diagonal tangentially. The lower terminal uses the
  same cut angle as c/e. No local correction handles or zero-length handles.
- An intermediate version had exact tangency at the masters but lost it between
  masters. The expanded regression caught this. The final s holds its tangent
  angle fixed and varies its radii/centre separation linearly, preserving tangency
  throughout interpolation instead of merely relaxing the test tolerance.
- g has genuinely concentric 139 / (139−stroke) bowl radii. Its returning hook
  uses concentric 133 / (133−stroke) radii as well. The old top spur is removed.
  Bowl and hook are separate same-winding overlapping contours; they render as
  a union, with the counter unaffected. Release overlap handling remains pending.
- H/O/0/Q/y outlines, grid metrics, named weights and coverage are unchanged.

### Verification and remaining judgement

All seven tests pass: the original four pilot gates plus the three geometry
regressions. Geometry tests include all 13 master/interpolated weight positions.
Updated Chromium captures are `verification/curves-after.{html,png}` and include
all seven weights at the requested small sizes. Both before and after captures
were inspected. FontTools interpolation checks and deterministic build checks
were rerun; specimen PNGs and font hashes were refreshed.

This fixes the demonstrated geometric defects, not every possible optical issue.
In particular, the new s's proportion/colour and g's simpler top remain design
choices for user review. The complete brief's release gates are still outstanding.

## 2026-11-20 / grid- and token-driven Bold direction study

Following user approval to explore a new direction, added an isolated study under
`studies/grid-token-bold/`. The original fonts and UFOs are not changed. This is
not an approved full-family replacement of the 697-unit design.

The experiment uses the supplied 80-unit module: 800 advance and cap height,
640 active width, 160 stems and outer radii. Three coupled treatments compare
140/32, 136/40 and 144/24 horizontal-bar / inner-fillet pairs. Their typographic
family is still Confinium Mono, with distinct study style names.

Drew H O 0 Q C E S G Y from blank grid- and token-driven geometry. No existing font outlines
were used as drawing inputs; the previous pilot appears only as an explicit
comparison proof. Original unmarked zero is retained as a constraint, but its
facets are provisionally replaced by narrower rounded-rectangle geometry. Q
explores the proposed centred tail. C/G use hooked flat-cut apertures; S uses
five alternating bands. Y follows vertical drops and 45-degree mitres without
an extra optical taper. These are documented experimental departures.

Quarter-circle fillets share analytic tangent construction. Inner and outer
corners intentionally have different centres: this is the requested architectural
fillet treatment, not the previous pilot's constant-offset approach. Grid- and token-driven
component overlaps are resolved using the existing booleanOperations component
before sources are saved; the dependency is now pinned explicitly.

Study output includes editable UFOs, three static TTFs, coverage and parameter
JSON, grid SVGs, browser proofs and an equal-cap-height pilot comparison. The
study's JSON tokens are for this reference geometry, not a generic glyph engine.
Chromium verified all three embedded font loads; enlarged C/E/S/G and small-size
proofs were inspected. Ten repository tests pass, including the original pilot
and new study grid/shaping/contour gates. Human transcription and full-family
release validation remain outstanding. See the study README for review questions.

## 2026-11-20 / Q-tail angle exploration

Added an isolated alternative to the grid- and token-driven Grid Q: its tail descends right at
45°, ending at y=−120 and x=720 with a horizontal cut. The bowl and counter,
all other outlines and the 800-unit advance remain unchanged. The baseline
centred Q and all three original study styles are retained for comparison.
The diagonal uses a 136-unit horizontal section (about 96 perpendicular units),
a lighter optical treatment rather than an equal-ink comparison.

The first Chromium proof exposed opposite-winding cancellation at the attachment.
Corrected the component winding before boolean union; a raster attachment check
and two-contour topology check now guard that failure. The updated Chromium
comparison was inspected at display size and 14/18/32/64 px. All 11 tests pass,
including 45° edge checks and unchanged non-Q outlines. Editable source, compiled
font, embedded-font comparison HTML and PNG are under `studies/grid-token-bold/q-tail/`.
This is still an alternative for review, not a decision to replace the centred Q.

## 2026-11-20 / optical diagonal thickness comparison

User review found the Q tail and Y diagonals disproportionately light relative
to the bowl/stems. Their old normal thicknesses were about 96.17 and 113.14 units,
respectively, versus 160-unit vertical stems. Added three isolated alternatives
with normal diagonal thicknesses of 128, 144 and 160. Each alternative changes
only Q and Y; every reference version is retained.

Q retains its centreline x+y=532, horizontal end cut and −120 depth. Thickening
extends its tip beyond the nominal active box, to x≈742.51 / 753.82 / 765.14,
but never outside the 800-unit cell. Its counter remains untouched. Y retains
its outside silhouette and lower stem while its inside diagonal edges move
parallel to the outside. All long diagonal edges remain 45°. There is no new
junction taper: this isolates thickness before any local optical join revision.

Added editable UFOs, compiled fonts, parameter tokens, grid diagrams and embedded
font browser comparisons under `studies/grid-token-bold/diagonals/`. Inspected the
four-column and enlarged O/Q/H/Y Chromium proofs. The comparison deliberately
allows Q and Y to be selected independently; no visual winner is promoted.
Tests verify normal widths/angles, fixed alignment, counter and attachment,
increasing raster ink, unchanged non-Q/Y outlines and shaping/grid behaviour.
All earlier acceptance gates remain applicable to their own reference fonts.
The optical assessment and human small-size readability remain review decisions.
