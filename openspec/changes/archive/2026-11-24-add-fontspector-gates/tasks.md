## 1. Baseline the checker

- [x] 1.1 Verify the current stable CLI release and supported installation paths, pin version and integrity, and select the universal profile and severity threshold.
- [x] 1.2 Run on one TTF and the five release TTFs; record timings and findings (see `verification/fontspector/README.md`).
- [x] 1.3 Map all 32 FAIL messages to check IDs, affected inputs, generating sources and proposed dispositions; document compatibility implications and alternatives.
- [x] 1.4 Obtain and record a human maintainer decision before changing compatibility-sensitive metadata or adding a narrowly scoped exception. Leave unresolved decisions blocked.
- [x] 1.5 Apply approved dispositions and straightforward source fixes; rebuild the five release candidates. Verify metadata deltas, unchanged outlines/advances and archived controls, run regression tests and rerun universal with the intended policy.
- [x] 1.6 Present before/after reports and remaining warnings. Record explicit human sign-off with reviewer, date, candidate revision or hashes and policy identity before enabling any gate; re-review changes before rollout.

## 2. Connect the gates

- [x] 2.1 Add a pre-commit hook limited to staged current-family TTF paths; document installation and the equivalent local full-family command.
- [x] 2.2 Add read-only PR CI using the shared policy on the full family, covering binary changes and rebuilt outputs for relevant source or builder changes.
- [x] 2.3 Validate the complete staged desktop set in the release package job before WOFF2 generation and archiving; preserve existing release checks.

## 3. Verify enforcement

- [x] 3.1 Exercise mixed staged inputs, a no-font commit, a binary-only PR and a builder-only PR. Confirm selected inputs and pinned policy.
- [x] 3.2 Demonstrate warning-only success and blocking failure/error/missing-file paths with disposable inputs; verify the package path without publishing. Run repository tests and configured pre-commit checks.
