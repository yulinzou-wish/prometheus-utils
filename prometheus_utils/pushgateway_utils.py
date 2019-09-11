""" prometheus pusgateway utils
This module wrappered prometheus four kinds of metric types: Counter,
Gauge, Histogram and Summary. And delegate the push metrics to pushgateway
function. Base on prometheus_client version 0.7.1
"""

import os
import sys
import json
import hashlib
import logging
import functools
from tornado.options import options
from . import prometheus_client
from .prometheus_client import CollectorRegistry

DEFAULT_PUSHGW_HOST = 'pushgateway{}bjs.i.wish.com'
DEFAULT_PUSHGW_PORT = "9091"

DEFAULT_REGISTRY = CollectorRegistry()
DEFAULT_BUCKETS = [0.01, 0.025, 0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.25, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 5, float("inf")]

class PromClient(object):
    """
    Integrate prometheus metrics pushing to pushgateway
    """
    _instance = None

    @classmethod
    def instance(cls):
        return cls._instance

    @classmethod
    def init_instance(cls, env=None):
        cls._instance = cls(env)

    def __init__(self, env=None):
        _env = options.env if 'env' in options else env
        self.pushgw_addr = DEFAULT_PUSHGW_HOST.format('.' if 'prod' in str(_env) else '.stage.')

    def push_gateway(self, job, registry=DEFAULT_REGISTRY, grouping_key=None, method='push_to_gateway'):
        """ Wrappered prometheus_client  push to gateway """
        try:
            getattr(prometheus_client, method)(self.pushgw_addr, job=job, registry=registry, grouping_key=grouping_key)
        except:
            logging.exception("Exception occurred when calling %s", method)


class PushWrapper(object):
    def __init__(self, metric_types=None):
        self.metric_types = metric_types

    def __call__(self, f, *args, **kwargs):
        @functools.wraps(f)
        def wrapper_f (cls, *args, **kwargs):
            if cls.type not in self.metric_types:
                logging.error("'%s' just available for %s", f.__name__, self.metric_types)
                return
            f(self, *args, **kwargs)
            getattr(cls.metric_instance.labels(*cls.label_values), f.__name__)(*args, **kwargs)
            PromClient.instance().push_gateway(job=cls.job, registry=cls.registry, grouping_key=cls.label_dict)
        return wrapper_f

class MetricWrapper(object):
    """ Wrapper prometheus Counter, Gauge, Summary and Histogram """
    registry_set = {}

    def __init__(self, metric_type, metric_name, label_dict={}):
        assert metric_type in ('Counter', 'Gauge', 'Summary', 'Histogram')
        assert isinstance(metric_name, str)
        assert isinstance(label_dict, dict)

        # Add timer suffix for histogram and summary
        if metric_type in ['Histogram', 'Summary'] and not metric_name.endswith('timer'):
            metric_name += '_timer'

        self.type = metric_type
        self.name = metric_name

        # job is mandatory for push gateway api
        # doc is mandatory for prometheus metric init
        self.doc = label_dict.pop('doc', 'doc')
        self.job = label_dict.get('job', 'job')

        label_dict.update({self.job: self.job})

        # Prometheus Pushgatewy officially not support metrics aggregation
        # and it just distinguish the metrics by grouping_key.
        # so set metric_name{label_dict} as grp key to avoid overwrite.
        self.label_dict = label_dict
        _signature = "{}{}".format(self.name, json.dumps(self.label_dict))
        _reg_key = hashlib.sha1(_signature).hexdigest()
        self.label_dict.update({'_gid': _reg_key})

        self.label_names = list(label_dict.keys())
        self.label_values = tuple(label_dict.values())

        _reg_dct = self.registry_set.get(_reg_key, {'r': None, 'm': None })

        if _reg_dct['r'] == None:
            _reg_dct['r'] = CollectorRegistry()
        self.registry = _reg_dct['r']

        if _reg_dct['m'] == None:
            _reg_dct['m'] = getattr(prometheus_client, metric_type)(
                self.name,
                self.doc,
                self.label_names,
                registry=self.registry
            )
        self.metric_instance = _reg_dct['m']

        # Since Pushgateway not support aggergation, need to cache 
        # the metric registry in client side.
        # Todo: use redis replace the in-memory registry_set
        self.registry_set[_reg_key] = _reg_dct


    @PushWrapper(metric_types=['Counter', 'Gauge'])
    def inc(self, inc_by=1):
        """ Wrapper inc method for Counter and Gauge """
        pass

    @PushWrapper(metric_types=['Gauge'])
    def dec(self, dec_by=1):
        """ Wrapper dec method for Gauge """
        pass

    @PushWrapper(metric_types=['Gauge'])
    def set(self, value):
        """ Wrapper set method for Gauge """
        pass

    @PushWrapper(metric_types=['Histogram', 'Summary'])
    def observe(self, amount):
        """ Wrapper observe method for Histogram and Summary """
        pass


Counter = functools.partial(MetricWrapper, 'Counter')
Gauge = functools.partial(MetricWrapper, 'Gauge')
Histogram = functools.partial(MetricWrapper, 'Histogram')
Summary = functools.partial(MetricWrapper, 'Summary')
