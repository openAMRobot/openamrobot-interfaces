# OpenAMRobot Interfaces

Shared ROS 2 messages, services, actions, schemas, and interface contracts for the OpenAMRobot ecosystem.

## Repository Status

Current maturity level: Experimental

## Purpose

This repository defines interface contracts shared across the OpenAMRobot ecosystem, including:

- ROS 2 messages
- ROS 2 services
- ROS 2 actions
- communication schemas
- JSON/YAML contracts
- API conventions
- versioning rules
- interoperability definitions

This repository acts as the contract layer between:

- platform software
- firmware
- UI systems
- simulation
- docking
- navigation
- humanoid systems
- external integrations

## Shared ROS 2 Interface Packages

The `ros2/` directory contains shared ROS 2 interface packages used across the OpenAMRobot ecosystem.

Example:

```text
ros2/openamr_ui_msgs
```

These packages may contain:

- ROS 2 messages (`msg`)
- ROS 2 services (`srv`)
- ROS 2 actions (`action`)

## Why Shared Interfaces Are Centralized

Shared ROS 2 interface packages should not belong to individual application repositories.

Instead, they are centralized in:

```text
openamrobot-interfaces
```

to provide:

- a single source of truth
- version consistency
- interoperability
- reusable contracts
- clean repository boundaries
- reduced duplication
- simulation and hardware compatibility

## Usage Across Repositories

Other repositories should depend on shared interface packages instead of redefining them.

Examples:

```text
openamr-platform-sw
openamrobot-ui
openamrobot-comm
future humanoid repositories
future fleet-management systems
```

## Recommended Dependency Pattern

Repositories should include shared interfaces as dependencies in their ROS 2 workspace.

Example workspace structure:

```text
workspace/
├── src/
│   ├── openamr-platform-sw/
│   ├── openamrobot-ui/
│   └── openamrobot-interfaces/
```

## Interface Ownership

Interface definitions should remain:

- hardware-agnostic
- reusable
- transport-independent where possible
- stable and version-aware

Application-specific logic should remain outside this repository.

## Repository Structure

```text
openamrobot-interfaces/
├── ros2/
│   ├── msg/
│   ├── srv/
│   └── action/
│
├── schemas/
│   ├── json/
│   └── yaml/
│
├── docs/
├── examples/
├── tools/
└── tests/
```

## Design Principles

Interfaces should be:

- stable
- minimal
- versioned
- backwards-compatible where possible
- hardware-agnostic
- simulation-compatible
- transport-independent when possible

## Repository Boundaries

This repository contains interface definitions only.

ROS 2 implementations belong in:

```text
openamr-platform-sw
```

Firmware implementations belong in:

```text
openamr-platform-fw
```

Hardware files belong in:

```text
openamr-platform-hw
```

## Future Scope

Planned future interfaces include:

- robot state
- battery state
- docking state
- actuator control
- perception detections
- safety events
- diagnostics
- fleet management
- remote operation
- humanoid interfaces

## License

MIT License.