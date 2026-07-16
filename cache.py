from dataclasses import dataclass

from memory_bus import MemoryBus


@dataclass
class CacheLine:
    """Represents one line in a direct-mapped cache."""

    valid: bool = False
    tag: int = 0
    address: int = 0
    value: int = 0


class Cache:
    """A small direct-mapped, write-through cache."""

    def __init__(
        self,
        memory_bus: MemoryBus,
        line_count: int = 4,
        block_size: int = 4,
    ) -> None:
        if line_count <= 0:
            raise ValueError("line_count must be greater than zero.")
        if block_size <= 0:
            raise ValueError("block_size must be greater than zero.")

        self.memory_bus = memory_bus
        self.line_count = line_count
        self.block_size = block_size
        self.enabled = False
        self.lines = [CacheLine() for _ in range(line_count)]

        self.hits = 0
        self.misses = 0
        self.writes = 0
        self.flushes = 0
        self.last_status = "IDLE"

    def enable(self) -> None:
        self.enabled = True
        self.last_status = "ENABLED"

    def disable(self) -> None:
        self.enabled = False
        self.last_status = "DISABLED"

    def flush(self) -> None:
        for line in self.lines:
            line.valid = False
            line.tag = 0
            line.address = 0
            line.value = 0

        self.flushes += 1
        self.last_status = "FLUSHED"

    def reset_stats(self) -> None:
        self.hits = 0
        self.misses = 0
        self.writes = 0
        self.flushes = 0
        self.last_status = "IDLE"

    def read(self, address: int) -> int:
        self._validate_address(address)

        if not self.enabled:
            self.last_status = "BYPASS"
            return self.memory_bus.read(address)

        index, tag = self._location(address)
        line = self.lines[index]

        if (
            line.valid
            and line.tag == tag
            and line.address == address
        ):
            self.hits += 1
            self.last_status = "HIT"
            return line.value

        value = self.memory_bus.read(address)
        line.valid = True
        line.tag = tag
        line.address = address
        line.value = value

        self.misses += 1
        self.last_status = "MISS"
        return value

    def write(
        self,
        address: int,
        value: int,
    ) -> None:
        """Use a write-through, write-allocate policy."""
        self._validate_address(address)

        if not isinstance(value, int):
            raise TypeError("Cache values must be integers.")

        self.memory_bus.write(address, value)
        self.writes += 1

        if not self.enabled:
            self.last_status = "BYPASS WRITE"
            return

        index, tag = self._location(address)
        line = self.lines[index]

        line.valid = True
        line.tag = tag
        line.address = address
        line.value = value
        self.last_status = "WRITE-THROUGH"

    def stats(self) -> dict[str, int | bool | str]:
        return {
            "enabled": self.enabled,
            "hits": self.hits,
            "misses": self.misses,
            "writes": self.writes,
            "flushes": self.flushes,
            "last_status": self.last_status,
        }

    def snapshot(self) -> list[dict[str, int | bool]]:
        return [
            {
                "index": index,
                "valid": line.valid,
                "tag": line.tag,
                "address": line.address,
                "value": line.value,
            }
            for index, line in enumerate(self.lines)
        ]

    def _location(
        self,
        address: int,
    ) -> tuple[int, int]:
        block_number = address // self.block_size
        index = block_number % self.line_count
        tag = block_number // self.line_count
        return index, tag

    @staticmethod
    def _validate_address(address: int) -> None:
        if not isinstance(address, int):
            raise TypeError("Cache addresses must be integers.")
        if address < 0:
            raise ValueError("Cache addresses cannot be negative.")

    def __str__(self) -> str:
        state = "ON" if self.enabled else "OFF"
        rows = [f"Cache: {state}"]

        for index, line in enumerate(self.lines):
            if line.valid:
                rows.append(
                    f"Line {index}: tag={line.tag}, "
                    f"address={line.address}, value={line.value}"
                )
            else:
                rows.append(f"Line {index}: empty")

        rows.append(
            f"Hits={self.hits}, Misses={self.misses}, "
            f"Writes={self.writes}, Flushes={self.flushes}"
        )
        return "\n".join(rows)