std_msgs/Header header

uint8 STATE_UNKNOWN=0
uint8 STATE_NOT_PARKED=1
uint8 STATE_PARKING=2
uint8 STATE_PARKED=3
uint8 STATE_LEAVING=4
uint8 STATE_PARK_FAILED=5
uint8 state

string target_id
uint16 reason                     # see NavigationStatus.msg
