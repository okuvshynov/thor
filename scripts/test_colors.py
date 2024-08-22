import unittest
from colors import to_scheme


class TestToScheme(unittest.TestCase):
    def test_to_scheme(self):
        observed = to_scheme('#00ff00', '#000000', 3)
        expected = ['#00ff00', '#007f00', '#000000']
        self.assertEqual(observed, expected)


if __name__ == '__main__':
    unittest.main()
