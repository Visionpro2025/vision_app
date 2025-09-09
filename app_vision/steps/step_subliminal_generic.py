from __future__ import annotations
from typing import Dict, Any, List, Tuple
from app_vision.engine.contracts import Step, StepContext, StepResult, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.subliminal_guarded import subliminal_guarded_from_pick3

@register_step("StepSubliminalGeneric")
class StepSubliminalGeneric(Step):
    name = "step_subliminal_generic"

    def run(self, ctx: StepContext, data: Dict[str, Any]) -> StepResult:
        cfg = data.get("game_cfg") or {}
        digits_mode = bool(cfg.get("digits_mode", False))
        label = data.get("label", "RUN")
        poem, topics, trace, hebs = "", [], [], []

        if digits_mode:
            prev_draw = data.get("prev_draw")
            if not isinstance(prev_draw, list) or not all(isinstance(x, int) for x in prev_draw):
                raise StepError("InputError", "prev_draw ausente o inválido para modo dígitos")
            tri = tuple(prev_draw[:3])
            out = subliminal_guarded_from_pick3(tri, label=label)
            poem, topics, trace, hebs = out.poem, out.topics, out.trace, out.hebrew_labels
        else:
            candidates: List[int] = list(map(int, data.get("candidates", [])))
            if not candidates:
                poem = f"({label}) Sin candidatos; escucha el silencio del sorteo."
                topics = ["anuncio","señal","comunicado"]
                trace = ["no candidates"]
                hebs = []
            else:
                tri: Tuple[int,int,int] = (candidates[0] % 10, (candidates[1] if len(candidates)>1 else 0) % 10, (candidates[2] if len(candidates)>2 else 0) % 10)
                out = subliminal_guarded_from_pick3(tri, label=label)
                poem, topics, trace, hebs = out.poem, topics_from_candidates(candidates, out.topics), out.trace, out.hebrew_labels

        return {"poem": poem, "topics": topics, "hebrews": hebs, "trace": trace}

def topics_from_candidates(cands: List[int], base_topics: List[str]) -> List[str]:
    extra = []
    for c in cands[:6]:
        if c % 10 == 0: extra.append("lanzamiento")
        if c in (10,20,30,40,50,60,70): extra.append("anuncio")
    dedup = []
    for w in (base_topics + extra):
        if w not in dedup:
            dedup.append(w)
    return dedup[:8]





