# Runtime contract

Status: **Proposed**, not approved. Source: I8 Base Controller Interface Proposal rev 4
(10 Nov 2026), with the 6 Nov frozen fields preserved. E-01 rev4-derived field mappings,
message choices, enums, fault lifecycle and lift semantics remain proposals wherever Section 8
of rev4 leaves a decision open. Nothing marked TODO or proposed in the .msg files is frozen.

Scope: base-controller status only. This is not a whole-robot readiness or safety interface,
and it is not a command or session protocol. It reports what the base-controller firmware
observes and the state it is in. It does not actuate, reset or validate the E-stop, and it does
not claim the robot is safe. The hardwired chain (two E-stops, Pilz PNOZ s3, K1/K2, brake
release) and the recovery sequence are owned by E-01
([openamr-platform-fw#17](https://github.com/openAMRobot/openamr-platform-fw/issues/17),
[#6](https://github.com/openAMRobot/openamr-platform-fw/issues/6)). Commands into the base
controller (UI Stop, UI Resume, Jetson Stop release, charge command, charger acknowledge) and the
session challenge and sequence rules (E-01 section 3) are part of the I8 firmware/host contract.
This package only reports their result.

## Topics and producers

| Topic | Message | Producer | Consumers |
|---|---|---|---|
| `/base/status` | `BaseStatus` | base-controller firmware (Teensy Gate A, STM32H723ZG Gate B), [openamr-platform-fw#10](https://github.com/openAMRobot/openamr-platform-fw/issues/10) | `navigation_status_node.py` in openamr-platform-sw, operator UI (openamrobot-ui #54), manipulation (openamrobot-manipulation #7), diagnostics, logging, tests |
| `/base/aux_status` | `BaseAuxStatus` | base-controller firmware, relayed from the lift node CTL-017 over CAN3 ([openamr-platform-fw#12](https://github.com/openAMRobot/openamr-platform-fw/issues/12), D17) | same as above |

Owners for each producer and consumer are recorded in the PR description.

## QoS and publish behavior

The two frozen topics are /base/status and /base/aux_status. Both use reliable,
transient-local, depth-1 QoS. Publish on field change plus the agreed heartbeat:

- /base/status: 10 Hz, stale after 0.5 s.
- /base/aux_status: 5 Hz, stale after 0.6 s.

No separate /base/stopped topic, QoS, rate or timeout is included in this candidate. The source
and transport of fresh base-stopped evidence required by the lift interlock remain open under
Decisions 1 and 8; a retained status snapshot must never be treated as proof of current standstill.

## Freshness and UNKNOWN rules

- Freshness is computed from the consumer's **local receipt time** of the latest message.
  `header.stamp` is ROS time when available and is diagnostic only. Use `monotonic_us` for
  controller-local elapsed-time calculations; never compare it across boots.
- No stale value is published. Staleness is the absence of timely messages.
- A retained message received on subscription does not show the publisher is alive. Treat the
  stream as live only after a further message arrives within the stale threshold. A further
  message shows the publisher is producing messages, not that the controller is healthy.
- Every enum's `0` is `UNKNOWN` (or the conservative reading). An unset, stale or unavailable
  value is never read as healthy, safe or as an observed E-stop.
- `UNKNOWN` (a valid message that cannot determine a value) is different from malformed (a
  message that breaks the schema or contradicts itself). Malformed is a failure, never mapped
  to `UNKNOWN` or nominal. A typed ROS publisher cannot emit a malformed message, so this is
  tested with a validator on raw data.
- `boot_id` and `sequence` detect publisher restarts and sequence gaps. Consumers also check
  `contract_version`.

## E-01 operating state and latches (BaseStatus)

The following E-01 rev4-derived operating-state and latch mapping is a proposal pending
Decision 2 approval. It must not be treated as an approved I8 consumer contract.

| Field | Meaning | Not the same as |
|---|---|---|
| `operating_state` | `LOCKED`, `RUN`, `INHIBITED`, `CHARGING`, `CHARGER_FAULT`; `UNKNOWN` until determined. Boot lands in `LOCKED`; there is no `BOOT` state | `state` (generic health summary from fault severity) |
| `readiness` | the readiness latch `reset_seen`: set only by a qualified short physical RESET press; cleared by E-01 invalidation/recovery events | `reset_pressed` (the RESET input level, which also reads high for an open wire) |
| `ui_stop_active` | UI Stop software inhibit, held by the controller; survives host reconnection | `host_stop_active`, `host_link` |
| `host_stop_active` | Jetson Stop: asserted at boot and on session loss | `host_link` (a connected Jetson can still assert Stop) |
| `command_acceptance` | `ACCEPTING` only while motion commands are accepted (RUN, current session) | `readiness` |
| `recovery` | a physical RESET or other recovery is still required | a fault being cleared |
| `first_reason`, `reason_mask` | first fault reason for the current LOCKED/CHARGER_FAULT episode; `reason_mask` contains active fault reasons only | fault history or UI Stop state |
| `session_epoch_counter` | paired with `boot_id`; starts at 0 each boot and increments once per detected Jetson session loss; a fresh challenge-response establishes the current epoch | a command sequence number |

`INHIBITED` is never reported as `SAFETY_STOPPED`; that term is reserved for the hardwired
chain. RUN needs `readiness` ready, `ui_stop_active` no, `host_stop_active` no and every other
RUN condition. Seeing `RUN` here is a report, not authority to command motion.

### Fault and inhibit effects on operating state

A recorded `BaseFault` does **not** automatically imply `LOCKED`. `operating_state` reports the
actual E-01 state after applying the transition table; `severity`, `faults` and `reason_mask`
are diagnostics and must not be used as a substitute state machine.

| Condition | Required reporting / effect |
|---|---|
| Boot/reset | Enter `LOCKED`; report the reset cause in `reset_cause`, not as a `BOOT_*` fault. |
| Jetson session loss (`COMMS_LOST`) | Assert `host_stop_active`, clear readiness as specified by E-01, and enter `LOCKED`. |
| UI Stop | Report `ui_stop_active`; from RUN enter `INHIBITED`. It is an inhibit, not a `BaseFault`. |
| UI Resume in INHIBITED | Clear ui_stop_active; transition to RUN only when readiness is set, fresh valid base-stopped evidence is available from an approved source, SAFETY_OK and every other E-01 RUN condition are satisfied. Otherwise remain inhibited. The base-stopped source/transport is not defined by this package candidate. |
| WCM_FAULT while `LOCKED`, `RUN` or `INHIBITED` | Record the charger fault and refuse/block charging. It does not by itself force `RUN` to `LOCKED` or prevent RUN. |
| WCM_FAULT while `CHARGING` | Enter `CHARGER_FAULT` and apply the E-01 charging fault handling. |
| Charge-interlock failure while `CHARGING` (including SAFETY_OK high after the 500 ms window) | Enter `CHARGER_FAULT`; acknowledgement does not prove KCHG opened. |
| Fresh PNOZ Y32/SAFETY_OK low outside the expected CHARGING condition | Report the diagnostic and apply the E-01 transition to `LOCKED`; while CHARGING, low is expected and is not this fault. |
| Motion/drive, BMS, encoder, IMU or other input faults | Apply the specific E-01 Fault and Inhibit Matrix row. Do not infer a transition from the mere presence of a fault entry; where the matrix does not require a state transition, preserve the current state and report the fault. |

The fault list may include active, latched, acknowledged and cleared entries. A fault being
present in history does not mean its condition is active or that it currently inhibits motion.
`inhibits_motion` is the entry's explicit effect, not a blanket consequence of `code != NONE`.

Base-stopped evidence is not defined as a message in this candidate. The lift interlock must
consume fresh, valid evidence from an explicitly approved source; it must not infer standstill
from a retained /base/status or /base/aux_status snapshot.

## Versioning

BaseStatus.contract_version and BaseAuxStatus.contract_version are set by the producer
to their message's CONTRACT_VERSION. Both are 1, as required by the frozen I8 contract.
The v3 candidate's BaseStatus=2 was not adopted: contract version 1 is frozen. Additional
E-01-derived fields remain proposed under Decision 2; they do not silently change the frozen
version field.

- Adding a fault code or enum constant does not require a version bump only after the registry
  owner confirms that policy.
- Adding, removing, renaming, reordering or retyping a message field requires owner review and
  the applicable interface versioning decision.
- Fault codes are append-only: never renumbered or reused.
- A consumer that sees an unsupported contract_version degrades safely.

## Lift position provenance (Decision 13 — proposed)

BaseAuxStatus carries two separate position values:

- lift_measured_position_m: independent physical measurement.
- lift_declared_position_m: actuator/controller-declared position.

Each has its own validity field. A declared position is never a substitute for a measured
position. The host adapter may publish lift_joint only from a valid independent measured
position. Homing state, source identity, freshness details, raw-device fault encoding,
mapping to the central fault registry, and the threshold/action for measured-versus-declared
disagreement remain unresolved. The fields in this draft are a working representation, not
approval of a particular sensor, encoder, CAN object or firmware owner.

The lift interlock requirement is base confirmed stopped AND both arms in the approved safe
pose (stowed or carry). UNKNOWN, invalid or stale base/arm observations do not satisfy either
condition. The exact carry pose and the robot enforcement owner/handshake remain open.

## Field validity

- `applied_command_*`: the velocity sent to the motor driver after limits, ramp and timeout.
  It is never a held or replayed command; on timeout the base stops. A stale `/cmd_vel` is
  non-latching (E-01 R7): zero velocity, no state change. A lost Jetson session is latching
  (T5) and shows as `LOCKED`, `host_stop_active`, and `readiness` not ready.
- lift_measured_position_m is the independent physical measurement and is meaningful only
  when lift_measured_position_valid == OBS_YES. A host adapter may publish lift_joint only from
  this valid measured value, never from lift_declared_position_m.
- lift_declared_position_m remains a separate controller/actuator declaration. Its source,
  validity semantics and disagreement threshold against measured position remain open (Decision 13).
- lift_raw_device_fault_code and lift_fault_code are distinct: raw device code versus mapped
  central registry code. Their exact encoding/mapping remains open (Decision 13).
- `second_estop` is `SECOND_ESTOP_UNKNOWN` whenever `lift_link != LIFT_LINK_OK`.
- `fault_code`, `reason` and `*_fault_code` are `NONE` exactly when the associated state is
  nominal.
- `reset_flags_raw` is `0` when the MCU cannot provide it, and `reset_cause` is then `UNKNOWN`.
- `powered_debug` is `UNKNOWN` when the firmware cannot identify the running build. `UNKNOWN`
  is never read as `DISABLED`.
- `reset_required` reports whether a qualified physical RESET is required before `readiness`
  can be set. It is not the live RESET input and is not itself the readiness latch. A high RESET
  input held for the E-01 two-second invalidation interval clears `reset_seen`, asserts the
  software-detected reset-input fault/inhibit, and requires the input to be observed low before
  another qualified reset press can set readiness. A short valid press is handled by the E-01
  reset qualification logic.
- `session_epoch_counter` is reset to 0 on each boot (the new `boot_id` distinguishes boots),
  then increments exactly once on each detected Jetson session loss. Heartbeats and ordinary
  supervisory commands do not increment it. Challenge-response wire fields and replay rejection
  remain in the I8 firmware/host contract, not in this package.

## Safety observations

`safety_ok`, `base_estop_pressed`, `reset_pressed`, `reset_required`, `charge_inhibit_active`
and `charger_fault` are firmware observations.

- `safety_ok` is the PNOZ s3 Y32 output read through the ISO1212 isolated input. It is
  diagnostic feedback only. It is not a safety-rated input, not proof of K1, K2 or KCHG contact
  state, and not proof the hardwired chain reached its intended safe state. The firmware does
  not monitor K1 or K2 (E-01 R6). ISO1212 is an isolated observation interface, not a
  substitute safety circuit.
- `safety_ok == OBS_NO` means the diagnostic reports the PNOZ output not enabled. It is **not**
  used to derive `SAFETY_STOPPED`. SAFETY_OK low is the expected condition while `CHARGING`;
  SAFETY_OK high while charging is the unsafe direction (E-01 5.6).
- `charge_inhibit_active` follows the controller's own output. Dropping `CHARGE_REQUEST` is not
  evidence that charging power was removed.
- An E-stop is reported as observed only when fresh telemetry explicitly reports it. Missing,
  stale or unknown telemetry is never an observed E-stop and never proof of safety.
- No firmware status field proves the physical state of K1, K2 or KCHG. No ROS 2 message is a
  safety function.
- The second E-stop comes through the lift node and is reported in `BaseAuxStatus`.

## Fault registry

Base-controller codes are group `18001`, owned by openamr-platform-fw
([#10](https://github.com/openAMRobot/openamr-platform-fw/issues/10)). The constants in BaseFault.msg are a proposed in-package representation, not an approved
authoritative registry. Decision 5 must settle the registry file format and whether message
constants are generated or maintained alongside it. Consumers must not treat provisional
individual IDs as approved until the registry owner confirms them.

E-01 reason/fault mapping is provisional and must be checked against the E-01 rev 4 Fault and
Inhibit Matrix. Codes `18018`, `18019`, `18021` to `18023` and `18028` are proposed additions;
all require central registry confirmation. The existing 18001–18017 block remains owned by
platform-fw #10; this package does not claim authorship of those existing IDs.

| E-01 condition / reason | Registry / reporting |
|---|---|
| `HW_SAFETY_NOT_ENABLED` | `PNOZ_DIAGNOSTIC_NOT_ENABLED` (18012): fresh Y32 low diagnostic only; not proof the whole hardwired chain is open. State effect is conditional on E-01 state; low is expected while CHARGING. |
| `ESTOP_DIAG` positively active | `ESTOP_DIAGNOSTIC_ACTIVE` (18018) |
| E-stop diagnostic missing/stale/unreadable | `ESTOP_DIAGNOSTIC_UNKNOWN` (18028), distinct from a positively observed active E-stop |
| `COMMS_LOST` | `BASE_HOST_LINK_LOST` (18002) |
| `BMS_FAULT` | `BMS_FAULT` (18009) |
| `INPUT_INVALID` (missing/stale) | `SAFETY_INPUT_UNKNOWN` (18010), with source identifying the input |
| `INPUT_INVALID` (implausible encoder) | `ENCODER_ODOMETRY_FAULT` (18006) |
| `INPUT_INVALID` (`RESET_HIGH`) | `RESET_INPUT_HIGH` (18019) |
| `CHARGER_FAULT` / `CHARGE_INTERLOCK` | `CHARGER_FAULT` (18021) / `CHARGE_INTERLOCK_FAULT` (18022) |
| `DRIVE_FAULT` / `DRIVE_COMMS` / `DRIVE_CONFIG` | `DRIVER_FAULT` (18004) / `DRIVER_COMM_LOST` (18003) / `DRIVE_CONFIG_MISMATCH` (18023) |
| UI Stop | `ui_stop_active`; not a fault code |
| Charge ended | charging command/state lifecycle; not a fault code |
| T8 reboot requested | `reboot_request_pending`; not a fault code |
| Boot power-on / watchdog / software | `reset_cause` and `reset_flags_raw`; not `BOOT_*` fault codes |

`BaseFault` contains faults/diagnostic fault conditions only. The `reason_mask` contains active
fault/inhibit reasons only; it excludes normal events, UI Stop itself, charge completion, and
boot/reset causes. ``first_reason` is the first fault reason for the current LOCKED/CHARGER_FAULT episode,
not a general event history. `PNOZ_DIAGNOSTIC_NOT_ENABLED` must not be raised merely because
SAFETY_OK is low during normal CHARGING.

### Fault lifecycle combinations

`BaseFault` keeps the live condition, retained latch, acknowledgement and recovery requirement
separate. The following combinations are intentional:

| `lifecycle` | `condition_active` | Meaning |
|---|---|---|
| `ACTIVE` | `OBS_YES` | Non-latching condition is present now. |
| `LATCHED` | `OBS_YES` or `OBS_NO` | Latch is held; the live condition may still be present or may have cleared. |
| `ACKNOWLEDGED` | `OBS_YES` or `OBS_NO` | Acknowledgement was accepted; it does not assert that the condition cleared. |
| `CLEARED` | `OBS_NO` | No active condition and no retained latch. |

`UNKNOWN` is never interpreted as cleared. `ACKNOWLEDGED + OBS_YES` is valid and required for
the charge-interlock case where SAFETY_OK may remain high (including a possible welded KCHG).
Acknowledgement records the operator/Jetson action only. It is not hardware verification, does
not prove KCHG or any contactor opened, does not clear `condition_active`, does not satisfy
`recovery_required`, and never grants motion authority. A charge-interlock acknowledgement may
be accepted while SAFETY_OK is high; every subsequent charge attempt reruns the full interlock
sequence. Do not require SAFETY_OK low as a precondition for acknowledging this fault.

A producer restart never clears a latched fault. Boot lands in `LOCKED` with charging off and
re-reads live conditions. Command timeout is non-latching. UI Stop, charge completion, T8 reboot
request and boot/reset causes are not fault codes: they are represented by `ui_stop_active`, the
charging command/state lifecycle, `reboot_request_pending`, and `reset_cause` respectively.

## Not covered

- A separate base-stopped evidence message/topic, its producer, QoS, rate and timeout (Decisions 1 and 8).
- ResetBaseController.srv (Decision 11).
- MB7060 range topic names, rate and publisher (Decision 12).
- Drive configuration (2000h, 1017h), brakes and the robot lift-interlock enforcement owner.
  The simulation-side guard is a mirror only, not the robot enforcement implementation.

## Open decisions

The following remain open in I8 rev4:

- Decision 1: final message set; whether BaseFault, BaseSubsystemStatus and BaseMotionConstraint
  are included in the first package; whether a separate base-stopped evidence interface is needed.
- Decision 2: controller state, readiness, command acceptance and recovery semantics.
  E-01 rev4 supplies a working proposal, not I8 approval.
- Decision 3: non-latching STM32 command-timeout behaviour and its relationship to the
  heartbeat/consumer timeout.
- Decision 4: fault lifecycle, active/latched/acknowledged/cleared semantics, retention,
  deterministic ordering and bounded-list overflow.
- Decision 5: registry file format, generated versus maintained constants, and whether
  BaseFault carries operator text or a registry key. Group 18001 ownership is frozen;
  proposed individual IDs still need registry-owner review.
- Decision 6: reset-cause enum after STM32H723 reset-flag verification.
- Decision 7: direction-specific travel inhibit when floor coverage is lost, with Navigation.
- Decision 8: robot lift/auxiliary interlock enforcement owner and handshake. The requirement
  is base confirmed stopped AND both arms in the approved safe pose (stowed or carry);
  UNKNOWN, invalid or stale inputs do not satisfy it. The exact carry pose and robot control
  owner remain unresolved. The simulation-side guard is not a substitute.
- Decision 11: whether ResetBaseController.srv belongs in the first package.
- Decision 12: MB7060 topic names, rate, publisher and consumer freshness contract.
- Decision 13: independent measured-position source, declared-position source, separate
  validity/freshness, homing semantics, raw-device versus mapped-registry fault representation,
  and measured/declared disagreement rule and threshold.

Decisions 9 and 10 are frozen: the two status topics/types, QoS, rates, stale thresholds,
receipt-time freshness, boot ID, uint32 sequence, uint16 contract version starting at 1,
fault group 18001 ownership, restart-not-clearing-latched-fault rule, powered debug off by
default and watchdog-first ordering. These frozen items are not reopened by this draft.

The four separate firmware decisions Alex requested by 11 Nov—ZLAC 2000h/heartbeat timeout,
robot lift-interlock owner, CTL-017 v1 object dictionary, and safety/IMU pin assignments—are
also still awaiting Evans' decision/recording. They are tracked separately from the I8
message-schema decisions above. Any change to a frozen field requires a change request in #30.
