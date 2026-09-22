# openamr_nav_msgs

Navigation health, readiness, and fault-status messages for OpenAMRobot 2.0.

This package answers one question for anything downstream: *is navigation okay right
now, and if not, why?* It covers stack readiness, sensor health, localization,
the current nav task, recovery, protection-layer coverage, docking, and parking.
It does not control motion and is not a safety function — it's status reporting only.

## Messages

`NavigationStatus` is the top-level message and the one most consumers will
subscribe to. It aggregates the others:

- `NavStackStatus` — Nav2 lifecycle rolled up to plain readiness terms
- `LocalizationStatus` — AMCL pose health and staleness
- `SensorStatus` — per-sensor health (one entry per declared sensor)
- `NavTaskStatus` — the current goal's state and outcome
- `RecoveryStatus` — what recovery behavior is running, if any
- `ProtectionStatus` / `MotionSourceCoverage` / `ActiveConstraint` — which motion
  sources are covered by the collision monitor, and what limits are active
- `DockingStatus` / `ParkingStatus` — kept separate on purpose; no charging
  states live here, since manual charging is the current baseline

## A couple of things worth knowing before you consume this

- **Every enum's `0` value is `UNKNOWN`**, except where `0` is already the safe
  reading (`NOT_READY`, "no recovery running"). This is deliberate: an
  uninitialized field should never look healthy by accident.
- **Reason codes live in one place** — the constants block at the bottom of
  `NavigationStatus.msg`. Every other message's `reason` field just points back
  to it rather than repeating the list. `0` is always `NONE`.
- **`MotionSourceCoverage.coverage` means collision-monitor coverage
  specifically**, not "protected in general." A source can show `UNPROTECTED`
  here and still have its own separate check elsewhere.

## Adding a new reason code

Append it to the relevant group in `NavigationStatus.msg` — never renumber or
reuse an existing value, since consumers may already depend on it.

## Status

Experimental. Fields and values may still change based on real-robot data,
particularly the docking failure reasons and the localization thresholds,
which are deliberately left open pending Gate A.
