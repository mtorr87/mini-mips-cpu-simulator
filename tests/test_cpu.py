import unittest

from cpu import CPU
from memory_bus import MemoryBus
from parser import Instruction, parse_instruction_line


class TestCPU(unittest.TestCase):

    def setUp(self) -> None:
        self.memory = MemoryBus()
        self.cpu = CPU(
            memory_bus=self.memory,
            trace=False,
        )

    def make_instruction(
        self,
        source: str,
    ) -> Instruction:
        instruction = parse_instruction_line(
            source,
            line_number=1,
        )

        if instruction is None:
            self.fail(
                f"Expected an instruction from: {source}"
            )

        return instruction

    def test_cpu_starts_with_zeroed_registers(self) -> None:
        expected = {
            f"R{number}": 0
            for number in range(8)
        }

        self.assertEqual(
            self.cpu.dump_registers(),
            expected,
        )
        self.assertEqual(self.cpu.pc, 0)
        self.assertFalse(self.cpu.halted)

    def test_r0_cannot_be_changed(self) -> None:
        self.cpu.write_register("R0", 500)

        self.assertEqual(
            self.cpu.read_register("R0"),
            0,
        )

    def test_addi_instruction(self) -> None:
        self.cpu.load_program(
            [
                self.make_instruction(
                    "ADDI R1, R0, 10"
                )
            ]
        )

        self.cpu.step()

        self.assertEqual(
            self.cpu.read_register("R1"),
            10,
        )

    def test_add_instruction(self) -> None:
        self.cpu.write_register("R1", 10)
        self.cpu.write_register("R2", 20)

        self.cpu.load_program(
            [
                self.make_instruction(
                    "ADD R3, R1, R2"
                )
            ]
        )

        self.cpu.step()

        self.assertEqual(
            self.cpu.read_register("R3"),
            30,
        )

    def test_sub_instruction(self) -> None:
        self.cpu.write_register("R1", 30)
        self.cpu.write_register("R2", 12)

        self.cpu.load_program(
            [
                self.make_instruction(
                    "SUB R3, R1, R2"
                )
            ]
        )

        self.cpu.step()

        self.assertEqual(
            self.cpu.read_register("R3"),
            18,
        )

    def test_program_counter_advances_by_four(self) -> None:
        self.cpu.load_program(
            [
                self.make_instruction(
                    "ADDI R1, R0, 5"
                )
            ]
        )

        self.cpu.step()

        self.assertEqual(self.cpu.pc, 4)

    def test_halt_stops_cpu(self) -> None:
        self.cpu.load_program(
            [
                self.make_instruction("HALT")
            ]
        )

        self.cpu.step()

        self.assertTrue(self.cpu.halted)
        self.assertEqual(self.cpu.pc, 0)

    def test_run_executes_until_halt(self) -> None:
        program = [
            self.make_instruction(
                "ADDI R1, R0, 10"
            ),
            self.make_instruction(
                "ADDI R2, R0, 20"
            ),
            self.make_instruction(
                "ADD R3, R1, R2"
            ),
            self.make_instruction(
                "SUB R4, R3, R1"
            ),
            self.make_instruction("HALT"),
        ]

        self.cpu.load_program(program)
        self.cpu.run()

        self.assertEqual(
            self.cpu.read_register("R1"),
            10,
        )
        self.assertEqual(
            self.cpu.read_register("R2"),
            20,
        )
        self.assertEqual(
            self.cpu.read_register("R3"),
            30,
        )
        self.assertEqual(
            self.cpu.read_register("R4"),
            20,
        )
        self.assertTrue(self.cpu.halted)

    def test_reset_clears_cpu_state(self) -> None:
        self.cpu.write_register("R1", 50)
        self.cpu.pc = 20
        self.cpu.halted = True

        self.cpu.reset()

        self.assertEqual(
            self.cpu.read_register("R1"),
            0,
        )
        self.assertEqual(self.cpu.pc, 0)
        self.assertFalse(self.cpu.halted)

    def test_invalid_register_raises_error(self) -> None:
        with self.assertRaises(ValueError):
            self.cpu.read_register("R8")

    def test_slt_sets_one_when_condition_is_true(self) -> None:
        self.cpu.write_register("R1", 10)
        self.cpu.write_register("R2", 20)

        self.cpu.load_program(
            [
                self.make_instruction(
                    "SLT R3, R1, R2"
                )
            ]
        )

        self.cpu.step()

        self.assertEqual(
            self.cpu.read_register("R3"),
            1,
        )

    def test_slt_sets_zero_when_condition_is_false(self) -> None:
        self.cpu.write_register("R1", 30)
        self.cpu.write_register("R2", 20)

        self.cpu.load_program(
            [
                self.make_instruction(
                    "SLT R3, R1, R2"
                )
            ]
        )

        self.cpu.step()

        self.assertEqual(
            self.cpu.read_register("R3"),
            0,
        )

    def test_sw_stores_register_value_in_memory(self) -> None:
        self.cpu.write_register("R1", 75)

        self.cpu.load_program(
            [
                self.make_instruction(
                    "SW R1, 8(R0)"
                )
            ]
        )

        self.cpu.step()

        self.assertEqual(
            self.memory.read(8),
            75,
        )

    def test_lw_loads_memory_value_into_register(self) -> None:
        self.memory.write(12, 125)

        self.cpu.load_program(
            [
                self.make_instruction(
                    "LW R2, 12(R0)"
                )
            ]
        )

        self.cpu.step()

        self.assertEqual(
            self.cpu.read_register("R2"),
            125,
        )

    def test_memory_address_uses_base_register_and_offset(
        self,
    ) -> None:
        self.cpu.write_register("R1", 20)
        self.memory.write(28, 500)

        self.cpu.load_program(
            [
                self.make_instruction(
                    "LW R2, 8(R1)"
                )
            ]
        )

        self.cpu.step()

        self.assertEqual(
            self.cpu.read_register("R2"),
            500,
        )

    def test_invalid_memory_operand_raises_error(self) -> None:
        self.cpu.load_program(
            [
                self.make_instruction(
                    "LW R1, INVALID"
                )
            ]
        )

        with self.assertRaises(ValueError):
            self.cpu.step()

    def test_bne_branches_when_registers_differ(self) -> None:
        self.cpu.write_register("R1", 10)
        self.cpu.write_register("R2", 20)

        self.cpu.load_program(
            [
                self.make_instruction("BNE R1, R2, 1"),
                self.make_instruction("HALT"),
                self.make_instruction("HALT"),
            ]
        )

        self.cpu.step()

        self.assertEqual(self.cpu.pc, 8)

    def test_bne_does_not_branch_when_registers_match(self) -> None:
        self.cpu.write_register("R1", 10)
        self.cpu.write_register("R2", 10)

        self.cpu.load_program(
            [
                self.make_instruction("BNE R1, R2, 1"),
                self.make_instruction("HALT"),
            ]
        )

        self.cpu.step()

        self.assertEqual(self.cpu.pc, 4)

    def test_jump_sets_program_counter(self) -> None:
        self.cpu.load_program(
            [
                self.make_instruction("J 3"),
                self.make_instruction("HALT"),
                self.make_instruction("HALT"),
                self.make_instruction("HALT"),
            ]
        )

        self.cpu.step()

        self.assertEqual(self.cpu.pc, 12)

    def test_jal_saves_return_address_in_r7(self) -> None:
        self.cpu.load_program(
            [
                self.make_instruction("JAL 2"),
                self.make_instruction("HALT"),
                self.make_instruction("HALT"),
            ]
        )

        self.cpu.step()

        self.assertEqual(
            self.cpu.read_register("R7"),
            4,
        )
        self.assertEqual(self.cpu.pc, 8)

    def test_jump_to_current_instruction_does_not_advance(self) -> None:
        self.cpu.load_program(
            [
                self.make_instruction("J 0"),
            ]
        )

        self.cpu.step()

        self.assertEqual(self.cpu.pc, 0)


if __name__ == "__main__":
    unittest.main()