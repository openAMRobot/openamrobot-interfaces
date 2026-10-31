# Whole-robot status and stop scope

Status: **Proposed**. For owner review; no owner has accepted any part of it yet.
Documentation only: this proposal adds no message, service or action file and no code.
Every topic, field, reason code and action named below is a proposal and changes only
through a contract change request, as AGENTS.md requires.

Scope: OpenAMRobot 2.0 (base, approved-in-principle DOLD Hexalift V4 lift, two OpenArm 2.0
arms, head light), Use_Case_1 baseline. This is functional status. It is not a safety
function and is never safety evidence. The hardwired chain (PNOZ s3, K1 and K2) cuts traction,
both arms and the lift in hardware; nothing here replaces, resets or validates it.

## 0. Owners and decisions this proposal builds on

Owner decisions of 30 October 2026, taken as given:

- Robot states: `READY`, `EXECUTING`, `WAITING`, `BLOCKED`, `RECOVERING`, `NEEDS_ASSISTANCE`,
  `SAFETY_STOPPED`, `FAULTED`.
- UI presentation states: `DISCONNECTED`, `UNKNOWN`, `STALE`, `STOPPED (SOFTWARE)`.
- `SAFETY_STOPPED` comes only from the hardwired chain's diagnostic signal.
- Stop scope target: one robot-side Stop (software) for base, arms and lift, designed by the
  platform lead and the safety owner. Until then it is labelled **base only**.

These decisions are registered in openAMRobot/.github PR 73 (decisions.yaml, not merged at the
time of writing):

| Register entry | Status in the register | Used in |
|---|---|---|
| `STATUS-VOCABULARY` | recorded | sections 3, 4 and 4.2 |
| `STOP-SCOPE` | recorded | section 5 |
| `UI-MANUAL-VELOCITY-INPUT` | open (Proposed until openamr-platform-sw PR 90 merges) | sections 1, 5 and 6 |

This proposal follows those entries and states no value that contradicts them. Where it adds
detail beyond them, the detail is a proposal for the entry's owner.

Roles (each pending acceptance by the person holding it):

| Area | Role | Contract home |
|---|---|---|
| Readiness roll-up (`/robot/status`) and this readiness contract | contract owner, who is also the platform lead | decided by the contract owner (Q1) |
| Base status, aux-device block, chain diagnostics, lift node | I8 owner, who is also the safety owner | `openamr_base_msgs`, issue 30 |
| Arm, gripper and motion-authority status | arm status owner (I1) | decided by the contract owner (Q1) |
| Configuration identity consumers (C9, C10) | Embodied AI lead | C9 contract |
| Review | tech lead reviewer | |

## 1. What the sources define today

