Use the CLI archive for your platform from [fontspector-v1.9.1](https://github.com/fonttools/fontspector/releases/tag/fontspector-v1.9.1). Before extraction verify its digest against `tool.sha256` (e.g. `sha256sum --check --ignore-missing tool.sha256` alongside the downloaded archive). The verified Linux executable reports 1.9.0 in its banner but identifies tag fontspector-v1.9.1 and commit 990bb930, matching upstream's tag. Pin by archive digest, not banner.

Use `fontspector --profile universal --error-code-on fail` with the desired input files. Show warnings, do not suppress failures, and treat execution errors as blocking. Do not enable hotfix mode.

## Run locally

Install pre-commit and uv. Download the archive for your platform from the release linked above, keeping its original filename. Export `FONTSPECTOR_ARCHIVE` as its **absolute path** in the environment used by Git. Run `uv sync --locked` and `pre-commit install`. The hook checks only staged release TTFs; no download is performed by the checker. To check all five from the repository root use `uv run --locked python scripts/font_qa.py`. The same command with `--desktop dist/desktop` checks the renamed release inputs. The checker verifies the pinned archive on each invocation.

## Initial Linux baseline (no exceptions)

| Inputs | Wall time, single run | Exit | WARN | FAIL | FATAL / ERROR |
| --- | ---: | ---: | ---: | ---: | ---: |
| Full Grid | 0.629 s | 1 | 11 | 1 | 0 / 0 |
| Four full-family static TTFs plus variable repertoire TTF, together | 0.602 s | 1 | 55 | 32 | 0 / 0 |

Family FAIL messages by keyword: `mac-names` (8), `missing-ps-name` (7), `instance-too-long` (7), `mono-bad-panose` (5), and one each of `inconsistent-family-name`, `inconsistency`, `nameid4-too-long`, `mismatch` (head vs name version), and `no-regular-instance`. Counts are messages, not 32 distinct glyph defects. Review style grouping and Book/Regular naming before modifying metadata. No suppressions approved; enforcement pending.
