import os
import sys
import json
import inspect
import random
import time
import threading
import functools
import logging
from __test__.models import BaseMon, ABCMon, XYZMon, ApiMon
from prometheus_utils import Gauge, Histogram
from string import ascii_letters as letters

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
test_logger = logging.getLogger('test_logger')

class TestMon(BaseMon):
    metric_name_ext = "TestMon"
    label_dict_ext = {'label_test': 'value_test'}

class TestABCMon(ABCMon, TestMon):
    pass

class TestXYZMon(XYZMon, TestMon):
    pass

class TestApiMon(ApiMon, TestMon):
    pass


def threaded(thread_num):
    def wrapper(f):
        @functools.wraps(f)
        def wrap_f(*a, **kw):
            ths = []
            for i in xrange(thread_num):
                th = threading.Thread(target=f, args=a, kwargs=kw)
                ths.append(th)
                th.start()
                logging.debug("Test thread '{}-{}' started".format(a[0].__name__, i))
            for th in ths:
                th.join()
            return ths
        return wrap_f
    return wrapper


@threaded(random.randint(1,100))
def test_benchmark(_tcls):
    """ Test for benchmark """
    logging.debug(test_benchmark.__doc__)

    for i in xrange(random.randint(1,10)):

       import itertools
       for x in map(''.join, itertools.product(letters[:3], repeat=2)):
           rand_int = random.randint(1,1234567890)
           rand_float = random.random()

           _tcls.inc(x, {'a':'inc11'})
           _tcls.inc(x, {'a':'inc11', 'b':'22'})
           _tcls.inc(x, {'a':'inc22', 'b':'11'}, rand_int)

           _tcls.val(x, {'a':'123'}, rand_float)
           _tcls.val(x, {'a':'321'})
           _tcls.val(x, {'a':'123', 'b':'321'}, rand_float)

           _tcls.set(x, {'a':'set11', 'b':'22'}, rand_int)
           _tcls.set(x, {'a':'set22', 'b':'11'}, rand_int)


def test_functionality(_tcls):
    """ Test for functionnality """
    logging.debug(test_benchmark.__doc__)

    _tcls.inc(incr_by=random.random())
    _tcls.set(value=random.random())
    _tcls.val(time=random.random())

    for x in ('inc', 'set', 'val'):
        f = getattr(_tcls, x)

        f()
        f("metric_name_only")
        f(label_dict_ext={"metric_name_less": ""})

        f("name_ext", {'test_label': 'test_1'})
        f("name_ext", {'test_label': 'test_2', 'job': ''})
        f("name_ext", {'test_label': 'test_3', 'job': 'test_job'})


class TestHandler(object):
    def prepare(self):
        pass

    def test(self):
        mod = __import__(os.path.splitext(os.path.basename(__file__))[0])
        testmon_clss = filter(lambda x: x[1].__name__.startswith('Test') \
                                    and x[1].__name__.endswith('Mon'),   \
                                 inspect.getmembers(mod, inspect.isclass))

        from multiprocessing import Process, Pool
        pl = Pool(processes=4)
        for (name, tcls) in list(testmon_clss):
            pl.apply_async(test_functionality, (tcls,))
            pl.apply_async(test_benchmark, (tcls,))
        pl.close()
        pl.join()
        logging.debug('Test done.')

