from __future__ import annotations
import os, json
from typing import Dict, Any
from app_vision.engine.contracts import Step, StepContext, StepResult, StepError
from app_vision.engine.fsm import register_step

@register_step("Step6Artifacts")
class Step6Artifacts(Step):
    name = "step6_artifacts"
    def validate_inputs(self, data: Dict[str, Any]):
        if "poem" not in data or "topics" not in data:
            raise StepError("InputError", "Se requieren 'poem' y 'topics' para guardar.")

    def run(self, ctx: StepContext, data: Dict[str, Any]) -> StepResult:
        self.validate_inputs(data)
        art_dir = os.path.join(ctx.state_dir, "artifacts", ctx.run_id)
        os.makedirs(art_dir, exist_ok=True)
        with open(os.path.join(art_dir, "poem.txt"), "w", encoding="utf-8") as f:
            f.write(data["poem"])
        with open(os.path.join(art_dir, "topics.json"), "w", encoding="utf-8") as f:
            json.dump(data["topics"], f, ensure_ascii=False, indent=2)
        return {"saved_to": art_dir}