| Source | What it defines today | What it leaves open |
|---|---|---|
| `openamr_nav_msgs` and its CONTRACT.md (this repository, main d048fb8) | `NavigationStatus` (contract version 1) aggregating stack, localization, sensors, task, recovery and protection; separate `DockingStatus` and `ParkingStatus`. Reliable, transient-local, depth 1, publish on change plus a 2 Hz heartbeat, staleness detected from silence. Enum value 0 is UNKNOWN (or the safe NOT_READY). Reason codes are append-only, grouped x001, 0 is NONE. Field validity rules per state. `ESTOP_ACTIVE` (9003) only on fresh I8 telemetry; stale or missing telemetry is `BASE_LINK_LOST` (9001) or `BASE_NOT_READY` (9002) and forces NOT_READY. Explicitly navigation only, not whole-robot readiness. | Topic names are proposals. No base status message exists yet. |
| openamrobot-interfaces issue 30 (I8 `openamr_base_msgs`) | Scope of the package: base controller status with reset reason and the monotonic microsecond time base; a generic aux-device block (lift, head light, Getac power-good, chest E-stop status); E-stop and SAFETY_OK as diagnostics only; fault codes in a central registry here, base-controller codes owned by platform-fw; a CONTRACT.md in the `openamr_nav_msgs` style. Owner: I8 owner. | Not on main. No field list, topic names or freshness values yet. Date to be agreed with the platform lead. |
| openamr-platform-fw issue 10 (I8 architecture review) | STM32H723ZG base controller; FDCAN1 traction, FDCAN2 BMS, FDCAN3 auxiliary actuators; ZLAC8015D stops on loss of STM32 communication; IWDG fed only by the control loop; reset reason in BaseControllerStatus; 64-bit monotonic microsecond time base; micro-ROS over Ethernet; central fault registry. | Message content. |
| openamr-platform-fw issue 6 | Base-controller side of E-stop observation, deliberate reset, actuator re-enable, brake and drive holding, validation before motion, safe recovery after restart, 15 s readiness target. Software never resumes motion after E-stop by itself. `ESTOP_ACTIVE` is not evidence of a safety implementation. | State machine and evidence not delivered. |
| openamrobot-manipulation issue 7 | Names the states and reasons to define: `BASE_SETTLING`, `MANIPULATION_READY`, configurable thresholds and hold times, `ARM_MOTION_ACTIVE`, `ARMS_NOT_IN_TRAVEL_POSE`, deterministic travel-inhibition reasons, ownership per state between I1, I8, manipulation and navigation, safe rejection of unsupported capabilities. | Definitions, transitions and ownership not written. |
| openamrobot-manipulation issue 24 (UC1-40) | Base and arms never move at the same time, enforced in the motion layer, not only the UI: arm goals refused while the base is commanded or moving, base commands refused during an arm trajectory, both with a typed reason; Stop and abort stay available. Owner: arm status owner, due 13 Nov 2026. | Arbiter location and reason codes. |
| openamr-upperbody-sw PR 14 (draft, head 4629075) | Joint names `openarm_{left,right}_joint1..7`, `openarm_{left,right}_finger_joint1` (finger_joint2 is a mimic), `lift_joint` (prismatic, 0 to 0.350 m, no controller, outside arm control authority). Controllers `left_arm_controller`, `right_arm_controller` (JointTrajectoryController), `left_gripper_controller`, `right_gripper_controller` (GripperActionController), `joint_state_broadcaster`, 100 Hz; mock, gazebo and real profiles. SRDF named states `home` and `hands_up`. `upperbody_configuration.yaml`: axes column, base_plate, head_pitch, base_tilt; lift stops L1000, L1175, L1350 as calibration IDs; `datums.yaml` revision 2026-10-28.a feeds every `config_id`; `config_id` is a digest of a compact sorted-key JSON payload. The PR records that no runtime producer of the configuration identity has an owner. | Neither upperbody main nor PR 14 has a STATE.md. No stowed or carry pose is declared. |
| openamr-platform-sw PR 90 (stop lock, changes requested 27 Oct) | `safety_stop_gate_node`: `/safety/stop_lock` (Bool), released only by `/safety/stop_lock_release` and engaged by `/safety/stop_lock_engage` (both `std_srvs/Trigger`); starts locked; zero on `cmd_vel_stop` while locked; post-mux gate forces zero on `cmd_vel_gated`; twist_mux lock timeout 0.3 s; `velocity_timeout` 0.3 s. Base velocity only. Functional stop, explicitly not the hardwired E-stop. | Arms and lift are outside it. UI wiring to the engage service unconfirmed. Not merged. |
| P-03 rev20.1 item 24 | Lift node CTL-017 (I8 owner) on CAN3; three inductive stop sensors, one per stop L1000, L1175, L1350, on the always-on 24 V rail; a sensor active at power-up gives a valid position without homing; between stops the node moves slowly to the nearest sensor; each stop cross-checks the Hall count (F02); two active sensors is a fault; no duty-cycle limit in firmware; stop to stop about 10 s. Second E-stop on the rear of the static lift profile, spare NO to a lift-node input for diagnostics. Head light Falcon FLDL-i150x15-W, on/off and optional PWM by a lift-node low-side output, on F-PANEL so it stays on during an E-stop. Aux status is the generic aux-device block (CAN3 decision D17): motor current, target stop, stop sensors, head light, Getac power-good, future sensors, chest E-stop observation. | Message fields. |
| P-03 rev20.1 items 14 and 15 (context) | Every auxiliary actuator is powered through the hardwired chain, with firmware interlocks: no motion while the base moves, while the arms are outside a safe pose, or on stale state. Lift motion only in the stowed or carry safe pose with the base stopped. Baseline head pitch hp30 since 28 Oct 2026. | Safe poses not yet declared in the model. |
| E-01 rev1.5 | An E-stop cuts actuator power only (traction, both arms, lift) through PNOZ s3 and K1/K2; Jetson, controller, 5 V and regulated 24 V stay on. One RESET button: short press is the monitored PNOZ reset, motion still needs a command; 5 s hold reboots the electronics. Diagnostics, not safety: `SAFETY_OK` (Y32), `ESTOP_BASE`, `ESTOP_CHEST` (via the lift node over CAN3), `RESET_PRESSED`, `BMS_STATUS`, `WCM_FAULT`; "PNOZ did not enable" diagnosis after the reset timeout. Charging opens the PNOZ supply, so actuators are off while charging. Lift holds on E-stop and power loss (supplier written confirmation recorded in E-01); stop sensors stay readable after an E-stop. No bus carries a safety function. | |

Source access note: P-03 rev20.1 and E-01 rev1.5 were read as the internal source documents;
this public file cites them by name and revision only.

## 2. Producers and topics

All names are proposals. Every message carries `std_msgs/Header`, a `contract_version`, and
uses the `openamr_nav_msgs` conventions: enum 0 is UNKNOWN, reason 0 is NONE, append-only reason
groups, field validity stated per state.

