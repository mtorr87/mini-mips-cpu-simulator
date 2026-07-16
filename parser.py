from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Instruction:
    """Represents one parsed CPU instruction."""

    opcode: str
    operands: tuple[str, ...]
    source: str
    line_number: int


OPERAND_COUNTS = {
    "ADD": 3,
    "ADDI": 3,
    "SUB": 3,
    "SLT": 3,
    "BNE": 3,
    "J": 1,
    "JAL": 1,
    "LW": 2,
    "SW": 2,
    "CACHE": 1,
    "HALT": 0,
}


def _remove_comments(raw_line: str) -> str:
    """Remove # comments and ; comments from one line."""
    line = raw_line

    for comment_marker in ("#", ";"):
        line = line.split(comment_marker, maxsplit=1)[0]

    return line.strip()


def parse_instruction_line(
    raw_line: str,
    line_number: int,
) -> Instruction | None:
    """
    Parse one assembly instruction.

    Blank lines and comment-only lines return None.
    """

    line = _remove_comments(raw_line)

    if not line:
        return None

    parts = line.split(maxsplit=1)
    opcode = parts[0].upper()

    if opcode not in OPERAND_COUNTS:
        raise ValueError(
            f"Unsupported opcode '{opcode}' on line {line_number}."
        )

    operand_text = parts[1] if len(parts) == 2 else ""

    if operand_text:
        raw_operands = [
            operand.strip()
            for operand in operand_text.split(",")
        ]

        if any(not operand for operand in raw_operands):
            raise ValueError(
                f"Empty operand on line {line_number}: {line}"
            )

        operands = tuple(
            operand.upper()
            for operand in raw_operands
        )
    else:
        operands = ()

    expected_count = OPERAND_COUNTS[opcode]

    if len(operands) != expected_count:
        raise ValueError(
            f"{opcode} expects {expected_count} operand(s), "
            f"but received {len(operands)} on line {line_number}."
        )

    return Instruction(
        opcode=opcode,
        operands=operands,
        source=line,
        line_number=line_number,
    )


def parse_instruction_file(
    file_path: str | Path,
) -> list[Instruction]:
    """Read and parse instructions from an assembly file."""

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Instruction file not found: {path}"
        )

    instructions: list[Instruction] = []

    with path.open("r", encoding="utf-8") as file:
        for line_number, raw_line in enumerate(file, start=1):
            instruction = parse_instruction_line(
                raw_line,
                line_number,
            )

            if instruction is not None:
                instructions.append(instruction)

    return instructions


def parse_memory_file(
    file_path: str | Path,
) -> dict[int, int]:
    """
    Read initial memory values from a text file.

    Expected format:
        address value

    Blank lines and comments beginning with # are ignored.
    """

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Memory file not found: {path}"
        )

    memory_values: dict[int, int] = {}

    with path.open("r", encoding="utf-8") as file:
        for line_number, raw_line in enumerate(file, start=1):
            line = raw_line.split(
                "#",
                maxsplit=1,
            )[0].strip()

            if not line:
                continue

            parts = line.split()

            if len(parts) != 2:
                raise ValueError(
                    f"Invalid memory entry on line {line_number}: "
                    f"expected 'address value'."
                )

            try:
                address = int(parts[0], 0)
                value = int(parts[1], 0)
            except ValueError as error:
                raise ValueError(
                    f"Invalid integer on line {line_number}: "
                    f"{raw_line.strip()}"
                ) from error

            if address < 0:
                raise ValueError(
                    f"Memory address cannot be negative "
                    f"on line {line_number}."
                )

            if address in memory_values:
                raise ValueError(
                    f"Duplicate memory address {address} "
                    f"on line {line_number}."
                )

            memory_values[address] = value

    return memory_values