from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.guardrails import apply_basic_guardrails

def _last2_p3(nums: List[int]) -> str: 
    """Extrae last2 del Pick3"""
    return f"{nums[1]}{nums[2]}"

def _last2_p4(nums4: Optional[List[int]]) -> Optional[str]:
    """Extrae last2 del Pick4 si existe"""
    if not nums4: 
        return None
    return f"{nums4[2]}{nums4[3]}"

def _parse_date(s: str) -> datetime: 
    """Parsea fecha en formato YYYY-MM-DD"""
    return datetime.strptime(s, "%Y-%m-%d")

def _dstr(dt: datetime) -> str: 
    """Convierte datetime a string YYYY-MM-DD"""
    return dt.strftime("%Y-%m-%d")

def _pick(draws: List[Dict[str,Any]], date: str, block: str) -> Optional[Dict[str,Any]]:
    """Busca un draw específico por fecha y bloque"""
    for d in draws:
        if str(d.get("date")) == date and str(d.get("block")).upper() == block:
            return d
    return None

def _mk_candado(d: Dict[str,Any], other_last2: Optional[str]) -> Dict[str,Any]:
    """Construye un candado a partir de un draw y el last2 del otro bloque"""
    fijo2d = _last2_p3(d["numbers"])
    corr2d = _last2_p4(d.get("pick4"))
    trio = [x for x in [fijo2d, corr2d, other_last2] if x]
    
    # parlés
    parles = []
    for i in range(len(trio)):
        for j in range(i+1, len(trio)):
            parles.append([trio[i], trio[j]])
    
    return {
        "date": d["date"], 
        "block": d["block"],
        "fijo2d": fijo2d, 
        "corrido2d": corr2d, 
        "extra2d": other_last2,
        "candado": trio, 
        "parles": parles,
        "source": d.get("source"),
        "pick3": d["numbers"],
        "pick4": d.get("pick4")
    }

@register_step("PrevDayCandadosStep")
class PrevDayCandadosStep(Step):
    """
    Entrega los 3 candados del día anterior (AM, MID, EVE) según práctica cubana:
      - AM  <= Florida EVE del día D-1
      - MID <= Florida MID del día D-1
      - EVE <= Florida EVE del día D-1
    Requiere draws REALES ({date:'YYYY-MM-DD', block:'MID|EVE', numbers:[3], pick4:[4]?}).
    Usa el EVE D-1 como "otro bloque" para AM; para MID/EVE usa el bloque complementario del propio día.
    """
    
    def run(self, ctx: StepContext, data: Dict[str,Any]) -> Dict[str,Any]:
        # Aplicar guardrails de entrada
        apply_basic_guardrails(
            step_name="PrevDayCandadosStep",
            input_data=data,
            output_data={},
            required_input_keys=["draws"]
        )
        
        draws: List[Dict[str,Any]] = data.get("draws") or []
        if not draws:
            raise StepError("InputError", "No llegaron draws reales.")
        
        # fecha base = fecha del draw más reciente
        draws_sorted = sorted(draws, key=lambda x: (x["date"], 1 if x["block"]=="MID" else 2), reverse=True)
        base_date = _parse_date(draws_sorted[0]["date"])
        prev_date = _dstr(base_date - timedelta(days=1))

        # Necesitamos (en D-1): MID y EVE; AM se mapea al EVE de D-2 vs práctica local,
        # pero en Cuba la "mañana" se juega con el EVE inmediatamente anterior. Entonces:
        # AM(D-1) = EVE(D-1-1) ? No: para el "día anterior completo" usamos:
        #   AM(D-1) = EVE(D-2)  [si quieres estricto calendario]
        #   PRÁCTICO: entreguemos los 3 de D-1 con esta convención:
        #   AM(D-1) = EVE(D-2) (si disponible); si no, se marca faltante.
        d1 = _parse_date(prev_date)
        d2 = _dstr(d1 - timedelta(days=1))

        eve_d2 = _pick(draws, d2, "EVE")
        mid_d1 = _pick(draws, prev_date, "MID")
        eve_d1 = _pick(draws, prev_date, "EVE")

        out = {"date": prev_date, "candados": []}

        # AM (usa EVE de D-2) y puede tomar como "otro" el MID de D-1 si existe
        if eve_d2:
            other_for_am = _last2_p3(mid_d1["numbers"]) if mid_d1 else None
            out["candados"].append({"slot":"AM", **_mk_candado(eve_d2, other_for_am)})
        else:
            out["candados"].append({"slot":"AM", "missing": True, "why":"No hay EVE D-2"})

        # MID (usa MID de D-1) con "otro" = EVE D-1
        if mid_d1:
            other_for_mid = _last2_p3(eve_d1["numbers"]) if eve_d1 else None
            out["candados"].append({"slot":"MID", **_mk_candado(mid_d1, other_for_mid)})
        else:
            out["candados"].append({"slot":"MID", "missing": True, "why":"No hay MID D-1"})

        # EVE (usa EVE de D-1) con "otro" = MID D-1
        if eve_d1:
            other_for_eve = _last2_p3(mid_d1["numbers"]) if mid_d1 else None
            out["candados"].append({"slot":"EVE", **_mk_candado(eve_d1, other_for_eve)})
        else:
            out["candados"].append({"slot":"EVE", "missing": True, "why":"No hay EVE D-1"})

        # Validar output
        output = {"prev_day_candados": out}
        
        apply_basic_guardrails(
            step_name="PrevDayCandadosStep",
            input_data=data,
            output_data=output,
            required_output_keys=["prev_day_candados"]
        )
        
        return output


