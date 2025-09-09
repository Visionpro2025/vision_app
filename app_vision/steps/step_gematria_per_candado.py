# app_vision/steps/step_gematria_per_candado.py
from __future__ import annotations
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.guardrails import apply_basic_guardrails

def _as_triplet_from_item(item: Dict[str, Any]) -> Tuple[int,int,int]:
    """
    Prioridad:
      1) item['pick3'] → [d1,d2,d3] reales.
      2) item['fijo2d'] → 'ab' e inferir c = (a+b)%10 para cerrar 3D de forma determinista.
    """
    p3 = item.get("pick3")
    if isinstance(p3, (list,tuple)) and len(p3)==3 and all(isinstance(x,int) and 0<=x<=9 for x in p3):
        return (int(p3[0]), int(p3[1]), int(p3[2]))
    fijo2d = str(item.get("fijo2d","")).strip()
    if len(fijo2d)==2 and fijo2d.isdigit():
        a, b = int(fijo2d[0]), int(fijo2d[1])
        c = (a + b) % 10   # cierre determinista
        return (a, b, c)
    raise StepError("InputError", f"Candado sin pick3 válido ni fijo2d usable: {item}")

def _iso(d: str) -> str:
    # Normaliza fecha a 'YYYY-MM-DD'
    d = str(d).split("T",1)[0].replace("/","-")
    datetime.strptime(d, "%Y-%m-%d")  # valida
    return d

def _subliminal_guarded_from_pick3(prev_draw: Tuple[int,int,int], draw_label: str, date_str: str) -> Dict[str, Any]:
    """
    Simula el análisis subliminal determinista basado en Pick3.
    En producción, esto llamaría al módulo real de subliminal.
    """
    # Análisis determinista basado en los números
    d1, d2, d3 = prev_draw
    
    # Topics basados en patrones numéricos
    topics = []
    if d1 == d2 == d3:
        topics.extend(["repeticion", "simetria", "estabilidad"])
    elif d1 + d2 + d3 == 15:
        topics.extend(["equilibrio", "armonia", "complecion"])
    elif d1 + d2 + d3 > 20:
        topics.extend(["intensidad", "dramatismo", "transformacion"])
    else:
        topics.extend(["progresion", "evolucion", "cambio"])
    
    # Keywords basados en suma y patrones
    suma = d1 + d2 + d3
    keywords = []
    if suma % 2 == 0:
        keywords.extend(["par", "balance", "dualidad"])
    else:
        keywords.extend(["impar", "singularidad", "unicidad"])
    
    # Familias numéricas
    families = []
    if d1 <= 3:
        families.append("inicio")
    if d2 >= 7:
        families.append("culminacion")
    if d3 == 0:
        families.append("renovacion")
    
    # Poema determinista
    poem = f"En {draw_label} del {date_str}, los números {d1}-{d2}-{d3} susurran: {' '.join(topics[:2])}"
    
    return {
        "topics": topics,
        "keywords_used": keywords,
        "poem": poem,
        "families_used": families,
        "input_draw": list(prev_draw),
        "draw_label": draw_label,
        "trace": f"Pick3={prev_draw} → topics={topics[:2]}"
    }

@register_step("GematriaPerCandadoStep")
class GematriaPerCandadoStep(Step):
    """
    IN:
      - candados: [
          { "date":"YYYY-MM-DD", "block":"AM|MID|EVE",
            "candado":["NN","NN"...], "fijo2d":"NN",
            "pick3":[d1,d2,d3]? , ... (metadatos opcionales)
          }, ...
        ]
    OUT:
      - per_candado: [
          { slot?, date, block, candado, topics, keywords, poem, seed_trace, weight_hint }
        ]
    """
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        # Aplicar guardrails de entrada
        apply_basic_guardrails(
            step_name="GematriaPerCandadoStep",
            input_data=data,
            output_data={},
            required_input_keys=["candados"]
        )
        
        items: List[Dict[str,Any]] = data.get("candados") or data.get("candado_context") or []
        if isinstance(items, dict) and "items" in items:
            items = items["items"]
        if not items:
            raise StepError("InputError", "GematriaPerCandadoStep: no llegaron candados.")

        out: List[Dict[str,Any]] = []
        for it in items:
            try:
                date = _iso(it.get("date"))
                block = str(it.get("block","")).upper() or "MID"
                trip = _as_triplet_from_item(it)
                sg = _subliminal_guarded_from_pick3(prev_draw=trip, draw_label=block, date_str=date)
                # Peso sugerido por recencia (se ajusta luego en la fusión):
                weight_hint = 1.0  # se normaliza en la fusión por fecha/bloque
                out.append({
                    "slot": it.get("slot"),
                    "date": date,
                    "block": block,
                    "candado": list(it.get("candado") or []),
                    "fijo2d": it.get("fijo2d"),
                    "pick3": list(trip),
                    "topics": list(sg["topics"]),
                    "keywords": list(sg["keywords_used"]),
                    "poem": sg["poem"],
                    "families": list(sg["families_used"]),
                    "seed_trace": {"input_draw": sg["input_draw"], "label": sg["draw_label"], "trace": sg["trace"]},
                    "weight_hint": weight_hint
                })
            except StepError:
                raise
            except Exception as e:
                raise StepError("Unhandled", f"Fallo procesando candado {it}: {e}")
        
        # Validar output con guardrails
        output = {"per_candado": out}
        apply_basic_guardrails(
            step_name="GematriaPerCandadoStep",
            input_data=data,
            output_data=output,
            required_output_keys=["per_candado"],
            sources_allowlist=["flalottery.com", "floridalottery.com"]
        )
        
        return output
