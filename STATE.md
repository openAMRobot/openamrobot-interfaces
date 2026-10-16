# STATE

Read this file before any work in this repository and update it in the same PR as the work.
Facts below are dated or tied to a commit/SHA.

## Repository

- Type and lifecycle: interface, active
- Readiness: R1 (evidence: PR #16 combined ROS 2 Jazzy verification, run 36445801182)
- Owner role: software-lead
- Verification: `bash tools/verify.sh`; latest documented combined PASS is run 36445801182 on PR #16, based on commit 4590089 (2026-09-28)

## Current work

| Work package | Branch or PR | Status | Next step |
|---|---|---|---|
| C10 dataset quality gate | PR #25 | draft / synthetic evidence only | Work-package owner reviews placement and supplies real-episode evidence |
| Combined verification gate | Issue #6 | open | Attach passing main-branch evidence before closing |

## Decisions this repository implements

- No explicit `decisions.yaml` IDs are embedded in the current interface sources; contract and compatibility values remain governed by the versioned schemas and verification documentation.

## Known gaps

- Harness rollout steps (b)–(e) are not installed, pinned or required on this repository as of main `87ab8a9` (2026-10-09).
- C10 real-episode and production-acceptance evidence is not verified; see PR #25.
- No runtime ownership or approved release pin is claimed for the proposed C10 reference checker.

## Not verified

- This step-(a) PR changes repository guidance only; it does not run ROS, DDS, hardware or production acceptance tests.
- No physical robot, safety-chain, released binary or cross-version deployment evidence is claimed.
