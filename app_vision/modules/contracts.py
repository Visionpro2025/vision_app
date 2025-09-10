# modules/contracts.py
from __future__ import annotations
from typing import Dict, Any, List, Union
from app_vision.engine.contracts import StepError
from datetime import datetime

def require_keys(obj: Dict[str, Any], keys: List[str], step: str) -> None:
    """Valida que el objeto contenga todas las claves requeridas"""
    missing = [k for k in keys if k not in obj]
    if missing: 
        raise StepError("InputError", f"{step}: faltan claves {missing}")

def forbid_sim_source(src: Union[str, None], step: str) -> None:
    """Prohíbe fuentes simuladas o de prueba"""
    s = (src or "").lower()
    forbidden_words = ["simul", "dummy", "test", "mock", "fake", "generated", "fallback"]
    if any(w in s for w in forbidden_words):
        raise StepError("InputError", f"{step}: fuente simulada '{src}' prohibida")

def assert_nonempty_list(name: str, lst: List[Any], step: str) -> None:
    """Valida que la lista no esté vacía"""
    if not lst:
        raise StepError("DeterminismError", f"{step}: {name} output vacío (debe fallar y loggear causa)")

def assert_valid_count(name: str, count: int, min_required: int, step: str) -> None:
    """Valida que el conteo cumpla el mínimo requerido"""
    if count < min_required:
        raise StepError("DeterminismError", f"{step}: {name} insuficiente ({count}/{min_required})")

def require_provenance(obj: Dict[str, Any], step: str) -> None:
    """Valida que el objeto tenga información de procedencia"""
    if "source" not in obj and "provenance" not in obj:
        raise StepError("InputError", f"{step}: falta información de procedencia")

def validate_domain_allowlist(url: str, allowlist: List[str], step: str) -> bool:
    """Valida que el dominio esté en la lista permitida"""
    if not url:
        return False
    
    domain = url.split("//")[-1].split("/")[0].lower()
    allowed = any(allowed_domain in domain for allowed_domain in allowlist)
    
    if not allowed:
        raise StepError("InputError", f"{step}: dominio '{domain}' no permitido")
    
    return True

def now_iso() -> str:
    """Retorna timestamp ISO actual"""
    return datetime.utcnow().isoformat()

def create_provenance(source: str, fetched_at: str = None) -> Dict[str, str]:
    """Crea objeto de procedencia estándar"""
    return {
        "source": source,
        "fetched_at": fetched_at or now_iso(),
        "verified": True
    }

def validate_draws_format(draws: List[Dict[str, Any]], step: str) -> None:
    """Valida formato de sorteos"""
    if not isinstance(draws, list):
        raise StepError("InputError", f"{step}: draws debe ser lista")
    
    if not draws:
        raise StepError("InputError", f"{step}: lista de draws vacía")
    
    required_fields = ["date", "block", "numbers"]
    for i, draw in enumerate(draws):
        if not isinstance(draw, dict):
            raise StepError("InputError", f"{step}: draw {i} debe ser diccionario")
        
        missing = [f for f in required_fields if f not in draw]
        if missing:
            raise StepError("InputError", f"{step}: draw {i} faltan campos {missing}")
        
        # Validar números
        numbers = draw.get("numbers", [])
        if not isinstance(numbers, list) or len(numbers) != 3:
            raise StepError("InputError", f"{step}: draw {i} numbers inválido {numbers}")
        
        if not all(isinstance(n, int) and 0 <= n <= 9 for n in numbers):
            raise StepError("InputError", f"{step}: draw {i} numbers fuera de rango {numbers}")
        
        # Validar bloque
        block = draw.get("block", "").upper()
        if block not in ["MID", "EVE"]:
            raise StepError("InputError", f"{step}: draw {i} block inválido {block}")
        
        # Prohibir fuentes simuladas
        forbid_sim_source(draw.get("source"), f"{step}_draw_{i}")

def validate_news_format(news: List[Dict[str, Any]], step: str) -> None:
    """Valida formato de noticias"""
    if not isinstance(news, list):
        raise StepError("InputError", f"{step}: news debe ser lista")
    
    for i, article in enumerate(news):
        if not isinstance(article, dict):
            raise StepError("InputError", f"{step}: article {i} debe ser diccionario")
        
        required_fields = ["url", "title"]
        missing = [f for f in required_fields if f not in article]
        if missing:
            raise StepError("InputError", f"{step}: article {i} faltan campos {missing}")
        
        # Validar URL
        url = article.get("url", "")
        if not url or not url.startswith(("http://", "https://")):
            raise StepError("InputError", f"{step}: article {i} URL inválida {url}")

def enforce_timeout(timeout_s: int, step: str) -> None:
    """Valida timeout configurado"""
    if timeout_s <= 0:
        raise StepError("ConfigError", f"{step}: timeout_s debe ser positivo")
    
    if timeout_s > 300:  # 5 minutos máximo
        raise StepError("ConfigError", f"{step}: timeout_s excesivo ({timeout_s}s)")

def validate_retry_config(retry: Dict[str, Any], step: str) -> None:
    """Valida configuración de reintentos"""
    if not isinstance(retry, dict):
        raise StepError("ConfigError", f"{step}: retry debe ser diccionario")
    
    max_retries = retry.get("max", 0)
    if not isinstance(max_retries, int) or max_retries < 0 or max_retries > 3:
        raise StepError("ConfigError", f"{step}: retry.max inválido {max_retries}")
    
    backoff_ms = retry.get("backoff_ms", 0)
    if not isinstance(backoff_ms, int) or backoff_ms < 0 or backoff_ms > 5000:
        raise StepError("ConfigError", f"{step}: retry.backoff_ms inválido {backoff_ms}")





