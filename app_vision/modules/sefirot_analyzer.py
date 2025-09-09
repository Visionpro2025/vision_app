from __future__ import annotations
from typing import List, Dict, Any, Tuple
import math
from collections import Counter, defaultdict

# Mapeo simple 0..9 → sefirá (10 sefirot)
SEFIROT = {
    0: {"name":"Keter",     "axis":"espiritual"},
    1: {"name":"Jojmá",     "axis":"espiritual"},
    2: {"name":"Biná",      "axis":"espiritual"},
    3: {"name":"Jésed",     "axis":"misericordia"},
    4: {"name":"Guevurá",   "axis":"disciplina"},
    5: {"name":"Tiféret",   "axis":"armonía"},
    6: {"name":"Nétzaj",    "axis":"victoria"},
    7: {"name":"Hod",       "axis":"esplendor"},
    8: {"name":"Yesod",     "axis":"fundación"},
    9: {"name":"Maljut",    "axis":"manifestación"},
}

def _pos_weights(n: int)->List[float]:
    """
    Peso por posición (centenas, decenas, unidades) y por recencia.
    Para 3 dígitos: [w0, w1, w2] = [1.0, 1.1, 1.2] (unidades pesa más)
    """
    return [1.0, 1.1, 1.2]

def _recency_weights(m: int)->List[float]:
    """
    Peso por recencia para m sorteos: más reciente pesa más.
    """
    base = [1.0 + 0.12*i for i in range(m)]  # 1.0, 1.12, 1.24, ...
    return list(reversed(base))

def analyze_draws(draws: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    draws = [{date:'YYYY-MM-DD', block:'MID|EVE', numbers:[d1,d2,d3], ...}, ...] (orden aleatorio)
    Retorna scores por dígito/sefirah y candidatos.
    """
    # Ordenar por fecha/bloque creciente y aplicar recencia invertida
    ordered = sorted(draws, key=lambda x: (x["date"], 1 if x["block"]=="MID" else 2))
    m = len(ordered)
    if m == 0:
        return {"digit_scores":{}, "sefirah_scores":{}, "patterns":{}, "candidates":{}}

    rw = _recency_weights(m)
    pw = _pos_weights(3)

    # Scoring por dígito con pesos de posición y recencia
    dscore = Counter()
    patterns = {"pairs":0, "triples":0, "runs":0}  # dobles, triples, secuencias
    for i, d in enumerate(reversed(ordered)):  # más reciente primero
        rec_w = rw[i]
        a,b,c = d["numbers"]
        # patrones
        if a==b or b==c or a==c: patterns["pairs"] += 1
        if a==b==c: patterns["triples"] += 1
        if (a+1==b and b+1==c) or (a-1==b and b-1==c): patterns["runs"] += 1

        for pos, val in enumerate([a,b,c]):
            dscore[val] += rec_w * pw[pos]

    # Normalizar 0..1
    maxv = max(dscore.values()) if dscore else 1.0
    dnorm = {k: float(v)/maxv for k,v in dscore.items()}

    # Score por sefirá = suma de sus dígitos
    sscore = defaultdict(float)
    for dig, sc in dnorm.items():
        s = SEFIROT[dig]["name"]
        sscore[s] += sc
    # Normalización sefirot
    maxs = max(sscore.values()) if sscore else 1.0
    snorm = {k: float(v)/maxs for k,v in sscore.items()}

    # Candidatos por banda
    bands = {"alta":[], "media":[], "baja":[]}
    for d, sc in sorted(dnorm.items(), key=lambda kv: kv[1], reverse=True):
        if sc >= 0.75: bands["alta"].append(d)
        elif sc >= 0.45: bands["media"].append(d)
        else: bands["baja"].append(d)

    return {
        "digit_scores": {int(k): round(v,3) for k,v in dnorm.items()},
        "sefirah_scores": {k: round(v,3) for k,v in snorm.items()},
        "patterns": patterns,
        "candidates": bands
    }




