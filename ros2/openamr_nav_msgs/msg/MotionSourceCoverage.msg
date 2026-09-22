uint8 SOURCE_UNKNOWN=0
uint8 SOURCE_NAV_CONTROLLER=1
uint8 SOURCE_RECOVERY=2
uint8 SOURCE_DOCKING=3
uint8 SOURCE_UNDOCK_REVERSE=4
uint8 SOURCE_TELEOP=5
uint8 SOURCE_PARKING=6
uint8 source

uint8 COVERAGE_UNKNOWN=0
uint8 COVERAGE_UNPROTECTED=1
uint8 COVERAGE_PARTIAL=2
uint8 COVERAGE_PROTECTED=3
uint8 coverage                    # collision-monitor coverage only, not overall protection

uint16 reason                     # see NavigationStatus.msg
