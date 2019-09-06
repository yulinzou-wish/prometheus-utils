""" prometheus pusgateway utils """
from functools import partial
from pushgateway_utils import PromClient, MetricWrapper

__all__ = ['PromClient', 'Counter', 'Gauge', 'Summary', 'Histogram']

# pylint: disable=C0103
Counter = partial(MetricWrapper, 'Counter')
Gauge = partial(MetricWrapper, 'Gauge')
Histogram = partial(MetricWrapper, 'Histogram')
Summary = partial(MetricWrapper, 'Summary')

