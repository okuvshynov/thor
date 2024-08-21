import subprocess
import sys
from threading import Thread

from macos_reader import MacOSReader
from measurements import Measurements
from ui import UI


W_CHART = 8  # Maximum number of measurements to store
DO_REFRESH = True
measurements = Measurements(W_CHART)
title = {'gpu': 'G:', 'ecpu': 'E:', 'pcpu': 'P:', 'wired': 'W:', 'rss': 'R:'}
ui = UI(W_CHART)


# Start data collection in a separate thread
def start_data_collection():
    reader = MacOSReader()
    thread = Thread(target=reader.start, args=(measurements, ))
    thread.daemon = True
    thread.start()


def plot(metrics, last_id):
    new_id, data = measurements.wait(last_id)
    results = []
    for metric in metrics:
        if metric not in data:
            results.append(f"N/A")
        else:
            results.append(ui.plot_bar_chart(data[metric], title[metric]))
    return new_id, results


def loop():
    curr_id = None
    metrics = title.keys()
    while True:
        curr_id, charts = plot(metrics, curr_id)
        for metric, chart in zip(metrics, charts):
            filename = f'/tmp/thor_metric_{metric}_data'
            with open(filename, 'w') as wfile:
                wfile.write(chart)
        #set_new_status('|'.join(status))
        if DO_REFRESH:
            subprocess.run(["tmux", "refresh-client", "-S"])


if __name__ == '__main__':
    start_data_collection()
    loop()
