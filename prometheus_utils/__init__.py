""" Use PromClient to init the pushgateway utils
and derive from Mon to delegate the inc/set/observe
as metrics pushing
"""

import inspect
from functools import partial
from tornado import gen
from .pushgateway_utils import PromClient, Gauge, Histogram

__all__ = ['PromClient', 'Mon']


class Mon(object):
    """ Base class for prometheus monitoring"""
    metric_name_ext = ''
    label_dict_ext = {}

    @classmethod
    def _get_lst(cls):
        cls_lst = inspect.getmro(cls)
        f = lambda _: map( lambda x:getattr(x, _), filter(lambda y:hasattr(y, _), cls_lst) )[::-1]
        return ( f('metric_name_ext'), f('label_dict_ext') )

    @classmethod
    def _bld_metric(cls, metric_type, name_ext, dict_ext):
        assert metric_type in (Gauge, Histogram)
        assert isinstance(name_ext, str)
        assert isinstance(dict_ext, dict)

        # Avoid duplicate metric name extend with direct parents
        if cls.metric_name_ext in (x.metric_name_ext for x in cls.__bases__ if hasattr(x, 'metric_name_ext')):
            cls.metric_name_ext = cls.__name__.rstrip('Mon')

        (metric_name_lst, label_dict_lst) = cls._get_lst()

        metric_name = reduce(lambda a,b: '{}_{}'.format(a,b), filter(lambda x: x!='', metric_name_lst))
        label_dict = reduce(lambda a,b: dict(a, **b), filter(lambda x: x!={}, label_dict_lst))

        # Append name_ext if given in argument and not ''
        if name_ext != '':
            metric_name += '_{}'.format(name_ext)

        # Append dict_ext if given in argument and not {}
        if dict_ext != None:
            label_dict.update(dict_ext)

        # Set default 'job' value as class name
        label_dict.update({'job': cls.__name__})

        return metric_type(metric_name, label_dict)


    @classmethod
#    @gen.coroutine
    def inc(cls, metric_name_ext='', label_dict_ext={}, incr_by=1):
        """ inc count value by using Gauge.inc(...) """
        _metric = cls._bld_metric(Gauge, metric_name_ext, label_dict_ext)
        if incr_by > 0:
            _metric.inc(incr_by)
        else:
            _metric.dec(incr_by)

    @classmethod
    @gen.coroutine
    def set(cls, metric_name_ext='', label_dict_ext={}, value=0):
        """ set count value by using Gauge.set(...) """
        cls._bld_metric(Gauge, metric_name_ext, label_dict_ext).set(value)

    @classmethod
    @gen.coroutine
    def val(cls, metric_name_ext='', label_dict_ext={}, time=0.0):
        """ push time value by using Histogram.observe(...) """
        cls._bld_metric(Histogram, metric_name_ext, label_dict_ext).observe(time)
