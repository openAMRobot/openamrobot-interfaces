string id

uint8 KIND_UNKNOWN=0
uint8 KIND_LIDAR=1
uint8 KIND_DEPTH_CAMERA=2
uint8 KIND_TOF=3
uint8 KIND_ULTRASONIC=4
uint8 KIND_IMU=5
uint8 KIND_ODOMETRY=6
uint8 kind

string frame_id

uint8 STATE_UNKNOWN=0
uint8 STATE_ABSENT=1
uint8 STATE_STALE=2
uint8 STATE_DEGRADED=3
uint8 STATE_OK=4
uint8 state

uint16 reason                     # see NavigationStatus.msg
builtin_interfaces/Duration data_age
float32 rate_hz
bool required
