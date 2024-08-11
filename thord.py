import json
import subprocess
import plistlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import time

# Configuration
W_CHART = 15  # Maximum number of measurements to store

# Global variables
measurements = []  # List to store measurements
lock = threading.Lock()  # Lock to synchronize access to measurements

def gen_blocks():
    # shades of green
    colors = [231, 157, 40, 28]
    blocks = [' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
    result = []

    for i in range(len(colors) - 1):
        color1, color2 = colors[i], colors[i + 1]
        for block in blocks:
            result.append(f"#[fg=colour{color2},bg=colour{color1}]{block}")

    return result

def plot_bar_chart(values):
    blocks = gen_blocks()

    out = []

    for value in values:
        if value < 0 or value > 1:
            raise ValueError("Value must be in range 0...1")

        block_index = int(value * len(blocks))
        block = blocks[min(block_index, len(blocks) - 1)]
        out.append(block)
    return "G:" + "".join(out)

def collect_data():
    # Start powermetrics process without -n qualifier
    process = subprocess.Popen(['sudo', 'powermetrics', '-i', '500', '-f', 'plist', '-s', 'gpu_power'], stdout=subprocess.PIPE)

    buffer = b''
    while True:
        # Read from process output until we receive '</plist>'
        while True:
            chunk = process.stdout.read(128)
            if not chunk:
                break
            buffer += chunk
            plist_end_pos = buffer.find(b'</plist>')
            if plist_end_pos != -1:
                break

        # Parse plist output and extract relevant data
        plist_data = buffer[:plist_end_pos + len(b'</plist>')]
        data = plistlib.loads(plist_data.strip(b'\n\x00'))
        parsed_data = parse_powermetrics_data(data)

        # Remove the parsed plist data from the buffer
        buffer = buffer[plist_end_pos + len(b'</plist>'):]

        # Append parsed data to measurements list
        with lock:
            measurements.append(parsed_data)
            if len(measurements) > W_CHART:
                measurements.pop(0)

def parse_powermetrics_data(data):
    return 1.0 - data['gpu']['idle_ratio']

# Start data collection in a separate thread
def start_data_collection():
    thread = threading.Thread(target=collect_data)
    thread.daemon = True  # Set as daemon thread so it exits when main thread exits
    thread.start()

# HTTP request handler
class PowerMetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        with lock:
            data = measurements[:]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(plot_bar_chart(data).encode())

# Start HTTP server
def start_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, PowerMetricsHandler)
    print('Starting httpd on port 8000...')
    httpd.serve_forever()

if __name__ == '__main__':
    start_data_collection()
    start_server()
