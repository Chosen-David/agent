"""Independent checks; optionally pass an implementation path on the command line."""
import importlib.util
import math
from pathlib import Path
import random
import sys
import unittest
from fractions import Fraction


target = Path(sys.argv.pop(1)) if len(sys.argv) > 1 else Path(__file__).with_name("buggy.py")
spec = importlib.util.spec_from_file_location("implementation", target)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
moving_average = module.moving_average


def reference(values, window):
    # Enumerate window endpoints and exact rational sums, without slicing.
    result = []
    for end in range(window, len(values) + 1):
        total = Fraction(0)
        for position in range(end - window, end):
            total += Fraction(values[position])
        result.append(float(total / window))
    return result


class MovingAverageChecks(unittest.TestCase):
    def check_case(self, values, window):
        before = values.copy() if isinstance(values, list) else tuple(values)
        actual = moving_average(values, window)
        expected = reference(values, window)
        self.assertIsInstance(actual, list)
        self.assertEqual(len(actual), len(expected))
        for observed, wanted in zip(actual, expected):
            self.assertTrue(math.isclose(observed, wanted, rel_tol=1e-12, abs_tol=1e-12),
                            (values, window, observed, wanted))
        self.assertEqual(values, before)

    def test_last_window_regression(self):
        self.assertEqual(moving_average([1, 2, 3], 2), [1.5, 2.5])

    def test_boundaries(self):
        for values, window in [([], 1), ([3], 1), ([1, 2], 1),
                               ([1, 2, 3], 3), ([1, 2], 3),
                               ([0, 0, 0], 2), ([-5, 4, -3, 2], 2)]:
            with self.subTest(values=values, window=window):
                self.check_case(values, window)

    def test_floats_and_tuple(self):
        self.check_case([0.1, 0.2, 0.3, -0.4, 1.5], 3)
        self.check_case((1, 2, 3, 4), 2)

    def test_seeded_inputs(self):
        rng = random.Random(20261003)
        for _ in range(200):
            values = [rng.randint(-10000, 10000) for _ in range(rng.randrange(40))]
            self.check_case(values, rng.randint(1, len(values) + 3))

    def test_nonpositive_window(self):
        for values in ([], [1, 2, 3]):
            for window in (0, -1, -10):
                before = values.copy()
                with self.subTest(values=values, window=window):
                    with self.assertRaises(ValueError):
                        moving_average(values, window)
                    self.assertEqual(values, before)

    def test_noninteger_window(self):
        for window in (1.0, 1.5, "2", None, True, False):
            values = [1, 2, 3]
            with self.subTest(window=window):
                with self.assertRaises(TypeError):
                    moving_average(values, window)
                self.assertEqual(values, [1, 2, 3])

    def test_integer_index_protocol(self):
        class Window:
            def __index__(self):
                return 2
        self.assertEqual(moving_average([1, 2, 3], Window()), [1.5, 2.5])


if __name__ == "__main__":
    unittest.main(verbosity=2)
