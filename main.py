from pathlib import Path

from cpu import CPU
from memory_bus import MemoryBus
from parser import (
    parse_instruction_file,
    parse_memory_file,
)


PROJECT_DIRECTORY = Path(__file__).parent

MEMORY_FILE = (
    PROJECT_DIRECTORY
    / "programs"
    / "memory.txt"
)

PROGRAM_FILE = (
    PROJECT_DIRECTORY
    / "programs"
    / "program.asm"
)


def main() -> None:
    print("Loading initial memory values...")

    initial_values = parse_memory_file(
        MEMORY_FILE
    )

    memory = MemoryBus()
    memory.load_initial_values(initial_values)

    for address, value in sorted(
        initial_values.items()
    ):
        print(
            f"Loaded MEM[{address}] = {value}"
        )

    print("\nLoading CPU instructions...")

    instructions = parse_instruction_file(
        PROGRAM_FILE
    )

    print(
        f"Loaded {len(instructions)} instructions."
    )

    cpu = CPU(
        memory_bus=memory,
        trace=True,
    )

    cpu.load_program(instructions)

    print("\nStarting CPU...\n")

    cpu.run()

    print("\nFinal Registers:")

    for register, value in (
        cpu.dump_registers().items()
    ):
        print(f"{register} = {value}")

    print(f"\nFinal PC = {cpu.pc}")
    print(f"CPU halted = {cpu.halted}")


if __name__ == "__main__":
    main()