from memory_bus import MemoryBus


def main() -> None:
    memory = MemoryBus()

    print("Loading initial memory values...")

    memory.load_initial_values(
        {
            0: 100,
            4: 200,
            8: 300,
        }
    )

    print(memory)

    print("\nWriting a new value...")
    memory.write(4, 999)

    print(memory)


if __name__ == "__main__":
    main()