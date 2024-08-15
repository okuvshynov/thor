import plistlib
import subprocess
import threading

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Configuration
W_CHART = 8  # Maximum number of measurements to store

# Global variables
measurements = {'gpu': [], 'ecpu': [], 'pcpu': [], 'wired': [], 'rss': []}
lock = threading.Lock()  # Lock to synchronize access to measurements
title = {'gpu': 'G:', 'ecpu': 'E:', 'pcpu': 'P:', 'wired': 'W:', 'rss': 'R:'}

def init_mem():
    page_size_out = subprocess.check_output(['pagesize']).decode('utf-8')
    page_size = int(page_size_out.strip())
    mem_size_out = subprocess.check_output(['sysctl', 'hw.memsize']).decode('utf-8')
    mem_size = int(mem_size_out.split(':')[-1].strip())
    return page_size, mem_size

page_size, mem_size = init_mem()

def get_vm_stat():
    """
    Call vm_stat and parse its output to return active and wired memory in bytes.
    """
    # Call vm_stat and capture its output
    output = subprocess.check_output(['vm_stat']).decode('utf-8')

    # Split the output into lines
    lines = output.split('\n')

    # Initialize variables to store active and wired memory
    active_pages = 0
    wired_pages = 0

    # Iterate over the lines to find the active and wired memory
    for line in lines:
        if 'Pages active:' in line:
            active_pages = int(line.split(':')[-1].strip().rstrip('.'))
        elif 'Pages wired down:' in line:
            wired_pages = int(line.split(':')[-1].strip().rstrip('.'))

    # Calculate active and wired memory in bytes
    active = 1.0 * active_pages * page_size / mem_size
    wired = 1.0 * wired_pages * page_size / mem_size

    return active + wired, wired

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
            print(out[-1])
    padding_length = W_CHART - len(values)
    if padding_length > 0:
        padding = [' '] * padding_length
        out = padding + out
    if len(values) == 0:
        out.append(" n/a")
    return f"{title[metric]}" + "".join(out)

def collect_data():
    # Start powermetrics process without -n qualifier
    process = subprocess.Popen(['sudo', 'powermetrics', '-i', '1000', '-f', 'plist', '-s', 'gpu_power,cpu_power'], stdout=subprocess.PIPE)

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

        parsed_data['rss'], parsed_data['wired'] = get_vm_stat()
        # Append parsed data to measurements list
        with lock:
            for k, v in parsed_data.items():
                measurements[k].append(v)
                if len(measurements[k]) > W_CHART:
                    measurements[k].pop(0)


def parse_powermetrics_data(data):
    res = {'gpu': 1.0 - data['gpu']['idle_ratio']}
    ecpu_idle = 0.0
    ecpu_n_cpus = 0
    pcpu_idle = 0.0
    pcpu_n_cpus = 0

    for cluster in data['processor']['clusters']:
        n_cpus = len(cluster['cpus'])
        idle   = 0.0
        for cpu in cluster['cpus']:
            idle += cpu['idle_ratio']

        if cluster['name'].startswith('E'):
            ecpu_idle += idle
            ecpu_n_cpus += n_cpus
        elif cluster['name'].startswith('P'):
            pcpu_idle += idle
            pcpu_n_cpus += n_cpus

    if ecpu_n_cpus > 0:
        res['ecpu'] = 1.0 - ecpu_idle / ecpu_n_cpus
    if pcpu_n_cpus > 0:
        res['pcpu'] = 1.0 - pcpu_idle / pcpu_n_cpus

    return res


# Start data collection in a separate thread
def start_data_collection():
    thread = threading.Thread(target=collect_data)
    thread.daemon = True  # Set as daemon thread so it exits when main thread exits
    thread.start()

# HTTP request handler
class PowerMetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)

        metrics = query_params.get('metric', [])
        if not metrics:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"No metrics specified")
            return

        results = []
        for metric in metrics:
            if metric not in measurements:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(f"Metric {metric} not found".encode())
                return
            with lock:
                data = measurements[metric][:]
            results.append(plot_bar_chart(data, metric))
        self.send_response(200)
        self.end_headers()
        self.wfile.write('|'.join(results).encode())

# Start HTTP server
def start_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, PowerMetricsHandler)
    print('Starting httpd on port 8000...')
    httpd.serve_forever()

if __name__ == '__main__':
    start_data_collection()
    start_server()
