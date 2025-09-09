from __future__ import annotations
from typing import Dict, Any
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.guardrails import apply_basic_guardrails
from app_vision.modules.candado_model import Candado

@register_step("PrevCandadoStep")
class PrevCandadoStep(Step):
    """
    Toma draws reales (ya ordenados desc) y construye el CANDADO del bloque anterior al focus.
    Inputs:
      - draws: lista de draws reales [{date, block, numbers:[...] , pick4:[...]? , source...}]
      - focus_index: int (por defecto 0 = más reciente)
      - other_last2: 'NN' (opcional)
    Output:
      - prev_candado: objeto con {date, block, fijo2d, corrido2d?, extra2d?, trio, parles}
    """
    
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        # Aplicar guardrails de entrada
        apply_basic_guardrails(
            step_name="PrevCandadoStep",
            input_data=data,
            output_data={},
            required_input_keys=["draws"]
        )
        
        draws = data.get("draws") or []
        fi = int(data.get("focus_index", 0)) + 1  # el anterior al foco
        other_last2 = data.get("other_last2")  # puede ser None
        
        if fi >= len(draws):
            raise StepError("InputError", "No hay bloque anterior disponible")
        
        prev = draws[fi]
        p3 = prev["numbers"]
        p4 = prev.get("pick4")
        
        if len(p3) < 3:
            raise StepError("InputError", f"Pick3 del bloque anterior incompleto: {p3}")
        
        try:
            # Construir candado del bloque anterior
            fijo2d = f"{p3[1]}{p3[2]}"
            corrido2d = f"{p4[2]}{p4[3]}" if p4 and len(p4) >= 4 else None
            
            candado = Candado(
                date=str(prev["date"]),
                block=str(prev["block"]).upper(),
                fijo2d=fijo2d,
                corrido2d=corrido2d,
                extra2d=str(other_last2) if other_last2 and len(str(other_last2)) == 2 else None,
                pick3=(p3[0], p3[1], p3[2]),
                pick4=tuple(p4) if p4 and len(p4) >= 4 else None,
                source_p3=prev.get("source"),
                source_p4=prev.get("source")
            )
            
            # Validar output
            output = {
                "prev_candado": candado.to_dict(),
                "focus_index": fi,
                "prev_draw": {
                    "date": prev["date"],
                    "block": prev["block"],
                    "pick3": p3,
                    "pick4": p4
                }
            }
            
            apply_basic_guardrails(
                step_name="PrevCandadoStep",
                input_data=data,
                output_data=output,
                required_output_keys=["prev_candado"]
            )
            
            return output
            
        except Exception as e:
            raise StepError("Unhandled", f"PrevCandadoStep fallo: {e}")


