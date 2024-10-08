import os
import subprocess
from threading import Thread

from lib.measurements import Measurements
from lib.horizon import Horizon
from platforms.readers import create_reader
from lib.tmux import get_tmux_opt, get_colorscheme


DEFAULT_WIDTH = 8
DATA_SIZE = 256  # Maximum number of measurements to store
FORCE_REDRAW = 1
INTERVAL_MS = 1000

interval_ms = int(get_tmux_opt('interval_ms', INTERVAL_MS))

measurements = Measurements(DATA_SIZE)
horizon = Horizon()
reader = create_reader({'interval_ms': interval_ms})


# Start data collection in a separate thread
def start_data_collection():
    # TODO: pass some options here
    thread = Thread(target=reader.start, args=(measurements, ))
    thread.daemon = True
    thread.start()


def plot(metrics, last_id, width, colors):
    new_id, data = measurements.wait(last_id)
    results = []
    for metric in metrics:
        if metric not in data:
            results.append("N/A".ljust(width))
        else:
            values = data[metric]
            if len(values) > width:
                values = values[-width:]
            else:
                values = [0.0] * (width - len(values)) + values
            results.append(horizon.plot(values, colors))
    return new_id, results


def cleanup_files():
    for metric in reader.metrics():
        filename = f'/tmp/thor_metric_{metric}_data'
        if os.path.exists(filename):
            os.remove(filename)


def loop():
    curr_id = None
    metrics = reader.metrics()
    while True:
        width = int(get_tmux_opt('width', DEFAULT_WIDTH))
        force_redraw = int(get_tmux_opt('force_redraw', FORCE_REDRAW))
        colors = get_colorscheme()
        curr_id, charts = plot(metrics, curr_id, width, colors)
        for metric, chart in zip(metrics, charts):
            filename = f'/tmp/thor_metric_{metric}_data'
            with open(filename, 'w') as wfile:
                wfile.write(chart)
        if force_redraw > 0:
            subprocess.run(["tmux", "refresh-client", "-S"])


if __name__ == '__main__':
    cleanup_files()
    start_data_collection()
    loop()
