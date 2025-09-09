# app_vision/steps/step_prev_day_candados_export.py
from __future__ import annotations
from typing import Dict, Any, List, Tuple
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.guardrails import apply_basic_guardrails

@register_step("PrevDayCandadosExportStep")
class PrevDayCandadosExportStep(Step):
    """
    Exporta los candados del día anterior en formato UI-friendly con tarjetas.
    Inputs:
      - candado_context: payload de BuildCandadoContextStep
      - for_block: 'AM'|'MID'|'EVE' (bloque actual)
    Output:
      - prev_day_export: {
          for_block: str,
          date: "YYYY-MM-DD",
          candados: [
            {slot, status, candado:[NN,NN,NN?], parles:[[NN,NN],...], fijo2d, corrido2d?, extra2d?, copy_button: true},
            ...
          ],
          summary: {complete: int, missing: int, all_parles_string: str}
        }
    """
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        # Aplicar guardrails de entrada
        apply_basic_guardrails(
            step_name="PrevDayCandadosExportStep",
            input_data=data,
            output_data={},
            required_input_keys=["candado_context"]
        )
        
        candado_context = data.get("candado_context") or {}
        for_block = data.get("for_block", candado_context.get("for_block", "MID"))
        items = candado_context.get("items", [])
        
        if not items:
            raise StepError("InputError", "PrevDayCandadosExportStep: falta 'candado_context.items' válido.")

        # Filtrar solo los candados del día anterior (D-1)
        prev_day_items = [item for item in items if "D-1" in item.get("slot", "")]
        
        exported_candados = []
        all_parles: List[Tuple[str, str]] = []
        complete_count = 0
        missing_count = 0

        for item in prev_day_items:
            slot = item.get("slot", "N/A")
            status = "complete" if not item.get("missing", False) else "missing"
            reason = item.get("why") if status == "missing" else None
            candado_list = item.get("candado", [])
            parles_list = item.get("parles", [])

            exported_candados.append({
                "slot": slot,
                "status": status,
                "reason": reason,
                "candado": candado_list,
                "parles": parles_list,
                "date": item.get("date"),
                "block": item.get("block"),
                "fijo2d": item.get("fijo2d"),
                "corrido2d": item.get("corrido2d"),
                "extra2d": item.get("extra2d"),
                "copy_button": True  # Siempre mostrar botón copiar
            })

            if status == "complete":
                complete_count += 1
                all_parles.extend(parles_list)
            else:
                missing_count += 1

        # Deduplicar parlés y formatear
        seen_parles = set()
        unique_parles_str_list = []
        for p in all_parles:
            sorted_p = tuple(sorted(p))
            if sorted_p not in seen_parles:
                seen_parles.add(sorted_p)
                unique_parles_str_list.append(f"{p[0]}-{p[1]}")
        all_parles_string = ", ".join(unique_parles_str_list)

        # Obtener fecha del día anterior
        prev_date = "2025-01-07"  # En producción, calcular desde los items
        if prev_day_items:
            prev_date = prev_day_items[0].get("date", "2025-01-07")

        output = {
            "prev_day_export": {
                "for_block": for_block,
                "date": prev_date,
                "candados": exported_candados,
                "summary": {
                    "complete": complete_count,
                    "missing": missing_count,
                    "all_parles_string": all_parles_string
                }
            }
        }

        # Validar output con guardrails
        apply_basic_guardrails(
            step_name="PrevDayCandadosExportStep",
            input_data=data,
            output_data=output,
            required_output_keys=["prev_day_export"]
        )

        return output


