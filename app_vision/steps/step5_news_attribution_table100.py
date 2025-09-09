from __future__ import annotations
from typing import Dict, Any, List
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.news_attribution_table100 import attribute_news_to_table100

@register_step("NewsAttributionTable100Step")
class NewsAttributionTable100Step(Step):
    """
    Paso 5 oficial: atribución de noticias a la Tabla 100 Universal.
    Inputs esperados:
      - selected_news: List[ {title, final_url/url, (text opcional), bucket, score} ]
      - guidance: { topics, keywords, families }  (del Paso 3)
      - min_attr: int (mínimo de números por encima de threshold para auditor OK)
      - threshold: float (umbral para 'fuerte')
    Output:
      - attribution: { per_article, global_rank, auditor }
    """
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        selected: List[Dict[str, Any]] = data.get("selected_news") or []
        guidance: Dict[str, Any] = data.get("guidance") or {}
        min_attr = int(data.get("min_attr", 3))
        try:
            threshold = float(data.get("threshold", 0.6))
        except Exception:
            threshold = 0.6

        # No fallar en vacío: devolver auditoría explicando la causa
        res = attribute_news_to_table100(selected, guidance, min_attr=min_attr, threshold=threshold)
        if not res["per_article"]:
            # No abortamos el run; devolvemos auditoría clara
            return {"attribution": res, "status": "OK_EMPTY"}
        return {"attribution": res, "status": "OK"}



