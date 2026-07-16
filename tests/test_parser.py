import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from parser import (
    Instruction,
    parse_instruction_file,
    parse_instruction_line,
    parse_memory_file,
)


class TestParseMemoryFile(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_directory = TemporaryDirectory()
        self.addCleanup(self.temp_directory.cleanup)

        self.file_path = (
            Path(self.temp_directory.name) / "memory.txt"
        )

    def write_file(self, contents: str) -> None:
        self.file_path.write_text(
            contents,
            encoding="utf-8",
        )

    def test_parse_valid_memory_file(self) -> None:
        self.write_file(
            """
            0 100
            4 200
            8 300
            """
        )

        result = parse_memory_file(self.file_path)

        self.assertEqual(
            result,
            {
                0: 100,
                4: 200,
                8: 300,
            },
        )

    def test_blank_lines_and_comments_are_ignored(self) -> None:
        self.write_file(
            """
            # Initial values

            0 25
            4 50  # Stored at address four
            """
        )

        result = parse_memory_file(self.file_path)

        self.assertEqual(result, {0: 25, 4: 50})

    def test_hexadecimal_values_are_supported(self) -> None:
        self.write_file(
            """
            0x0 0x10
            0x4 0x20
            """
        )

        result = parse_memory_file(self.file_path)

        self.assertEqual(result, {0: 16, 4: 32})

    def test_invalid_line_format_raises_error(self) -> None:
        self.write_file("0 100 extra-value")

        with self.assertRaises(ValueError):
            parse_memory_file(self.file_path)

    def test_non_integer_value_raises_error(self) -> None:
        self.write_file("0 one-hundred")

        with self.assertRaises(ValueError):
            parse_memory_file(self.file_path)

    def test_negative_address_raises_error(self) -> None:
        self.write_file("-4 100")

        with self.assertRaises(ValueError):
            parse_memory_file(self.file_path)

    def test_duplicate_address_raises_error(self) -> None:
        self.write_file(
            """
            0 100
            0 200
            """
        )

        with self.assertRaises(ValueError):
            parse_memory_file(self.file_path)

    def test_missing_memory_file_raises_error(self) -> None:
        missing_file = (
            Path(self.temp_directory.name) / "missing.txt"
        )

        with self.assertRaises(FileNotFoundError):
            parse_memory_file(missing_file)


class TestInstructionParser(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_directory = TemporaryDirectory()
        self.addCleanup(self.temp_directory.cleanup)

        self.file_path = (
            Path(self.temp_directory.name) / "program.asm"
        )

    def write_file(self, contents: str) -> None:
        self.file_path.write_text(
            contents,
            encoding="utf-8",
        )

    def test_parse_arithmetic_instruction(self) -> None:
        instruction = parse_instruction_line(
            "ADD R3, R1, R2",
            1,
        )

        self.assertEqual(
            instruction,
            Instruction(
                opcode="ADD",
                operands=("R3", "R1", "R2"),
                source="ADD R3, R1, R2",
                line_number=1,
            ),
        )

    def test_lowercase_instruction_is_normalized(self) -> None:
        instruction = parse_instruction_line(
            "addi r1, r0, 10",
            3,
        )

        self.assertIsNotNone(instruction)
        self.assertEqual(instruction.opcode, "ADDI")
        self.assertEqual(
            instruction.operands,
            ("R1", "R0", "10"),
        )

    def test_memory_operand_is_preserved(self) -> None:
        instruction = parse_instruction_line(
            "LW R4, 8(R2)",
            5,
        )

        self.assertIsNotNone(instruction)
        self.assertEqual(
            instruction.operands,
            ("R4", "8(R2)"),
        )

    def test_halt_has_no_operands(self) -> None:
        instruction = parse_instruction_line(
            "HALT ; stop execution",
            7,
        )

        self.assertIsNotNone(instruction)
        self.assertEqual(instruction.opcode, "HALT")
        self.assertEqual(instruction.operands, ())

    def test_comments_and_blank_lines_are_ignored(self) -> None:
        self.write_file(
            """
            # Test program

            ADDI R1, R0, 5
            ; another comment
            HALT
            """
        )

        instructions = parse_instruction_file(
            self.file_path
        )

        self.assertEqual(len(instructions), 2)
        self.assertEqual(
            instructions[0].opcode,
            "ADDI",
        )
        self.assertEqual(
            instructions[1].opcode,
            "HALT",
        )

    def test_unsupported_opcode_raises_error(self) -> None:
        with self.assertRaises(ValueError):
            parse_instruction_line(
                "MULT R1, R2, R3",
                1,
            )

    def test_wrong_operand_count_raises_error(self) -> None:
        with self.assertRaises(ValueError):
            parse_instruction_line(
                "ADD R1, R2",
                1,
            )

    def test_missing_instruction_file_raises_error(self) -> None:
        missing_file = (
            Path(self.temp_directory.name) / "missing.asm"
        )

        with self.assertRaises(FileNotFoundError):
            parse_instruction_file(missing_file)


if __name__ == "__main__":
    unittest.main()