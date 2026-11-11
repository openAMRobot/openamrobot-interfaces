# I8 base controller status on /base/status. PROPOSED, not approved (I8 proposal, aligned to
# E-01 safety state machine rev 4, interfaces #30). Functional observations only: not a
# safety function, and not proof that the hardwired safety path (two E-stops, PNOZ s3, K1/K2,
# brake release) achieved a safe state (E-01: no bus carries a safety function). This message
# reports controller state. It is not a command or session protocol; commands and session
# rules live in the I8 firmware/host contract.
#
# Rules for every field below:
# - 0 is UNKNOWN. An unset, stale or unavailable value must never read as healthy, safe or
#   as an observed E-stop.
# - Freshness comes from the consumer's local receipt time, never from header.stamp.

# header.stamp is the ROS time stamp when available; diagnostic only. Use monotonic_us for
# controller-local elapsed-time calculations. Freshness is based on local receipt time.
std_msgs/Header header

uint16 CONTRACT_VERSION=1         # frozen I8 contract version starts at 1; remaining field semantics are proposed under decision 2
uint16 contract_version           # producer sets this to CONTRACT_VERSION

# --- identity, restart and ordering ---
string controller_id              # e.g. "teensy_gate_a", "stm32h723_gate_b"; "" if unknown
string firmware_version           # "" if unknown
uint32 boot_id                    # changes on every controller boot; uint32 is part of the frozen I8 identity contract
uint32 sequence                   # +1 per published message, wraps; a gap is a discontinuity
uint64 monotonic_us               # 64-bit monotonic microsecond time base

uint8 POWERED_DEBUG_UNKNOWN=0     # firmware cannot identify the running build
uint8 POWERED_DEBUG_DISABLED=1
uint8 POWERED_DEBUG_ENABLED=2     # commissioning build (decision 10: off by default)
uint8 powered_debug

# --- controller health summary (generic, kept) ---
# Derived from the severity of the active faults. It does not replace the E-01 operating
# state below: LOCKED, INHIBITED and CHARGING are not "faulted" and not "ready".
uint8 STATE_UNKNOWN=0
uint8 STATE_INITIALIZING=1
uint8 STATE_READY=2
uint8 STATE_DEGRADED=3
uint8 STATE_FAULTED=4
uint8 state

# --- E-01 rev 4 operating state ---
# Boot always lands in LOCKED (E-01 T1); there is no separate BOOT state. 0 means the
# controller has not yet determined its state. INHIBITED (software UI Stop) is never reported
# as SAFETY_STOPPED: that term is reserved for the hardwired chain.
uint8 OPERATING_STATE_UNKNOWN=0
uint8 OPERATING_STATE_LOCKED=1          # boot state and state for faults/conditions that E-01 maps to LOCKED
uint8 OPERATING_STATE_RUN=2             # all run conditions valid, motion allowed
uint8 OPERATING_STATE_INHIBITED=3       # UI Stop asserted from RUN, readiness latch kept
uint8 OPERATING_STATE_CHARGING=4        # charge command accepted, interlock active
uint8 OPERATING_STATE_CHARGER_FAULT=5   # charger or charge-interlock fault latched
uint8 operating_state

# --- E-01 rev 4 latches (three separate things, never merged) ---
# readiness is the readiness latch (reset_seen): set only by a qualified short physical RESET
# press, cleared by the events in E-01 section 2.2. It is NOT the RESET input level
# (reset_pressed) and does not mean the robot may move: RUN also needs ui_stop and host stop
# clear and every other run condition.
uint8 READINESS_UNKNOWN=0
uint8 READINESS_NOT_READY=1             # reset_seen clear
uint8 READINESS_READY=2                 # reset_seen set. Readiness is not hardware safety
uint8 readiness

uint8 ui_stop_active                    # OBS_*. UI Stop software inhibit; UI Resume clears this latch only, subject to E-01 state rules
uint8 host_stop_active                  # OBS_*. Jetson Stop. Asserted at boot and on session loss; independent of host_link

# Motion commands are accepted only in RUN, only from the current session.
uint8 COMMAND_ACCEPTANCE_UNKNOWN=0
uint8 COMMAND_ACCEPTANCE_REJECTING=1
uint8 COMMAND_ACCEPTANCE_ACCEPTING=2
uint8 command_acceptance

uint8 RECOVERY_UNKNOWN=0
uint8 RECOVERY_NOT_REQUIRED=1
uint8 RECOVERY_REQUIRED=2               # clearing the cause or a reset alone never authorizes motion
uint8 recovery

