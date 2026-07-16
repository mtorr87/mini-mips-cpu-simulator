import unittest

from cache import Cache
from cpu import CPU
from memory_bus import MemoryBus
from parser import Instruction, parse_instruction_line


class TestCache(unittest.TestCase):

    def setUp(self) -> None:
        self.memory = MemoryBus()
        self.memory.load_initial_values(
            {
                0: 100,
                4: 200,
                8: 300,
            }
        )
        self.cache = Cache(
            memory_bus=self.memory,
            line_count=2,
            block_size=4,
        )

    def test_cache_starts_disabled(self) -> None:
        self.assertFalse(self.cache.enabled)

    def test_disabled_cache_bypasses_lines(self) -> None:
        value = self.cache.read(0)

        self.assertEqual(value, 100)
        self.assertEqual(
            self.cache.last_status,
            "BYPASS",
        )
        self.assertEqual(self.cache.hits, 0)
        self.assertEqual(self.cache.misses, 0)

    def test_first_enabled_read_is_a_miss(self) -> None:
        self.cache.enable()

        value = self.cache.read(0)

        self.assertEqual(value, 100)
        self.assertEqual(
            self.cache.last_status,
            "MISS",
        )
        self.assertEqual(self.cache.misses, 1)

    def test_repeated_enabled_read_is_a_hit(self) -> None:
        self.cache.enable()

        self.cache.read(0)
        value = self.cache.read(0)

        self.assertEqual(value, 100)
        self.assertEqual(
            self.cache.last_status,
            "HIT",
        )
        self.assertEqual(self.cache.hits, 1)
        self.assertEqual(self.cache.misses, 1)

    def test_conflicting_address_replaces_line(self) -> None:
        self.cache.enable()

        self.cache.read(0)
        self.cache.read(8)
        self.cache.read(0)

        self.assertEqual(self.cache.misses, 3)
        self.assertEqual(self.cache.hits, 0)

    def test_write_through_updates_memory(self) -> None:
        self.cache.enable()

        self.cache.write(4, 999)

        self.assertEqual(self.memory.read(4), 999)
        self.assertEqual(
            self.cache.last_status,
            "WRITE-THROUGH",
        )

    def test_flush_invalidates_cache_lines(self) -> None:
        self.cache.enable()
        self.cache.read(0)

        self.cache.flush()

        self.assertFalse(
            any(
                line["valid"]
                for line in self.cache.snapshot()
            )
        )

        self.cache.read(0)

        self.assertEqual(
            self.cache.last_status,
            "MISS",
        )


class TestCPUCacheInstruction(unittest.TestCase):

    def setUp(self) -> None:
        self.memory = MemoryBus()
        self.memory.write(0, 100)

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

    def test_cache_one_enables_cache(self) -> None:
        self.cpu.load_program(
            [
                self.make_instruction("CACHE 1"),
            ]
        )

        self.cpu.step()

        self.assertTrue(self.cpu.cache.enabled)

    def test_cache_zero_disables_cache(self) -> None:
        self.cpu.cache.enable()

        self.cpu.load_program(
            [
                self.make_instruction("CACHE 0"),
            ]
        )

        self.cpu.step()

        self.assertFalse(self.cpu.cache.enabled)

    def test_cache_two_flushes_cache(self) -> None:
        self.cpu.cache.enable()
        self.cpu.cache.read(0)

        self.cpu.load_program(
            [
                self.make_instruction("CACHE 2"),
            ]
        )

        self.cpu.step()

        self.assertFalse(
            any(
                line["valid"]
                for line in self.cpu.cache.snapshot()
            )
        )

    def test_invalid_cache_code_raises_error(self) -> None:
        self.cpu.load_program(
            [
                self.make_instruction("CACHE 9"),
            ]
        )

        with self.assertRaises(ValueError):
            self.cpu.step()

    def test_lw_uses_cache_when_enabled(self) -> None:
        self.cpu.load_program(
            [
                self.make_instruction("CACHE 1"),
                self.make_instruction("LW R1, 0(R0)"),
                self.make_instruction("LW R2, 0(R0)"),
                self.make_instruction("HALT"),
            ]
        )

        self.cpu.run()

        self.assertEqual(
            self.cpu.read_register("R1"),
            100,
        )
        self.assertEqual(
            self.cpu.read_register("R2"),
            100,
        )
        self.assertEqual(self.cpu.cache.misses, 1)
        self.assertEqual(self.cpu.cache.hits, 1)


if __name__ == "__main__":
    unittest.main()