## Why

The family is already used on a live site, but the release workflow has no dedicated technical font-conformance gate. Catch binary defects before distribution without treating a clean report as evidence of readability.

## What Changes

- Remediate the documented universal-profile baseline failures at their source. Require a human maintainer to review compatibility decisions and the resulting evidence before enforcement.
- Check changed family TTFs at commit time, the full family on pull requests, and the exact TTF release candidates before packaging.
- Share the tool version, severity policy and exceptions across these checks.

## Capabilities

### New Capabilities
- `family-font-qa`: Reproducible technical QA of current-family TrueType binaries across local development and distribution.

### Modified Capabilities

None.

## Impact

Adds a developer tool, hook configuration, PR automation and a gate in `.github/workflows/release.yml`. No changes to outlines, historical controls, public APIs or supported repertoire.
