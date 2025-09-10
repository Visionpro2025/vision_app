from __future__ import annotations
from typing import List, Dict, Optional

LETTER_VALUES = [400,300,200,100,90,80,70,60,50,40,30,20,10,9,8,7,6,5,4,3,2,1]

def _partitions_greedy(n: int, limit_solutions: int = 32) -> List[List[int]]:
    sols: List[List[int]] = []
    def greedy(base: List[int], rem: int, start: int = 0):
        nonlocal sols
        if len(sols) >= limit_solutions: return
        if rem == 0:
            sols.append(base[:]); return
        for i in range(start, len(LETTER_VALUES)):
            v = LETTER_VALUES[i]
            if v <= rem:
                base.append(v)
                greedy(base, rem - v, i)
                base.pop()
    greedy([], n, 0)
    return sols if sols else [[n]]

def seleccionar_semejantes_generico(values: List[int],
                                    rango_max: int,
                                    anchors: Optional[List[int]] = None,
                                    exclude: Optional[List[int]] = None,
                                    top_k: int = 16) -> List[Dict]:
    anchors = anchors or [26, 52, 65]
    ex_set = set(exclude or [])
    cand_scores: Dict[int, Dict[str, float]] = {}

    for num in values:
        if num <= rango_max and num not in ex_set:
            c = cand_scores.setdefault(num, {"score": 0.0, "hits": 0})
            c["hits"] += 1
            c["score"] += 0.6
            continue

        parts = _partitions_greedy(num, limit_solutions=32)
        local: Dict[int, int] = {}
        for p in parts:
            for v in p:
                if v <= rango_max and v not in ex_set:
                    local[v] = local.get(v, 0) + 1

        if not local:
            continue

        max_hits = max(local.values())
        for v, hits in local.items():
            freq = hits / max_hits
            centrality = 1.0 if v in (10,20,30,40,50,60) else (0.8 if v % 10 == 0 else 0.5)
            c = cand_scores.setdefault(v, {"score": 0.0, "hits": 0})
            c["hits"] += hits
            c["score"] += 0.5 * freq + 0.3 * centrality

    for a in anchors:
        if a in cand_scores:
            cand_scores[a]["score"] += 0.2

    ranked = sorted(
        [{"value": v, "score": m["score"], "hits": m["hits"], "method": "gematria"} for v, m in cand_scores.items()],
        key=lambda x: (x["score"], x["hits"]), reverse=True
    )
    return ranked[:top_k]