# --- E-01 rev 4 lock episode and reasons ---
# A lock episode begins on a transition into LOCKED or CHARGER_FAULT and ends on entering RUN.
# first_reason is the first fault reason (BaseFault code, 0=NONE). reason_mask contains
# only currently active fault/inhibit conditions, never normal events, reset causes or UI Stop
# itself (UI Stop is reported by ui_stop_active).
uint32 REASON_PNOZ_DIAGNOSTIC_NOT_ENABLED=1 # fresh Y32 low outside expected CHARGING condition
uint32 REASON_ESTOP_DIAG_ACTIVE=2
uint32 REASON_COMMS_LOST=4                  # Jetson session lost
uint32 REASON_BMS_FAULT=8
uint32 REASON_INPUT_INVALID=16
uint32 REASON_CHARGER_FAULT=32
uint32 REASON_CHARGE_INTERLOCK=64
uint32 REASON_DRIVE_FAULT=128
uint32 REASON_DRIVE_COMMS=256
uint32 REASON_DRIVE_CONFIG=512
uint32 REASON_RESET_INPUT_HIGH=1024
uint32 REASON_ESTOP_DIAG_UNKNOWN=2048
uint16 first_reason                         # BaseFault code, 0=NONE
uint32 reason_mask

# --- E-01 rev 4 session epoch ---
# Epoch = (boot_id, session_epoch_counter). boot_id changes on every boot and the counter
# starts at 0 for that boot; it increments exactly once for each detected Jetson session loss
# (T5), not for heartbeats or ordinary commands. A new challenge-response establishes the
# current epoch; delayed traffic from an older epoch is rejected. Wire details live in I8.
uint32 session_epoch_counter
bool reboot_request_pending          # T8 supervisory event/state; not a BaseFault code

# --- command and host communication ---
uint8 HOST_LINK_UNKNOWN=0
uint8 HOST_LINK_OK=1
uint8 HOST_LINK_LOST=2
uint8 host_link

# The velocity actually sent to the motor driver after limits, ramp and timeout
# (platform-sw #116). Never a held or replayed command: on timeout the base stops.
uint8 APPLIED_COMMAND_UNKNOWN=0
uint8 APPLIED_COMMAND_OK=1
uint8 APPLIED_COMMAND_TIMEOUT=2   # non-latching (decision 3)
uint8 APPLIED_COMMAND_INHIBITED=3 # by a safety stop or a constraint
uint8 applied_command_state
float32 applied_linear_x_mps
float32 applied_angular_z_radps
builtin_interfaces/Duration applied_command_age

# --- safety-chain observations (diagnostics only; E-01 rev 4, hardware baseline rev1.8) ---
uint8 OBS_UNKNOWN=0               # not determined, stale or unreadable: never read as NO
uint8 OBS_NO=1
uint8 OBS_YES=2

# safety_ok is the PNOZ s3 Y32 output read through the ISO1212 isolated input. It is
# diagnostic feedback only: not a safety-rated input, not proof of K1/K2/KCHG contact state,
# and not proof the hardwired chain reached its intended safe state. OBS_NO means the
# diagnostic reports the PNOZ output not enabled. The firmware does not monitor K1 or K2
# (E-01 R6). SAFETY_OK low is expected while CHARGING.
uint8 safety_ok
uint8 base_estop_pressed          # base E-stop spare NO contact (diagnostic)
uint8 reset_pressed               # RESET NC contact level. An open wire also reads pressed. Not the readiness latch
uint8 reset_required              # a physical RESET is required before readiness can be set
uint8 charge_inhibit_active       # follows the controller's own CHARGE_REQUEST/KCHG output. Not evidence charging power is removed
uint8 charger_fault               # TZBOT charger fault line (WCM_FAULT)
uint16 safety_diagnosis           # BaseFault code for a current diagnostic fault, 0=NONE

# --- faults ---
# TODO(decision 4): bound, ordering and overflow behaviour are provisional.
BaseFault[<=16] faults
bool fault_list_overflow

# --- subsystem health and motion constraints (decision 1: provisional nested messages) ---
BaseSubsystemStatus[<=16] subsystems
BaseMotionConstraint[<=8] constraints

# --- reset cause ---
# TODO(decision 6): exhaustive mapping after the STM32H723ZG reset-flag check.
uint8 RESET_CAUSE_UNKNOWN=0
uint8 RESET_CAUSE_POWER_ON=1
uint8 RESET_CAUSE_BROWNOUT=2
uint8 RESET_CAUSE_WATCHDOG=3
uint8 RESET_CAUSE_SOFTWARE=4
uint8 RESET_CAUSE_PIN=5
uint8 reset_cause
uint32 reset_flags_raw            # raw MCU reset flags captured before clearing; 0 if unavailable
