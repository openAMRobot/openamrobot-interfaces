uint8 STATE_UNKNOWN=0
uint8 STATE_IDLE=1
uint8 STATE_ACTIVE=2
uint8 STATE_RECOVERING=3
uint8 STATE_SUCCEEDED=4
uint8 STATE_ABORTED=5
uint8 STATE_CANCELED=6
uint8 state

uint16 reason                     # see NavigationStatus.msg
uint16 native_error_code          # raw Nav2 result code, 0 if none
builtin_interfaces/Time goal_stamp
float32 distance_remaining
