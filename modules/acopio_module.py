# modules/acopio_module.py (añadir estas utilidades)
import hashlib
import re
from typing import List
from dateutil import tz
from config.settings import TZ, THRESH
from modules.schemas import NewsItem

URL_UTM_RE = re.compile(r"[?&](utm_[^=]+|gclid|fbclid)=[^&#]+")

def canonical_url(url: str) -> str:
    return URL_UTM_RE.sub("", url).rstrip("?&")

def news_hash(title: str, url: str) -> str:
    base = (title.strip().lower() + "|" + canonical_url(url)).encode("utf-8")
    return hashlib.sha256(base).hexdigest()

def dedupe_news(items: List[NewsItem]) -> List[NewsItem]:
    seen = set()
    out = []
    for it in items:
        h = news_hash(it.title, it.url)
        if h in seen:
            continue
        seen.add(h)
        out.append(it)
    return out

def to_usa(dt):
    return dt.astimezone(tz.gettz(TZ))

def acopio_masivo(fetch_batch_fn, target: int = THRESH.min_news, batch_size: int = 8, max_cycles: int = 20) -> List[NewsItem]:
    """
    fetch_batch_fn() debe devolver List[NewsItem] (8 por lote). Se itera hasta cubrir target.
    """
    pool: List[NewsItem] = []
    for _ in range(max_cycles):
        batch = fetch_batch_fn() or []
        # normalizar TZ
        for b in batch:
            b.published_at = to_usa(b.published_at)
        pool.extend(batch)
        pool = dedupe_news(pool)
        if len(pool) >= target:
            break
    return pool

