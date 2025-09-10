# app_vision/modules/contracts_runtime.py
"""
Contratos de Runtime para Protocolo Universal
Tipos ligeros y claves mínimas para blindar el protocolo
"""

from typing import List, Dict, Any, Optional, TypedDict

class CandadoItem(TypedDict):
    date: str          # YYYY-MM-DD (ET)
    block: str         # AM|MID|EVE
    fijo2d: str        # last2(P3)
    p4_front2d: str    # first2(P4)
    p4_back2d: str     # last2(P4)
    candado: List[str] # [FIJO, FRONT, BACK] (≥2)
    parles: List[List[str]]
    source: str
    fetched_at: str    # ISO ET

class Paso3Output(TypedDict):
    candado_items: List[CandadoItem]
    mensaje_guia_parcial: Dict[str, Any]  # {topics, keywords, message}
    trace3: List[str]

class Paso4NewsItem(TypedDict):
    title: str
    url: str
    domain: str
    published_at: str
    match_score: float

class Paso4Output(TypedDict):
    news: List[Paso4NewsItem]
    news_stats: Dict[str, int]

class Paso5Output(TypedDict):
    tabla100_ranking: Dict[str, Any]
    trace5: List[str]

class Paso6Output(TypedDict):
    sefirot_profile: Dict[str, Any]
    candidatos: Dict[str, List[int]]
    series_pre: List[List[int]]
    trace6: List[str]

class PasoZOutput(TypedDict):
    reporte_final: Dict[str, Any]
    status: str
    timestamp: str
    trace_completo: List[str]




