# MiniMIPS control-flow demonstration

ADDI R1, R0, 1
ADDI R2, R0, 2

# R1 and R2 differ, so skip the next instruction
BNE R1, R2, 1
ADDI R3, R0, 999

# Save PC + 4 in R7 and jump to instruction 6
JAL 6
ADDI R4, R0, 111

ADDI R5, R0, 55

# Jump to instruction 9
J 9
ADDI R6, R0, 999

HALT