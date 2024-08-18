import plistlib
import subprocess


def init_mem():
    page_size_out = subprocess.check_output(['pagesize'])
    page_size = int(page_size_out.decode('utf-8').strip())
    mem_size_out = subprocess.check_output(['sysctl', 'hw.memsize'])
    mem_size = int(mem_size_out.decode('utf-8').split(':')[-1].strip())
    return page_size, mem_size


page_size, mem_size = init_mem()


def get_vm_stat():
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
    active = 1.0 * active_pages * page_size / mem_size
    wired = 1.0 * wired_pages * page_size / mem_size

    return active + wired, wired


def parse_powermetrics_data(data):
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


def collect_data(measurements):
    # Start powermetrics process without -n qualifier
    process = subprocess.Popen(
        [
            'sudo', 'powermetrics',
            '-i', '1000',
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
        parsed_data = parse_powermetrics_data(data)

        # Remove the parsed plist data from the buffer
        buffer = buffer[plist_end_pos + len(b'</plist>'):]

        parsed_data['rss'], parsed_data['wired'] = get_vm_stat()
        measurements.append(parsed_data)