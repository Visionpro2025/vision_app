from __future__ import annotations
from typing import Dict, Any, List
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.sefirot_core import analyze_draws, SEFIROT

REQUIRED_FIELDS = ("date","block","numbers")

def _validate_real_draws(draws: List[Dict[str,Any]])->List[Dict[str,Any]]:
    """
    Regla de hierro:
    - Deben venir del step1_fetch_real (tu plan lo cablea así).
    - Cada draw con campos obligatorios y 3 dígitos 0..9.
    - Bloque MID|EVE.
    - Si encuentra indicios de simulación (p.ej. 'simulated' en source), falla.
    """
    if not isinstance(draws, list) or not draws:
        raise StepError("InputError", "No hay sorteos para analizar (esperados: reales).")

    clean = []
    for i, d in enumerate(draws, 1):
        if not all(k in d for k in REQUIRED_FIELDS):
            raise StepError("InputError", f"Draw {i} incompleto; faltan campos {REQUIRED_FIELDS}.")
        date = str(d["date"]).strip()
        block = str(d["block"]).strip().upper()
        nums = d["numbers"]
        if block not in ("MID","EVE"):
            raise StepError("InputError", f"Draw {i} con block inválido: {block} (MID|EVE).")
        if not (isinstance(nums, list) and len(nums)==3 and all(isinstance(x,int) and 0<=x<=9 for x in nums)):
            raise StepError("InputError", f"Draw {i} 'numbers' inválidos: {nums}.")
        # anti-simulación: fuente
        src = (d.get("source") or "").lower()
        if "simul" in src or "dummy" in src or "test" in src:
            raise StepError("InputError", f"Draw {i} parece simulado (source='{d.get('source')}').")
        clean.append({"date":date,"block":block,"numbers":nums,"source":d.get("source")})
    return clean

@register_step("SefiroticAnalysisStepV2")
class SefiroticAnalysisStepV2(Step):
    """
    Analiza sefirot sobre draws REALES (del step1_fetch_real).
    - Valida entradas y aborta si no son reales o están mal formadas.
    - Devuelve candidatos por banda + trazabilidad.
    Inputs:
      - draws: List[{date,block,numbers,source?}]  (REQUIRED)
    Output:
      - status: OK
      - analyzed_count: int
      - input_echo: lista corta de draws usados (para auditoría)
      - digit_scores, sefirah_scores, patterns
      - candidates: {alta, media, baja}
    """
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        draws = data.get("draws")
        clean = _validate_real_draws(draws)

        res = analyze_draws(clean)

        # Auditoría mínima
        ok_candidates = any(res["candidates"].values())
        auditor = {
            "ok": bool(ok_candidates),
            "why": "Se generaron bandas de candidatos" if ok_candidates else "Sin masa crítica para candidatos",
            "analyzed_count": len(clean)
        }

        # Eco de entradas (recorte a 5 para reporte)
        echo = [{"date":d["date"],"block":d["block"],"numbers":d["numbers"],"source":d.get("source")} for d in clean[:5]]

        return {
            "status": "OK",
            "analyzed_count": len(clean),
            "input_echo": echo,
            "digit_scores": res["digit_scores"],
            "sefirah_scores": res["sefirah_scores"],
            "patterns": res["patterns"],
            "candidates": res["candidates"],
            "auditor": auditor
        }



