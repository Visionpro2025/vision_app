from __future__ import annotations
from typing import List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import json, os, uuid

CATALOG_DIR = ".catalog"
os.makedirs(CATALOG_DIR, exist_ok=True)

@dataclass
class DatasetVersion:
    id: str
    created_at: str
    source_summary: Dict[str, Any]
    filters: Dict[str, Any]
    record_count: int


def save_dataset_version(source_summary: Dict[str,Any], filters: Dict[str,Any], record_count: int) -> str:
    vid = str(uuid.uuid4())
    dv = DatasetVersion(id=vid, created_at=datetime.utcnow().isoformat(), source_summary=source_summary, filters=filters, record_count=record_count)
    path = os.path.join(CATALOG_DIR, f"dataset_{vid}.json")
    with open(path,"w",encoding="utf-8") as f:
        json.dump(dv._dict_, f, ensure_ascii=False, indent=2)
    return vid

