<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Proposed C9 component-profile extension v1

Contract request: [upperbody#35](https://github.com/openAMRobot/openamr-upperbody-sw/issues/35).
Status: **Proposed**, pending software-lead acceptance and source-owner mapping review.

C9 v1 already describes ordered `observation.state` and `action` dimensions with
name, unit, meaning and profile. Its schema and accepted fixture remain byte-for-byte
unchanged. The extension adds `schemas/json/c9-component-profile.schema.json` and
`profiles/c9/mobile-lift-qpos-v1-proposed.json`, a versioned mapping adjunct consumed
alongside the unchanged episode contract. It does not replace native LeRobot or
add fields to v1's closed episode objects. Existing C9/C10 consumers continue to
read their existing sidecars. New consumers bind the adjunct's exact bytes/hash;
C11 must continue rejecting an unsupported full-body policy.

The proposed `openamrobot-mobile-lift-qpos-v1-proposed` vector contains seven left
joints, left gripper, seven right joints, right gripper, lift position, base
forward velocity and base yaw rate. The historical `openamrobot-fixed-mast-19dof`
vector has three base channels, two torso placeholders, six joints per arm and
two grippers. Neither 19-channel profile may
be padded, truncated or relabelled as the other. Model joint names and ROS radian
units are recorded; arm/gripper ranges now match the exact pinned generated-model
bounds; they remain model values, not physically validated limits. No normalized gripper opening, motor angle, finger-joint
angle or Cartesian pose is silently treated as another representation.

The model source pin is upperbody `2ca739202f5c51114de1520902e811817d9b2a62`.
`lift_joint` is prismatic; lower limit is 0 and upper is the `dold_v4_350` stroke
0.350 m from `upperbody_configuration.yaml`. `lift` is its own MoveIt group.
Mock/Gazebo expose lift position control; real hardware does not. Observation
existence does not authorize learned lift action. Action source bindings remain
null until Device Package/CTL-017 and capture owners confirm them. The base mapping
is blocked on platform#116; requested velocity, Nav2 goals, Nav2 outputs,
post-arbitration accepted commands and firmware-applied telemetry remain separate.
No timeout/watchdog/control behavior changes here.

Baseline 1 `firmware_sil` run `44448676604` binds lift position to the `position`
entry for `lift_joint` on merged `/joint_states`. Direct decoding of the published MCAP
found the lift in all 5,512 merged messages and in zero of the 53,209
`/arm/joint_states` messages. The latter supplies the 16 arm and primary gripper
positions. The lift also appears in all 11,024 `/sil/gz/joint_states` messages,
which represent a distinct simulator stream. Counts match `metadata.yaml`.
Measured merged lift positions span −0.0005 m to 0.1752 m. The profile's bounds
describe the pinned model, and capture tolerance remains a separate proposal.
Consumers must bind the corrected adjunct hash when adopting these bytes.
[Simulation recording and source hashes](https://github.com/openAMRobot/openamr-upperbody-sw/releases/tag/dev-evidence-baseline1-c9-2026-11-19).

The pinned revolute gripper models use mirrored joint coordinates in radians,
with left bounds `[0, 0.7854]` and right bounds `[-0.7854, 0]`. The Baseline 1
drivers use the `pinch_gripper` configuration. The driver's `parallel_link`
configuration instead uses a prismatic position in metres.
[Driver configuration review](https://github.com/openAMRobot/openamr-upperbody-sw/issues/79#issuecomment-6953533442).

The Baseline 1 capture candidate reads odometry from `/odom`. In the recorded
navigation route, `/cmd_vel` comes from the collision monitor downstream of
the velocity smoother and upstream of firmware. It carries a command with
forward velocity in m/s and yaw rate in rad/s. The production command and
firmware-applied telemetry bindings remain open.
[Recording command map](https://github.com/openAMRobot/openamr-upperbody-sw/blob/a20746338701e7961c28ba4650e11996a1a76919/ros2/src/openamrobot_build1_scene/config/command_map.yaml#L72).

The referenced Enactic sample at `1add81f9390afbbe1c1ebdf6bac0b22d687c56b4`
records `arms/{left,right}/qpos` (joint1–7 + gripper, eight each) and optionally
`lifter/elevation`. A 16D pair may instead contain Cartesian `pose`
(x/y/z/quaternion/gripper). Dimension alone therefore cannot select a mapping.
17D qpos-plus-lifter is not full body: it has no base command. The consumer
requires explicit representation, ordered names, units and gripper semantics.
Radian/degrees and mm/metres conversions are explicit; the source's lift unit
must be established by metadata, never inferred from magnitude. A ceiling
camera is not silently renamed to the canonical C9 base camera. The accepted
LeRobot OpenArm adapter's degree profile remains distinct.

`lift_positioning` is a proposed recording label, not an approved robot state
machine. Every measured lift-motion sample needs timestamped phase coverage,
measured zero base velocity, a complete reviewed stowed-arm pose and its evidence.
Missing or stale evidence rejects conversion. The current `park` pose is a
placeholder. This check documents data compliance and enforces no interlock.

Verification commands (Python dependencies from existing interfaces verification):

```bash
python -m unittest discover -s tests -p test_c9_components.py -v
python tools/check_c9_component_model.py --upperbody-root ../openamr-upperbody-sw
bash tools/verify.sh
```

The first command checks registered fixtures and immutable v1 bytes. The second
checks pinned source names, order, stroke and groups. The additional generated-model
command below checks expanded URDFs; neither establishes live simulation. The third remains the full required ROS/DDS gate. On the local
macOS host it is BLOCKED at ROS prerequisites. Native conversion and explicit
16/17/unit regressions live in the dependent embodied-AI consumer draft; no QA
implementation is duplicated here. LeRobot v0.6.1 is an inspected development pin,
not a release approval; it requires Python >=3.12 and Torch <2.12.

Review checklist:

- [ ] Software lead adopts/adapts/rejects the adjunct and target ordering.
- [ ] Arm/Device Package owners confirm joint versus motor/gripper representation,
      source units, physical limits, commanded-action capture and reference frames.
- [ ] Combined-model owner supplies expanded URDF and checks exact ranges.
- [ ] Platform owners confirm requested base velocity source and separate accepted/applied telemetry.
- [ ] Lift/firmware and manipulation owners confirm CTL-017 telemetry and a reviewed stowed pose.
- [ ] Camera owner supplies topic/type/frame/acquisition-clock/calibration bindings.
- [ ] Release owner validates the supported LeRobot/runtime pin separately.

Dependencies: no new package dependency in interfaces. Source facts derive from
MIT OpenAMRobot contracts/model configuration and the cited upstream inventory;
no upstream implementation is copied. Software is MIT; this document is CC-BY-4.0.
Codex assisted with schema, tests, mapping and documentation. The published
simulation recording establishes the source binding for that run. Physical
evidence, safety acceptance and new profile acceptance remain outstanding.

## Generated-model follow-up

ROS Jazzy xacro expansion and check_urdf were executed locally in an isolated
Linux container for mock, Gazebo and real profiles. Arm/gripper ranges in the
proposed mapping come from these generated models. The dedicated CI job repeats:

```bash
source /opt/ros/jazzy/setup.bash
python3 tools/verify_c9_generated_model.py --upperbody-root external/upperbody --platform-root external/platform --openarm-root external/openarm --output-dir .verification/c9-generated
```

Pins: upperbody 2ca739202f5c51114de1520902e811817d9b2a62; platform
131e500fc4e5afc9f648cbd7dbf5b416280761fb; openarm_description
14ff67b638ff1c738a1b9a6be8aaa5ce5ed2c831. The tool refuses dirty or different
source heads. Sources are registered in a temporary ament prefix solely for
package resolution; no hardware plugin is loaded and no robot graph is started.

Every mapped joint must exist with the expected revolute/radian or prismatic/metre
type and exact lower/upper model range. The real lift has effort/velocity 0 and no
ROS command interface; mock/Gazebo have one position interface. Unit regressions
reject modified lift/gripper ranges, wrong lift units and an invented real-profile
lift command. CI publishes URDFs, check_urdf logs and source/hash manifest.
No arm/gripper motor-to-joint equivalence or physical measurement is inferred.
The base remains a separately blocked velocity mapping with unknown bounds.
