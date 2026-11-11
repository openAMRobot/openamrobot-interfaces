# One active or latched base-controller fault. PROPOSED, not approved (I8 proposal, aligned to E-01 rev 4).
# Functional status only. Not a safety function and not evidence that the hardwired
# safety path operated (E-01: no bus carries a safety function).
# Operator text and clear/recovery conditions live in the fault registry (interfaces #30,
# decision 5), not in the message. Consumers resolve `code` against the registry.

# code: group 18001, owned by openamr-platform-fw#10. 0=NONE, append-only, never renumbered or reused.
# Existing group ownership is frozen; individual proposed additions and lifecycle remain
# subject to central-registry and reviewer approval. Package merge alone does not approve them.
uint16 NONE=0

# command and host link
uint16 BASE_COMMAND_TIMEOUT=18001          # non-latching (decision 3): clears on the next fresh command
uint16 BASE_HOST_LINK_LOST=18002

# motor driver
uint16 DRIVER_COMM_LOST=18003
uint16 DRIVER_FAULT=18004
uint16 DRIVER_FEEDBACK_INVALID=18005

# encoders / odometry and IMU
uint16 ENCODER_ODOMETRY_FAULT=18006
uint16 IMU_FAULT=18007

# BMS
uint16 BMS_COMM_LOST=18008
uint16 BMS_FAULT=18009

# safety inputs (observations only)
uint16 SAFETY_INPUT_UNKNOWN=18010          # missing, stale or unreadable
uint16 SAFETY_INPUT_CONTRADICTORY=18011
uint16 PNOZ_DIAGNOSTIC_NOT_ENABLED=18012  # fresh Y32/SAFETY_OK diagnostic is low; not proof the physical chain is open

# configuration, transport, list
uint16 CONTRACT_MISMATCH=18013
uint16 TRANSPORT_FAILURE=18014
uint16 FAULT_LIST_OVERFLOW=18015

# Reset causes are reported through BaseStatus reset_cause/reset_flags_raw, not BaseFault.
# The v3 draft proposed reset fault constants at 18016/18017. Rev4 treats reset causes as
# status/reset-cause reporting; confirm any existing registry allocation with platform-fw #10
# before exposing either identifier as a BaseFault constant.

# E-01 rev 4 reason codes (section 4). PROVISIONAL numbers: final IDs are assigned with the
# central registry. Existing codes are reused where the meaning is the same:
#   HW_SAFETY_NOT_ENABLED -> PNOZ_DIAGNOSTIC_NOT_ENABLED (18012)    COMMS_LOST -> BASE_HOST_LINK_LOST (18002)
#   BMS_FAULT -> BMS_FAULT (18009)                         DRIVE_FAULT -> DRIVER_FAULT (18004)
#   INPUT_INVALID: MISSING or STALE -> SAFETY_INPUT_UNKNOWN (18010),
#                  IMPLAUSIBLE encoder -> ENCODER_ODOMETRY_FAULT (18006), RESET_HIGH -> 18019
uint16 ESTOP_DIAGNOSTIC_ACTIVE=18018       # fresh diagnostic positively reports E-stop active
uint16 RESET_INPUT_HIGH=18019              # INPUT_INVALID sub-cause RESET_HIGH: RESET held high 2 s
uint16 CHARGER_FAULT=18021                 # WCM_FAULT latched while charging
uint16 CHARGE_INTERLOCK_FAULT=18022        # SAFETY_OK not low within 500 ms of CHARGE_REQUEST, or high again while charging
uint16 DRIVE_CONFIG_MISMATCH=18023         # link-loss time or heartbeat interval read back differs from the D-24 values
uint16 ESTOP_DIAGNOSTIC_UNKNOWN=18028      # diagnostic input missing, stale or unreadable; distinct from active E-stop

uint16 code

uint8 SEVERITY_UNKNOWN=0                   # unset field must never read as benign
uint8 SEVERITY_WARNING=1                   # controller state DEGRADED
uint8 SEVERITY_FAULT=2                     # controller state FAULTED
uint8 severity

uint8 SOURCE_UNKNOWN=0
uint8 SOURCE_COMMAND=1
uint8 SOURCE_HOST_LINK=2
uint8 SOURCE_MOTOR_DRIVER=3
uint8 SOURCE_ENCODER=4
uint8 SOURCE_IMU=5
uint8 SOURCE_BMS=6
uint8 SOURCE_SAFETY_INPUT=7
uint8 SOURCE_RANGE_SENSOR=8
uint8 SOURCE_LIFT=9
uint8 SOURCE_CONFIG=10
uint8 SOURCE_RESET=11
uint8 source

# TODO(decision 4): retention, list bound and overflow are not decided. The model below follows
# E-01 rev 4 and is still provisional: do not build consumers on it yet.
#
# Five things are kept apart (E-01 section 5.3 and 5.6):
#   condition_active   the fault condition is present now
#   lifecycle          ACTIVE, LATCHED, ACKNOWLEDGED or CLEARED latch/ack state
#   acknowledgement    ACKNOWLEDGED means accepted; it is not a sensor observation
#   condition cleared  condition_active == OBS_NO (independent of lifecycle)
#   recovery_required  a physical RESET or other recovery is still needed before RUN
# Acknowledgement is independent of condition_active: ACKNOWLEDGED may coexist with OBS_YES.
# It never clears the condition, verifies KCHG/contactors, or grants motion authority. A
# charge-interlock fault may be acknowledged while SAFETY_OK remains high.
uint8 LIFECYCLE_UNKNOWN=0
uint8 LIFECYCLE_ACTIVE=1          # non-latching: present now, clears by itself (e.g. command timeout)
uint8 LIFECYCLE_LATCHED=2         # latch held; the condition may or may not still be present
uint8 LIFECYCLE_ACKNOWLEDGED=3    # acknowledgement accepted; condition may still be active and recovery may still be required
uint8 LIFECYCLE_CLEARED=4         # no latch and no condition
uint8 lifecycle

uint8 OBS_UNKNOWN=0
uint8 OBS_NO=1
uint8 OBS_YES=2
uint8 condition_active            # OBS_*. ACKNOWLEDGED with OBS_YES is also valid
uint8 recovery_required           # OBS_*

bool inhibits_motion
