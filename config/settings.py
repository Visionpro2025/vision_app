# config/settings.py
from dataclasses import dataclass
from typing import Dict, List, Any

TZ = "America/New_York"  # Zona horaria del Este de Estados Unidos

@dataclass
class Weights:
    t70: float = 0.30
    gematria: float = 0.40
    subliminal: float = 0.20
    quantum: float = 0.10

WEIGHTS = Weights()

@dataclass
class Thresholds:
    min_news: int = 50  # objetivo 100
    min_categories: int = 3
    min_archetypes: int = 2
    min_subliminal_msgs: int = 1
    min_quantum_states: int = 1

THRESH = Thresholds()

@dataclass
class GameRules:
    name: str = "MegaMillions"
    main_count: int = 5
    main_min: int = 1
    main_max: int = 70
    special_count: int = 1
    special_min: int = 1
    special_max: int = 25
    allow_duplicates: bool = False

RULES = GameRules()

RANDOM_SEED = 1337

@dataclass
class DataQualityCfg:
    min_news: int = 50
    timezone: str = "America/New_York"  # Cambiado de Cuba a Estados Unidos
    dedupe_utm: bool = True
    max_age_hours: int = 48  # freshness

@dataclass
class ObservabilityCfg:
    enable_metrics: bool = True
    enable_tracing: bool = True
    metrics_port: int = 9108

@dataclass
class SecurityCfg:
    rbac_enabled: bool = False
    pii_masking: bool = True
    audit_retention_days: int = 365

@dataclass
class OrchestrationCfg:
    max_retries: int = 3
    backoff_sec: int = 5

@dataclass
class SemanticsCfg:
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    top_k: int = 5

DATA_QUALITY = DataQualityCfg()
OBS = ObservabilityCfg()
SEC = SecurityCfg()
ORCH = OrchestrationCfg()
SEM = SemanticsCfg()
