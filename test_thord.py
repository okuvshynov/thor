import unittest

from measurements import generate_random_id


class TestGenerateRandomID(unittest.TestCase):
    def test_length(self):
        length = 10
        generated_id = generate_random_id(length)
        self.assertEqual(len(generated_id), length)

    def test_uniqueness(self):
        length = 8
        id1 = generate_random_id(length)
        id2 = generate_random_id(length)
        self.assertNotEqual(id1, id2)


if __name__ == '__main__':
    unittest.main()
