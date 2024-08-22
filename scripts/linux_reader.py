import time


METRICS = ['cpu']


class LinuxReader:
    def __init__(self, options):
        pass

    def metrics(self):
        return METRICS

    def start(self, measurements):
        prev_idle = -1
        prev_total = -1
        while True:
            with open('/proc/stat', 'r') as f:
                cpu_stats = f.readline().split()[1:]

            cpu_stats = [int(stat) for stat in cpu_stats]
            print(cpu_stats)
            total = sum(cpu_stats)
            idle = cpu_stats[3]
            if prev_total > 0:
                diff_idle = idle - prev_idle
                diff_total = total - prev_total

                diff_usage = diff_total - diff_idle
                usage = 1.0 * diff_usage / diff_total


                print(usage)
                measurements.append({'cpu': usage})

            prev_total = total
            prev_idle = idle

            time.sleep(1)