| Topic (proposed) | Content | Producer | Owner |
|---|---|---|---|
| `/base/status` | Base controller status: ready state, reset reason, time base, fault codes | base controller (micro-ROS) | I8 owner |
| `/base/aux_status` | Aux-device block: lift entry, head light, Getac power-good, chest E-stop observation | base controller, relaying CTL-017 over CAN3 | I8 owner |
| `/base/safety_chain` | Hardwired chain diagnostics (may be a block inside `/base/status`, Q3) | base controller | I8 owner |
| `/joint_states` (existing) | `lift_joint` position from the I8 lift entry | adapter in platform-sw or upperbody-sw (Q5) | I8 owner (data), arm status owner (consumer) |
| `/manipulation/arm_status` | One entry per arm and per gripper | manipulation status node | arm status owner |
| `/manipulation/motion_authority` | Who may move now, and why others are inhibited | motion arbiter of manipulation issue 24 | arm status owner, base side contract owner |
| `/robot/configuration` | Configuration identity record and hash (section 7) | robot-side configuration node | Q11 |
| `/robot/status` | Robot state, robot readiness, reasons, per-source summary, stop scope | readiness roll-up | contract owner |
| `/safety/stop_lock` (existing, PR 90) | Software stop lock | `safety_stop_gate_node` | contract owner |

### 2.1 Arm status (per arm, `left` and `right`)

- `arm_id`: `left` or `right`.
- `hardware_profile`: `mock`, `gazebo` or `real`, copied from the launch profile. A UI shows the
  profile next to the state, so fake hardware never reads as the robot.
- `mode`: `UNKNOWN`, `ABSENT` (not in the active profile), `DISCONNECTED` (hardware interface
  reports no link), `INACTIVE` (hardware up, trajectory controller not active), `HOLDING`
  (controller active, no goal), `EXECUTING` (a trajectory goal is active), `FAULT`.
- `controller_active`: state of `{side}_arm_controller` as reported by controller_manager.
- `fault`: `HEALTH_UNKNOWN`, `HEALTH_OK`, `HEALTH_FAULT`, plus `reason` and the hardware's native
  error code where one exists.
- `in_safe_pose`: `UNKNOWN`, `NO`, `STOWED`, `CARRY`. Stays `UNKNOWN` until the stowed and carry
  poses are declared in the SRDF (Q7); `UNKNOWN` never counts as safe.
- `joint_state_age`: age of the newest `openarm_{side}_joint1..7` sample.

### 2.2 Gripper status (per side)

- `controller_active` for `{side}_gripper_controller`, `position` of `openarm_{side}_finger_joint1`,
  `moving`, `last_result` (`NONE`, `SUCCEEDED`, `ABORTED`, `CANCELED`), `fault`, `reason`.
- No grasp, contact or load field. A fake or simulated gripper result does not show contact,
  load or that an object is held, and this status does not claim it.

### 2.3 Lift (inside the I8 aux-device block)

- `position_m` on `lift_joint` (0 to 0.350 m), from the Hall count; `position_valid` (a stop
  sensor was seen since power-up, or the node is at a sensor now).
- `moving`, `direction`, `motor_current_a`.
- `at_stop`: `UNKNOWN`, `NONE` (between stops), `L1000`, `L1175`, `L1350`.
- `target_stop`: same enum, `NONE` when idle.
- `stop_sensors`: three booleans in the order L1000, L1175, L1350, raw from the sensors.
- `fault`, `reason`: covers two sensors active, Hall cross-check mismatch at a stop (F02), motor
  over-current, lift node link lost.
- `seeking_nearest_stop`: true while the node moves slowly to the nearest sensor after power-up.

The lift is described only as approved in principle. Its holding evidence, CAD and CAN3
interface remain release gates.

### 2.4 Head light, Getac and chest E-stop (aux-device block)

- Head light: `state` (`UNKNOWN`, `OFF`, `ON`), `level` (0 to 1, 1 when not dimmed), `reason`.
- Getac power-good: boolean with UNKNOWN.
- Chest E-stop observation: `UNKNOWN`, `RELEASED`, `PRESSED`, from the spare NO at the lift node.
  It is `UNKNOWN` whenever the lift node link is lost, even when `/base/status` is fresh.

### 2.5 Motion authority

- `holder`: `UNKNOWN`, `NONE`, `BASE`, `ARMS`, `LIFT`. One holder at a time, which is the issue 24
  rule (base and arms exclusive) extended by P-03 items 14 and 15 (lift only with the base
  stopped and the arms in a safe pose).
- `inhibited`: one entry per subsystem with a reason: `BASE_MOTION_ACTIVE`, `ARM_MOTION_ACTIVE`,
  `LIFT_MOTION_ACTIVE`, `BASE_SETTLING`, `ARMS_NOT_IN_TRAVEL_POSE`, `ARMS_NOT_IN_SAFE_POSE`,
  `SOFTWARE_STOP_ENGAGED`, `SAFETY_STOPPED`, `SOURCE_STALE`.
- `MANIPULATION_READY` and `BASE_SETTLING` keep the meanings issue 7 will define; this
  proposal only reserves where they appear.
