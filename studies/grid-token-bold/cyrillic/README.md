# East Slavic Cyrillic · upright Bold study

[Language proof](index.html) · [Alphabet raster](verification/east-slavic.png) · [TTF](fonts/ConfiniumMono-Cyrillic.ttf)

The study adds the modern Russian, Ukrainian and Belarusian alphabets (76
letters across both cases) to the European Latin study binary, without changing
that font or promoting the repertoire into the variable pilot. Forms are drawn
from original paths and this family's existing outlines. Grid advance 800,
cap 800, x-height 560; line metrics 1040/−200. No Bulgarian or Serbian
localized alternates or extended non-Slavic Cyrillic alphabets are claimed.

```
uv run python scripts/cyrillic_study.py build
uv run python scripts/cyrillic_study.py proof
```

Use the Explorer's Cyrillic Study entry to type mixed-script text. Review the
counter widths in `Ш Щ Ы Ю`, the descenders in `Д Ц Щ`, and breve clearance in
`Й Ў` before extending coverage or promoting the outlines.
