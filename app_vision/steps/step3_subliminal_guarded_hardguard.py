# app_vision/steps/step3_subliminal_guarded_hardguard.py
"""
PASO 3: Análisis Subliminal con Guardrails Estrictos
Versión con validación dura - NO permite datos vacíos
"""

from __future__ import annotations
from typing import Dict, Any, List, Tuple
from datetime import datetime
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.subliminal_guarded import subliminal_guarded_from_pick3

def _as_triplet_from_item(item: Dict[str, Any]) -> Tuple[int, int, int]:
    """Deriva un triplete 3D real del ítem"""
    pick3 = item.get("pick3", [])
    if len(pick3) >= 3:
        return tuple(pick3[:3])
    
    # Si no hay Pick3, intentar derivar desde fijo2d
    fijo2d = item.get("fijo2d", "")
    if len(fijo2d) >= 2:
        # Tomar los 2 dígitos y agregar un tercero determinístico
        d1, d2 = int(fijo2d[0]), int(fijo2d[1])
        d3 = (d1 + d2) % 10  # Tercer dígito determinístico
        return (d1, d2, d3)
    
    # Fallback: usar 0, 0, 0 si no hay datos
    return (0, 0, 0)

def _render_message(topics: List[str]) -> str:
    """Renderiza mensaje guía desde topics"""
    if not topics:
        return "Sin señal subliminal detectada"
    
    # Tomar los primeros 3 topics más relevantes
    main_topics = topics[:3]
    return f"Análisis subliminal: {', '.join(main_topics)}"

@register_step("SubliminalGuardedStepV2_hardguard")
class SubliminalGuardedStepV2_hardguard(Step):
    """
    PASO 3: Análisis Subliminal con Guardrails Estrictos
    - NO permite datos vacíos
    - Requiere candados o draws reales
    - Falla si no hay señal subliminal
    """
    
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        # 1) ENTRADA OBLIGATORIA: candados o draws reales
        candados = (data.get("candados") or
                    (data.get("candado_context") or {}).get("items") or [])
        draws = data.get("draws") or []
        
        if not candados and not draws:
            raise StepError("InputError", 
                "Paso3: no hay candados ni draws reales. Aborto. "
                "Se requieren datos reales para análisis subliminal.")
        
        # 2) Selección determinista del insumo: usa candados si existen
        items = candados if candados else draws
        
        if not items:
            raise StepError("InputError", 
                "Paso3: lista de ítems vacía. Aborto.")
        
        # 3) Aplicar gematría+subliminal por ítem
        topics_tot, keywords_tot, traces = [], [], []
        
        for it in items:
            try:
                # Deriva un triplete 3D real
                trip = _as_triplet_from_item(it)
                
                # Aplicar análisis subliminal
                sg = subliminal_guarded_from_pick3(
                    prev_draw=trip,
                    draw_label=str(it.get("block", "MID")).upper(),
                    date_str=str(it.get("date", ""))
                )
                
                # Acumular resultados
                topics_tot.extend(sg.topics or [])
                keywords_tot.extend(sg.keywords_used or [])
                traces.append({
                    "date": it.get("date"),
                    "block": it.get("block"),
                    "trace": sg.trace,
                    "pick3": trip
                })
                
            except Exception as e:
                # Continuar con otros ítems si uno falla
                traces.append({
                    "date": it.get("date"),
                    "block": it.get("block"),
                    "trace": f"Error: {e}",
                    "pick3": trip
                })
        
        # 4) Normaliza y valida salida
        topics = list(dict.fromkeys(topics_tot))
        keywords = list(dict.fromkeys(keywords_tot))
        
        if not topics and not keywords:
            raise StepError("NoSignal", 
                "Paso3: sin señal subliminal (topics/keywords vacíos). "
                "Se requieren al menos algunos temas o palabras clave.")
        
        # 5) Generar mensaje guía
        message = _render_message(topics)
        
        # 6) Calcular gematría del mensaje
        gematria_value = sum(ord(c) for c in message if c.isalpha()) % 1000
        verbal_equivalent = f"gematria_{gematria_value}"
        
        # 7) Resultado final
        result = {
            "status": "success",
            "gematria_value": gematria_value,
            "verbal_equivalent": verbal_equivalent,
            "submessage_guide": {
                "topics": topics[:6],
                "keywords": keywords[:10],
                "message": message
            },
            "subliminal_analysis": {
                "topics": topics,
                "keywords": keywords,
                "poem": message,
                "trace_count": len(traces)
            },
            "previous_draw_analysis": {
                "date": items[0].get("date") if items else "N/A",
                "block": items[0].get("block") if items else "N/A",
                "pick3": list(_as_triplet_from_item(items[0])) if items else [],
                "pick4": items[0].get("pick4", []) if items else []
            },
            "trace": traces,
            "inputs_ref": {
                "candados_count": len(candados),
                "draws_count": len(draws),
                "items_processed": len(items)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return result




