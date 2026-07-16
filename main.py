from pathlib import Path

from memory_bus import MemoryBus
from parser import parse_memory_file


PROJECT_DIRECTORY = Path(__file__).parent
MEMORY_FILE = PROJECT_DIRECTORY / "programs" / "memory.txt"


def main() -> None:
    print("Loading initial memory values...")

    initial_values = parse_memory_file(MEMORY_FILE)

    memory = MemoryBus()
    memory.load_initial_values(initial_values)

    for address, value in sorted(initial_values.items()):
        print(f"Loaded MEM[{address}] = {value}")

    print("\nMemory Bus:")
    print(memory)


if __name__ == "__main__":
    main()