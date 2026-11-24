# Baseline remediation review

The counts below are FAIL subresults from the pinned universal profile, not warnings or unique outline defects. Static means Full Grid/Open/Dense/Hollow; VF means Variable Repertoire. No exception is active.

| Check / finding | Count and input | Source and proposed disposition |
|---|---|---|
| opentype/monospace / mono-bad-panose | 5, all | full_grid_family.py inherits the master's OS/2, then variable_repertoire.py inherits Grid's. Set Latin text family type and monospaced proportion in the static builder; verify inheritance, fixed pitch and unchanged advances. |
| opentype/font_version / mismatch | 1, VF | variable_repertoire.py copies pilot name but retains Grid head. Align name ID 5 to the actual head revision (rounds to 0.002); not a release version bump. |
| no_mac_entries / mac-names | 8, VF | Same pilot name copy. Remove obsolete platform-1 entries in the derivative only, after verifying equivalent Unicode-accessible strings for every referenced name ID. Legacy platform-1 consumers lose those records. |
| fvar_instance_ps_names / missing-ps-name | 7, VF | Pilot fvar copy lacks explicit instance PS names. Assign unique stable PS names to the seven existing instances, preserving coordinates; PDF/PostScript consumers may identify instances differently. |
| name/family_and_style_max_length / nameid4-too-long and instance-too-long | 1 + 7, VF | Final name rewrite sets the long Variable Repertoire family/full name. Shorten the family to **Confinium Mono VF** and use **ConfiniumMonoVF** as PS prefix, preserving style labels unless approved below. Existing installed-family references may require migration. Alternative: retain identity and investigate a tightly scoped exception, not a global name-length exemption. |
| opentype/fvar/regular_coords_correct / no-regular-instance | 1, VF | Copied pilot fvar names weight 400 Book. Prefer retaining Book, monitoring only this exact finding at this input; alternative: rename 400 Regular, consistently across name/fvar/STAT, proof labels and downstream expectations. Do not create duplicate coordinates by default. |
| opentype/family/consistent_family_name / inconsistent-family-name; typographic_family_name / inconsistency | 1 each, four-static directory | full_grid_family.py deliberately writes different family names to IDs 1/16 for the four treatments; each is Bold. Preserve separate installed families. Prefer checking each actual family separately while requiring all five files in PR/release; retain a separate assertion of the expected family identities so accidental regrouping is detected. Alternative: redesign grouping and style names, with installation compatibility review. |

## Decision (2026-11-24, requesting maintainer via interactive review)

Approved shortening the variable family to Confinium Mono VF, creating ConfiniumMonoVF instance identities, renaming weight 400 to Regular, retaining four separate static families, and removing only verified duplicate legacy Mac records. No exceptions approved. Final candidate approval pending.

The following contingency was not selected: for Book, any approved exception must match the VF, check ID and finding code, and only while weight 400 is intentionally Book. Revisit if naming, default coordinates or the tool changes. If the CLI cannot scope this precisely, keep enforcement blocked until a safe policy is verified. Re-run without suppressions as part of candidate review. Human approval of these decisions does not authorize rollout; candidate hashes, before/after evidence and final sign-off remain outstanding.
