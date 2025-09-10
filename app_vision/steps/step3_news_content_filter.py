# ============================================
# 📌 STEP 3: FILTRO DE CONTENIDO SOCIAL/EMOCIONAL
# Step de FSM que filtra contenido alineado con mensaje del sorteo anterior
# ============================================

from __future__ import annotations
from typing import Dict, Any, List
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.news_content_filter import classify_articles

@register_step("NewsContentFilterStep")
class NewsContentFilterStep(Step):
    """
    Step que filtra contenido social/emocional sin lotería,
    alineado con el mensaje del sorteo anterior.
    """
    
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        # URLs ya validadas por NewsGuarded (sin fechas viejas, sin duplicados, etc.)
        urls: List[str] = data.get("valid_news_urls") or []
        if not urls:
            raise StepError("InputError", "No hay URLs válidas para filtrar.")

        # Guía del mensaje del sorteo anterior (SubliminalGuarded)
        guidance = {
            "topics": data.get("subliminal_topics") or [],
            "keywords_used": data.get("subliminal_keywords") or [],
            "families_used": data.get("subliminal_families") or []
        }

        # Configuración
        rules_path = data.get("rules_path") or "plans/news_content_rules.yaml"
        top_k = int(data.get("top_k", 24))
        
        # Filtrar contenido
        res = classify_articles(urls, rules_path, guidance, top_k)

        # Verificar que quedó contenido utilizable
        if res["metrics"]["kept"] == 0:
            raise StepError(
                "ContentFilterZero", 
                "Tras filtrar lotería y no-social, no quedó contenido utilizable."
            )

        return {
            "selected_articles": res["selected"],
            "metrics": res["metrics"],
            "guidance_used": res["guidance_used"],
            "filtered_count": res["metrics"]["kept"],
            "buckets": res["metrics"]["buckets"]
        }





