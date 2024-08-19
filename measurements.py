import threading
import secrets
import string

from collections import defaultdict


def generate_random_id(length=8):
    """Generate a random alphanumeric ID of a specified length."""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


class Measurements:
    def __init__(self, width=8):
        self.data = defaultdict(list)
        self.last_id = None
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.width = width

    def append(self, slice):
        with self.condition:
            for k, v in slice.items():
                self.data[k].append(v)
                if len(self.data[k]) > self.width:
                    self.data[k].pop(0)
            self.last_id = generate_random_id()
            self.condition.notify_all()

    def get(self):
        with self.lock:
            return {k: v[:] for k, v in self.data.items()}

    def wait(self, id):
        with self.condition:
            while self.last_id == id:
                self.condition.wait()  # Wait until the condition is notified
            return self.last_id, {k: v[:] for k, v in self.data.items()}
