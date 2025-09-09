from __future__ import annotations
from typing import Dict, Any, List
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.guardrails import apply_basic_guardrails
from app_vision.modules.candado_model import Candado

def _last2(nums: List[int]) -> str:
    """Extrae last2 del Pick3"""
    return f"{nums[1]}{nums[2]}"

@register_step("BuildLast5CandadosStep")
class BuildLast5CandadosStep(Step):
    """
    Construye los últimos 5 candados a partir de draws reales.
    Regla: por cada bloque, candado = { last2(P3 bloque), last2(P4 bloque)?, last2(P3 otro bloque)? }
    """
    
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        # Aplicar guardrails de entrada
        apply_basic_guardrails(
            step_name="BuildLast5CandadosStep",
            input_data=data,
            output_data={},
            required_input_keys=["draws"]
        )
        
        draws = data.get("draws") or []
        if len(draws) < 5:
            raise StepError("InputError", f"Se requieren ≥5 draws; llegaron {len(draws)}")
        
        out = []
        for i in range(min(5, len(draws))):
            d = draws[i]
            
            # Validar que el draw tiene los datos necesarios
            if len(d.get("numbers", [])) < 3:
                raise StepError("InputError", f"Draw {i} tiene Pick3 incompleto: {d.get('numbers')}")
            
            fijo = _last2(d["numbers"])
            corrido = f"{d['pick4'][2]}{d['pick4'][3]}" if d.get("pick4") and len(d["pick4"]) >= 4 else None
            
            # Buscar otro bloque del mismo día
            extra = None
            for j in range(i+1, min(i+4, len(draws))):
                if draws[j]["date"] == d["date"] and draws[j]["block"] != d["block"]:
                    if len(draws[j].get("numbers", [])) >= 3:
                        extra = _last2(draws[j]["numbers"])
                        break
            
            # Crear candado
            candado = Candado(
                date=str(d["date"]),
                block=str(d["block"]).upper(),
                fijo2d=fijo,
                corrido2d=corrido,
                extra2d=extra,
                pick3=tuple(d["numbers"][:3]),
                pick4=tuple(d["pick4"]) if d.get("pick4") and len(d["pick4"]) >= 4 else None,
                source_p3=d.get("source"),
                source_p4=d.get("source")
            )
            
            out.append(candado.to_dict())
        
        # Validar output
        output = {
            "last5_candados": out,
            "count": len(out),
            "date_range": {
                "first": out[0]["date"] if out else None,
                "last": out[-1]["date"] if out else None
            }
        }
        
        apply_basic_guardrails(
            step_name="BuildLast5CandadosStep",
            input_data=data,
            output_data=output,
            required_output_keys=["last5_candados"]
        )
        
        return output


