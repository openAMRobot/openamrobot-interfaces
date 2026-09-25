# ROS 2 Jazzy verification

From a checkout on Ubuntu 24.04 with ROS 2 Jazzy installed, run:

```bash
bash tools/verify.sh
```

The command works from any directory, returns nonzero on any failed stage,
and is the same command used by the `quality/build` job in the `ROS 2 Jazzy`
workflow. It requires no robot and never actuates hardware. Message tests publish
only on a unique verification topic with discovery restricted to localhost.

## Prerequisites

Install ROS 2 Jazzy using the [official Ubuntu installation instructions](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html).
Install verification tools and manifest dependencies once, from the checkout:

```bash
sudo apt-get update
sudo apt-get install -y python3-colcon-common-extensions python3-rosdep python3-jsonschema python3-yaml
# Only on machines where rosdep has not been initialized:
sudo rosdep init
rosdep update --rosdistro jazzy
rosdep install --from-paths ros2 --ignore-src --rosdistro jazzy -y
```

Verification runs `rosdep check` and fails if dependencies are missing; it does
not silently install software or require sudo. CI provisions dependencies first
in the official `ros:jazzy-ros-base` container. These prerequisites are separate
from the checks, which always run through `tools/verify.sh`.

## What is checked

1. Check dependencies in a fresh shell that does not inherit the developer's
   ROS overlays, Python paths, CMake prefixes, or shell startup files.
2. Copy all interface packages under `ros2/` into a new workspace and build with
   colcon, using only `/opt/ros/jazzy` as the underlay. No cached build or symlink
   install is used.
3. Copy the installed packages to a new prefix and rename the original producer
   workspace. Its recorded source, build, and install paths no longer exist.
4. Source ROS Jazzy and the relocated install's `local_setup.bash`. Check every
   source `.msg`, `.srv`, and `.action` definition through `ros2 interface show`,
   Python class loading, and generated native Python type-support loading.
   Discovering no interfaces fails.
5. Build the standalone `tests/install_consumer` package in another new
   workspace and clean shell. It finds both `openamr_nav_msgs` and
   `openamr_ui_msgs` through their installed CMake exports, compiles representative
   navigation/message/action headers, links generated C++ type support, and runs
   the resulting executable to check runtime loading.
6. Start a fake publisher in a separate process, publish one navigation status,
   and then start a late consumer. Require reliable, transient-local, depth-1
   delivery and check the header, contract version, profile/threshold IDs,
   health/readiness, reason arrays, and nested sensor values against explicit
   expected values. Startup and receipt each have a 10-second deadline; the
   whole test has an outer 45-second timeout and cleans up its publisher.
7. Remove `NavigationStatus.thresholds_id` from a temporary copy of the source
   and build that package in a separate workspace. Run the unchanged consumer
   against only that install and ROS Jazzy. Require exit 42 and the exact
   missing-field diagnostic. Success, timeouts, import errors, and failed builds
   are failures of this verification stage, not acceptable negative results.

The message test uses `rclpy` and Fast DDS from the Jazzy ROS base environment.
It checks that package discovery resolves the intended install. The negative
fixture simulates reverting a required field, not a historical Git commit or a
general compatibility/version policy. It does not modify tracked message files.
The consumer rejects the reverted definition in its contract preflight before
starting message exchange. The positive run must complete real DDS exchange;
neither missing dependencies nor test timeouts are skipped.
Fixture values and consumer checks use the generated message constants. This
tests message exchange, not independent constant-value/version enforcement.
The preflight rejection does not establish old-producer/new-consumer compatibility.

The consumer has no source/build include paths to the interface packages. The
retired producer files are retained for diagnosis; this is environment and path
isolation, not an OS filesystem security boundary. This verifies a freshly built,
relocated install, not a released binary artifact or a pinned release manifest.
It does not prove general ROS install relocatability.

## Evidence and CI

Each invocation creates a new ignored `.verification/run.*` directory containing:

- `verification.log`: full command output, including the consumer execution;
- `result.txt`: overall PASS or the failing stage and exit code;
- `generated-interfaces.log`: generated-interface output, when reached;
- `navigation-exchange.log`: positive publisher/consumer result;
- `reverted-consumer.log`: expected missing-field failure (exit 42);
- `reverted-interface.patch`: exact temporary field-removal change;
- `producer-retired/log/` (or `producer/log/` on an earlier failure): colcon build logs;
- `consumer/log/`: downstream build logs, when reached.
- `reverted/log/`: build logs for the temporary reverted interface.

CI uploads these files as `ros2-jazzy-evidence`, including available partial
evidence on failure. The build and install trees remain local and are not uploaded.
An artifact alone does not mean verification passed: require a successful
`quality/build` job and a PASS in `result.txt`. Remove old `.verification/run.*`
directories manually when their diagnostic workspaces are no longer needed.

The workflow runs on pull requests and pushes to `main`. Fork pull requests use
the ordinary `pull_request` event with read-only permissions and no secrets;
maintainer approval may be required by GitHub's Actions policy.

## Troubleshooting

- **Prerequisites fail:** ensure `/opt/ros/jazzy/setup.bash` exists, initialize and
  update rosdep, and install the dependencies listed by `rosdep check`.
- **A developer overlay used to make the build pass:** verification deliberately
  ignores it. Declare and install the missing dependency instead.
- **Generated interfaces or consumer fail:** inspect the failing stage in
  `verification.log` and the corresponding colcon logs. Check exported runtime
  dependencies and installed headers/libraries; do not add producer source or
  build paths to the consumer.

## Remaining Issue #6 scope

The shared command runs [interface lint and schema validation](schema-validation.md)
before building, including rejection tests and explicit JSON/YAML coverage.

This extends the first build gate in [Issue #6](https://github.com/openAMRobot/openamrobot-interfaces/issues/6).
Compatibility/version validation remains a separate follow-up in PR #12.
This command does not report those checks as passing or claim release readiness.
