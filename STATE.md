# STATE

Read this file before any work in this repository and update it in the same PR as the work.
The PR evidence check fails when STATE.md exists and a PR neither updates it nor says
"no change" with a reason. Keep it under 60 lines; facts only, each with a date or SHA.

## Repository

- Type and lifecycle: interface, active
- Readiness: R1 (evidence: ROS 2 Jazzy workflow running `tools/verify.sh` on main, run 37936438992)
- Owner role: software-lead
- Verification: `bash tools/verify.sh`; last PASS on main at 87ab8a9 (2026-10-09), run 37936438992
- I8 verification: `bash tools/verify.sh` passed on the working tree (2026-11-11); evidence at `.verification/run.LmU15W`.

## Current work

| Work package | Branch or PR | Status | Next step |
|---|---|---|---|
| C10 dataset quality gate | PR #25 | draft / synthetic evidence only | Work-package owner reviews placement and supplies real-episode evidence |
| Shared rules v2 (rollout step a, pilot) | PR #26 | in review | merge, then step (b) pin the harness |
| I8 base-controller interfaces | Issue #30 / PR #38 / `feat/i8-base-controller-msgs` | five-message implementation with proposed lift-permit fields and ArmStatus dependency documented; contract remains proposed (2026-11-17) | resolve three-vs-five scope, ArmStatus sign-off, permit timing/CAN mapping, diagnostics owner; rerun hosted verification |
| StopState.msg for the stop-gate contract (platform-sw#119) | PR #35 | changes requested (panthera-momagdii) - rebased on main `14912e1`, hosted CI/DCO/CLA green at head `025ee28caf7e72b31e9b134d09e5fa3a8606aac0` | push, Mohamed approves same day; then platform-sw#90 repins nav-status-tests.yml from the fork pin to the merge SHA |

## Decisions this repository implements

- CHARGING, DOCK-NO-CONTACTS, DOCKING-NOT-CHARGING (register scope includes this repository;
  `DockingStatus.msg` carries no charging or contact state). Watchdog decisions check: 0
  findings at e63311d (2026-10-17).

## Known gaps

- Harness rollout steps (b) to (e) not done as of main 87ab8a9: `repository-quality` calls the
  reusable workflow at `@main`; Watchdog reports 3 unpinned actions (2026-10-17).
- C10 real-episode and production-acceptance evidence is not verified; see PR #25.
- No runtime ownership or approved release pin is claimed for the proposed C10 reference checker.

## Not verified

- I8 verification is local ROS 2 Jazzy software verification only; firmware integration, physical robot, safety-chain and hardware validation are not established (2026-11-11).
- PR #38 review follow-up: timestamp thread corrected and resolved; named I8/platform/UI/manipulation owners recorded; diagnostics/logging owner remains TBD (2026-11-17).
- PR #38 head `5b8efed328f802d31645d14f8005082ac3b1b5ba`: proposed `lift_permit`, reason-code candidates and maximum-age field added to `BaseAuxStatus`; `ArmStatus` dependency and fail-closed/restart/withdrawal semantics documented; 23 static checks; Jazzy compatibility snapshot regenerated. Hosted verification pending (2026-11-17).
- No physical robot, safety-chain, released binary or cross-version deployment evidence is claimed.
