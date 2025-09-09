# modules/correlation_module.py
from typing import Dict, List
from math import isfinite
from collections import Counter
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity

from modules.schemas import T70Result, GematriaResult, SubliminalResult, QuantumResult, CorrelationPair, CorrelationReport
from config.settings import WEIGHTS

ARCHETYPE_AFFINITY = {  # 0..1 proximidad arquetipal
    ("Sabio","Héroe"): 0.6,
    ("Héroe","Sombra"): 0.3,
    ("Sabio","Sombra"): 0.2,
}

def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / max(1, len(a | b))

def archetype_similarity(A: List[str], B: List[str]) -> float:
    A, B = set(A), set(B)
    base = jaccard(A, B)
    bonus = 0.0
    for a in A:
        for b in B:
            bonus = max(bonus, ARCHETYPE_AFFINITY.get((a,b), ARCHETYPE_AFFINITY.get((b,a), 0.0)))
    return min(1.0, base + 0.5*bonus)

def tfidf_similarity(texts_a: List[str], texts_b: List[str]) -> float:
    # Versión simplificada sin sklearn
    if not texts_a or not texts_b:
        return 0.0
    
    # Similitud simple basada en palabras comunes
    words_a = set(' '.join(texts_a).lower().split())
    words_b = set(' '.join(texts_b).lower().split())
    
    if not words_a or not words_b:
        return 0.0
    
    intersection = len(words_a & words_b)
    union = len(words_a | words_b)
    
    return intersection / union if union > 0 else 0.0

def correlate(t70: T70Result, g: GematriaResult, s: SubliminalResult, q: QuantumResult) -> CorrelationReport:
    # T70 ↔ Gematría (keywords vs números/arquetipos)
    t70_keys = set(t70.keyword_map.keys())
    g_arch = set(g.archetypes)
    pair_t70_g = 0.5*jaccard(t70_keys, set(g.hebrew_conversion)) + 0.5*archetype_similarity(list(g_arch), list(g_arch))

    # Gematría ↔ Subliminal (arquetipos y mensajes)
    pair_g_s = 0.5*archetype_similarity(g.archetypes, g.archetypes) + 0.5*tfidf_similarity(g.hebrew_conversion, s.messages)

    # T70 ↔ Subliminal (keywords ↔ mensajes)
    pair_t70_s = tfidf_similarity(list(t70.keyword_map.keys()), s.messages)

    # T70 ↔ Cuántico (categorías ↔ estados)
    pair_t70_q = jaccard(set(t70.categories.keys()), set(q.states))

    # Gematría ↔ Cuántico (arquetipos ↔ estados)
    pair_g_q = jaccard(set(g.archetypes), set(q.states))

    # Subliminal ↔ Cuántico (mensajes ↔ estados)
    pair_s_q = tfidf_similarity(s.messages, list(q.states))

    pairs = [
        CorrelationPair("T70","Gematría", float(pair_t70_g)),
        CorrelationPair("Gematría","Subliminal", float(pair_g_s)),
        CorrelationPair("T70","Subliminal", float(pair_t70_s)),
        CorrelationPair("T70","Cuántico", float(pair_t70_q)),
        CorrelationPair("Gematría","Cuántico", float(pair_g_q)),
        CorrelationPair("Subliminal","Cuántico", float(pair_s_q)),
    ]

    weights = {
        ("T70","Gematría"): WEIGHTS.t70*WEIGHTS.gematria,
        ("Gematría","Subliminal"): WEIGHTS.gematria*WEIGHTS.subliminal,
        ("T70","Subliminal"): WEIGHTS.t70*WEIGHTS.subliminal,
        ("T70","Cuántico"): WEIGHTS.t70*WEIGHTS.quantum,
        ("Gematría","Cuántico"): WEIGHTS.gematria*WEIGHTS.quantum,
        ("Subliminal","Cuántico"): WEIGHTS.subliminal*WEIGHTS.quantum,
    }

    num = 0.0
    den = 0.0
    for p in pairs:
        w = weights.get((p.a,p.b), weights.get((p.b,p.a), 0.0))
        num += w * p.score
        den += w
    global_score = float(num / den) if den else 0.0

    return CorrelationReport(pairs=pairs, global_score=global_score, details={})
