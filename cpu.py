from memory_bus import MemoryBus
from parser import Instruction


class CPU:
    """Simulates a simplified MIPS-style CPU."""

    REGISTER_NAMES = tuple(f"R{number}" for number in range(8))

    def __init__(
        self,
        memory_bus: MemoryBus,
        trace: bool = True,
    ) -> None:
        self.memory_bus = memory_bus
        self.trace = trace

        self.registers: dict[str, int] = {
            register: 0
            for register in self.REGISTER_NAMES
        }

        self.instructions: list[Instruction] = []
        self.pc = 0
        self.halted = False

    def load_program(
        self,
        instructions: list[Instruction],
    ) -> None:
        """Load instructions and prepare the CPU to run."""

        self.instructions = list(instructions)
        self.pc = 0
        self.halted = False

    def reset(self) -> None:
        """Reset the registers and CPU state."""

        for register in self.registers:
            self.registers[register] = 0

        self.pc = 0
        self.halted = False

    def read_register(self, register: str) -> int:
        """Read a value from a register."""

        register = register.upper()
        self._validate_register(register)

        return self.registers[register]

    def write_register(
        self,
        register: str,
        value: int,
    ) -> None:
        """
        Write a value to a register.

        R0 always remains zero.
        """

        register = register.upper()
        self._validate_register(register)

        if not isinstance(value, int):
            raise TypeError("Register values must be integers.")

        if register == "R0":
            return

        self.registers[register] = value

    def fetch(self) -> Instruction:
        """Fetch the instruction at the current PC address."""

        if self.pc % 4 != 0:
            raise RuntimeError(
                f"Program counter must be word-aligned: PC={self.pc}"
            )

        instruction_index = self.pc // 4

        if instruction_index >= len(self.instructions):
            raise RuntimeError(
                f"No instruction exists at PC={self.pc}. "
                "The program may be missing HALT."
            )

        instruction = self.instructions[instruction_index]

        self._print_trace(
            f"FETCH   PC={self.pc}: {instruction.source}"
        )

        return instruction

    def decode(self, instruction: Instruction) -> None:
        """Display the decoded opcode and operands."""

        self._print_trace(
            f"DECODE  opcode={instruction.opcode} "
            f"operands={list(instruction.operands)}"
        )

    def step(self) -> None:
        """Fetch, decode, and execute one instruction."""

        if self.halted:
            raise RuntimeError("The CPU is already halted.")

        instruction = self.fetch()
        self.decode(instruction)

        handlers = {
            "ADD": self._execute_add,
            "ADDI": self._execute_addi,
            "SUB": self._execute_sub,
            "HALT": self._execute_halt,
        }

        handler = handlers.get(instruction.opcode)

        if handler is None:
            raise ValueError(
                f"CPU does not yet support "
                f"{instruction.opcode} execution."
            )

        handler(instruction)

        # HALT leaves the PC pointing at the HALT instruction.
        if not self.halted:
            self.pc += 4

        # Enforce the MIPS rule that R0 is always zero.
        self.registers["R0"] = 0

    def run(self, max_steps: int = 1000) -> None:
        """Run instructions until HALT is executed."""

        steps = 0

        while not self.halted:
            if steps >= max_steps:
                raise RuntimeError(
                    "Maximum instruction count exceeded. "
                    "The program may contain an infinite loop."
                )

            self.step()
            steps += 1

    def dump_registers(self) -> dict[str, int]:
        """Return a copy of the CPU registers."""

        return self.registers.copy()

    def _execute_add(
        self,
        instruction: Instruction,
    ) -> None:
        destination, source_one, source_two = (
            instruction.operands
        )

        first_value = self.read_register(source_one)
        second_value = self.read_register(source_two)
        result = first_value + second_value

        self.write_register(destination, result)

        self._print_trace(
            f"EXECUTE {destination} <- "
            f"{source_one}({first_value}) + "
            f"{source_two}({second_value}) = {result}"
        )

    def _execute_addi(
        self,
        instruction: Instruction,
    ) -> None:
        destination, source, immediate_text = (
            instruction.operands
        )

        source_value = self.read_register(source)
        immediate = self._parse_integer(immediate_text)
        result = source_value + immediate

        self.write_register(destination, result)

        self._print_trace(
            f"EXECUTE {destination} <- "
            f"{source}({source_value}) + "
            f"{immediate} = {result}"
        )

    def _execute_sub(
        self,
        instruction: Instruction,
    ) -> None:
        destination, source_one, source_two = (
            instruction.operands
        )

        first_value = self.read_register(source_one)
        second_value = self.read_register(source_two)
        result = first_value - second_value

        self.write_register(destination, result)

        self._print_trace(
            f"EXECUTE {destination} <- "
            f"{source_one}({first_value}) - "
            f"{source_two}({second_value}) = {result}"
        )

    def _execute_halt(
        self,
        instruction: Instruction,
    ) -> None:
        self.halted = True
        self._print_trace("EXECUTE CPU halted")

    @staticmethod
    def _parse_integer(value: str) -> int:
        """Parse decimal, negative, or hexadecimal integers."""

        try:
            return int(value, 0)
        except ValueError as error:
            raise ValueError(
                f"Invalid integer value: {value}"
            ) from error

    @classmethod
    def _validate_register(
        cls,
        register: str,
    ) -> None:
        if register not in cls.REGISTER_NAMES:
            raise ValueError(
                f"Invalid register '{register}'. "
                "Expected R0 through R7."
            )

    def _print_trace(self, message: str) -> None:
        if self.trace:
            print(message)