# Auxiliary-device block on /base/aux_status. PROPOSED, not approved (I8 proposal rev 4).
# Includes lift measured and declared position as separate values, validity, homing, motion,
# stop sensors and faults; head light; Getac power-good; moving-adapter-plate E-stop.
# Reports observations only. It does not enforce the lift interlock or prove a safety function.
# Lift interlock enforcement owner and inter-controller handshake remain undecided.
# 0 is UNKNOWN. Freshness comes from consumer-local receipt time, never header.stamp.
# Decision 13: position sources, homing semantics, raw/mapped fault rules and disagreement
# threshold remain open. Do not interpret proposed fields/enums as an approved device map.

std_msgs/Header header            # stamp = base controller monotonic time base, diagnostic only

uint16 CONTRACT_VERSION=1
uint16 contract_version

uint32 boot_id                    # same value as in the BaseStatus of this boot
uint32 sequence
uint64 monotonic_us

uint8 OBS_UNKNOWN=0
uint8 OBS_NO=1
uint8 OBS_YES=2

# --- lift node link ---
uint8 LIFT_LINK_UNKNOWN=0
uint8 LIFT_LINK_OK=1
uint8 LIFT_LINK_LOST=2
uint8 lift_link

# --- lift ---
# The two values must never be substituted for one another.
float32 lift_measured_position_m  # independent physical measurement; 0 to 0.350 m
uint8 lift_measured_position_valid # OBS_YES only when the independent measurement is trustworthy
float32 lift_declared_position_m  # actuator/controller-declared position; not a measurement
uint8 lift_declared_position_valid # OBS_YES only when the declared value is trustworthy
uint8 LIFT_HOMING_UNKNOWN=0
uint8 lift_homing_state            # other values/semantics pending Decision 13
uint8 LIFT_MOTION_UNKNOWN=0
uint8 LIFT_MOTION_STOPPED=1
uint8 LIFT_MOTION_UP=2
uint8 LIFT_MOTION_DOWN=3
uint8 lift_motion
float32 lift_motor_current_a

uint8 STOP_UNKNOWN=0
uint8 STOP_NONE=1
uint8 STOP_L1000=2
uint8 STOP_L1175=3
uint8 STOP_L1350=4
uint8 lift_target_stop
uint8 lift_at_stop

uint8 lift_stop_sensor_l1000      # OBS_YES = sensor active
uint8 lift_stop_sensor_l1175
uint8 lift_stop_sensor_l1350
uint32 lift_raw_device_fault_code # raw CTL-017/device code; representation/mapping pending Decision 13
uint16 lift_fault_code             # mapped central registry code, 0=NONE; mapping pending Decision 13
# A late or stale lift target halts the lift at its current position (interfaces #31, Q10).

# --- head light ---
uint8 HEAD_LIGHT_UNKNOWN=0
uint8 HEAD_LIGHT_OFF=1
uint8 HEAD_LIGHT_ON=2
uint8 head_light_state
uint8 head_light_dim_percent      # proposed 0 to 100 percent; confirm encoding with device owner
uint16 head_light_fault_code      # BaseFault code, 0=NONE

# --- Getac ---
uint8 getac_power_good

# --- second E-stop (moving adapter plate, in the same hardwired chain) ---
uint8 SECOND_ESTOP_UNKNOWN=0      # always UNKNOWN while lift_link != LIFT_LINK_OK
uint8 SECOND_ESTOP_RELEASED=1
uint8 SECOND_ESTOP_PRESSED=2
uint8 second_estop

# --- reserved generic inputs for later arm and lift-body ToF and ultrasonic sensors ---
# No hardware yet; empty today. Adding entries later needs no field change.
BaseSubsystemStatus[<=8] reserved_inputs
