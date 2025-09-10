# ============================================
# 📌 GUARDIÁN DE ROLES - MIDDLEWARE DE VERIFICACIÓN
# Asegura que Cursor mantenga su rol de orquestador únicamente
# ============================================

from typing import Dict, Any, Optional
from app_vision.engine.contracts import StepError

def verify_cursor_role(ctx, data: Dict[str, Any], step_name: str) -> None:
    """
    Verifica que Cursor mantenga su rol de orquestador.
    
    Args:
        ctx: Contexto del step
        data: Datos del step
        step_name: Nombre del step para logging
    
    Raises:
        StepError: Si Cursor intenta actuar fuera de su rol
    """
    
    # Verificar que el rol esté establecido
    if not hasattr(ctx, 'cfg') or not ctx.cfg.get('cursor_role'):
        raise StepError(
            "ConfigError", 
            f"Step {step_name}: Rol de Cursor no establecido. Ejecutar step0_cursor_role primero."
        )
    
    # Verificar que sea orquestador únicamente
    if ctx.cfg.get('cursor_role') != 'orchestrator_only':
        raise StepError(
            "ConfigError",
            f"Step {step_name}: Cursor intentó actuar fuera de su rol de orquestador."
        )
    
    # Verificar que la App sea el maestro
    if not ctx.cfg.get('app_is_master', False):
        raise StepError(
            "ConfigError",
            f"Step {step_name}: App.Vision no está establecida como autoridad maestra."
        )

def check_content_generation_attempt(data: Dict[str, Any], step_name: str) -> None:
    """
    Verifica que no se esté intentando generar contenido propio.
    
    Args:
        data: Datos del step
        step_name: Nombre del step para logging
    
    Raises:
        StepError: Si se detecta intento de generación de contenido
    """
    
    # Indicadores de generación de contenido propio
    content_indicators = [
        'generate_news', 'create_content', 'suggest_plan', 'invent_data',
        'make_up', 'fabricate', 'imagine', 'assume', 'guess', 'speculate'
    ]
    
    # Verificar en claves de datos
    for key in data.keys():
        if any(indicator in key.lower() for indicator in content_indicators):
            raise StepError(
                "ContentGenerationForbidden",
                f"Step {step_name}: Cursor intentó generar contenido propio en '{key}'. Solo orquestación permitida."
            )
    
    # Verificar en valores de datos
    for key, value in data.items():
        if isinstance(value, str):
            if any(indicator in value.lower() for indicator in content_indicators):
                raise StepError(
                    "ContentGenerationForbidden",
                    f"Step {step_name}: Cursor intentó generar contenido propio en valor de '{key}'. Solo orquestación permitida."
                )

def check_external_resource_request(data: Dict[str, Any], step_name: str) -> None:
    """
    Verifica que no se esté solicitando recursos externos sin autorización de la App.
    
    Args:
        data: Datos del step
        step_name: Nombre del step para logging
    
    Raises:
        StepError: Si se detecta solicitud no autorizada de recursos
    """
    
    # Indicadores de solicitud de recursos externos
    resource_indicators = [
        'fetch_news', 'scrape_web', 'call_api', 'request_data',
        'download', 'pull_data', 'get_external', 'retrieve_remote'
    ]
    
    # Verificar en claves de datos
    for key in data.keys():
        if any(indicator in key.lower() for indicator in resource_indicators):
            raise StepError(
                "ExternalResourceForbidden",
                f"Step {step_name}: Cursor intentó solicitar recursos externos en '{key}'. Solo App.Vision puede autorizar esto."
            )

def check_interpretation_attempt(data: Dict[str, Any], step_name: str) -> None:
    """
    Verifica que no se esté intentando interpretar o decidir resultados.
    
    Args:
        data: Datos del step
        step_name: Nombre del step para logging
    
    Raises:
        StepError: Si se detecta intento de interpretación
    """
    
    # Indicadores de interpretación o decisión
    interpretation_indicators = [
        'interpret', 'decide', 'conclude', 'determine', 'judge',
        'evaluate', 'assess', 'analyze_meaning', 'extract_insight'
    ]
    
    # Verificar en claves de datos
    for key in data.keys():
        if any(indicator in key.lower() for indicator in interpretation_indicators):
            raise StepError(
                "InterpretationForbidden",
                f"Step {step_name}: Cursor intentó interpretar resultados en '{key}'. Solo App.Vision puede interpretar."
            )

def enforce_orchestrator_role(ctx, data: Dict[str, Any], step_name: str) -> None:
    """
    Función principal que aplica todas las verificaciones de rol.
    
    Args:
        ctx: Contexto del step
        data: Datos del step
        step_name: Nombre del step para logging
    
    Raises:
        StepError: Si Cursor intenta actuar fuera de su rol
    """
    
    # Verificar rol básico
    verify_cursor_role(ctx, data, step_name)
    
    # Verificar intentos de generación de contenido
    check_content_generation_attempt(data, step_name)
    
    # Verificar solicitudes de recursos externos
    check_external_resource_request(data, step_name)
    
    # Verificar intentos de interpretación
    check_interpretation_attempt(data, step_name)





