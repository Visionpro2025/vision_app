from __future__ import annotations
from typing import Dict, Any, List
from app_vision.engine.contracts import Step, StepContext, StepResult, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.game_registry import get_game_cfg

@register_step("StepRouter")
class StepRouter(Step):
    name = "step_router"
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> StepResult:
        game = data.get("game")
        if not game:
            raise StepError("InputError", "Falta 'game'")
        cfg = get_game_cfg(game)

        externals: List[int] = list(map(int, data.get("externals", [])))
        exclude: List[int]   = list(map(int, data.get("exclude", [])))
        anchors: List[int]   = list(map(int, data.get("anchors", []))) if "anchors" in data else []

        payload = {
            "game_cfg": {
                "name": cfg.name,
                "draw_len": cfg.draw_len,
                "min_val": cfg.min_val,
                "max_val": cfg.max_val,
                "special_len": cfg.special_len,
                "special_min": cfg.special_min,
                "special_max": cfg.special_max,
                "digits_mode": cfg.digits_mode
            },
            "externals": externals,
            "exclude": exclude,
            "anchors": anchors
        }

        if cfg.digits_mode:
            prev_draw = data.get("prev_draw")
            label     = data.get("label")
            if not isinstance(prev_draw, list) or len(prev_draw) != cfg.draw_len or not all(isinstance(x, int) for x in prev_draw):
                raise StepError("InputError", f"prev_draw debe ser lista de {cfg.draw_len} enteros para {cfg.name}")
            if not isinstance(label, str):
                raise StepError("InputError", "Falta 'label'")
            payload["prev_draw"] = prev_draw
            payload["label"] = label
            payload["mode"] = "digits"
        else:
            payload["mode"] = "balls"

        return payload






