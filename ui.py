color_green6 = ["#ffffff", "#edf8e9", "#bae4b3", "#74c476", "#31a354", "#006d2c"]
color_green5 = ["#ffffff", "#edf8e9","#bae4b3","#74c476","#238b45"]
color_yor6 = ["#ffffff", "#ffffb2","#fed976","#feb24c","#fd8d3c","#f03b20","#bd0026"]

class UI:
    def __init__(self, width):
        colors = color_yor6
        # TODO: make configurable
        #colors = ['colour2', 'colour28', 'colour22', '#003000']
        #blocks = [' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
        # TODO -- this way 100% won't be complete.
        # need to add one block for the last
        blocks = [' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇']
        self.blocks = []

        # TODO: add check that we have >= 2 colors
        for i in range(len(colors) - 1):
            color1, color2 = colors[i], colors[i + 1]
            for block in blocks:
                self.blocks.append(f"#[fg={color2},bg={color1}]{block}")
        self.width = width
        # resetting fg to default and bg to color 0
        self.style = f"#[default,bg={colors[0]}]"

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
