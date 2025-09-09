from __future__ import annotations
from typing import Dict, Any, List
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.news_selector25 import select_min25

@register_step("NewsSelector25Step")
class NewsSelector25Step(Step):
    """
    Garantiza >=25 noticias reales alineadas a la guía del Paso 3, sin inventar datos.
    Inputs:
      - valid_news: List[{title, url|final_url, (summary|text opc)}]  # del NewsGuardedStep
      - guidance: {topics, keywords, families, guide_terms?}         # del Paso 3
      - start_threshold: float (default 0.6)
      - min_keep: int (default 25)
      - require_body: bool (default False)  # si True, exige summary/text
    Output:
      - selected_25: List[...]
      - selector_audit: {...}
    """
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        news: List[Dict[str, Any]] = data.get("valid_news") or []
        guidance: Dict[str, Any] = data.get("guidance") or {}
        start = float(data.get("start_threshold", 0.6))
        min_keep = int(data.get("min_keep", 25))
        require_body = bool(data.get("require_body", False))

        if not news:
            # No fallamos: cumplimos regla "datos reales o vacío con motivo"
            return {
                "selected_25": [],
                "selector_audit": {
                    "input_total": 0,
                    "scored_total": 0,
                    "selected": 0,
                    "threshold_chosen": None,
                    "fallback_applied": False,
                    "reasons": ["no_valid_news_from_previous_step"],
                    "guide_terms_used": []
                }
            }

        res = select_min25(news, guidance, start_thr=start, min_keep=min_keep, min_body=require_body)
        return {"selected_25": res["selected"], "selector_audit": res["audit"]}




