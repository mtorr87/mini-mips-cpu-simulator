import unittest

from memory_bus import MemoryBus


class TestMemoryBus(unittest.TestCase):

    def setUp(self) -> None:
        self.memory = MemoryBus()

    def test_uninitialized_address_returns_zero(self) -> None:
        self.assertEqual(self.memory.read(0), 0)

    def test_write_and_read_value(self) -> None:
        self.memory.write(4, 25)

        self.assertEqual(self.memory.read(4), 25)

    def test_write_overwrites_existing_value(self) -> None:
        self.memory.write(8, 10)
        self.memory.write(8, 50)

        self.assertEqual(self.memory.read(8), 50)

    def test_load_initial_values(self) -> None:
        values = {
            0: 100,
            4: 200,
            8: 300,
        }

        self.memory.load_initial_values(values)

        self.assertEqual(self.memory.read(0), 100)
        self.assertEqual(self.memory.read(4), 200)
        self.assertEqual(self.memory.read(8), 300)

    def test_negative_address_raises_error(self) -> None:
        with self.assertRaises(ValueError):
            self.memory.read(-4)

    def test_non_integer_address_raises_error(self) -> None:
        with self.assertRaises(TypeError):
            self.memory.read("four")

    def test_non_integer_value_raises_error(self) -> None:
        with self.assertRaises(TypeError):
            self.memory.write(0, "one hundred")

    def test_dump_returns_memory_copy(self) -> None:
        self.memory.write(0, 75)

        memory_copy = self.memory.dump()
        memory_copy[0] = 999

        self.assertEqual(self.memory.read(0), 75)


if __name__ == "__main__":
    unittest.main()