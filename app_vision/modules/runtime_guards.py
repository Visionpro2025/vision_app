# ============================================
# 📌 GUARDAS RUNTIME PARA PROTOCOLO UNIVERSAL
# Validaciones y bloqueos para evitar "OK vacíos"
# ============================================

from app_vision.engine.contracts import StepError
from datetime import datetime, time
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")

def ensure(cond: bool, kind: str, msg: str):
    """Función de validación que lanza StepError si la condición es falsa"""
    if not cond:
        raise StepError(kind, msg)

def block_now_et(now_iso: str | None, am_end="06:30", mid_end="14:10"):
    """Determina el bloque actual basado en la hora ET"""
    dt = datetime.now(ET) if not now_iso else datetime.fromisoformat(now_iso).astimezone(ET)
    t = dt.timetz()
    h, m = map(int, am_end.split(":")); am_limit = time(h, m)
    h, m = map(int, mid_end.split(":")); mid_limit = time(h, m)
    if t <= am_limit:  return "AM"
    if t <= mid_limit: return "MID"
    return "EVE"