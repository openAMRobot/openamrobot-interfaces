# openamr_nav_msgs

Navigation health, readiness, and fault-status messages for OpenAMRobot 2.0.

Scoped to the **navigation subsystem only** — not whole-robot readiness, and
not a safety interface. Arm/base authority and E-stop logic live in I1/I8;
this package only relays what navigation has observed about them.

## Messages

`NavigationStatus` is the top-level message and the one most consumers will
subscribe to. It aggregates:

- `NavStackStatus` — Nav2 lifecycle rolled up to plain readiness terms
- `LocalizationStatus` — AMCL pose health and staleness
- `SensorStatus` — per-sensor health (one entry per declared sensor)
- `NavTaskStatus` — the current goal's state and outcome
- `RecoveryStatus` — what recovery behavior is running, if any
- `ProtectionStatus` / `MotionSourceCoverage` / `ActiveConstraint` — which motion
  sources are covered by the collision monitor, and what limits are active

`DockingStatus` and `ParkingStatus` are **separate top-level messages with
separate producers**, not fields of `NavigationStatus`. No charging states
live in either, since manual charging is the current release baseline.

See [CONTRACT.md](CONTRACT.md) for topics, producers, QoS, versioning, and
field validity rules.

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
which are deliberately left open pending Gate A. Build/schema/consumer tests
are tracked in #6.
