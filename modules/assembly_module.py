# modules/assembly_module.py
import random
from typing import List, Dict
from collections import Counter
from config.settings import RULES, WEIGHTS, RANDOM_SEED
from modules.schemas import T70Result, GematriaResult, SubliminalResult, QuantumResult, SeriesProposal

random.seed(RANDOM_SEED)

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def pool_from_gematria(g: GematriaResult) -> List[int]:
    return [n for n in g.numbers if RULES.main_min <= n <= RULES.main_max]

def pool_from_t70(t70: T70Result) -> List[int]:
    return [n for n in t70.keyword_map.values() if RULES.main_min <= n <= RULES.main_max]

def pool_from_subliminal(s: SubliminalResult) -> List[int]:
    # Heurística: features (0..1) → selección top-N proporcional
    items = sorted(s.features.items(), key=lambda kv: kv[1], reverse=True)
    out = []
    for k,v in items[:RULES.main_count*4]:
        try:
            n = int(k)
            if RULES.main_min <= n <= RULES.main_max:
                out.append(n)
        except Exception:
            continue
    return out

def pool_from_quantum(q: QuantumResult) -> List[int]:
    # Mapear estados a números si procede
    out = []
    for st, p in q.probabilities.items():
        try:
            n = int(''.join(filter(str.isdigit, st))[:2] or 0)
            if RULES.main_min <= n <= RULES.main_max:
                out += [n] * max(1, int(10*p))
        except Exception:
            pass
    return out

def candidate_pool(t70, g, s, q) -> List[int]:
    pool = pool_from_gematria(g) * int(WEIGHTS.gematria*10)
    pool += pool_from_t70(t70) * int(WEIGHTS.t70*10)
    pool += pool_from_subliminal(s) * max(1, int(WEIGHTS.subliminal*10))
    pool += pool_from_quantum(q) * max(1, int(WEIGHTS.quantum*10))
    return pool

def score_series(series: List[int], freq: Dict[int,int]) -> float:
    # Frecuencia ponderada + dispersión simple
    base = sum(freq.get(n,0) for n in series)
    dispersion = len(set(series)) / len(series)
    return clamp(0.7*base/ max(1, max(freq.values())) + 0.3*dispersion)

def generate_series(t70: T70Result, g: GematriaResult, s: SubliminalResult, q: QuantumResult, k: int = 5) -> List[SeriesProposal]:
    pool = candidate_pool(t70,g,s,q)
    if not pool:
        return []
    freq = Counter(pool)
    proposals: List[SeriesProposal] = []

    # Búsqueda simple por muestreo proporcional a frecuencia
    for _ in range(200):
        cand = []
        seen = set()
        while len(cand) < RULES.main_count and pool:
            n = random.choices(list(freq.keys()), weights=list(freq.values()), k=1)[0]
            if not RULES.allow_duplicates and n in seen:
                continue
            seen.add(n)
            cand.append(n)
        cand.sort()
        prob = score_series(cand, freq)
        proposals.append(SeriesProposal(main=cand, special=None, probability=prob, reasoning="Frecuencia ponderada + dispersión"))

    # Top-k únicas
    uniq = {}
    for p in proposals:
        key = tuple(p.main)
        if key not in uniq or p.probability > uniq[key].probability:
            uniq[key] = p
    top = sorted(uniq.values(), key=lambda x: x.probability, reverse=True)[:k]
    return top









