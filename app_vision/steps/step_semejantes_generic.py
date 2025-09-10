from __future__ import annotations
from typing import Dict, Any, List
from app_vision.engine.contracts import Step, StepContext, StepResult, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.semejantes import seleccionar_semejantes_generico

@register_step("StepSemejantesGeneric")
class StepSemejantesGeneric(Step):
    name = "step_semejantes_generic"
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> StepResult:
        cfg = data.get("game_cfg") or {}
        max_val = int(cfg.get("max_val", 0))
        externals: List[int] = list(map(int, data.get("externals", [])))
        exclude: List[int]   = list(map(int, data.get("exclude", [])))
        anchors: List[int]   = list(map(int, data.get("anchors", [])))

        if not max_val:
            raise StepError("ConfigError", "game_cfg.max_val ausente")

        if not externals:
            return {"ranked": [], "candidates": [], "note": "sin externals"}

        ranked = seleccionar_semejantes_generico(
            externals, rango_max=max_val, anchors=anchors, exclude=exclude, top_k=16
        )
        candidates = [r["value"] for r in ranked]
        return {"ranked": ranked, "candidates": candidates}






