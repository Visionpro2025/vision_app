from __future__ import annotations
from typing import List
import re, hashlib
from datetime import datetime, timedelta
from dateutil import tz
from pydantic import BaseModel
from config.settings import DATA_QUALITY

UTM = re.compile(r"[?&](utm[^=]+|gclid|fbclid)=[^&#]+")

class NewsRecord(BaseModel):
    id: str
    title: str
    url: str
    published_at: datetime
    source: str
    category: str
    emotion: float

    def canonical_url(self) -> str:
        u = UTM.sub("", self.url).rstrip("?&") if DATA_QUALITY.dedupe_utm else self.url
        return u

    def hashkey(self) -> str:
        s = (self.title.strip().lower()+"|"+self.canonical_url()).encode("utf-8")
        return hashlib.sha256(s).hexdigest()


def normalize_tz(dt: datetime) -> datetime:
    tz_hav = tz.gettz(DATA_QUALITY.timezone)
    return dt.astimezone(tz_hav)


def dedupe(records: List[NewsRecord]) -> List[NewsRecord]:
    seen=set(); out=[]
    for r in records:
        h=r.hashkey()
        if h in seen: continue
        seen.add(h); out.append(r)
    return out


def enforce_freshness(records: List[NewsRecord]) -> List[NewsRecord]:
    if DATA_QUALITY.max_age_hours <= 0:
        return records
    cutoff = datetime.now(tz=tz.gettz(DATA_QUALITY.timezone)) - timedelta(hours=DATA_QUALITY.max_age_hours)
    return [r for r in records if normalize_tz(r.published_at) >= cutoff]


def validate_minimum(records: List[NewsRecord]):
    if len(records) < DATA_QUALITY.min_news:
        raise ValueError(f"Se requieren {DATA_QUALITY.min_news} noticias. Hay {len(records)}.")


def run_quality_pipeline(records: List[NewsRecord]) -> List[NewsRecord]:
    x = [r.copy(update={"published_at": normalize_tz(r.published_at)}) for r in records]
    x = enforce_freshness(x)
    x = dedupe(x)
    validate_minimum(x)
    return x

