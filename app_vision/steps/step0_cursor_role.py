# ============================================
# 📌 STEP 0: ROL ORQUESTADOR DE CURSOR
# Establece el rol de Cursor como orquestador, no como cerebro
# ============================================

from __future__ import annotations
from typing import Dict, Any
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step

@register_step("CursorRoleStep")
class CursorRoleStep(Step):
    """
    Step que establece el rol de Cursor como ORQUESTADOR únicamente.
    
    REGLAS FUNDAMENTALES:
    1. Cursor NO aporta ideas, inferencias ni resultados por sí mismo
    2. Cursor SOLO ejecuta lo que se le ordena desde la App.Vision
    3. La App es la única que define pasos, solicita recursos e interpreta resultados
    4. Cursor actúa como orquestador: lee planes, ejecuta pasos, devuelve outputs exactos
    5. Todo lo que reciba Cursor debe percibirse como recibido por la App
    6. Cursor debe rechazar cualquier intento de "aportar contenido" propio
    """
    
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        # Establecer rol de orquestador
        role_payload = {
            "cursor_role": "orchestrator_only",
            "app_is_master": True,
            "execution_mode": "strict_orchestration",
            "content_generation_forbidden": True,
            "external_resource_requests": "app_controlled_only",
            "decision_making": "app_exclusive",
            "interpretation": "app_exclusive"
        }
        
        # Registrar en contexto para verificación por otros steps
        ctx.cfg.update(role_payload)
        
        return {
            "role_established": True,
            "cursor_role": "orchestrator_only",
            "app_is_master": True,
            "execution_rules": {
                "no_content_generation": True,
                "no_external_requests": True,
                "no_interpretation": True,
                "no_suggestions": True,
                "strict_execution_only": True
            },
            "app_vision_authority": {
                "step_definition": "app_controlled",
                "resource_requests": "app_controlled", 
                "result_interpretation": "app_controlled",
                "decision_making": "app_controlled"
            }
        }





