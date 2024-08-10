import json
import subprocess
import plistlib
from http.server import BaseHTTPRequestHandler, HTTPServer

# Call powermetrics tool and capture output
def get_powermetrics_data():
    output = subprocess.check_output(['sudo', 'powermetrics', '-n', '1', '-f', 'plist', '-s', 'gpu_power'])
    return plistlib.loads(output)

# Parse plist output and extract relevant data
def parse_powermetrics_data(data):
    return {'gpu_usage': 1.0 - data['gpu']['idle_ratio']}

# HTTP request handler
class PowerMetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        data = get_powermetrics_data()
        parsed_data = parse_powermetrics_data(data)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(parsed_data).encode())

# Start HTTP server
def start_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, PowerMetricsHandler)
    print('Starting httpd on port 8000...')
    httpd.serve_forever()

if __name__ == '__main__':
    start_server()

