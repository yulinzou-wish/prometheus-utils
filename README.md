# BJS Prometheus PushGateway utils
Provide the Promethtues metrics monitoring APIs to push metrics to Prometheus PushGateway.

#### - Init Wrappered Prometheus Client instance
```
from prometheus_utils import PromClient
PromClient.init_instance(env='stage')
```

#### Counter
```
# Counter(metric_name, label_dict).inc(value)
Counter('counter_metric', {'c1_lab1': 'c1_v1', 'c1_lab2': 'c1_v2', 'job': 'jc1'}).inc()
```

#### Gauge
```
# Gauge(metric_name, label_dict).inc(value)
Gauge('gauge_metric', {'g1_lab1': 'g1_v1', 'g1_lab2': 'g1_v2', 'job': 'jg1'}).inc()

# Gauge(metric_name, label_dict).dec(value)
Gauge('gauge_metric', {'g1_lab1': 'g1_v1', 'g1_lab2': 'g1_v2', 'job': 'jg1'}).dec()

# Gauge(metric_name, label_dict).set(value)
Gauge('gauge_metric', {'g1_lab1': 'g1_v1', 'g1_lab2': 'g1_v2', 'job': 'jg1'}).set(3.6)
```

#### Histogram
```
# Default buckets
Histogram('histogram_metric1', {'h1_lab1': 'h1_v1', 'h1_lab2': 'h1_v2', 'job': 'jh1'}).observe(1.2)

# Custom buckets
bkts = [0.01, 0.025, 0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.25, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 5]
Histogram('histogram_metric2', {'h2_lab1': 'h2_v1', 'h2_lab2': 'h2_v2', 'job': 'jh2', 'buckets': bkts}).observe(2.3)
```

#### Summary
```
Summary('summary_metric', {'s1_lab1': 's1_v1', 's1_lab2': 's1_v2', 'job': 'js1'}).observe(1.23)
```
