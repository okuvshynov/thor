import unittest
from ..horizon import gen_blocks


class TestGetBlocks(unittest.TestCase):
    def test_get_blocks_with_two_colors(self):
        colors = ["red", "blue"]
        result = gen_blocks(colors)
        blocks = [' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
        expected = [
            f"#[fg=blue,bg=red]{block}" for block in blocks
        ]
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
