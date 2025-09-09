from __future__ import annotations
import os, json, hashlib
from typing import Dict, Any
from app_vision.engine.contracts import Step, StepContext, StepError, StepResult
from app_vision.engine.fsm import register_step

@register_step("StepZFinalize")
class StepZFinalize(Step):
    name = "stepZ_finalize"
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> StepResult:
        art_dir = os.path.join(ctx.state_dir, "artifacts", ctx.run_id)
        os.makedirs(art_dir, exist_ok=True)
        manifest = {}
        for root, _, files in os.walk(art_dir):
            for fn in files:
                path = os.path.join(root, fn)
                with open(path, "rb") as f:
                    h = hashlib.sha256(f.read()).hexdigest()
                manifest[fn] = {"sha256": h, "bytes": os.path.getsize(path)}
        with open(os.path.join(art_dir, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        return {"manifest_files": len(manifest)}





