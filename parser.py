from pathlib import Path


def parse_memory_file(file_path: str | Path) -> dict[int, int]:
    """
    Read initial memory values from a text file.

    Expected format:
        address value

    Blank lines and comments beginning with # are ignored.
    """

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"Memory file not found: {path}")

    memory_values: dict[int, int] = {}

    with path.open("r", encoding="utf-8") as file:
        for line_number, raw_line in enumerate(file, start=1):
            # Remove comments and surrounding whitespace.
            line = raw_line.split("#", maxsplit=1)[0].strip()

            if not line:
                continue

            parts = line.split()

            if len(parts) != 2:
                raise ValueError(
                    f"Invalid memory entry on line {line_number}: "
                    f"expected 'address value'."
                )

            try:
                # Base 0 supports ordinary numbers and hexadecimal values.
                address = int(parts[0], 0)
                value = int(parts[1], 0)
            except ValueError as error:
                raise ValueError(
                    f"Invalid integer on line {line_number}: {raw_line.strip()}"
                ) from error

            if address < 0:
                raise ValueError(
                    f"Memory address cannot be negative on line {line_number}."
                )

            if address in memory_values:
                raise ValueError(
                    f"Duplicate memory address {address} on line {line_number}."
                )

            memory_values[address] = value

    return memory_values