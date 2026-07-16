from pathlib import Path

from memory_bus import MemoryBus
from parser import (
    parse_instruction_file,
    parse_memory_file,
)


PROJECT_DIRECTORY = Path(__file__).parent
MEMORY_FILE = (
    PROJECT_DIRECTORY / "programs" / "memory.txt"
)
PROGRAM_FILE = (
    PROJECT_DIRECTORY / "programs" / "program.asm"
)


def main() -> None:
    print("Loading initial memory values...")

    initial_values = parse_memory_file(MEMORY_FILE)

    memory = MemoryBus()
    memory.load_initial_values(initial_values)

    for address, value in sorted(initial_values.items()):
        print(f"Loaded MEM[{address}] = {value}")

    print("\nLoading CPU instructions...")

    instructions = parse_instruction_file(PROGRAM_FILE)

    for index, instruction in enumerate(instructions):
        address = index * 4
        print(
            f"PC={address:>3}: "
            f"{instruction.opcode} "
            f"{', '.join(instruction.operands)}"
        )

    print(
        f"\nLoaded {len(instructions)} instructions."
    )

    print("\nInitial Memory Bus:")
    print(memory)


if __name__ == "__main__":
    main()