import subprocess
import sys
from threading import Thread

from macos_reader import MacOSReader
from measurements import Measurements
from ui import UI


W_CHART = 8  # Maximum number of measurements to store
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
            results.append(f"{metric} not found")
        else:
            results.append(ui.plot_bar_chart(data[metric], title[metric]))
    return new_id, results


def set_new_status(status):
    """
    Sets the new status in tmux status-right option and refreshes the client.
    Parameters:
    status (str): The new status to set.
    """
    # Set the status-right option in tmux
    subprocess.run(["tmux", "set-option", "-g", "status-right", status])
    # Refresh the tmux client
    subprocess.run(["tmux", "refresh-client", "-S"])


def loop(metrics):
    print(metrics)
    curr_id = None
    while True:
        curr_id, status = plot(metrics, curr_id)
        set_new_status('|'.join(status))


if __name__ == '__main__':
    start_data_collection()
    loop(sys.argv[1:])
