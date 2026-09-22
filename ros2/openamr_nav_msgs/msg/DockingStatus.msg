std_msgs/Header header

uint8 ACTIVITY_UNKNOWN=0
uint8 ACTIVITY_NONE=1
uint8 ACTIVITY_DOCKING=2
uint8 ACTIVITY_UNDOCKING=3
uint8 ACTIVITY_FAILED=4
uint8 activity                    # latched until next command

uint8 ENGAGEMENT_UNKNOWN=0
uint8 ENGAGEMENT_DOCKED=1
uint8 ENGAGEMENT_NOT_DOCKED=2
uint8 engagement                  # kept separate from activity on purpose

uint8 PHASE_UNKNOWN=0
uint8 PHASE_NONE=1
uint8 PHASE_STAGING=2
uint8 PHASE_SCAN=3
uint8 PHASE_NORMAL_ESTIMATE=4
uint8 PHASE_APPROACH=5
uint8 PHASE_FINAL=6
uint8 phase

uint16 failure_reason              # see NavigationStatus.msg, latched with ACTIVITY_FAILED
float32 lateral_error_m
float32 yaw_error_rad
uint8 visible_tag_count            # 0-3
builtin_interfaces/Duration elapsed
