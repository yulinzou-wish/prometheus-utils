import inspect
from functools import partial
from tornado import gen
from pushgateway_utils import PromClient, Gauge, Histogram

__all__ = ['PromClient', 'Mon']

class MetaMon(type):
    def __new__(cls, name, bases, namespace):
        namespace.update({
            '_metric_name': MetaMon._metric_name,
            '_label_dict': MetaMon._label_dict
        })
        return super(MetaMon, cls).__new__(cls, name, bases, namespace)

    @property
    def _metric_name(cls):
        if not inspect.isclass(cls):
            cls = type(cls)
        return cls.metric_name

    @_metric_name.setter
    def _metric_name(cls, _name):
        if not inspect.isclass(cls):
            cls = type(cls)
        cls.metric_name = _name

    @property
    def _label_dict(cls):
        if not inspect.isclass(cls):
            cls = type(cls)
        return cls.label_dict

    @_label_dict.setter
    def _label_dict(cls, _dict):
        if not inspect.isclass(cls):
            cls = type(cls)
        cls.label_dict= _dict

class Mon(object):
    __metaclass__ = MetaMon

    metric_name = ''
    label_dict = {}

    @classmethod
    def _get_cls_lst(cls):
        return filter(lambda x:x.__class__ is not type, inspect.getmro(cls))

    @classmethod
    def _bld_metric_name(cls, name):
        name_lst = [name] + [x.metric_name for x in cls._get_cls_lst() if x.metric_name!='']
        return '_'.join( name_lst[::-1] )

    @classmethod
    def _bld_label_dict(cls, dct):
        dct_lst = (x.label_dict for x in cls._get_cls_lst() if x.label_dict!={})
        return dict(reduce(lambda x,y: dict(x,**y), dct_lst), **dct)

    @classmethod
    def _bld_metric(cls, metric_type, name, dct):
        return metric_type(cls._bld_metric_name(name), cls._bld_label_dict(dct))

    @classmethod
    @gen.coroutine
    def inc(cls, metric_name='', label_dict={}, incr_by=1):
        _metric = cls._bld_metric(Gauge, metric_name, label_dict)
        if incr_by > 0:
            _metric.inc(incr_by)
        else:
            _metric.dec(incr_by)

    @classmethod
    @gen.coroutine
    def set(cls, metric_name='', label_dict={}, value=0):
        cls._bld_metric(Gauge, metric_name, label_dict).set(value)

    @classmethod
    @gen.coroutine
    def val(cls, metric_name='', label_dict={}, time=0.0):
        cls._bld_metric(Histogram, metric_name, label_dict).observe(time)
