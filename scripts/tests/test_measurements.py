import unittest
import threading
import time

from ..lib.measurements import Measurements, generate_random_id


class TestGenerateRandomID(unittest.TestCase):
    def test_length(self):
        length = 10
        generated_id = generate_random_id(length)
        self.assertEqual(len(generated_id), length)

    def test_uniqueness(self):
        length = 8
        id1 = generate_random_id(length)
        id2 = generate_random_id(length)
        self.assertNotEqual(id1, id2)


class TestMeasurements(unittest.TestCase):
    def test_append(self):
        measurements = Measurements(width=8)
        d = {'gpu': 1, 'ecpu': 2, 'pcpu': 3, 'wired': 4, 'rss': 5}
        measurements.append(d)
        expected = {k: [v] for k, v in d.items()}
        self.assertEqual(measurements.get(), expected)

    def test_width(self):
        measurements = Measurements(width=2)
        d1 = {'gpu': 1, 'ecpu': 2, 'pcpu': 3, 'wired': 4, 'rss': 5}
        d2 = {'gpu': 6, 'ecpu': 7, 'pcpu': 8, 'wired': 9, 'rss': 10}
        d3 = {'gpu': 11, 'ecpu': 12, 'pcpu': 13, 'wired': 14, 'rss': 15}
        measurements.append(d1)
        measurements.append(d2)
        measurements.append(d3)
        d = zip(d2.items(), d3.items())
        expected = {k2: [v2, v3] for (k2, v2), (k3, v3) in d}
        self.assertEqual(measurements.get(), expected)

    def test_wait(self):
        measurements = Measurements(width=8)
        d1 = {'gpu': 1, 'ecpu': 2, 'pcpu': 3, 'wired': 4, 'rss': 5}

        def append_data():
            time.sleep(0.1)  # Simulate some delay
            measurements.append(d1)
        thread = threading.Thread(target=append_data)
        thread.start()
        initial_id = measurements.last_id
        start = time.time()
        new_id, data = measurements.wait(initial_id)
        duration = time.time() - start
        self.assertGreater(duration, 0.1)
        self.assertLess(duration, 1.0)
        self.assertNotEqual(initial_id, new_id)
        expected = {k: [v] for k, v in d1.items()}
        self.assertEqual(data, expected)
        thread.join()

    def test_multithreading(self):
        measurements = Measurements(width=8)
        d1 = {'gpu': 1, 'ecpu': 2, 'pcpu': 3, 'wired': 4, 'rss': 5}
        d2 = {'gpu': 6, 'ecpu': 7, 'pcpu': 8, 'wired': 9, 'rss': 10}

        def append_data(data):
            measurements.append(data)
        thread1 = threading.Thread(target=append_data, args=(d1,))
        thread2 = threading.Thread(target=append_data, args=(d2,))
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
        data = measurements.get()
        d = zip(d1.items(), d2.items())
        combined_data = {k1: [v1, v2] for (k1, v1), (k2, v2) in d}
        self.assertEqual(data, combined_data)


if __name__ == '__main__':
    unittest.main()
