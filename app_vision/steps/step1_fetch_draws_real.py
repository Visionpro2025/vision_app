# app_vision/steps/step1_fetch_draws_real.py
from __future__ import annotations
from typing import Dict, Any, List
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.fl_pick3_fetcher import fetch_last_n

@register_step("FetchFLPick3RealStep")
class FetchFLPick3RealStep(Step):
    """
    Trae N sorteos REALES de Florida Pick 3 (oficial). Prohíbe simulación.
    Inputs:
      - min_results: int (default 5)
    Output:
      - draws: [{date:'YYYY-MM-DD', block:'MID|EVE', numbers:[d1,d2,d3], fireball:int|None, source:url}]
    Falla si no se alcanzan min_results.
    """
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        n = int(data.get("min_results", 5))
        draws = fetch_last_n(n)
        if len(draws) < n:
            raise StepError("InputError", f"Solo se obtuvieron {len(draws)} sorteos reales; se requieren {n}.")
        return {"draws": draws, "count": len(draws)}




