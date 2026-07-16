import argparse
import sys
from pathlib import Path
from typing import Sequence

from cpu import CPU
from memory_bus import MemoryBus
from parser import (
    parse_instruction_file,
    parse_memory_file,
)


PROJECT_DIRECTORY = Path(__file__).parent
DEFAULT_PROGRAM_FILE = (
    PROJECT_DIRECTORY
    / "programs"
    / "program.asm"
)
DEFAULT_MEMORY_FILE = (
    PROJECT_DIRECTORY
    / "programs"
    / "memory.txt"
)


def build_argument_parser() -> argparse.ArgumentParser:
    """Create the command-line interface for the simulator."""
    parser = argparse.ArgumentParser(
        description=(
            "Run a simplified MIPS CPU simulation using "
            "assembly and memory initialization files."
        )
    )

    parser.add_argument(
        "--program",
        type=Path,
        default=DEFAULT_PROGRAM_FILE,
        help=(
            "Path to the assembly program file. "
            "Defaults to programs/program.asm."
        ),
    )

    parser.add_argument(
        "--memory",
        type=Path,
        default=DEFAULT_MEMORY_FILE,
        help=(
            "Path to the memory initialization file. "
            "Defaults to programs/memory.txt."
        ),
    )

    parser.add_argument(
        "--max-steps",
        type=int,
        default=1000,
        help=(
            "Maximum number of instructions to execute "
            "before stopping. Defaults to 1000."
        ),
    )

    parser.add_argument(
        "--no-trace",
        action="store_true",
        help="Disable fetch, decode, and execute output.",
    )

    return parser


def run_simulation(
    program_file: str | Path,
    memory_file: str | Path,
    *,
    trace: bool = True,
    max_steps: int = 1000,
) -> tuple[CPU, MemoryBus]:
    """
    Load input files and run the CPU simulation.

    Returns:
        A tuple containing the completed CPU and MemoryBus.
    """
    if max_steps <= 0:
        raise ValueError(
            "Maximum steps must be greater than zero."
        )

    program_path = Path(program_file)
    memory_path = Path(memory_file)

    print("Loading initial memory values...")
    initial_values = parse_memory_file(memory_path)

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
        program_path
    )

    print(
        f"Loaded {len(instructions)} instructions."
    )

    cpu = CPU(
        memory_bus=memory,
        trace=trace,
    )
    cpu.load_program(instructions)

    print("\nStarting CPU...\n")
    cpu.run(max_steps=max_steps)

    print_simulation_summary(cpu, memory)

    return cpu, memory


def print_simulation_summary(
    cpu: CPU,
    memory: MemoryBus,
) -> None:
    """Print final CPU, memory, and cache state."""
    print("\nFinal Registers:")

    for register, value in (
        cpu.dump_registers().items()
    ):
        print(f"{register} = {value}")

    print("\nFinal Memory Bus:")
    print(memory)

    print("\nFinal Cache:")
    print(cpu.cache)

    print(f"\nFinal PC = {cpu.pc}")
    print(f"CPU halted = {cpu.halted}")


def main(
    argv: Sequence[str] | None = None,
) -> int:
    """Run the command-line application."""
    parser = build_argument_parser()
    arguments = parser.parse_args(argv)

    try:
        run_simulation(
            program_file=arguments.program,
            memory_file=arguments.memory,
            trace=not arguments.no_trace,
            max_steps=arguments.max_steps,
        )
    except (
        FileNotFoundError,
        TypeError,
        ValueError,
        RuntimeError,
    ) as error:
        print(
            f"Simulation error: {error}",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())