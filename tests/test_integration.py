import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from main import main, run_simulation


class TestSimulatorIntegration(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_directory = TemporaryDirectory()
        self.addCleanup(
            self.temp_directory.cleanup
        )

        self.directory = Path(
            self.temp_directory.name
        )

        self.program_file = (
            self.directory / "program.asm"
        )
        self.memory_file = (
            self.directory / "memory.txt"
        )

    def write_program(
        self,
        contents: str,
    ) -> None:
        self.program_file.write_text(
            contents,
            encoding="utf-8",
        )

    def write_memory(
        self,
        contents: str,
    ) -> None:
        self.memory_file.write_text(
            contents,
            encoding="utf-8",
        )

    def test_end_to_end_program_execution(self) -> None:
        self.write_memory(
            """
            0 40
            4 60
            """
        )

        self.write_program(
            """
            CACHE 1
            LW R1, 0(R0)
            LW R2, 4(R0)
            ADD R3, R1, R2
            SW R3, 8(R0)
            HALT
            """
        )

        output = io.StringIO()

        with redirect_stdout(output):
            cpu, memory = run_simulation(
                program_file=self.program_file,
                memory_file=self.memory_file,
                trace=False,
            )

        self.assertTrue(cpu.halted)
        self.assertEqual(
            cpu.read_register("R3"),
            100,
        )
        self.assertEqual(
            memory.read(8),
            100,
        )
        self.assertEqual(
            cpu.cache.misses,
            2,
        )
        self.assertEqual(
            cpu.cache.writes,
            1,
        )

    def test_main_returns_zero_for_valid_files(self) -> None:
        self.write_memory("0 10")
        self.write_program("HALT")

        output = io.StringIO()

        with redirect_stdout(output):
            result = main(
                [
                    "--program",
                    str(self.program_file),
                    "--memory",
                    str(self.memory_file),
                    "--no-trace",
                ]
            )

        self.assertEqual(result, 0)

    def test_main_returns_one_for_missing_program(
        self,
    ) -> None:
        self.write_memory("0 10")

        missing_program = (
            self.directory / "missing.asm"
        )

        errors = io.StringIO()

        with redirect_stderr(errors):
            result = main(
                [
                    "--program",
                    str(missing_program),
                    "--memory",
                    str(self.memory_file),
                ]
            )

        self.assertEqual(result, 1)
        self.assertIn(
            "Simulation error:",
            errors.getvalue(),
        )


if __name__ == "__main__":
    unittest.main()