from __future__ import annotations
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
import yaml
from pathlib import Path

@register_step("EnforceOrchestratorStep")
class EnforceOrchestratorStep(Step):
    """
    Sentinela universal que se ejecuta como primer paso de todos los planes.
    Enforce la política global: Cursor solo orquesta, App decide, sin simulaciones.
    """
    
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        # Cargar política global
        policy_path = Path("plans/policy_app.yaml")
        if not policy_path.exists():
            raise StepError("ConfigError", "Política global no encontrada en plans/policy_app.yaml")
        
        try:
            with open(policy_path, 'r', encoding='utf-8') as f:
                global_policy = yaml.safe_load(f)
        except Exception as e:
            raise StepError("ConfigError", f"Error cargando política global: {e}")
        
        # Validar política recibida vs política global
        received_policy = data.get("policy", {})
        
        # Enforce: allow_simulation debe ser False
        if received_policy.get("allow_simulation", False):
            raise StepError("ConfigError", "allow_simulation debe ser False según política global")
        
        # Enforce: require_sources debe ser True
        if not received_policy.get("require_sources", True):
            raise StepError("ConfigError", "require_sources debe ser True según política global")
        
        # Enforce: abort_on_empty debe ser True
        if not received_policy.get("abort_on_empty", True):
            raise StepError("ConfigError", "abort_on_empty debe ser True según política global")
        
        # Validar que el orquestador es Cursor
        if global_policy.get("app", {}).get("orchestrator") != "cursor_only":
            raise StepError("ConfigError", "Orquestador debe ser 'cursor_only' según política global")
        
        # Retornar confirmación de enforcement
        return {
            "cursor_role": "orchestrator_only",
            "app_is_master": True,
            "policy_enforced": True,
            "global_policy": global_policy,
            "enforcement_checks": {
                "allow_simulation": False,
                "require_sources": True,
                "abort_on_empty": True,
                "orchestrator": "cursor_only"
            },
            "sources_allowlist": global_policy.get("sources_allowlist", {}),
            "timeouts": global_policy.get("app", {}).get("timeouts", {}),
            "observability": global_policy.get("observability", {})
        }