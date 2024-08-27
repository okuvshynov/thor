import json
import sys

from horizon import Horizon
from tmux import get_tmux_opt, get_colorscheme

DEFAULT_WIDTH = 8


def parse_json():
    """Parse JSON from stdin and extract metrics"""
    # Read JSON from stdin
    json_input = sys.stdin.read()
    data = json.loads(json_input)

    horizon = Horizon()
    width = int(get_tmux_opt('width', DEFAULT_WIDTH))
    colors = get_colorscheme()

    # Extract metrics
    for metric in data:
        # target = metric["target"]
        # tags = metric["tags"]
        datapoints = metric["datapoints"]

        values = [min(1.0, max(p[0] or 0.0, 0.0)) for p in datapoints]
        if len(values) > width:
            values = values[-width:]
        else:
            values = [0.0] * (width - len(values)) + values
        return horizon.plot(values, colors)


if __name__ == "__main__":
    print(parse_json())
