### Prometheus utils
Provide Prometheus metrics wrapper and pushgateway utils
Integrated with prometheus_client version 0.7.1

#### Getting Started

- Init Wrappered Prometheus Client instance globally:

```
from prometheus_utils import PromClient
PromClient.init_instance(env=tornado.options.env)
```

- Define monitoring classes (*Mon)

Import and inherite the base `Mon` class, derive per your needs. Speicify the metric name extend and label dict extends which will be automatically append to the super class relevant attributes.

```
from prometheus_utils import Mon

class BaseAppMon(Mon):
    metric_name_ext = 'base'
    label_dict_ext = {'app': 'base_app'}

class ABCMon(BaseMon):
    metric_name_ext = 'abc'
    label_dict_ext = {'module': 'abc'}
```

For `BaseAppMon` the metric name and label dict will be same as set since its supper class Mon defined empty relevant attributes.
For `ABCMon`, as expected, the metric name will be 'base_abc', and label dict is `{'app': 'base_app', 'module': 'abc'}`

- Issue the metrics via defined `*Mon` classes
  There are 3 methods provided with `Mon` class, to help exposing the metrics.
  All the 3 method

    - **inc** - `inc(metric_name_ext='', label_dict_ext={}, incr_by=1)`
    Will increase/decrease metric's count with given increasing number(default value is 1), if the given numer below zero, will do decreasing.
    e.g.

    ```
       # increasing the default metric with default value 1
       ABCMon.inc()

       # extend the metric name and label dict
       ABCMon.inc('metric_name', {'label_key':'label_val'})

       # specified increasing value
       ABCMon.inc(incr_by=100)

       # decreasing
       ABCMon.inc(incr_by=-123)
    ```

    - **set**  - `set(metric_name_ext='', label_dict_ext={}, value=0)`
    Will reset the value for given metric.
    e.g.

    ```
       # Reset the metric count to 0
       ABCMon.set()

       # extend the metric name and label dict
       ABCMon.set('metric_name', {'label_key':'label_val'}, value=1234)

       # specify the set value
       ABCMon.set(value=1234)
    ```

    > Note: The default value for **set** is **0**.


    - **val**   - `val(metric_name_ext='', label_dict_ext={}, time=0.0)`
    This method designed for issue the timer value
    e.g.

    ```
       # issue the default metric timer as default value 0.0
       ABCMon.val()

       # extend the metric name and label dict
       ABCMon.val('metric_name',{'label_key':'label_val'}, time=1234.4321)

       # specified the val time
       ABCMon.val(time=1234.4321)
    ```

    > Note: The default value for **val** is **0.0**.
