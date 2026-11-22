# Structural capitals — Bold comparison

[Open the proof](index.html). This archived comparison preserves the approved structural study; 0.2.1 uses a subsequently balanced `W` crown at the same midline height. The control is the released 0.2.0 Full Grid, pinned in `reference/` (SHA-256 `61b69594206840e4b83941cc78a598ea5c5da425b3564c603c0f316ce3061ee4`). Regenerate using `uv run --locked python scripts/structural_capitals_study.py`.

| Base | Candidate | Covered dependents |
| --- | --- | --- |
| `X` U+0058 | Use `Y`’s upper terminal lands and cleft; reflect them across y=400 for the legs. The outer walls turn at y=580 and y=220. | Cyrillic `Х` U+0425 |
| `N` U+004E | The diagonal meets the right stem above its foot; the lower edge joins at y=400. | `Ñ Ń Ņ Ň` U+00D1/0143/0145/0147; `Ŋ` U+014A keeps its hook |
| `M` U+004D | The brace ends in a flat cut at y=400, rather than y=140. | `Ṁ` U+1E40; Cyrillic `М` U+041C |
| `I` U+0049 | Extend the crossbars from 480 to 640 ink units to match `J` and `L`. Keep the 160-unit stem and 140-unit crossbars. | `Ì Í Î Ï Ĩ Ī Ĭ Į İ` U+00CC–00CF/0128/012A/012C/012E/0130; Cyrillic `І Ї` U+0406/0407 |
| `W` U+0057 | Lower the inner crown from y=560 to y=400; keep the feet and lower notch. | `Ŵ Ẁ Ẃ Ẅ` U+0174/1E80/1E82/1E84 |

The inventory checks every encoded outline for canonical decomposition or a shared construction. Marks and the `Ŋ` hook retain their own contours and position. All advances remain 800 units.

**Independent controls:** Latin `Ĳ` is separately fitted as a single-cell ligature: widening its `I` component to the standalone bounds would collide with `J`. Cyrillic `И/Й` use a distinct ascending diagonal, not the Latin `N` outline. `Ж` has a central stem and a different arm arrangement; `Ш/Щ` are upright-stroke forms, not copies of `W`. Lowercase and independently drawn forms stay unchanged for this first comparison. The font has no Greek glyphs, so Greek lookalikes are not in the study.
