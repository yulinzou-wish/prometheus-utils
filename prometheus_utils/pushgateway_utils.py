""" prometheus pusgateway utils
This module wrappered prometheus four kinds of metric types: Counter,
Gauge, Histogram and Summary. And delegate the push metrics to pushgateway
function. Base on prometheus_client version 0.7.1
"""

import os
import sys
import json
import time
import hashlib
import logging
import threading
import functools
import dill as pickle
from redis import Redis, ConnectionPool
from tornado import gen
from tornado.options import options
from tornado.web import Application
from . import prometheus_client
from .prometheus_client import CollectorRegistry

DOMAIN_SUFFIX = lambda env: '{}bjs.i.wish.com'.format('.' if 'prod' in env else '.stage.')
DEFAULT_PUSHGW = lambda x: 'pushgateway{}'.format( DOMAIN_SUFFIX(x) )
DEFAULT_REDIS = lambda x: Redis(
                    connection_pool=ConnectionPool.from_url(
                        'redis://pushgw-cache{}:6379/0'.format( DOMAIN_SUFFIX(x) )
                    )
                )

DEFAULT_REGISTRY = CollectorRegistry()
DEFAULT_BUCKETS = [0.01, 0.025, 0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.25, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 5, float("inf")]

class PromClient(object):
    """
    Integrate prometheus metrics pushing to pushgateway
    """
    _instance = None
    _pushgw_addr = None
    _pushgw_cache = None

    @classmethod
    def instance(cls):
        return cls._instance

    @classmethod
    def pushgw_addr(cls):
        return cls._pushgw_addr

    @classmethod
    def pushgw_cache(cls):
        return cls._pushgw_cache

    @classmethod
    def init_instance(cls, env=None):
        _env = options.env if 'env' in options else str(env)
        cls._instance = cls()
        cls._pushgw_cache = DEFAULT_REDIS(_env)
        cls._pushgw_addr = DEFAULT_PUSHGW(_env)

    @gen.coroutine
    def push_gateway(self, job, registry=DEFAULT_REGISTRY, grp_key=None, method='push_to_gateway'):
        """ Wrappered prometheus_client  push to gateway """
        getattr(prometheus_client, method)(self._pushgw_addr, job=job, registry=registry, grouping_key=grp_key)


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
            logging.debug('{}({}) {} {}'.format(cls.name, cls.type, f.__name__, args[0]))

            # Since Pushgateway not support aggergation,
            # need to cache the metric registry.
            PromClient.pushgw_cache().set(cls.job, pickle.dumps(cls.registry))

            PromClient.instance().push_gateway(job=cls.job, registry=cls.registry, grp_key=None)
        return wrapper_f


class MetricWrapper(object):
    """ Wrapper prometheus Counter, Gauge, Summary and Histogram """

    def __init__(self, metric_type, metric_name, label_dict={}):
        # assert metric_type in ('Counter', 'Gauge', 'Summary', 'Histogram')
        # assert isinstance(metric_name, str)
        # assert isinstance(label_dict, dict)

        # Add timer suffix for histogram and summary
        if metric_type in ['Histogram', 'Summary'] and not metric_name.endswith('timer'):
            metric_name += '_timer'

        self.type = metric_type
        self.name = metric_name

        # doc is mandatory for prometheus metric init
        self.doc = label_dict.pop('doc', 'doc')
        self.label_dict = label_dict

        # job is mandatory for push gateway api
        #  - for gague/count, set job as default *Mon class name
        #  - for histogram/summary(timer), set job as metric_name
        _search_key = self.name
        if self.type in ['Histogram', 'Summary']:
            _search_key = self.name+'_created'

        self.job = '%s{%s}' % (self.name, ','.join(label_dict.keys()))
        self.label_dict.update({'job': self.job})

        self.label_names = list(label_dict.keys())
        self.label_values = tuple(label_dict.values())

        self.registry = CollectorRegistry() if PromClient.pushgw_cache().get(self.job)==None \
                             else pickle.loads(PromClient.pushgw_cache().get(self.job))

        self.metric_instance = self.registry._names_to_collectors.get(_search_key) \
                               or getattr(prometheus_client, metric_type)(
                                      self.name,
                                      self.doc,
                                      self.label_names,
                                      registry=self.registry
                                  )


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
