color_green4 = ['colour2', 'colour28', 'colour22', '#003000']


def get_blocks(colors):
    blocks = [' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
    res = []

    for i in range(len(colors) - 1):
        color1, color2 = colors[i], colors[i + 1]
        j = 0 if i == 0 else 1
        for block in blocks[j:]:
            res.append(f"#[fg={color2},bg={color1}]{block}")

    return res


class UI:
    def __init__(self, width, colors=color_green4):
        self.width = width
        # resetting fg to default and bg to color 0
        self.style = f"#[default,bg={colors[0]}]"
        self.blocks = get_blocks(colors)

    def plot_bar_chart(self, values, title):
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
                percentage_str = f'{percentage:3d}%%'
                out.append(f"{self.style}{percentage_str}")
        padding_length = self.width - len(values)
        if padding_length > 0:
            padding = [' '] * padding_length
            out = padding + out
        if len(values) == 0:
            out.append(" n/a")
        return f"{self.style}{title}" + "".join(out)
