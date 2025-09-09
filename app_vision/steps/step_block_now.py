# app_vision/steps/step_block_now.py
from __future__ import annotations
from datetime import datetime, time
from app_vision.engine.contracts import Step, StepContext
from app_vision.engine.fsm import register_step
from app_vision.modules.guardrails import apply_basic_guardrails

def _et_now_iso(now_override: str | None = None) -> str:
    # Permite inyectar 'now_et' (YYYY-MM-DDTHH:MM:SS) para pruebas; si no, usa zona ET real.
    if now_override:
        return now_override.split('.', 1)[0]
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo("America/New_York")
        return datetime.now(tz).replace(microsecond=0).isoformat()
    except Exception:
        # Fallback: hora local como ISO (documenta si tu servidor no está en ET)
        return datetime.now().replace(microsecond=0).isoformat()

def _block_from_et_time(t: time) -> str:
    # Ventanas de cierre (ET)
    am_close  = time(6, 30)
    mid_close = time(14, 10)
    eve_close = time(22, 20)
    if t <= am_close:  return "AM"
    if t <= mid_close: return "MID"
    return "EVE"

@register_step("BlockNowStep")
class BlockNowStep(Step):
    """
    OUT: { "now_et": ISO, "block_now": "AM"|"MID"|"EVE" }
    IN opcional: { "now_et": ISO } para pruebas reproducibles.
    """
    def run(self, ctx: StepContext, data):
        now_iso = _et_now_iso(data.get("now_et"))
        # Extrae HH:MM:SS de ISO sin depender de TZ textual
        hhmmss = now_iso.split("T",1)[1][:8]
        h, m, s = map(int, hhmmss.split(":"))
        block = _block_from_et_time(time(h, m, s))
        
        output = {"now_et": now_iso, "block_now": block}
        
        # Validar output con guardrails (sin sources_allowlist para este step)
        apply_basic_guardrails(
            step_name="BlockNowStep",
            input_data=data,
            output_data=output,
            required_output_keys=["now_et", "block_now"]
        )
        
        return output
