# ============================================
# 📌 STEP 5B: CANDADO FLORIDA QUINIELA
# Step registrado en FSM para análisis de candado cubano
# ============================================

from __future__ import annotations
from typing import Dict, Any
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.validate import ensure_inputs
from app_vision.modules.bolita_florida import candado_florida_quini
from app_vision.modules.role_guard import enforce_orchestrator_role

@register_step("CandadoFloridaStep")
class CandadoFloridaStep(Step):
    """
    Step especializado para Florida Quiniela (bolita cubana).
    Objetivo: hallar el candado (lo que más paga).
    """
    
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        # Verificar rol de orquestador
        enforce_orchestrator_role(ctx, data, "CandadoFloridaStep")
        
        # Gate de modo/juego
        if data.get("game") != "Florida_Quiniela" or data.get("mode") != "FLORIDA_QUINIELA":
            raise StepError("ConfigError", "Este step solo aplica a Florida Quiniela (mode=FLORIDA_QUINIELA).")

        # Validación de inputs
        try:
            ensure_inputs(data)
        except Exception as e:
            raise StepError("InputError", f"Inputs inválidos: {e}")

        # Extraer parámetros
        p3_mid = data["p3_mid"]
        p4_mid = data["p4_mid"]
        p3_eve = data["p3_eve"]
        p4_eve = data["p4_eve"]
        cfg = data.get("cfg", {})

        # Ejecutar análisis del candado
        try:
            out = candado_florida_quini(p3_mid, p4_mid, p3_eve, p4_eve, cfg)
        except Exception as e:
            raise StepError("Unhandled", f"Fallo candado: {e}")

        # Payload final (lo que verá status/auditoría)
        return {
            "game": "Florida_Quiniela",
            "candado_mid": out["candado_mid"],
            "candado_eve": out["candado_eve"],
            "parles_mid": out["parles_mid"],
            "parles_eve": out["parles_eve"],
            "conjunto_2D_mid": out["conjunto_2D_mid"],
            "conjunto_2D_eve": out["conjunto_2D_eve"],
            "metadatos": out["metadatos"],
            "equivalencia": out["equivalencia"],
            "explicacion_mid": out["explicacion_mid"],
            "explicacion_eve": out["explicacion_eve"]
        }
