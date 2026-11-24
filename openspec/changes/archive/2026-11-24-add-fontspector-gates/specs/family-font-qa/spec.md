## ADDED Requirements

### Requirement: Shared technical QA policy
All gates SHALL use the same pinned Fontspector release, universal profile and documented exceptions. Warnings SHALL be visible but non-blocking; unexcepted failures and tool errors SHALL block.

#### Scenario: Warning without failure
- **WHEN** the only findings are warnings
- **THEN** the gate reports them and succeeds

#### Scenario: Failed check or checker error
- **WHEN** a required check fails without an approved exception or the checker cannot run
- **THEN** the gate reports the cause and exits unsuccessfully

### Requirement: Human-reviewed baseline remediation
Before enforcement, maintainers SHALL account for every baseline failure, correct defects in their generating sources, and verify the rebuilt five-font set. The work SHALL preserve outlines, advances and archived controls. Compatibility-sensitive decisions and exceptions SHALL require explicit prior approval from a human maintainer.

#### Scenario: A failure has a straightforward metadata correction
- **WHEN** a metadata value is inconsistent with the intended font identity or version
- **THEN** the source is corrected and a rebuilt candidate, before/after evidence and regression results are presented for review

#### Scenario: A correction could change how installed styles are identified
- **WHEN** remediation would change a user-visible name such as Book, a PostScript identity or style grouping
- **THEN** implementation pauses on that decision until a human maintainer reviews the options and records a choice

#### Scenario: An intentional design triggers a failure
- **WHEN** an exception is proposed instead of a fix
- **THEN** it remains inactive unless a human maintainer approves its specific check, finding, inputs, rationale and revisit condition; unrelated failures must still block

#### Scenario: Authorizing enforcement
- **WHEN** all five rebuilt candidates have no unexcepted failures or errors
- **THEN** enforcement remains disabled until a human maintainer signs off on the identified candidate and policy after reviewing the baseline dispositions, rerun and regression evidence; changes to either before rollout require renewed approval

### Requirement: Staged font checks
The pre-commit hook SHALL inspect only staged TTFs among the four current static styles and variable repertoire release input.

#### Scenario: Mixed staged changes
- **WHEN** a commit changes Full Grid, an archived TTF and documentation
- **THEN** only the staged Full Grid TTF is checked

#### Scenario: No current-family font
- **WHEN** no release TTF is staged
- **THEN** the hook skips Fontspector

### Requirement: Full-family PR validation
PR CI SHALL validate all five current-family inputs and SHALL check rebuilt outputs when build inputs change.

#### Scenario: Builder-only change
- **WHEN** a PR modifies a family construction script without changing a checked-in font
- **THEN** CI builds the affected outputs and validates the full family including those outputs

#### Scenario: Binary-only change
- **WHEN** a PR replaces only a checked-in release TTF
- **THEN** CI checks the family including the replacement bytes

### Requirement: Release candidate validation
Packaging SHALL require all five staged desktop release TTFs to pass the shared policy.

#### Scenario: Incomplete or failing release set
- **WHEN** a required desktop TTF is absent or fails validation
- **THEN** the release job does not produce or publish the package
