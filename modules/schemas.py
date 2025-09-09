# modules/schemas.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime

@dataclass
class NewsItem:
    id: str
    title: str
    url: str
    published_at: datetime
    source: str
    category: str
    emotion: float
    keywords: List[str]
    language: str = "es"
    tz: str = "America/New_York"

@dataclass
class T70Result:
    categories: Dict[str, int]
    keyword_map: Dict[str, int]  # keyword -> T70 number
    features: Dict[str, float] = field(default_factory=dict)

@dataclass
class GematriaSeed:
    mode: str  # "predictiva" | "backtest"
    source_info: Dict[str, Any]

@dataclass
class GematriaResult:
    hebrew_conversion: List[str]
    numbers: List[int]
    archetypes: List[str]
    seed: GematriaSeed

@dataclass
class SubliminalResult:
    messages: List[str]
    impact_scores: List[float]
    features: Dict[str, float]

@dataclass
class QuantumResult:
    states: Set[str]
    entanglements: List[Tuple[str, str, float]]
    probabilities: Dict[str, float]

@dataclass
class CorrelationPair:
    a: str
    b: str
    score: float

@dataclass
class CorrelationReport:
    pairs: List[CorrelationPair]
    global_score: float
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SeriesProposal:
    main: List[int]
    special: Optional[List[int]]
    probability: float
    reasoning: str

@dataclass
class FinalOutcome:
    proposals: List[SeriesProposal]
    correlation: CorrelationReport
    dominant_pattern: str
    dominant_category: str
    dominant_archetype: str
    subliminal_msg: Optional[str]
    quantum_state: Optional[str]

