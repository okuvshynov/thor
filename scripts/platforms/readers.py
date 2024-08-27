import sys


def create_reader(options={}):
    if sys.platform == "darwin":
        from .macos_reader import MacOSReader
        return MacOSReader(options)
    if sys.platform == "linux" or sys.platform == "linux2":
        from .linux_reader import LinuxReader
        return LinuxReader(options)
    raise ValueError(f"Unsupported platform: {sys.platform}")
