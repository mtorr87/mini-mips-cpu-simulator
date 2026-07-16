class MemoryBus:
    """
    Simulates the CPU's main memory.

    Memory is stored as address-value pairs:
        address -> integer value
    """

    def __init__(self) -> None:
        self.memory: dict[int, int] = {}

    def read(self, address: int) -> int:
        """
        Read a value from memory.

        Uninitialized addresses contain 0.
        """
        self._validate_address(address)
        return self.memory.get(address, 0)

    def write(self, address: int, value: int) -> None:
        """Write an integer value to a memory address."""
        self._validate_address(address)

        if not isinstance(value, int):
            raise TypeError("Memory values must be integers.")

        self.memory[address] = value

    def load_initial_values(self, values: dict[int, int]) -> None:
        """Load multiple address-value pairs into memory."""
        for address, value in values.items():
            self.write(address, value)

    def dump(self) -> dict[int, int]:
        """Return a copy of the current memory contents."""
        return self.memory.copy()

    @staticmethod
    def _validate_address(address: int) -> None:
        """Verify that an address is a non-negative integer."""
        if not isinstance(address, int):
            raise TypeError("Memory addresses must be integers.")

        if address < 0:
            raise ValueError("Memory addresses cannot be negative.")

    def __str__(self) -> str:
        """Return a readable representation of memory."""
        if not self.memory:
            return "Memory is empty."

        entries = []

        for address, value in sorted(self.memory.items()):
            entries.append(f"MEM[{address}] = {value}")

        return "\n".join(entries)