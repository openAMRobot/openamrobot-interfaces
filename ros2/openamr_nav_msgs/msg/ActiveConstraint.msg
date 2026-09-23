uint8 TYPE_UNKNOWN=0
uint8 TYPE_SPEED_LIMIT=1
uint8 TYPE_REVERSE_LIMIT=2
uint8 TYPE_COLLISION_APPROACH=3
uint8 type

float32 value                     # m/s for SPEED_LIMIT/REVERSE_LIMIT, s for COLLISION_APPROACH
uint16 reason                     # see NavigationStatus.msg
