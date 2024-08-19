from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from urllib.parse import urlparse, parse_qs

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
