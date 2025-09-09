from tenacity import retry, stop_after_attempt, wait_fixed
from config.settings import ORCH


def with_retry(fn):
    @retry(stop=stop_after_attempt(ORCH.max_retries), wait=wait_fixed(ORCH.backoff_sec))
    def wrapped(*a, **k):
        return fn(*a, **k)
    return wrapped

