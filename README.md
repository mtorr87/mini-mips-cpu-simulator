# MiniMIPS CPU Simulator

A Python portfolio project that simulates a simplified MIPS-style CPU, including registers, memory, control flow, and a direct-mapped cache.

## Project overview

The simulator demonstrates the fetch-decode-execute cycle used by a CPU.

It can:

- Load assembly instructions from a text file
- Load initial memory values from a separate file
- Execute arithmetic and comparison instructions
- Read and write values through a memory bus
- Perform branches and jumps
- Simulate a direct-mapped cache
- Display execution traces and final machine state
- Detect invalid instructions, registers, addresses, and operands

## Supported instruction set

| Instruction | Operands | Behavior |
|---|---|---|
| `ADD` | `Rd, Rs, Rt` | `Rd = Rs + Rt` |
| `ADDI` | `Rt, Rs, immediate` | `Rt = Rs + immediate` |
| `SUB` | `Rd, Rs, Rt` | `Rd = Rs - Rt` |
| `SLT` | `Rd, Rs, Rt` | Set `Rd` to `1` when `Rs < Rt`, otherwise `0` |
| `BNE` | `Rs, Rt, offset` | Branch when the register values differ |
| `J` | `target` | Jump to `target * 4` |
| `JAL` | `target` | Store `PC + 4` in `R7`, then jump |
| `LW` | `Rt, offset(Rs)` | Load a value from memory |
| `SW` | `Rt, offset(Rs)` | Store a value in memory |
| `CACHE` | `code` | Disable, enable, or flush the cache |
| `HALT` | none | Stop execution |

### Cache commands

| Command | Meaning |
|---|---|
| `CACHE 0` | Disable the cache |
| `CACHE 1` | Enable the cache |
| `CACHE 2` | Flush all cache lines |

## Architecture

The project uses four main components:

### CPU

The `CPU` class contains:

- Eight registers, `R0` through `R7`
- A program counter named `pc`
- The fetch-decode-execute cycle
- Instruction execution methods
- Branch and jump control
- Cache access for load and store instructions

`R0` always contains `0`.

`R7` stores the return address written by `JAL`.

### Memory bus

The `MemoryBus` stores integer values using integer addresses.

Uninitialized addresses return `0`.

### Cache

The cache is:

- Direct-mapped
- Four lines by default
- Write-through
- Write-allocate
- Disabled when the simulator starts

The cache tracks hits, misses, writes, flushes, and its most recent operation.

### Parser

The parser reads:

- Assembly instructions from `.asm` files
- Memory initialization values from `.txt` files

Blank lines and comments beginning with `#` or `;` are ignored.

## Project structure

```text
mini-mips-cpu-simulator/
├── cache.py
├── cpu.py
├── main.py
├── memory_bus.py
├── parser.py
├── programs/
│   ├── program.asm
│   ├── memory.txt
│   ├── arithmetic_demo.asm
│   ├── memory_demo.asm
│   ├── control_flow_demo.asm
│   └── cache_demo.asm
└── tests/
    ├── test_cache.py
    ├── test_cpu.py
    ├── test_integration.py
    ├── test_memory.py
    └── test_parser.py
```

## Requirements

- Python 3.10 or newer
- No third-party packages are required

## Running the simulator

Run the default program:

```bash
python3 main.py
```

Run without the execution trace:

```bash
python3 main.py --no-trace
```

Run a different assembly program:

```bash
python3 main.py \
  --program programs/arithmetic_demo.asm
```

Use a different memory file:

```bash
python3 main.py \
  --program programs/memory_demo.asm \
  --memory programs/memory.txt
```

Set an instruction limit:

```bash
python3 main.py --max-steps 200
```

Display command-line help:

```bash
python3 main.py --help
```

## Assembly-file format

Example:

```asm
# Add two values

ADDI R1, R0, 10
ADDI R2, R0, 20
ADD R3, R1, R2
HALT
```

Each instruction occupies four bytes. The program counter begins at `0`.

## Memory-file format

Each line contains an address and an initial value:

```text
0 100
4 200
8 300
```

Hexadecimal values are also supported:

```text
0x0 0x64
0x4 0xC8
```

## Running the tests

Run the complete test suite:

```bash
python3 -m unittest discover -s tests -v
```

The tests cover:

- Register behavior
- Arithmetic instructions
- Comparison instructions
- Memory reads and writes
- Branches and jumps
- Cache hits, misses, flushes, and bypasses
- Input-file parsing
- End-to-end simulation

## Example cache trace

```text
FETCH   PC=4: LW R1, 0(R0)
DECODE  opcode=LW operands=['R1', '0(R0)']
EXECUTE R1 <- MEM[R0(0) + 0] = MEM[0] = 100 [CACHE MISS]

FETCH   PC=8: LW R2, 0(R0)
DECODE  opcode=LW operands=['R2', '0(R0)']
EXECUTE R2 <- MEM[R0(0) + 0] = MEM[0] = 100 [CACHE HIT]
```

## Computer architecture concepts demonstrated

This project demonstrates:

- CPU registers
- Program counters
- Instruction sets
- Fetch-decode-execute cycles
- Word-aligned instructions
- Immediate values
- Memory addressing
- Branches and jumps
- Return addresses
- Cache hits and misses
- Direct mapping
- Write-through caching
- Input validation
- Automated testing

## Future improvements

Possible extensions include:

- Labels in assembly programs
- Additional MIPS instructions
- Multi-word cache blocks
- Write-back caching
- Cache replacement strategies
- Binary instruction encoding
- Pipeline simulation
- Cycle counting
- A graphical interface

## Author

Created as a Codecademy CS104 Computer Architecture portfolio project.