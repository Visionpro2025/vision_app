from prometheus_client import Counter, Histogram

REQUESTS = Counter('vision_requests_total', 'Requests total', ['endpoint'])
LATENCY = Histogram('vision_latency_seconds', 'Latency seconds', ['endpoint'])

from contextlib import contextmanager
import time

@contextmanager
def observe(endpoint: str):
    REQUESTS.labels(endpoint).inc()
    start = time.time()
    try:
        yield
    finally:
        LATENCY.labels(endpoint).observe(time.time()-start)

