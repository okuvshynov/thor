from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from urllib.parse import urlparse, parse_qs

from macos_reader import MacOSReader
from measurements import Measurements


W_CHART = 8  # Maximum number of measurements to store
measurements = Measurements(W_CHART)
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


def start_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, PowerMetricsHandler)
    httpd.serve_forever()


if __name__ == '__main__':
    start_data_collection()
    start_server()
