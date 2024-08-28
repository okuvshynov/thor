import plistlib
import subprocess

METRICS = ['ecpu', 'pcpu', 'rss', 'wired', 'gpu']


class MacOSReader:
    def __init__(self, options):
        self.interval_ms = options.get('interval_ms', 1000)
        out = subprocess.check_output(['pagesize'])
        self.page_size = int(out.decode('utf-8').strip())
        out = subprocess.check_output(['sysctl', 'hw.memsize'])
        self.mem_size = int(out.decode('utf-8').split(':')[-1].strip())

    def metrics(self):
        return METRICS

    def get_vm_stat(self):
        """
        Call vm_stat and parse its output to return active and wired memory.
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
        active = 1.0 * active_pages * self.page_size / self.mem_size
        wired = 1.0 * wired_pages * self.page_size / self.mem_size

        return active + wired, wired

    def parse_powermetrics_data(self, data):
        res = {'gpu': 1.0 - data['gpu']['idle_ratio']}
        ecpu_idle = 0.0
        ecpu_n_cpus = 0
        pcpu_idle = 0.0
        pcpu_n_cpus = 0

        for cluster in data['processor']['clusters']:
            n_cpus = len(cluster['cpus'])
            idle = 0.0
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

    def start(self, measurements):
        # Start powermetrics process without -n qualifier
        process = subprocess.Popen(
            [
                'sudo', 'powermetrics',
                '-i', f'{self.interval_ms}',
                '-f', 'plist',
                '-s', 'gpu_power,cpu_power'
            ],
            stdout=subprocess.PIPE
        )

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
            parsed_data = self.parse_powermetrics_data(data)

            # Remove the parsed plist data from the buffer
            buffer = buffer[plist_end_pos + len(b'</plist>'):]

            parsed_data['rss'], parsed_data['wired'] = self.get_vm_stat()
            measurements.append(parsed_data)
