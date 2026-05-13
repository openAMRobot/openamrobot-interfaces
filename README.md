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