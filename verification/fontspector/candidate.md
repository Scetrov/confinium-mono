# Candidate for rollout review — 2026-11-24

Policy: verified fontspector-v1.9.1 archive (tool.sha256), universal, --error-code-on fail, no exclusions. Validate the five required identities separately: Confinium Mono Full {Dense,Grid,Hollow,Open}, each Bold, and Confinium Mono VF, default Regular 400. Full-set orchestration must reject missing or unexpected identities. Separate families are not a suppression.

| Candidate | SHA-256 | WARN |
|---|---|---:|
| Full Dense | f00359becd62f37e0fd151bb37e55ba1c94be2f7aa43625f8c5b88f5e95925b6 | 12 |
| Full Grid | a9ef5ae01d5692f8f694c6570b70a85ca5264dde8ce23ef6fd3c950105a3544e | 11 |
| Full Hollow | c2c0e00f4db7b1cd5e2cab5135e83e7a935e08964c9c2bc0bbebe555f17b0c02 | 12 |
| Full Open | b0de301a1f96fc937d8769835e5acdb0a5a5769b1e689d37d6e5a46f33c886ee | 11 |
| Variable | 2665495339f6d267f8642d310c9a2fb2c649cdd39fc986b2341c35cc6d438a02 | 11 |

All five: zero FAIL, FATAL or ERROR. Originally 32 FAILs in a combined invocation. All now have Latin-text monospaced PANOSE; VF version fields agree, instance PS names exist, and only duplicate legacy names were removed. Variable display name/PS identity changed: existing users may need to reselect the family.

Remaining nonblocking warning keywords: bad-numberOfHMetrics, contour-count, decomposed-outline, missing-avar, missing-rupee, nameid6-too-long, no-overlaps-bit, no-stat-table, no-wws-without-wws-names, not-recommended-00A0, unreachable-glyphs. Not a readability certification.

Against d716952, only head and OS/2 differ for statics; VF additionally differs in name and fvar. glyf, hmtx, cmap and VF gvar match byte for byte. Archived controls untouched. All 78 unit tests passed. Rebuilt Hugo Explorer served and inspected in Chromium; all five embedded binaries matched the candidates.

**Rollout approved, 2026-11-24.** The requesting maintainer explicitly selected “Approve these hashes and policy” for the five SHA-256 values and policy above. Changes to either before rollout require renewed review.
