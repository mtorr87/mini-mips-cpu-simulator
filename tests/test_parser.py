import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from parser import parse_memory_file


class TestParseMemoryFile(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_directory = TemporaryDirectory()
        self.addCleanup(self.temp_directory.cleanup)

        self.file_path = Path(self.temp_directory.name) / "memory.txt"

    def write_file(self, contents: str) -> None:
        self.file_path.write_text(contents, encoding="utf-8")

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

    def test_missing_file_raises_error(self) -> None:
        missing_file = Path(self.temp_directory.name) / "missing.txt"

        with self.assertRaises(FileNotFoundError):
            parse_memory_file(missing_file)


if __name__ == "__main__":
    unittest.main()