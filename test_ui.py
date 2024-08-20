import unittest
from ui import get_blocks


class TestGetBlocks(unittest.TestCase):
    def test_get_blocks_with_two_colors(self):
        colors = ["red", "blue"]
        result = get_blocks(colors)
        blocks = [' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
        expected = [
            f"#[fg=blue,bg=red]{block}" for block in blocks
        ]
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