- Firmware interlocks on the lift (item 14) stay in firmware. This topic reports the arbiter's
  view; it is not the interlock.

### 2.6 Hardwired chain diagnostics

Diagnostics only, as issue 30 and E-01 require:

- `safety_ok`: `UNKNOWN`, `OPEN`, `CLOSED`, from Y32.
- `estop_base`: `UNKNOWN`, `RELEASED`, `PRESSED`; `estop_chest` taken from the aux block.
- `reset_required`: RESET lamp state as the controller drives it.
- `reset_pressed`.
- `charge_inhibit_active`: the charge request is on, so the PNOZ supply is open.
- `diagnosis`: `NONE`, `ESTOP_PRESSED`, `RESET_REQUIRED`, `CHARGE_INHIBIT`, `PNOZ_DID_NOT_ENABLE`
  (the E-01 reset-timeout case), `CAUSE_UNKNOWN`.

`SAFETY_STOPPED` is derived only from `safety_ok == OPEN` in a fresh message. A pressed-button
observation without `OPEN` is reported as a diagnostic mismatch, not as `SAFETY_STOPPED`.
Whether `safety_ok == OPEN` caused by charging is `SAFETY_STOPPED` is not settled; it is
pending Q8 (section 4.1).

### 2.7 Reason code groups

Proposed new groups, continuing the `NavigationStatus` scheme (no overlap with 1001 to 9004):

| Group | Area |
|---|---|
| 10001 | arm |
| 11001 | gripper |
| 12001 | lift |
| 13001 | motion authority and travel inhibition (issue 7, issue 24) |
| 14001 | hardwired chain diagnostics |
| 15001 | software stop |
| 16001 | configuration identity |
| 17001 | command acceptance and results (section 6) |

Base-controller fault codes stay owned by platform-fw in the central registry (issue 10). Where
the registry lives is Q2.

## 3. Freshness, UNKNOWN and fault rules

Every source follows the `NavigationStatus` publish behaviour: reliable, transient-local,
depth 1, publish on change plus a heartbeat. Freshness is measured by the consumer on a
monotonic (steady) clock from the last receipt, never on simulated time, so a paused or zero
`/clock` cannot make a source look fresh (the PR 90 sim-clock finding). Header stamps are used
for ordering and age reporting; the base controller's monotonic microsecond time base is the
stamp source for `/base/*`.

Default values below are proposals, recorded under a `thresholds_id` like `NavigationStatus`,
and are not decisions until the owner accepts them.

| Source | Heartbeat | Stale after | When stale or never received |
|---|---|---|---|
| `/base/status`, `/base/safety_chain` | 10 Hz | 0.3 s | base `UNKNOWN`, reason `BASE_LINK_LOST`; chain `safety_ok = UNKNOWN`, never `SAFETY_STOPPED` |
| `/base/aux_status` | 5 Hz | 0.6 s | lift, head light, Getac and chest E-stop `UNKNOWN` |
| lift entry with fresh aux block but lift node link lost | | | lift `UNKNOWN`, reason `LIFT_LINK_LOST`; chest E-stop `UNKNOWN` |
| `/manipulation/arm_status` | 2 Hz | 1.5 s | each arm `UNKNOWN`, reason `ARM_STATUS_STALE` |
| arm joint states inside a fresh arm status | 100 Hz | 0.2 s | that arm `mode = UNKNOWN`, reason `ARM_JOINT_STATE_STALE` |
| `/manipulation/motion_authority` | 2 Hz | 1.5 s | `holder = UNKNOWN`; every motion command is rejected |
| `/robot/configuration` | latched, 0.2 Hz heartbeat | 15 s | identity `UNKNOWN`, robot not ready |
| `/navigation/status` | 2 Hz | 1.5 s | navigation readiness treated as NOT_READY |
| `/robot/status` (UI side) | 2 Hz | 1.5 s | UI presents `STALE` |

Rules:

1. A source never heard since start is `UNKNOWN`, not `ABSENT`. `ABSENT` means the active
   profile does not include it (a base-only profile has no arms).
2. Stale is `UNKNOWN` with a link or stale reason. Stale never reads as OK, never as
   `SAFETY_STOPPED` and never as `FAULTED` by itself.
3. A required source that is `UNKNOWN` makes the robot not ready.
4. **Fault latch, per source.** A fault reported by source S is latched by the roll-up under S's
   source ID. The latch clears only when S itself publishes a fresh message with no fault.
   Another source, staleness, a UI action or a timeout does not clear it. A stale source with a
   latched fault shows both: `FAULTED` and the stale reason.
5. A producer restart (new reset reason or new process) is the same source for the latch; the
   first fresh message after the restart decides. Whether a restart alone may clear a latch is
   Q4.
6. Field validity as in CONTRACT.md: `position_m` is meaningful only when `position_valid`;
   `target_stop` only while `moving` or `seeking_nearest_stop`; `joint_state_age` is 0 when
   `mode` is `ABSENT`; any `reason` is NONE exactly when its state is in its nothing-wrong value.

