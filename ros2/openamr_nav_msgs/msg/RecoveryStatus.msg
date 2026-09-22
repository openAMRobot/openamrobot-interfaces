uint8 ACTION_NONE=0
uint8 ACTION_CLEAR_COSTMAP=1
uint8 ACTION_SPIN=2
uint8 ACTION_WAIT=3
uint8 ACTION_BACKUP=4
uint8 action

uint8 attempt                     # own counter, not Nav2's number_of_recoveries
uint8 attempt_limit
uint16 reason                     # see NavigationStatus.msg
