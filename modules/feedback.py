from __future__ import annotations
from typing import List, Dict, Any
import json, os, time

FB_DIR = ".feedback"
os.makedirs(FB_DIR, exist_ok=True)


def record_feedback(series: List[int], useful: bool, note: str = ""):
    path = os.path.join(FB_DIR, f"fb-{int(time.time())}.json")
    with open(path,'w',encoding='utf-8') as f:
        json.dump({"series":series, "useful":useful, "note":note}, f, ensure_ascii=False, indent=2)
