# app_vision/steps/step_build_candado_context.py
from __future__ import annotations
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.guardrails import apply_basic_guardrails

def _d(d: str) -> datetime:
    return datetime.strptime(str(d).split("T",1)[0].replace("/","-"), "%Y-%m-%d")

def _ds(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")

def _last2_p3(nums: List[int]) -> str:
    assert len(nums)==3
    return f"{nums[1]}{nums[2]}"

def _last2_p4(nums4: Optional[List[int]]) -> Optional[str]:
    if not nums4: return None
    return f"{nums4[2]}{nums4[3]}"

def _pick(draws: List[Dict[str,Any]], date: str, block: str) -> Optional[Dict[str,Any]]:
    for d in draws:
        if str(d.get("date")) == date and str(d.get("block")).upper() == block.upper():
            return d
    return None

def _mk_item(slot: str, src: Optional[Dict[str,Any]], other_src: Optional[Dict[str,Any]]) -> Dict[str,Any]:
    if not src:
        return {"slot": slot, "missing": True, "why": "no source draw"}
    fijo = _last2_p3(src["numbers"])
    corr = _last2_p4(src.get("pick4"))
    extra = _last2_p3(other_src["numbers"]) if other_src else None
    trio = [x for x in [fijo, corr, extra] if x]
    parles = []
    for i in range(len(trio)):
        for j in range(i+1, len(trio)):
            parles.append([trio[i], trio[j]])
    return {
        "slot": slot,
        "date": src["date"],
        "block": src["block"],
        "fijo2d": fijo,
        "corrido2d": corr,
        "extra2d": extra,
        "candado": trio,
        "parles": parles,
        "source": src.get("source","flalottery.com")
    }

@register_step("BuildCandadoContextStep")
class BuildCandadoContextStep(Step):
    """
    IN:
      - draws: [{date:'YYYY-MM-DD', block:'MID'|'EVE', numbers:[3], pick4:[4]? , source?...}, ...]
      - for_block: 'AM'|'MID'|'EVE'  (bloque en curso, ET)
    OUT:
      - candado_context: { for_block, items:[ ... ] }
    Regla Cuba (operativa):
      AM run  → 3 candados de D-1 (AM~EVE(D-2), MID(D-1), EVE(D-1))
      MID run → AM(hoy=EVE(D-1)) + 3 de D-1
      EVE run → AM(hoy=EVE(D-1)) + MID(hoy) + 3 de D-1
    * Los "AM" se mapean a EVE del día previo (no existe AM como draw oficial Florida).
    """
    def run(self, ctx: StepContext, data: Dict[str,Any]) -> Dict[str,Any]:
        # Aplicar guardrails de entrada
        apply_basic_guardrails(
            step_name="BuildCandadoContextStep",
            input_data=data,
            output_data={},
            required_input_keys=["draws", "for_block"]
        )
        
        draws: List[Dict[str,Any]] = data.get("draws") or []
        if not draws:
            raise StepError("InputError","BuildCandadoContextStep: faltan draws.")
        for_block = str(data.get("for_block","")).upper()
        if for_block not in ("AM","MID","EVE"):
            raise StepError("InputError", f"for_block inválido: {for_block}")

        # Ordena por fecha y bloque (EVE > MID para desempate descendente)
        draws_sorted = sorted(draws, key=lambda x: (_d(x["date"]), 2 if x["block"].upper()=="EVE" else 1), reverse=True)
        newest_date = _d(draws_sorted[0]["date"])
        d0 = _ds(newest_date)              # hoy según draws
        d_1 = _ds(newest_date - timedelta(days=1))
        d_2 = _ds(newest_date - timedelta(days=2))

        # Accesos rápidos
        mid_d0 = _pick(draws_sorted, d0, "MID")
        eve_d0 = _pick(draws_sorted, d0, "EVE")
        mid_d1 = _pick(draws_sorted, d_1, "MID")
        eve_d1 = _pick(draws_sorted, d_1, "EVE")
        eve_d2 = _pick(draws_sorted, d_2, "EVE")

        items: List[Dict[str,Any]] = []

        if for_block == "AM":
            # Solo los 3 de D-1 (AM ~ EVE(D-2))
            items.append(_mk_item("AM_D-1",  eve_d2, mid_d1))  # usa MID(D-1) como "otro"
            items.append(_mk_item("MID_D-1", mid_d1,  eve_d1))
            items.append(_mk_item("EVE_D-1", eve_d1,  mid_d1))

        elif for_block == "MID":
            # AM hoy (EVE D-1) + 3 de D-1
            items.append(_mk_item("AM_today", eve_d1, mid_d0))  # AM(hoy) := EVE(D-1)
            items.append(_mk_item("AM_D-1",   eve_d2, mid_d1))
            items.append(_mk_item("MID_D-1",  mid_d1, eve_d1))
            items.append(_mk_item("EVE_D-1",  eve_d1, mid_d1))

        else:  # EVE
            # AM hoy (EVE D-1) + MID hoy + 3 de D-1
            items.append(_mk_item("AM_today",  eve_d1, mid_d0))
            items.append(_mk_item("MID_today", mid_d0, eve_d0))
            items.append(_mk_item("AM_D-1",    eve_d2, mid_d1))
            items.append(_mk_item("MID_D-1",   mid_d1, eve_d1))
            items.append(_mk_item("EVE_D-1",   eve_d1, mid_d1))

        output = {"candado_context": {"for_block": for_block, "items": items}}
        
        # Validar output con guardrails (sin sources_allowlist para este step)
        apply_basic_guardrails(
            step_name="BuildCandadoContextStep",
            input_data=data,
            output_data=output,
            required_output_keys=["candado_context"]
        )
        
        return output
