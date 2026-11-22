# One active motion constraint reported by the base controller. PROVISIONAL (decision 1).
# Status reports constraints; enforcement stays in the designated control logic.

uint8 TYPE_UNKNOWN=0
uint8 TYPE_SPEED_LIMIT=1                 # value in m/s
uint8 TYPE_TRAVEL_INHIBIT_FORWARD=2      # TODO(decision 7): policy when floor coverage is lost
uint8 TYPE_TRAVEL_INHIBIT_REVERSE=3      # TODO(decision 7)
uint8 TYPE_LIFT_HOLD=4                   # lift moving, base held stopped
uint8 type

float32 value                            # m/s for TYPE_SPEED_LIMIT, 0 otherwise
uint16 reason                            # BaseFault code, 0=NONE