## 4. Robot ready, kept separate from navigation readiness

This section separates two things:

- **Global `robot_readiness`** (this section): is the whole robot ready to run tasks.
- **Per-subsystem goal admissibility** (section 4.3): may one specific goal for one subsystem
  be accepted now. For task goals, admissibility includes `robot_readiness`. For the recovery
  goals of section 4.3 it does not.

`robot_readiness` (NOT_READY by default, READY) answers one question: is the robot ready to
run tasks now. It is an explicit AND, and the roll-up lists every unmet term in
`not_ready_reasons`:

1. All sources required by the active profile are fresh and not `UNKNOWN`.
2. Hardwired chain `safety_ok == CLOSED` in a fresh message.
3. Base controller reports ready (the issue 6 conditions), no `BASE_NOT_READY`.
4. Software stop lock released.
5. No latched fault in any required source.
6. Each required arm: `mode == HOLDING`, `controller_active`, `fault == HEALTH_OK`,
   `in_safe_pose` is `STOWED` or `CARRY`.
7. Each required gripper: controller active, no fault.
8. Lift: `position_valid`, not moving, no fault, `at_stop` is a calibrated stop.
9. Motion authority `holder == NONE`.
10. Configuration identity present and its hash equals the expected hash for this deployment.

Navigation readiness stays in `NavigationStatus.navigation_readiness` and is not an input to
`robot_readiness`, and `robot_readiness` is not fed back into `NavigationStatus`. A navigation
goal needs both. An arm, gripper or lift task goal needs `robot_readiness` and a grant from the
motion arbiter. An arm recovery goal follows section 4.3 instead. The UI shows navigation
readiness and robot readiness as two separate signals. This keeps CONTRACT.md's statement that navigation status is
not whole-robot readiness true.

### 4.1 Robot state

The roll-up publishes one `robot_state`. The first matching row wins:

| Robot state | Condition |
|---|---|
| pending Q8 (platform and safety owners) | fresh `safety_ok == OPEN` while fresh `charge_inhibit_active` is true (the chain is open because of charging). Not a settled rule. The alternatives are `SAFETY_STOPPED` with diagnosis `CHARGE_INHIBIT`, or a separate presentation; Q8 decides. Whichever is chosen, term 2 keeps `robot_readiness` NOT_READY and no motion goal is admissible, because the actuators are unpowered |
| `SAFETY_STOPPED` | fresh `safety_ok == OPEN` in every other case |
| `FAULTED` | any latched fault in a required source, or a Stop not confirmed (section 5) |
| `NEEDS_ASSISTANCE` | a condition only a person clears: recovery limit reached, a task aborted with a reason marked operator-required, lift position not valid after the seek timed out, an arm healthy but outside a safe pose with no goal active (it needs a recovery goal, section 4.3) |
| `RECOVERING` | a navigation recovery is running, or the lift is seeking its nearest stop |
| `BLOCKED` | a goal is active but cannot progress: travel inhibited, authority held by another subsystem, software stop engaged during a goal, path blocked |
| `EXECUTING` | an accepted goal is active (navigation, docking, arm, gripper, lift) |
| `WAITING` | no goal, not ready, and every unmet term is expected to clear without a person (startup, base settling, a source still starting) |
| `READY` | `robot_readiness == READY` and nothing is executing |

When no required source has been received, `robot_state` is `WAITING` with the reason
`NO_DATA_YET`, and the UI presents `UNKNOWN`.

### 4.2 UI presentation

Per `STATUS-VOCABULARY`, these are UI presentation states, not robot states. The UI derives
its presentation state before showing the robot state:

1. `DISCONNECTED`: the UI has no link to the robot.
2. `STALE`: `/robot/status` is older than its stale limit; last values greyed out.
3. `UNKNOWN`: `robot_state` received but the contract version is unknown, or the roll-up itself
   reports no data yet.
4. `STOPPED (SOFTWARE)`: lock engaged and `robot_state` is not `SAFETY_STOPPED` or `FAULTED`;
   shown with the stop scope label (section 5).
5. Otherwise the robot state as published.

`SAFETY_STOPPED` is never shown from a UI-side guess, only from the published robot state.

### 4.3 Goal admissibility per subsystem

Term 6 of section 4 needs every required arm in `STOWED` or `CARRY`, and `ArmToNamedPose`
(section 6) is the way an arm reaches those poses. If every arm goal needed
`robot_readiness`, a healthy arm in any other pose could never be moved to a safe pose. Goal
admissibility is therefore decided per goal and per subsystem, not by `robot_readiness` alone.

**Task goals.** Navigation, docking, `LiftToStop`, gripper goals, and `ArmToNamedPose` to any
pose other than the stowed and carry poses are admissible only when all of these hold:

1. `robot_readiness == READY` (navigation goals also need `navigation_readiness`).
2. The motion arbiter grants authority to the subsystem.

