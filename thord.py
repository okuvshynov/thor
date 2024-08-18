import threading
import secrets
import string

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

from macos_reader import collect_data


def generate_random_id(length=8):
    """Generate a random alphanumeric ID of a specified length."""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


W_CHART = 8  # Maximum number of measurements to store


# Global variables
class Measurements:
    def __init__(self):
        self.data = {'gpu': [], 'ecpu': [], 'pcpu': [], 'wired': [], 'rss': []}
        self.last_id = None
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

    def append(self, slice):
        with self.condition:
            for k, v in slice.items():
                self.data[k].append(v)
                if len(self.data[k]) > W_CHART:
                    self.data[k].pop(0)
            self.last_id = generate_random_id()
            self.condition.notify_all()

    def get(self):
        with self.lock:
            return {k: v[:] for k, v in self.data.items()}

    def wait(self, id):
        with self.condition:
            while self.last_id == id:
                self.condition.wait()  # Wait until the condition is notified
            return self.last_id, {k: v[:] for k, v in self.data.items()}


measurements = Measurements()
title = {'gpu': 'G:', 'ecpu': 'E:', 'pcpu': 'P:', 'wired': 'W:', 'rss': 'R:'}


def gen_blocks():
    # shades of green
    colors = ['colour2', 'colour28', 'colour22', '#003000']
    blocks = [' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
    result = []

    for i in range(len(colors) - 1):
        color1, color2 = colors[i], colors[i + 1]
        for block in blocks:
            result.append(f"#[fg={color2},bg={color1}]{block}")

    return result


def plot_bar_chart(values, metric):
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
    padding_length = W_CHART - len(values)
    if padding_length > 0:
        padding = [' '] * padding_length
        out = padding + out
    if len(values) == 0:
        out.append(" n/a")
    return f"{title[metric]}" + "".join(out)


# Start data collection in a separate thread
def start_data_collection():
    thread = threading.Thread(target=collect_data, args=(measurements, ))
    thread.daemon = True
    thread.start()


def plot(metrics, last_id):
    new_id, data = measurements.wait(last_id)
    results = []
    for metric in metrics:
        if metric not in data:
            results.append(f"{metric} not found")
        else:
            results.append(plot_bar_chart(data[metric], metric))
    return new_id, results


# HTTP request handler
class PowerMetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)

        metrics = query_params.get('metric', [])
        last = query_params.get('last', [])
        last = last[0] if last else None
        if not metrics:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"No metrics specified")
            return

        new_id, results = plot(metrics, last)
        chart = '|'.join(results)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(f'{new_id}\n'.encode())
        self.wfile.write(f'{chart}\n'.encode())


# Start HTTP server
def start_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, PowerMetricsHandler)
    httpd.serve_forever()


if __name__ == '__main__':
    start_data_collection()
    start_server()
