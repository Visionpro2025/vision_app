from __future__ import annotations
from typing import Dict, Any, List
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.guardrails import apply_basic_guardrails

@register_step("PrevDayCandadosExportStep")
class PrevDayCandadosExportStep(Step):
    """
    Exporta los 3 candados del día anterior en formato UI-friendly.
    Incluye funcionalidad para copiar todos los parlés del día.
    """
    
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        # Aplicar guardrails de entrada
        apply_basic_guardrails(
            step_name="PrevDayCandadosExportStep",
            input_data=data,
            output_data={},
            required_input_keys=["prev_day_candados"]
        )
        
        prev_day_data = data.get("prev_day_candados", {})
        candados = prev_day_data.get("candados", [])
        date = prev_day_data.get("date", "N/A")
        
        # Procesar cada candado del día anterior
        processed_candados = []
        all_parles = []
        
        for candado in candados:
            if candado.get("missing"):
                processed_candados.append({
                    "slot": candado["slot"],
                    "status": "missing",
                    "reason": candado.get("why", "Datos no disponibles"),
                    "candado": [],
                    "parles": [],
                    "fijo2d": None,
                    "corrido2d": None,
                    "extra2d": None
                })
            else:
                # Candado completo
                parles = candado.get("parles", [])
                all_parles.extend(parles)
                
                processed_candados.append({
                    "slot": candado["slot"],
                    "status": "complete",
                    "date": candado.get("date"),
                    "block": candado.get("block"),
                    "candado": candado.get("candado", []),
                    "parles": parles,
                    "fijo2d": candado.get("fijo2d"),
                    "corrido2d": candado.get("corrido2d"),
                    "extra2d": candado.get("extra2d"),
                    "pick3": candado.get("pick3", []),
                    "pick4": candado.get("pick4"),
                    "source": candado.get("source")
                })
        
        # Generar resumen del día
        complete_candados = [c for c in processed_candados if c["status"] == "complete"]
        missing_candados = [c for c in processed_candados if c["status"] == "missing"]
        
        # Crear string de parlés para copiar
        all_parles_str = ""
        if all_parles:
            parles_pairs = [f"{p[0]}-{p[1]}" for p in all_parles]
            all_parles_str = " | ".join(parles_pairs)
        
        # Validar output
        output = {
            "prev_day_export": {
                "date": date,
                "candados": processed_candados,
                "summary": {
                    "total_slots": len(processed_candados),
                    "complete": len(complete_candados),
                    "missing": len(missing_candados),
                    "all_parles": all_parles,
                    "all_parles_string": all_parles_str,
                    "total_parles": len(all_parles)
                },
                "ui_ready": True
            }
        }
        
        apply_basic_guardrails(
            step_name="PrevDayCandadosExportStep",
            input_data=data,
            output_data=output,
            required_output_keys=["prev_day_export"]
        )
        
        return output


