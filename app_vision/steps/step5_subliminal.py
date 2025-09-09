from __future__ import annotations
from typing import Dict, Any
from app_vision.engine.contracts import Step, StepContext, StepResult, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.subliminal_guarded import subliminal_guarded_from_pick3

@register_step("Step5Subliminal")
class Step5Subliminal(Step):
    name = "step5_subliminal"
    def validate_inputs(self, data: Dict[str, Any]):
        req = ("prev_draw","label","game")
        missing = [k for k in req if k not in data]
        if missing: 
            raise StepError("InputError", f"Faltan campos: {missing}")
        d = data["prev_draw"]
        if not (isinstance(d, list) and len(d)==3 and all(isinstance(x,int) for x in d)):
            raise StepError("InputError", "prev_draw debe ser [int,int,int]")

    def run(self, ctx: StepContext, data: Dict[str, Any]) -> StepResult:
        self.validate_inputs(data)
        out = subliminal_guarded_from_pick3(tuple(data["prev_draw"]), data["label"])
        return {
            "poem": out.poem,
            "topics": out.topics,
            "hebrews": out.hebrew_labels,
            "trace": out.trace,
            "provenance": {
                "step_version": "1.1.0",
                "seed": ctx.seed,
                "lock_hash": ctx.cfg.get("_lock_hash",""),
                "plan_path": ctx.plan_path,
            }
        }





