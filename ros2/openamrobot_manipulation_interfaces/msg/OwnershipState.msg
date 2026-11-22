# Current ownership state. NORMAL is the safe default.
uint8 NORMAL=0
uint8 DECLARED_POLICY=1
uint8 DIRECT_CONTROL=2
uint8 state

# Client currently holding ownership. Empty when state is NORMAL.
string owner_client_id

# Time at which the current ownership state began.
builtin_interfaces/Time since_timestamp

# Expiration time of the current ownership lease.
builtin_interfaces/Time lease_expires_at
