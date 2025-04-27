import unittest

from ..welch import calculate_welch_frequencies


class WelchTestCase(unittest.TestCase):
    def test_calculate_welch_frequencies(self):

        f = open("app4shm/apps/core/tests/sample_readings.txt", "r")
        frequencies_list, x_list, y_list, z_list = calculate_welch_frequencies(f.readlines())
        f.close()

        self.assertEqual(39, len(frequencies_list))
        self.assertEqual(39, len(x_list))
        self.assertEqual(39, len(y_list))
        self.assertEqual(39, len(z_list))


if __name__ == '__main__':
    unittest.main()
