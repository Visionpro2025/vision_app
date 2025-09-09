"""
Guardrails universales para todos los steps del sistema VISION PREMIUM.
Enforce la política global: datos reales, fuentes verificadas, sin simulaciones.
"""

from __future__ import annotations
from app_vision.engine.contracts import StepError
from typing import Dict, List, Any, Optional
import re
from urllib.parse import urlparse

def require_keys(obj: dict, keys: list, step: str) -> None:
    """
    Valida que un objeto contenga todas las claves requeridas.
    Aborta ruidosamente si faltan claves.
    """
    if not isinstance(obj, dict):
        raise StepError("InputError", f"{step}: input debe ser dict, recibido {type(obj)}")
    
    missing = [k for k in keys if k not in obj]
    if missing:
        raise StepError("InputError", f"{step}: faltan claves requeridas {missing}")

def forbid_sim_source(src: str | None, step: str) -> None:
    """
    Prohíbe explícitamente fuentes simuladas, dummy o de test.
    Política global: solo datos reales.
    """
    if src is None:
        return  # None está permitido
    
    s = str(src).lower()
    forbidden_patterns = [
        "simul", "dummy", "test", "mock", "fake", "example", 
        "placeholder", "sample", "demo", "trial"
    ]
    
    for pattern in forbidden_patterns:
        if pattern in s:
            raise StepError("InputError", f"{step}: fuente simulada '{src}' prohibida (patrón: {pattern})")

def assert_nonempty_list(name: str, lst: List[Any], step: str) -> None:
    """
    Valida que una lista no esté vacía.
    Política global: abort_on_empty = true
    """
    if not isinstance(lst, list):
        raise StepError("InputError", f"{step}: {name} debe ser lista, recibido {type(lst)}")
    
    if not lst:
        raise StepError("DeterminismError", f"{step}: {name} está vacío (política abort_on_empty)")

def assert_allowlisted(domain: str, allowlist: List[str], step: str) -> None:
    """
    Valida que un dominio esté en la allowlist de fuentes permitidas.
    """
    if not allowlist:
        return  # Sin allowlist = permitir todo
    
    domain_lower = domain.lower()
    is_allowed = any(allowed_domain in domain_lower for allowed_domain in allowlist)
    
    if not is_allowed:
        raise StepError("InputError", f"{step}: dominio '{domain}' fuera de allowlist permitida: {allowlist}")

def validate_url_source(url: str, step: str, allowlist: List[str] = None) -> str:
    """
    Valida una URL como fuente de datos.
    Verifica formato, dominio y allowlist.
    """
    if not url:
        raise StepError("InputError", f"{step}: URL vacía no permitida")
    
    # Validar formato de URL
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("URL inválida")
    except Exception:
        raise StepError("InputError", f"{step}: URL inválida '{url}'")
    
    # Prohibir fuentes simuladas
    forbid_sim_source(url, step)
    
    # Validar allowlist si se proporciona
    if allowlist:
        assert_allowlisted(parsed.netloc, allowlist, step)
    
    return url

def validate_data_quality(data: Dict[str, Any], step: str, required_fields: List[str] = None) -> None:
    """
    Valida la calidad de los datos de salida.
    Enforce: datos reales, no simulados, con fuentes.
    """
    # Validar campos requeridos
    if required_fields:
        require_keys(data, required_fields, step)
    
    # Prohibir datos simulados en el contenido
    for key, value in data.items():
        if isinstance(value, str):
            forbid_sim_source(value, f"{step}.{key}")
        elif isinstance(value, dict):
            validate_data_quality(value, f"{step}.{key}")
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, str):
                    forbid_sim_source(item, f"{step}.{key}[{i}]")
                elif isinstance(item, dict):
                    validate_data_quality(item, f"{step}.{key}[{i}]")

def enforce_timeout(timeout_s: int, step: str) -> None:
    """
    Valida que el timeout esté dentro de los límites permitidos.
    """
    max_timeout = 300  # 5 minutos máximo
    min_timeout = 1    # 1 segundo mínimo
    
    if timeout_s > max_timeout:
        raise StepError("ConfigError", f"{step}: timeout {timeout_s}s excede máximo {max_timeout}s")
    
    if timeout_s < min_timeout:
        raise StepError("ConfigError", f"{step}: timeout {timeout_s}s menor que mínimo {min_timeout}s")

def validate_output_completeness(output: Dict[str, Any], step: str, expected_keys: List[str] = None) -> None:
    """
    Valida que el output esté completo y no vacío.
    Política global: abort_on_empty = true
    """
    if not output:
        raise StepError("DeterminismError", f"{step}: output vacío (política abort_on_empty)")
    
    # Validar claves esperadas
    if expected_keys:
        missing_keys = [k for k in expected_keys if k not in output]
        if missing_keys:
            raise StepError("OutputError", f"{step}: output incompleto, faltan claves {missing_keys}")
    
    # Validar que no hay valores vacíos críticos (excluyendo listas que pueden estar vacías inicialmente)
    for key, value in output.items():
        if value is None or value == "" or value == {}:
            raise StepError("OutputError", f"{step}: output.{key} está vacío (política abort_on_empty)")
        # Para listas, solo validar si están explícitamente marcadas como requeridas
        if isinstance(value, list) and len(value) == 0 and key in (expected_keys or []):
            raise StepError("OutputError", f"{step}: output.{key} está vacío (política abort_on_empty)")

def log_guardrail_check(step: str, check_type: str, status: str, details: str = "") -> None:
    """
    Registra verificaciones de guardrails para auditoría.
    """
    # En un sistema real, esto iría a un logger estructurado
    print(f"[GUARDRAIL] {step} | {check_type} | {status} | {details}")

# Función de conveniencia para aplicar todos los guardrails básicos
def apply_basic_guardrails(
    step_name: str,
    input_data: Dict[str, Any],
    output_data: Dict[str, Any],
    required_input_keys: List[str] = None,
    required_output_keys: List[str] = None,
    sources_allowlist: List[str] = None
) -> None:
    """
    Aplica todos los guardrails básicos a un step.
    Función de conveniencia para uso común.
    """
    # Validar input
    if required_input_keys:
        require_keys(input_data, required_input_keys, step_name)
    
    # Validar fuentes en input
    for key, value in input_data.items():
        if isinstance(value, str) and ("http" in value or "www" in value):
            validate_url_source(value, f"{step_name}.input.{key}", sources_allowlist)
    
    # Validar output
    validate_output_completeness(output_data, step_name, required_output_keys)
    
    # Validar calidad de datos
    validate_data_quality(output_data, step_name)
    
    # Log de verificación
    log_guardrail_check(step_name, "basic_validation", "PASSED")
