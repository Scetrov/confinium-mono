# European Latin · Icelandic first

[Language proof](index.html) · [Full-height capital raster](verification/full-height-caps.png)

This isolated study extends the mixed-text repertoire without editing its
parents. It includes all letters in Latin-1 Supplement and Latin Extended-A,
Romanian comma-below letters, capital sharp S, selected additional accented
letters and common European signs. Capital bodies retain their full 800-unit height and advance.
Above marks rise beyond the cap line; this study alone uses 1040/−200
line metrics to accommodate them. Icelandic eth and thorn are distinct
letters, not accent combinations. Supported single-mark decompositions have
zero-advance combining marks and explicit `ccmp` substitutions.

Build and refresh from the repository root:

```
uv run python scripts/european_study.py build
uv run python scripts/european_study.py proof
```

Scope is Latin script, not a claim of coverage for every European language,
symbol or Sámi orthography. Arbitrary stacked marks, Greek and Cyrillic are
not part of this pass. Review the Icelandic upper/lowercase pairs first,
then compare ring, acute, double acute, caron and comma below in context.
