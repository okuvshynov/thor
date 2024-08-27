def gen_blocks(colors):
    blocks = [' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
    res = []

    for i in range(len(colors) - 1):
        color1, color2 = colors[i], colors[i + 1]
        j = 0 if i == 0 else 1
        for block in blocks[j:]:
            res.append(f"#[fg={color2},bg={color1}]{block}")

    return res


class Horizon:
    def __init__(self):
        self.colors = None

    def plot(self, values, colors):
        if colors != self.colors:
            self.style = f"#[default,bg={colors[0]}]"
            self.blocks = gen_blocks(colors)
            self.colors = colors

        blocks = self.blocks

        out = []

        for i, value in enumerate(values):
            if value < 0 or value > 1:
                raise ValueError("Value must be in range 0...1")

            block_index = int(value * len(blocks))
            block = blocks[min(block_index, len(blocks) - 1)]
            out.append(block)
            if i == len(values) - 1:
                percentage = int(value * 100)
                percentage_str = f'{percentage:3d}%'
                out.append(f"{self.style}{percentage_str}")
        if len(values) == 0:
            out.append(" n/a")
        return "".join(out) + "#[default]"