Otherwise the goal is rejected with `NOT_READY` or the arbiter's reason.

**Arm recovery goals.** `ArmToNamedPose` with `pose_name` `stowed` or `carry` (the SRDF named
states for the `STOWED` and `CARRY` safe poses) is admissible
even while `robot_readiness` is NOT_READY. It is admissible when all of these hold:

1. The target pose is declared in the SRDF (Q7). Until Q7 declares the stowed and carry poses,
   no recovery goal exists and this path is not available.
2. The arm's own subsystem is healthy: its `/manipulation/arm_status` entry and its joint
   states are fresh, `mode == HOLDING`, `controller_active`, `fault == HEALTH_OK`, and no latched
   fault under that arm's source. With `arm: BOTH`, both arms must meet this.
3. The motion arbiter grants `ARMS` authority. Under openamrobot-manipulation issue 24 the
   arbiter refuses while the base is commanded or moving, and under P-03 items 14 and 15 while
   the lift moves. It also refuses while the software stop is engaged, while `safety_ok` is not
   `CLOSED` in a fresh message, and while any source it needs is stale.

Faults, staleness and pose in other subsystems (lift, grippers, the other arm when `arm` names
one side, configuration identity) do not block a recovery goal by themselves. They only block it
when the arbiter's own rules use them.

A recovery goal always goes through the motion arbiter and the hardware interlocks, never
around them:

- There is no bypass flag, override field or maintenance mode in this contract.
- The firmware interlocks and the hardwired chain apply unchanged. If an interlock stops the
  motion, the goal aborts with its reason.
- While the recovery goal runs, the arbiter holds `ARMS` authority, so base commands are
  refused with `ARM_MOTION_ACTIVE` and lift goals with `AUTHORITY_HELD`.
- A Stop (software) or a hardwired stop aborts the recovery goal like any other goal.
- A successful recovery goal does not make the robot ready by itself. It only meets term 6 for
  that arm; every other term is still checked.

**Worked example: an arm left outside a safe pose after a fault reset.**

1. The left arm reported a fault during a task. Its fault latched, and the robot was `FAULTED`.
2. The fault is reset. The left arm source publishes a fresh message with no fault, so the latch
   clears (section 3, rule 4). The arm is `HOLDING`, controller active, `HEALTH_OK`, but
   `in_safe_pose == NO`.
3. `robot_readiness` is NOT_READY with `ARMS_NOT_IN_SAFE_POSE` (term 6). `robot_state` is
   `NEEDS_ASSISTANCE`. The base is stopped, the lift is still, and the software stop is released.
4. The operator sends `ArmToNamedPose` with `arm: LEFT` and `pose_name: stowed`. The pose is
   declared, the left arm is healthy, and the arbiter grants `ARMS`. The goal is accepted and
   `robot_state` is `EXECUTING`.
5. While it runs, a base command is refused with `ARM_MOTION_ACTIVE`. A `LiftToStop` goal sent
   at the same time is rejected with `NOT_READY`.
6. The arm reaches the pose. The result is `SUCCEEDED` only when the joint error is within
   tolerance on fresh joint states (section 6). The arm reports `in_safe_pose == STOWED`, and the
   arbiter returns to `holder == NONE`.
7. Term 6 is now met for the left arm. If every other term holds, `robot_readiness` becomes
   READY and `robot_state` is `READY`.

In the same situation, `ArmToNamedPose` to `home` is rejected with `NOT_READY`, because `home`
is not a recovery pose.

## 5. Stop scope (for the platform lead and the safety owner)

This section states requirements and a proposed shape. The design and any implementation
belong to the platform lead and the safety owner. An agent does not author it; the
functional stop path needs two human approvals including the platform lead.

Register: `STOP-SCOPE` (recorded) fixes the meaning and today's scope; the lock interface is
`UI-MANUAL-VELOCITY-INPUT` (open): `/safety/stop_lock` (`std_msgs/Bool`, reliable, transient
local), engaged by `/safety/stop_lock_engage` and released only by `/safety/stop_lock_release`
(both `std_srvs/Trigger`). "E-stop" means only the hardwired buttons.

**Today (PR 90, not merged):** the lock gates base velocity only. The UI button is labelled
"Stop (software)" with the scope text **base only**. Arms and lift continue an active goal.

**Target:** one robot-side Stop (software) with one lock state, owned by one node, engaged by
the existing `/safety/stop_lock_engage` and released by `/safety/stop_lock_release`. It is a
functional stop; it does not remove power, does not touch motor enable, brakes or contactors,
and is never described as an E-stop or as making the robot safe.

