# MiniMIPS cache demonstration

# Turn the cache on
CACHE 1

# First read is a miss; second read is a hit
LW R1, 0(R0)
LW R2, 0(R0)

# Store through the cache and read the cached value
ADDI R3, R0, 123
SW R3, 16(R0)
LW R4, 16(R0)

# Flush the cache; the next read is a miss again
CACHE 2
LW R5, 0(R0)

# Turn the cache off; this read bypasses the cache
CACHE 0
LW R6, 4(R0)

HALT