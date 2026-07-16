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
        self._pc_changed = False

    def load_program(
        self,
        instructions: list[Instruction],
    ) -> None:
        """Load instructions and prepare the CPU to run."""
        self.instructions = list(instructions)
        self.pc = 0
        self.halted = False
        self._pc_changed = False

    def reset(self) -> None:
        """Reset registers and CPU state."""
        for register in self.registers:
            self.registers[register] = 0

        self.pc = 0
        self.halted = False
        self._pc_changed = False

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
        Write an integer value to a register.

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

        if (
            instruction_index < 0
            or instruction_index >= len(self.instructions)
        ):
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

        self._pc_changed = False

        instruction = self.fetch()
        self.decode(instruction)

        handlers = {
            "ADD": self._execute_add,
            "ADDI": self._execute_addi,
            "SUB": self._execute_sub,
            "SLT": self._execute_slt,
            "BNE": self._execute_bne,
            "J": self._execute_j,
            "JAL": self._execute_jal,
            "LW": self._execute_lw,
            "SW": self._execute_sw,
            "HALT": self._execute_halt,
        }

        handler = handlers.get(instruction.opcode)

        if handler is None:
            raise ValueError(
                f"CPU does not yet support "
                f"{instruction.opcode} execution."
            )

        handler(instruction)

        if not self.halted and not self._pc_changed:
            self.pc += 4

        self.registers["R0"] = 0

    def run(self, max_steps: int = 1000) -> None:
        """Run instructions until HALT is executed."""
        if max_steps <= 0:
            raise ValueError("max_steps must be greater than zero.")

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
        destination, source_one, source_two = instruction.operands

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
        destination, source, immediate_text = instruction.operands

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
        destination, source_one, source_two = instruction.operands

        first_value = self.read_register(source_one)
        second_value = self.read_register(source_two)
        result = first_value - second_value

        self.write_register(destination, result)

        self._print_trace(
            f"EXECUTE {destination} <- "
            f"{source_one}({first_value}) - "
            f"{source_two}({second_value}) = {result}"
        )

    def _execute_slt(
        self,
        instruction: Instruction,
    ) -> None:
        """Set destination to 1 if source one is less than source two."""
        destination, source_one, source_two = instruction.operands

        first_value = self.read_register(source_one)
        second_value = self.read_register(source_two)
        result = 1 if first_value < second_value else 0

        self.write_register(destination, result)

        self._print_trace(
            f"EXECUTE {destination} <- "
            f"1 if {source_one}({first_value}) < "
            f"{source_two}({second_value}) else 0 "
            f"= {result}"
        )

    def _execute_bne(
        self,
        instruction: Instruction,
    ) -> None:
        """Branch when two registers are not equal."""
        source_one, source_two, offset_text = instruction.operands

        first_value = self.read_register(source_one)
        second_value = self.read_register(source_two)
        offset = self._parse_integer(offset_text)

        if first_value != second_value:
            target_address = self.pc + 4 + (offset * 4)
            self._set_pc(target_address)

            self._print_trace(
                f"EXECUTE {source_one}({first_value}) != "
                f"{source_two}({second_value}); "
                f"branch to PC={target_address}"
            )
        else:
            self._print_trace(
                f"EXECUTE {source_one}({first_value}) == "
                f"{source_two}({second_value}); "
                "branch not taken"
            )

    def _execute_j(
        self,
        instruction: Instruction,
    ) -> None:
        """Jump to target instruction address."""
        (target_text,) = instruction.operands
        target = self._parse_integer(target_text)

        if target < 0:
            raise ValueError("Jump target cannot be negative.")

        target_address = target * 4
        self._set_pc(target_address)

        self._print_trace(
            f"EXECUTE jump to PC={target_address}"
        )

    def _execute_jal(
        self,
        instruction: Instruction,
    ) -> None:
        """Save the return address in R7 and jump."""
        (target_text,) = instruction.operands
        target = self._parse_integer(target_text)

        if target < 0:
            raise ValueError("Jump target cannot be negative.")

        return_address = self.pc + 4
        target_address = target * 4

        self.write_register("R7", return_address)
        self._set_pc(target_address)

        self._print_trace(
            f"EXECUTE R7 <- {return_address}; "
            f"jump to PC={target_address}"
        )

    def _execute_lw(
        self,
        instruction: Instruction,
    ) -> None:
        """Load a value from memory into a register."""
        destination, memory_operand = instruction.operands

        offset, base_register = self._parse_memory_operand(
            memory_operand
        )

        base_address = self.read_register(base_register)
        address = base_address + offset
        value = self.memory_bus.read(address)

        self.write_register(destination, value)

        self._print_trace(
            f"EXECUTE {destination} <- "
            f"MEM[{base_register}({base_address}) + "
            f"{offset}] = MEM[{address}] = {value}"
        )

    def _execute_sw(
        self,
        instruction: Instruction,
    ) -> None:
        """Store a register value in memory."""
        source, memory_operand = instruction.operands

        offset, base_register = self._parse_memory_operand(
            memory_operand
        )

        base_address = self.read_register(base_register)
        address = base_address + offset
        value = self.read_register(source)

        self.memory_bus.write(address, value)

        self._print_trace(
            f"EXECUTE MEM[{base_register}({base_address}) + "
            f"{offset}] = MEM[{address}] <- "
            f"{source}({value})"
        )

    def _execute_halt(
        self,
        instruction: Instruction,
    ) -> None:
        """Stop program execution."""
        self.halted = True
        self._print_trace("EXECUTE CPU halted")

    def _set_pc(self, address: int) -> None:
        """Set the program counter during a branch or jump."""
        if address < 0:
            raise ValueError(
                "Program counter cannot be negative."
            )

        if address % 4 != 0:
            raise ValueError(
                f"Program counter must be word-aligned: {address}"
            )

        self.pc = address
        self._pc_changed = True

    @classmethod
    def _parse_memory_operand(
        cls,
        operand: str,
    ) -> tuple[int, str]:
        """
        Parse an operand such as 8(R2), -4(R3), or 0x10(R1).

        Returns:
            A tuple containing (offset, base_register).
        """
        if not operand.endswith(")") or "(" not in operand:
            raise ValueError(
                f"Invalid memory operand: {operand}. "
                "Expected format offset(register)."
            )

        offset_text, register_text = operand[:-1].split(
            "(",
            maxsplit=1,
        )

        if not offset_text or not register_text:
            raise ValueError(
                f"Invalid memory operand: {operand}. "
                "Expected format offset(register)."
            )

        offset = cls._parse_integer(offset_text)
        base_register = register_text.upper()
        cls._validate_register(base_register)

        return offset, base_register

    @staticmethod
    def _parse_integer(value: str) -> int:
        """Parse a decimal, negative, or hexadecimal integer."""
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