| Subsystem | On engage (proposed) | Confirmation reported |
|---|---|---|
| Base | unchanged PR 90 gate: zero on `cmd_vel_gated` | gate node reports locked |
| Arms | cancel active trajectory goals; the trajectory controller holds the current position; new arm goals rejected with `SOFTWARE_STOP_ENGAGED` | arm `mode == HOLDING`, joint velocities below a threshold |
| Grippers | cancel active goals and hold the current position; never open on Stop, so a held object is not dropped | gripper not moving |
| Lift | halt command to the lift node over I8; the column holds by itself; new lift goals rejected | lift `moving == false` |
| Head light | unchanged; not a motion source | none |

- `/robot/status` carries `stop_scope` (`BASE_ONLY` until the target is accepted, then
  `WHOLE_ROBOT`) and one confirmation per subsystem in scope.
- If a subsystem in scope does not confirm within a timeout (proposed 1 s), the robot state is
  `FAULTED` with `STOP_NOT_CONFIRMED_<SUBSYSTEM>`, latched until that subsystem confirms.
- **Release** is a deliberate operator action through the release service. It is refused, with
  a reason in the `std_srvs/Trigger` message, while any in-scope subsystem is stale or
  `UNKNOWN` or has a stop-confirmation fault. Release never resumes anything: cancelled goals
  stay cancelled and motion needs a new command, as E-01 states for the hardwired reset.
- After a hardwired stop clears, the software lock is engaged (proposed), so the operator
  releases it explicitly. The software lock already starts engaged (PR 90).
- **UI:** "Stop (software)" button always available while connected, including during
  `SAFETY_STOPPED`; presentation `STOPPED (SOFTWARE)` with the scope label "base only" or
  "base, arms and lift"; the per-subsystem confirmation list; a "Release" control that shows the
  refusal reason. The UI never labels this button E-stop.

## 6. Future commands: actions only

The UI commands arms, grippers, lift and head light only through actions with named
targets. No joint jogging, no lift jogging and no per-joint position or velocity command from
the UI. Manual base driving is outside this section: it stays the UI manual velocity input of
register entry `UI-MANUAL-VELOCITY-INPUT` (Proposed), gated by the stop lock.

| Action (proposed) | Goal | Feedback | Result |
|---|---|---|---|
| `LiftToStop` | `stop_id`: `L1000`, `L1175`, `L1350` | `position_m`, `at_stop`, `moving` | final `at_stop`, `position_m`, outcome, reason |
| `ArmToNamedPose` | `arm`: `LEFT`, `RIGHT`, `BOTH`; `pose_name` from SRDF named states (`home`, `hands_up`, later `stowed` and `carry`, which are the recovery poses of section 4.3) | progress 0 to 1, current joint error | outcome, reason, final joint error |
| `SetHeadLight` | `on`, `level` 0 to 1 | none | outcome, reason, resulting state |

Common semantics:

- **Accept or reject at goal time**, with a reason from group 17001: `SOFTWARE_STOP_ENGAGED`,
  `SAFETY_STOPPED`, `NOT_READY`, `AUTHORITY_HELD` (base moving, arm active, lift active),
  `ARMS_NOT_IN_SAFE_POSE` (lift), `UNKNOWN_TARGET`, `NOT_SUPPORTED` (capability absent in the
  profile, issue 7), `SOURCE_STALE`, `FAULT_LATCHED`, `CONFIGURATION_MISMATCH`, `BUSY`. A rejected
  goal changes nothing. `NOT_READY` applies to task goals only; an arm recovery goal is
  admissible under section 4.3 and is rejected only with its own arm's reason or the arbiter's
  reason (`AUTHORITY_HELD`, `SOFTWARE_STOP_ENGAGED`, `SAFETY_STOPPED`, `SOURCE_STALE`,
  `FAULT_LATCHED`, `UNKNOWN_TARGET`). ROS 2 actions have no reason field on rejection, so the server accepts
  only goals it can run and reports a rejection through an immediate abort with the reason
  (Q9).
- **Timeout:** the server owns a deadline per goal: lift 20 s by default (stop to stop is about
  10 s), arm planned duration plus 50 percent, head light 1 s. On expiry the server halts (lift
  halt, arm hold) and aborts with `TIMEOUT`.
- **Cancel:** the UI shows "cancel requested" from the moment it sends the cancel until the
  result arrives, then the result. Cancel halts and holds; it never returns to the start pose.
  A cancel the server rejects shows "cancel rejected" and the goal continues.
- **Result:** `SUCCEEDED` only when the target is reached and confirmed by an independent
  signal (lift: the stop sensor active and the Hall cross-check passes; arm: joint error within
  tolerance on fresh joint states). Otherwise `ABORTED` with a reason, or `CANCELED`. A Stop
  (software) or a hardwired stop aborts active goals with `ABORTED_SOFTWARE_STOP` or
  `ABORTED_SAFETY_STOPPED`.
- A result from mock or gazebo hardware carries the hardware profile and is not evidence of
  physical reach, contact, load or safety.

## 7. Configuration identity

One robot-side record, published latched on `/robot/configuration`:

