# app_vision/steps/step_florida_lottery_config.py
"""
PASO 2: Configuración de Lotería Florida Pick 3
Adaptado para bolita cubana con características específicas
"""

from __future__ import annotations
from typing import Dict, Any
from datetime import datetime
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.guardrails import apply_basic_guardrails

@register_step("FloridaLotteryConfigurationStep")
class FloridaLotteryConfigurationStep(Step):
    """
    PASO 2: Configuración de Lotería Florida Pick 3
    - Configurar perfil de Florida Pick 3
    - Establecer formato bolita cubana
    - Configurar ventanas de tiempo (AM/MID/EVE)
    - Validar configuración
    """
    
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        lottery_type = data.get("lottery_type", "florida_pick3")
        bolita_format = data.get("bolita_format", "cubana")
        windows = data.get("windows", ["AM", "MID", "EVE"])
        candado_rule = data.get("candado_rule", "deterministic_fixed")
        
        results = {
            "step": 2,
            "step_name": "FloridaLotteryConfigurationStep",
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "lottery_config": {}
        }
        
        try:
            # Configuración específica de Florida Pick 3
            lottery_config = {
                "lottery_type": lottery_type,
                "bolita_format": bolita_format,
                "windows": windows,
                "candado_rule": candado_rule,
                "timezone": "ET",
                "draw_schedule": {
                    "AM": {"open": "06:00", "close": "06:30", "description": "Ventana matutina"},
                    "MID": {"open": "13:35", "close": "14:10", "description": "Ventana mediodía"},
                    "EVE": {"open": "21:40", "close": "22:20", "description": "Ventana vespertina"}
                },
                "candado_construction": {
                    "fijo_2d": "últimos 2 del Pick3 del bloque",
                    "corrido_2d": "últimos 2 del Pick4 del mismo bloque",
                    "tercero": "últimos 2 del Pick3 del otro bloque",
                    "min_elements": 2,
                    "max_elements": 3
                },
                "bolita_components": {
                    "fijo": "Número fijo del candado",
                    "corridos": "Números que corren del fijo",
                    "parles": "Combinaciones 2-a-2",
                    "candado": "Conjunto de 2-3 elementos",
                    "empuje": "Número de empuje (opcional)"
                },
                "analysis_enabled": {
                    "gematria": True,
                    "subliminal": True,
                    "sefirotic": True,
                    "quantum": True,
                    "news_guided": True
                },
                "sources": {
                    "primary": "flalottery.com",
                    "secondary": "floridalottery.com",
                    "validation_required": True
                }
            }
            
            results["lottery_config"] = lottery_config
            
            # Validar configuración
            validation_results = self._validate_configuration(lottery_config)
            results["validation"] = validation_results
            
            if not validation_results["valid"]:
                raise StepError("ConfigurationError", f"Configuración inválida: {validation_results['errors']}")
            
            # Validar output con guardrails
            apply_basic_guardrails(
                step_name="FloridaLotteryConfigurationStep",
                input_data=data,
                output_data=results,
                required_output_keys=["step", "step_name", "timestamp", "status", "lottery_config"]
            )
            
            return results
            
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
            raise StepError("ConfigurationError", f"Error en configuración de lotería: {e}")
    
    def _validate_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Valida la configuración de la lotería"""
        errors = []
        
        # Validar tipo de lotería
        if config.get("lottery_type") != "florida_pick3":
            errors.append("Tipo de lotería debe ser 'florida_pick3'")
        
        # Validar formato bolita
        if config.get("bolita_format") != "cubana":
            errors.append("Formato bolita debe ser 'cubana'")
        
        # Validar ventanas
        expected_windows = ["AM", "MID", "EVE"]
        if config.get("windows") != expected_windows:
            errors.append(f"Ventanas deben ser {expected_windows}")
        
        # Validar regla candado
        if config.get("candado_rule") != "deterministic_fixed":
            errors.append("Regla candado debe ser 'deterministic_fixed'")
        
        # Validar zona horaria
        if config.get("timezone") != "ET":
            errors.append("Zona horaria debe ser 'ET'")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "validated_at": datetime.now().isoformat()
        }



