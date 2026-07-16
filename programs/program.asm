# MiniMIPS arithmetic and memory demonstration

ADDI R1, R0, 10
ADDI R2, R0, 20

ADD R3, R1, R2
SUB R4, R3, R1

SW R3, 16(R0)
LW R5, 16(R0)

SLT R6, R1, R2
SLT R7, R2, R1

HALT