| Field | Source |
|---|---|
| `column` | `upperbody_configuration.yaml` (`dold_v4_350`, `tl3_400`) |
| `base_plate` | `bp000`, `bp050` |
| `head_pitch` | `hp15` to `hp35`; baseline `hp30` (P-03 rev20.1, Q12 resolved) |
| `base_tilt` | `bt05`, `bt10`, `bt15` |
| `datums_revision` | `datums.yaml` `revision` |
| `calibration_ids` | head camera per lift stop (L1000, L1175, L1350), base camera; the lift stops are calibration IDs, not configuration axes |
| `config_id` | the PR 14 digest of the canonical description payload |
| `hardware_profile`, `arm_package`, upstream pins, platform-sw pin | as PR 14 records them |
| `record_hash` | `sha256:<hex>` over the compact sorted-key JSON of the record without `record_hash`, the format the C9 schema uses for configuration hashes |

- The roll-up compares `record_hash` with the expected hash for the deployment; a mismatch is
  `CONFIGURATION_MISMATCH` and the robot is not ready.
- C9 and C10 record `record_hash` per episode; an ID recorded under another datums revision is
  not comparable (as PR 14 states).
- The node reads the same files the description uses, so there is one source of the IDs.

## 8. Open questions

| ID | Question | Owner |
|---|---|---|
| Q1 | Contract homes: `/robot/status` in a new `openamr_robot_msgs` package or elsewhere; arm and authority status in the I1 package or a manipulation package | contract owner decides; tech lead reviewer |
| Q2 | Where the central fault registry lives and how the 10001 to 17001 groups relate to platform-fw base codes | I8 owner; tech lead reviewer |
| Q3 | Chain diagnostics as their own topic or a block inside `/base/status`; final topic names for I8 | I8 owner |
| Q4 | May a producer restart alone clear a latched fault, or must a fault-free message follow a deliberate reset | I8 owner (base), arm status owner (arms), contract owner (roll-up) |
| Q5 | Which repository publishes `lift_joint` into `/joint_states` from the I8 lift entry | I8 owner, arm status owner |
| Q6 | Heartbeat and stale values in section 3 | I8 owner (base, lift), arm status owner (arms), contract owner (roll-up) |
| Q7 | Joint values of the stowed and carry safe poses, and the tolerance for `in_safe_pose` | arm status owner, with the manipulation co-owner |
| Q8 | Whether `safety_ok == OPEN` because of charging is `SAFETY_STOPPED` with `CHARGE_INHIBIT` or a separate presentation. Section 4.1 marks this branch as pending Q8, not as a settled rule | contract owner (platform lead) and safety owner |
| Q9 | Rejection pattern for actions: reject at the goal callback (no reason reaches the client) or accept and abort with a reason | arm status owner, contract owner; tech lead reviewer |
| Q10 | Whole-robot Stop design: arm hold method, lift halt path over I8, gripper hold, confirmation timeout, release refusal conditions, lock state after a hardwired reset | contract owner (platform lead) and safety owner |
| Q11 | Owner of the runtime configuration identity producer (PR 14 records none) | Embodied AI lead, with the arm status owner |
| Q12 | **Resolved 30 Oct 2026.** Baseline head pitch is hp30 (P-03 rev20.1). The hp25 default in `upperbody_configuration.yaml` on PR 14 is stale; the PR 14 author fixes it there. Section 7 assumes hp30 | PR 14 author (fix) |
| Q13 | Robot-ready term 8: must the lift be at a calibrated stop, or is any valid position enough | I8 owner, arm status owner |
| Q14 | **Resolved 30 Oct 2026.** The platform lead is the contract owner of this readiness contract; the safety owner is the I8 owner, who leads hardware, firmware and the safety layer | none |
| Q15 | Whether `MANIPULATION_READY` from issue 7 equals terms 6 to 8 of section 4 | arm status owner, manipulation co-owner |
| Q16 | Section 4.3 defines recovery goals for arms only. Term 8 needs the lift at a calibrated stop and `LiftToStop` is a task goal, so a healthy lift between stops after the seek has timed out has the same kind of deadlock. Should `LiftToStop` to the nearest stop be a recovery goal, and under which arbiter conditions (P-03 item 14 needs the arms in a safe pose and the base stopped) | contract owner, I8 owner, arm status owner |
| Q17 | Who may send an arm recovery goal: only an operator from the UI, or also an automatic recovery behaviour on the robot. Section 4.1 assumes an operator (`NEEDS_ASSISTANCE`) | contract owner, arm status owner |
| Q18 | Must a recovery goal also need a matching configuration identity (term 10), so the stowed and carry joint values come from the expected description. Section 4.3 does not require it | contract owner, Embodied AI lead, arm status owner |

## Not verified

- No message, build, DDS or UI test exists for anything here; it is a design text.
- The register entries were read from openAMRobot/.github PR 73 as it stood on 30 Oct 2026;
  this repository is not in their `applies_to` list, so `check_decisions.py` does not scan
  this file in CI.
- No physical robot, safety-chain, lift, arm or stopping-distance evidence is claimed.
