# Health and freshness of one base-controller subsystem. PROVISIONAL (decision 1):
# kept only if a nested message is justified over flat fields in BaseStatus.
# Mirrors openamr_nav_msgs/SensorStatus.state so consumers read both the same way.

uint8 SUBSYSTEM_UNKNOWN=0
uint8 SUBSYSTEM_MOTOR_DRIVER=1
uint8 SUBSYSTEM_ENCODERS=2
uint8 SUBSYSTEM_IMU=3
uint8 SUBSYSTEM_BMS=4
uint8 SUBSYSTEM_RANGE_FRONT_LEFT=5       # MaxBotix MB7060
uint8 SUBSYSTEM_RANGE_FRONT_RIGHT=6
uint8 SUBSYSTEM_RANGE_REAR_LEFT=7
uint8 SUBSYSTEM_RANGE_REAR_RIGHT=8
uint8 SUBSYSTEM_CLIFF_FRONT=9            # TF-Luna
uint8 SUBSYSTEM_CLIFF_REAR=10
uint8 SUBSYSTEM_LIFT_NODE_LINK=11
uint8 subsystem

uint8 STATE_UNKNOWN=0                    # unset field should never read as healthy
uint8 STATE_ABSENT=1
uint8 STATE_STALE=2
uint8 STATE_DEGRADED=3
uint8 STATE_OK=4
uint8 state

builtin_interfaces/Duration data_age     # 0 when STATE_ABSENT or STATE_UNKNOWN
uint16 fault_code                        # BaseFault code, 0=NONE exactly when state is OK
