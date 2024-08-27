import sys

from lib.horizon import Horizon
from lib.tmux import get_tmux_opt, get_colorscheme

DEFAULT_WIDTH = 8


def parse_stdin():
    data = sys.stdin.read().split()

    horizon = Horizon()
    width = int(get_tmux_opt('width', DEFAULT_WIDTH))
    colors = get_colorscheme()

    # Extract metrics
    values = [min(1.0, max(float(v) or 0.0, 0.0)) for v in data]
    if len(values) > width:
        values = values[-width:]
    else:
        values = [0.0] * (width - len(values)) + values
    return horizon.plot(values, colors)


if __name__ == "__main__":
    print(parse_stdin())
