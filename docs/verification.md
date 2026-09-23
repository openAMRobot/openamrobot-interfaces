# ROS 2 Jazzy build gate

The `ROS 2 Jazzy` workflow runs on pull requests and pushes to `main`, on
Ubuntu 24.04 in the official `ros:jazzy-ros-base` container. It resolves
dependencies from the manifests under `ros2/` using rosdep, builds all packages
with colcon, sources the install, and checks every source `.msg`, `.srv`, and
`.action` definition using `ros2 interface show`, Python class loading, and
generated native Python type-support loading. New packages, including the
navigation messages, are discovered automatically. No robot is required.

The required result is **quality/build** passing. A dependency,
build, lookup, or import failure fails the job; discovering no interfaces also
fails. No tests are skipped or failures ignored. The Actions log contains the
dependency/build output and a `PASS` line per interface. The
`ros2-jazzy-evidence` artifact contains colcon's `log/` directory and
`generated-interfaces.log` when those stages have run. On an earlier failure,
consult the failed step's Actions log; an artifact alone is not a passing result.

Fork pull requests use the ordinary `pull_request` event with read-only
repository permissions and no secrets. A maintainer may need to approve the
workflow run according to the repository's GitHub Actions settings. No
`pull_request_target` execution is used.

For manual reproduction in a fresh Ubuntu 24.04 / ROS 2 Jazzy environment,
run the three workflow `run` blocks in order from the repository root (the
dependency installation block requires root privileges). The workflow is the
canonical command source for this initial gate.

This is the first step of [Issue #6](https://github.com/openAMRobot/openamrobot-interfaces/issues/6),
not its complete verification suite. Lint/schema validation, compatibility and
version checks, fake publisher/consumer tests (including reverted-interface
failures), consumption from a separate clean workspace, and a reusable local/CI
verification command remain follow-up work. This gate does not claim those
checks pass and does not alter interface contracts.
