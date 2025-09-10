# ============================================
# 🚀 STEP: FETCH DE NOTICIAS CORREGIDO
# Reemplazo/implementación del paso de ingesta de noticias
# Usa ProfessionalNewsIngestion (RSS) para traer URLs
# ============================================

from __future__ import annotations
from typing import Dict, Any, List
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.news_ingestion import ProfessionalNewsIngestion

@register_step("YourNewsFetchStep")
class YourNewsFetchStep(Step):
    """
    Reemplazo/implementación del paso de ingesta:
    - Usa ProfessionalNewsIngestion (RSS) para traer URLs.
    - Si guidance_terms se provee, puede filtrar 'emocionales'.
    Inputs:
      feeds: lista de URLs RSS
      max_per_feed: int
      mode: 'collect' | 'emotional' (default 'collect')
      guidance_terms: lista de strings (opcional, para 'emotional')
    Output:
      urls: List[str]
      meta: {count, sources, log}
    """
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        feeds: List[str] = data.get("feeds") or []
        if not feeds:
            raise StepError("InputError", "Feeds RSS no provistos en inputs.feeds")

        mode = (data.get("mode") or "collect").lower().strip()
        max_per_feed = int(data.get("max_per_feed", 20))
        guidance_terms = data.get("guidance_terms") or []

        ing = ProfessionalNewsIngestion(feeds=feeds, max_per_feed=max_per_feed)

        try:
            if mode == "emotional":
                res = ing.search_emotional_news(guidance_terms)
            else:
                res = ing.collect_news()
        except AttributeError as e:
            # Si el pipeline viejo llamaba métodos inexistentes, aquí nunca pasará,
            # porque estos métodos ya existen. Dejamos error explícito por si rebotan.
            raise StepError("ConfigError", f"Método no disponible: {e}")

        # Si no trajo nada, devolvemos igualmente log para auditar
        return {
            "urls": res.get("urls", []),
            "count": res.get("count", 0),
            "sources": res.get("sources", []),
            "log": res.get("log", [])
        }





