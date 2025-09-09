# app_vision/steps/step_guide_message_fuse.py
from __future__ import annotations
from typing import Dict, Any, List, Tuple
from datetime import datetime
from collections import Counter, defaultdict
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.guardrails import apply_basic_guardrails

def _parse_date(d: str) -> datetime:
    d = str(d).split("T",1)[0].replace("/","-")
    return datetime.strptime(d, "%Y-%m-%d")

def _score_items(per_candado: List[Dict[str,Any]], for_block: str|None) -> Tuple[Dict[str,float], Dict[str,float]]:
    """
    Devuelve (score_topics, score_keywords) tras ponderar:
      - Recencia: fecha máxima = 1.0; D-1 = 0.75; >1 día = 0.6
      - Bonus por bloque (si se provee for_block):
         * for_block='MID'  → bonus AM: +0.15
         * for_block='EVE'  → bonus AM: +0.15, bonus MID: +0.10
    """
    if not per_candado:
        return {}, {}

    dates = [_parse_date(x["date"]) for x in per_candado]
    dmax = max(dates)

    bonus_by_block = defaultdict(float)
    fc = (for_block or "").upper()
    if fc == "MID":
        bonus_by_block["AM"] = 0.15
    elif fc == "EVE":
        bonus_by_block["AM"] = 0.15
        bonus_by_block["MID"] = 0.10

    score_topics: Dict[str,float] = defaultdict(float)
    score_keywords: Dict[str,float] = defaultdict(float)

    for it in per_candado:
        dd = _parse_date(it["date"])
        delta = (dmax - dd).days
        recency = 1.0 if delta == 0 else (0.75 if delta == 1 else 0.6)
        bbonus = bonus_by_block[it.get("block","").upper()] if it.get("block") else 0.0
        w = recency + bbonus
        for t in it.get("topics") or []:
            score_topics[t] += w
        for k in it.get("keywords") or []:
            score_keywords[k] += w

    return dict(score_topics), dict(score_keywords)

def _topn(d: Dict[str,float], n: int) -> List[str]:
    return [k for k,_ in sorted(d.items(), key=lambda kv: (-kv[1], kv[0]))[:n]]

def _render_message(topics: List[str]) -> str:
    """Línea ejecutiva breve con los 4–6 topics principales."""
    if not topics:
        return "Sin señal suficiente: continuar acopio con amplio espectro social."
    sel = topics[:6]
    # Plantilla corta, clara:
    return (" · ".join(sel[:2]) + " — " + " ".join(sel[2:])).strip(" —")

@register_step("GuideMessageFuseStep")
class GuideMessageFuseStep(Step):
    """
    IN:
      - per_candado: salida de GematriaPerCandadoStep
      - for_block: 'AM'|'MID'|'EVE' (opcional, bonus de bloque)
      - top_topics: int (default 6)
      - top_keywords: int (default 10)
    OUT:
      - guide: { topics[], keywords[], message, trace[] }
    """
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        # Aplicar guardrails de entrada
        apply_basic_guardrails(
            step_name="GuideMessageFuseStep",
            input_data=data,
            output_data={},
            required_input_keys=["per_candado"]
        )
        
        per_c: List[Dict[str,Any]] = data.get("per_candado") or []
        if not per_c:
            raise StepError("InputError", "GuideMessageFuseStep: falta 'per_candado'.")

        for_block = str(data.get("for_block") or "").upper() or None
        top_topics_n = int(data.get("top_topics", 6))
        top_keywords_n = int(data.get("top_keywords", 10))

        score_topics, score_keywords = _score_items(per_c, for_block)
        topics = _topn(score_topics, top_topics_n)
        keywords = _topn(score_keywords, top_keywords_n)
        message = _render_message(topics)

        trace = []
        for it in per_c:
            tline = f"{it.get('slot') or it['block']} {it['date']} → topics={list(it.get('topics') or [])[:3]}..."
            trace.append(tline)

        guide = {
            "topics": topics,
            "keywords": keywords,
            "message": message,
            "trace": trace,
            "for_block": for_block
        }
        
        # Validar output con guardrails
        output = {"guide": guide}
        apply_basic_guardrails(
            step_name="GuideMessageFuseStep",
            input_data=data,
            output_data=output,
            required_output_keys=["guide"],
            sources_allowlist=["flalottery.com", "floridalottery.com"]
        )
        
        return output
