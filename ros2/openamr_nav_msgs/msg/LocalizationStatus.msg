uint8 STATE_UNKNOWN=0
uint8 STATE_LOST=1
uint8 STATE_DEGRADED=2
uint8 STATE_OK=3
uint8 state

uint8 HEALTH_UNKNOWN=0
uint8 HEALTH_OK=1
uint8 HEALTH_DEGRADED=2
uint8 HEALTH_FAULT=3
uint8 health

uint16 reason                     # see NavigationStatus.msg
builtin_interfaces/Duration pose_age
float32 covariance_xy             # worse of AMCL's x/y variance, m^2
float32 covariance_yaw            # rad^2
bool tf_available
bool correction_paused
