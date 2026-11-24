## Context

The package job copies four Full Grid-family static TTFs and the variable repertoire TTF into `dist/desktop`, renames the variable file, then produces WOFF2s and a ZIP. The top-level `fonts/` is an archived experiment, not a release input.

## Goals / Non-Goals

Use one reproducible technical check at three boundaries without running the whole build on commit. Readability scoring, font redesign, WOFF2 conformance checks and a parallel FontBakery installation are out of scope. Preserve existing tests and webfont checks.

## Decisions

- Select a verified stable Fontspector CLI release, pin it with artifact integrity verification, and use its universal profile rather than vendor-specific publishing rules. If using a setup action, pin its full commit SHA and independently pin the CLI. Prefer existing CLI severity controls and pre-commit file filtering over custom tooling.
- Allowlist the five release input paths for the hook; pass matching staged filenames as arguments. No recursive discovery of studies. For PRs check all five, including freshly built outputs when their sources or builders change. A binary-only change must check the proposed binary, not overwrite it first.
- In the release package job validate the five copied TTFs before compression and ZIP creation. Fail closed on missing inputs or tool errors. Keep PR permissions read-only.
- Surface warnings; block on failures and errors. Record the tool version, findings and timings before enabling enforcement. Review each exception by check ID, affected inputs and rationale; never ignore the entire baseline.

## Risks / Trade-offs

A subset hook cannot replace family-wide checks. Slow checks would discourage local use: measure one-font and five-font runtimes and revisit local scope before rollout if necessary. A baseline defect needing an outline or licensing decision blocks enforcement until resolved or explicitly excepted; do not silently change historical sources or invent metadata.

## Baseline remediation and approval

Track all nine failure keywords in the [initial baseline](../../../verification/fontspector/README.md) by check ID and affected font or family invocation. Investigate repeated messages together, but verify every affected input. Correct PANOSE and version values against the intended release metadata; trace naming, instance and platform-record findings to the family builders before editing. Preserve existing display names (including Book), installed-font identity and style grouping by default. Do not add a Regular alias or rename styles solely to silence a check.

Make the decisions reviewable in a tracked remediation record: diagnosis, proposed source change, affected consumers, before/after metadata and checker results. Obtain an identifiable human maintainer's decision **before** any compatibility-sensitive change or exception. Prefer fixing the source over suppressing checks. An intentional exception needs the exact check, finding, inputs, rationale and a condition for revisiting it. If it cannot be scoped without hiding other failures, do not enable it.

After rebuilding, provide the full-family rerun, regression results and confirmation that outlines, advances and archived controls are unchanged. Request explicit human sign-off on the actual candidate and policy before enforcement. Record reviewer, decision, date and reviewed revision or artifact hashes; an agent must not approve on the maintainer's behalf. Changed candidate bytes or policy invalidate that sign-off. This is an adoption checkpoint, not manual approval on every subsequent hook run.

## Migration Plan

Baseline first; then enable the hook and CI with the same policy. Document local setup, reproduction and how to review pin updates. No release artifact format or font migration is required.
