import unittest
import random

from prometheus_utils import PromClient, Gauge, Histogram

class TestPushGWClient(unittest.TestCase):
    def setUp(self):
        PromClient.init_instance(env='stage')


    def test_gauge(self):
        # push gauge samples
        Gauge('metric_name', {'lab1': 'x1', 'lab2': 'x2', 'job': 'gx12'}).inc()
        Gauge('metric_name', {'lab1': 'y1', 'lab2': 'y2', 'job': 'gy12'}).inc(11)
        Gauge('metric_name_A', {'lab1': 'x1', 'lab2': 'x2', 'job': 'job1122'}).inc(14.6)

        # no job
        Gauge('metric_name', {'lab1': 'z1', 'lab2': 'z2'}).inc(22)

        # no labels
        Gauge('metric_name').inc(33)

        # dec
        Gauge('metric_name_B', {'lab1': 'y11', 'lab2': 'y22', 'job': 'job1122'}).dec(3.2)
        Gauge('metric_name_B', {'lab1': 'y22', 'lab2': 'y33', 'job': 'job1122'}).dec(4.3)

        # set
        Gauge('metric_name_C', {'lab1': 'z1', 'lab2': 'z2'}).set(1234)


    def test_histogram(self):
        # push histogram samples

        v = random.randrange(100)/15.0
        Histogram('test_of_histogram', {'h1_lab1': 'h1_v1', 'h1_lab2': 'h1_v2', 'job': 'h11'}).observe(v)

        v = random.randrange(100)/25.0
        Histogram('test_of_histogram', {'h2_lab1': 'h2_v1', 'h2_lab2': 'h2_v2', 'job': 'h11'}).observe(v)

        # same metric_name with Gauge
        v = random.randrange(100)/35.0
        Histogram('metric_name_A', {'h2_lab1': 'h2_v1', 'h2_lab2': 'h2_v2', 'job': 'h11'}).observe(v)

        # no job
        v = random.randrange(100)/55.0
        Histogram('metric_name_A', {'h2_lab1': 'h2_v1', 'h2_lab2': 'h2_v2'}).observe(v)
        Histogram('metric_name_B', {'h2_lab1': 'h2_v1', 'h2_lab2': 'h2_v2'}).observe(v)

        # custom buckets
        bkts = [0.01, 0.025, 0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.25, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 5]
        v = random.randrange(100)/75.0
        Histogram('test_of_histogram', {'h2_lab1': 'h2_v1', 'h2_lab2': 'h2_v2', 'job': 'h22', 'buckets': bkts}).observe(v)


if __name__ == '__main__':
    unittest.main()
