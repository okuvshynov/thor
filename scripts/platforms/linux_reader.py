import time


METRICS = ['cpu', 'rss', 'swap']


class LinuxReader:
    def __init__(self, options={}):
        self.interval = options.get('interval_ms', 5000) / 1000.0
        self.total_memory = None

    def metrics(self):
        return METRICS

    def read_rss(self):
        if self.total_memory is None:
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.readlines()
                for line in meminfo:
                    if line.startswith('MemTotal:'):
                        self.total_memory = int(line.split()[1])
                        break

        # Read RSS usage from /proc/meminfo
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.readlines()
            rss = None
            for line in meminfo:
                if line.startswith('Active:'):
                    rss = int(line.split()[1])
                if line.startswith('SwapTotal:'):
                    swap_total = int(line.split()[1])
                if line.startswith('SwapFree:'):
                    swap_free = int(line.split()[1])

        if swap_total > 0:
            swap_usage = 1.0 - 1.0 * swap_free / swap_total
        else:
            swap_usage = 0.0
        # Both rss and total_memory are in KB
        return 1.0 * rss / self.total_memory, swap_usage

    def start(self, measurements):
        prev_idle = -1
        prev_total = -1
        while True:
            start = time.monotonic()
            with open('/proc/stat', 'r') as f:
                cpu_stats = f.readline().split()[1:]

            cpu_stats = [int(stat) for stat in cpu_stats]
            total = sum(cpu_stats)
            idle = cpu_stats[3]
            if prev_total >= 0:
                diff_idle = idle - prev_idle
                diff_total = total - prev_total

                diff_usage = diff_total - diff_idle
                usage = 1.0 * diff_usage / diff_total

                rss, swap = self.read_rss()

                measurements.append({'cpu': usage, 'rss': rss, 'swap': swap})

            prev_total = total
            prev_idle = idle

            duration = time.monotonic() - start
            to_sleep = self.interval - duration
            if to_sleep > 0:
                time.sleep(to_sleep)
