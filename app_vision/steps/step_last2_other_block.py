from __future__ import annotations
from typing import Dict, Any, List
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.guardrails import apply_basic_guardrails

def _last2(nums: List[int]) -> str:
    """Extrae last2 del Pick3"""
    assert len(nums) == 3
    return f"{nums[1]}{nums[2]}"

@register_step("Last2OtherBlockStep")
class Last2OtherBlockStep(Step):
    """
    Dado draws reales (mezcla MID/EVE/AM si aplica), devuelve last2 del Pick3 del otro bloque
    respecto a focus_index (por defecto 0 = más reciente).
    Reglas simples:
      - Si focus es MID → otro = EVE más cercano anterior (o AM si usas ese flujo).
      - Si focus es EVE → otro = MID del mismo día (o AM si mantienes 3 ventanas).
      - Si focus es AM → otro = EVE del día anterior (si disponible).
    """
    
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        # Aplicar guardrails de entrada
        apply_basic_guardrails(
            step_name="Last2OtherBlockStep",
            input_data=data,
            output_data={},
            required_input_keys=["draws"]
        )
        
        draws = data.get("draws") or []
        focus_i = int(data.get("focus_index", 0))
        
        if not draws or focus_i >= len(draws):
            raise StepError("InputError", "Last2OtherBlockStep: draws insuficientes o focus_index inválido")
        
        focus = draws[focus_i]
        fb = str(focus.get("block", "")).upper()
        fd = str(focus.get("date", ""))
        
        # Buscar "otro" con preferencia por mismo día
        other = None
        if fb in ("MID", "AM"):
            # buscar EVE del mismo día
            other = next((d for d in draws if d.get("date") == fd and str(d.get("block")).upper() == "EVE"), None)
        if not other and fb in ("EVE",):
            # buscar MID del mismo día
            other = next((d for d in draws if d.get("date") == fd and str(d.get("block")).upper() == "MID"), None)
        # fallback: cualquiera del día más próximo distinto al foco
        if not other:
            other = next((d for d in draws if not (d.get("date") == fd and str(d.get("block")).upper() == fb)), None)
        
        last2 = _last2(other["numbers"]) if other else None
        
        # Validar output
        output = {
            "other_last2": last2,
            "other_block": other.get("block", "").upper() if other else None,
            "other_date": other.get("date") if other else None,
            "focus_block": fb,
            "focus_date": fd
        }
        
        apply_basic_guardrails(
            step_name="Last2OtherBlockStep",
            input_data=data,
            output_data=output,
            required_output_keys=["other_last2"]
        )
        
        return output
