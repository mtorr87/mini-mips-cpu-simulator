# Memory demonstration

LW R1, 0(R0)
LW R2, 4(R0)
ADD R3, R1, R2
SW R3, 16(R0)
LW R4, 16(R0)
HALT