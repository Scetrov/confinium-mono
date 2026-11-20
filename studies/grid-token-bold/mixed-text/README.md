# Mixed text · Grid Bold

[Standalone proof](index.html) · [Raster sample](verification/mixed-text.png)

All 95 printable ASCII characters share one 800-unit advance. Build reads the
lowercase-alphabet UFO (letters, figures, space) and the punctuation UFO (32
symbols) directly; neither parent is written. No new outlines are drawn here.

```
uv run python scripts/mixed_text_study.py build
uv run python scripts/mixed_text_study.py proof
```

In the raster sample, underscores remain separate from adjacent descenders.
The uppercase O and zero are close at reading sizes: compare `O0o` before
considering any change to either approved form. The PNG is an outline raster,
not a browser screenshot; check the HTML on the intended display as well.
