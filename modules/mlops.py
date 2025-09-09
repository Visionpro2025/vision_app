from __future__ import annotations
from typing import Dict, Any
import json, os, time

REG_DIR = ".models"
os.makedirs(REG_DIR, exist_ok=True)


def log_experiment(name: str, metrics: Dict[str,Any], params: Dict[str,Any]):
    path = os.path.join(REG_DIR, f"{name}-{int(time.time())}.json")
    with open(path,'w',encoding='utf-8') as f:
        json.dump({"metrics":metrics, "params":params}, f, ensure_ascii=False, indent=2)
