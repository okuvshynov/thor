def gen_blocks():
    # TODO: make configurable
    colors = ['colour2', 'colour28', 'colour22', '#003000']
    blocks = [' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
    result = []

    for i in range(len(colors) - 1):
        color1, color2 = colors[i], colors[i + 1]
        for block in blocks:
            result.append(f"#[fg={color2},bg={color1}]{block}")
    return result


class UI:
    def __init__(self, width):
        self.blocks = gen_blocks()
        self.width = width

    def plot_bar_chart(self, values, title):
        blocks = gen_blocks()

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
                out.append(f"#[default]{percentage_str}")
        padding_length = self.width - len(values)
        if padding_length > 0:
            padding = [' '] * padding_length
            out = padding + out
        if len(values) == 0:
            out.append(" n/a")
        return f"{title}" + "".join(out)
