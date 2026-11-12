# Selects the workspace representation.
uint8 UNKNOWN=0
uint8 BOUNDING_BOX=1
uint8 REACH_RADIUS=2
uint8 type

# Minimum XYZ corner when type is BOUNDING_BOX.
geometry_msgs/Point min_corner

# Maximum XYZ corner when type is BOUNDING_BOX.
geometry_msgs/Point max_corner

# Reach radius when type is REACH_RADIUS, in metres.
float64 reach_radius
