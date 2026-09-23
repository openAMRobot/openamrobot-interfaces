# Runtime contract

Scope: navigation subsystem only. This is not a whole-robot readiness or
safety interface — see the E-stop note under Validity below.

## Topics and producers

| Topic (proposed) | Message | Producer |
|---|---|---|
| `/navigation/status` | `NavigationStatus` | new node in `openamr-platform-sw` — [openamr-platform-sw#34](https://github.com/openAMRobot/openamr-platform-sw/issues/34) |
| `/navigation/docking_status` | `DockingStatus` | `openamrobot_docking` — [openamr-platform-sw#33](https://github.com/openAMRobot/openamr-platform-sw/issues/33) |
| `/navigation/parking_status` | `ParkingStatus` | not yet implemented |

Topic names above are a proposal from this package, not yet fixed by any
producer — confirm before implementation starts.

## QoS and publish behavior

Reliable, transient-local, depth 1, so a late-joining subscriber gets the
last known status immediately. Publish on any field change, plus a heartbeat
(2 Hz by default, configurable per producer) so a subscriber can tell a
producer has gone silent from staleness alone.

## Versioning

`NavigationStatus.contract_version` is set by the producer to
`NavigationStatus.CONTRACT_VERSION` (currently `1`).

- Adding a field, or a reason/enum value, does not require a version bump.
- Removing, renumbering, or changing the type of a field requires a version
  bump and coordination with consumers.
- Reason codes are append-only: never renumbered or reused, per group.

## Field validity

Some fields are only meaningful in certain states; elsewhere they're `0` and
should not be read as a real value.

- `LocalizationStatus`: `covariance_xy`, `covariance_yaw`, `pose_age`, and
  `tf_available` are only meaningful when `state != STATE_UNKNOWN`.
- `SensorStatus`: `data_age` and `rate_hz` are `0` when `state == STATE_ABSENT`
  — the sensor isn't in the active profile, not silently stale.
- `NavTaskStatus`: `native_error_code`, `distance_remaining`, and `goal_stamp`
  are only meaningful when `state` is `STATE_ACTIVE` or a terminal state
  (`STATE_SUCCEEDED`/`STATE_ABORTED`/`STATE_CANCELED`).
- `RecoveryStatus`: `attempt` and `attempt_limit` are only meaningful when
  `action != ACTION_NONE`.
- `DockingStatus`: `phase`, `lateral_error_m`, `yaw_error_rad`, and
  `visible_tag_count` are only meaningful while `activity` is `ACTIVITY_DOCKING`
  or `ACTIVITY_UNDOCKING`.
- Any `reason` field is `NONE` exactly when its associated state/enum is in
  its "nothing wrong" value (e.g. `coverage == COVERAGE_PROTECTED`,
  `health == HEALTH_OK`); otherwise it should be non-`NONE`.

## E-stop and base dependency

`ESTOP_ACTIVE`, `BASE_LINK_LOST`, `BASE_NOT_READY`, and `BATTERY_LOW`
(`NavigationStatus.msg`, 9000s) reflect what navigation has observed about
the base/I8 controller — they are relayed, not determined here, and this
package implements no E-stop or safety logic of its own. Authoritative
base/E-stop state belongs to I8.
