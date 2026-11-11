# openamr_base_msgs

**Bundle revision:** v4 reconciliation candidate (10 November 2026). See [REVISION_NOTES.md](../../REVISION_NOTES.md).

Base-controller (I8) status, auxiliary-device and fault messages for
OpenAMRobot 2.0, aligned to E-01 rev 4. **Proposed**, not approved: see
[CONTRACT.md](CONTRACT.md) for topics, QoS, freshness and UNKNOWN rules, versioning and the
open decisions.

## Messages

- BaseStatus on /base/status: controller-state/readiness proposal, identity, timing/freshness,
  diagnostic observations, faults and proposed subsystem/constraint summaries. E-01-derived
  state semantics remain open under Decision 2.
- `BaseAuxStatus` on `/base/aux_status`: lift measured and declared position (separate), position validity, proposed homing state, head light, Getac power-good, second E-stop.
- `BaseFault`: one fault/diagnostic entry. Normal events, reset causes and UI Stop are represented by state fields, not fault codes.
- `BaseSubsystemStatus`, `BaseMotionConstraint`: provisional nested messages (decision 1).

The package contains only the two frozen status topics. Optional message definitions and E-01-derived field semantics remain proposed pending the decisions listed in the contract. No separate base-stopped topic is included.

## Before you consume this

- Every enum's `0` is `UNKNOWN`. An unset field never looks healthy.
- Freshness comes from your local receipt time. `header.stamp` is diagnostic only.
- These are firmware observations. They are not a safety function and not proof that the
  hardwired safety path worked. `safety_ok` is diagnostic feedback, not proof of K1/K2/KCHG state; low is expected during CHARGING. WCM_FAULT outside CHARGING blocks/refuses charging but does not by itself block RUN.
- `readiness` is the readiness latch, not the RESET input level, and not permission to move.
- This package reports state. It does not carry commands or sessions.
