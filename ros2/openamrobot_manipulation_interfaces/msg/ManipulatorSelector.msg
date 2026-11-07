# Selects a single manipulator or a coordinated manipulator group.
uint8 UNKNOWN=0
uint8 MANIPULATOR=1
uint8 GROUP=2
uint8 selector_type

# UUID identifying the physical manipulator.
# Meaningful only when selector_type is MANIPULATOR.
string manipulator_id

# Standard group identifiers: LEFT, RIGHT, BIMANUAL.
# Meaningful only when selector_type is GROUP.
string group_id
