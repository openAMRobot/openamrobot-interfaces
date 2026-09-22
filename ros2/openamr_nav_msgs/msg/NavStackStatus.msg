uint8 STATE_UNKNOWN=0
uint8 STATE_NOT_STARTED=1
uint8 STATE_STARTING=2
uint8 STATE_ACTIVE=3
uint8 STATE_RESETTING=4
uint8 STATE_FAILED=5
uint8 state

uint16 reason                     # see NavigationStatus.msg
string[] inactive_nodes           # debug info, not normative
