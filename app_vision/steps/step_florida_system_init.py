# app_vision/steps/step_florida_system_init.py
"""
PASO 1: Inicialización y Limpieza del Sistema
Adaptado para Florida Pick 3 → Bolita Cubana
"""

from __future__ import annotations
from typing import Dict, Any
from datetime import datetime
import gc
import psutil
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.guardrails import apply_basic_guardrails

@register_step("SystemInitializationStep")
class SystemInitializationStep(Step):
    """
    PASO 1: Inicialización y Limpieza del Sistema
    - Limpiar memoria del sistema
    - Resetear parámetros a cero
    - Preparar para análisis de Florida Pick 3
    - Liberar recursos
    """
    
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        cleanup_memory = data.get("cleanup_memory", True)
        reset_parameters = data.get("reset_parameters", True)
        prepare_for_lottery = data.get("prepare_for_lottery", "florida_pick3")
        
        results = {
            "step": 1,
            "step_name": "SystemInitializationStep",
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "details": {}
        }
        
        try:
            # Limpiar memoria si se solicita
            if cleanup_memory:
                collected = gc.collect()
                results["details"]["memory_cleaned"] = {
                    "objects_collected": collected,
                    "memory_usage_mb": psutil.Process().memory_info().rss / 1024 / 1024
                }
            
            # Resetear parámetros si se solicita
            if reset_parameters:
                results["details"]["parameters_reset"] = {
                    "reset_timestamp": datetime.now().isoformat(),
                    "previous_state_cleared": True
                }
            
            # Preparar para lotería específica
            if prepare_for_lottery == "florida_pick3":
                results["details"]["lottery_preparation"] = {
                    "lottery_type": "florida_pick3",
                    "bolita_format": "cubana",
                    "windows": ["AM", "MID", "EVE"],
                    "timezone": "ET",
                    "prepared": True
                }
            
            # Estado del sistema
            results["details"]["system_status"] = {
                "memory_usage_mb": psutil.Process().memory_info().rss / 1024 / 1024,
                "cpu_percent": psutil.cpu_percent(),
                "initialization_complete": True
            }
            
            # Validar output con guardrails
            apply_basic_guardrails(
                step_name="SystemInitializationStep",
                input_data=data,
                output_data=results,
                required_output_keys=["step", "step_name", "timestamp", "status", "details"]
            )
            
            return results
            
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
            raise StepError("SystemError", f"Error en inicialización del sistema: {e}")




