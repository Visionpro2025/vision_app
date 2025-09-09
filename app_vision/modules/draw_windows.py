from __future__ import annotations
from datetime import datetime, time
from typing import Dict, Optional

# Todas las horas en ET (ajusta si tu fetch ya normaliza)
WINDOWS = {
    "AM":  {"close": time(6,30)},
    "MID": {"close": time(14,10)},
    "EVE": {"close": time(22,20)},
}

def current_block(now: datetime) -> str:
    """
    Determina el bloque actual basado en la hora.
    Regla operativa (Cuba):
    - AM: 06:00–06:30 (cierra aprox. 06:30)
    - MID: 13:35–14:10 (cierra aprox. 14:10)
    - EVE: 21:40–22:20 (cierra aprox. 22:20)
    """
    t = now.time()
    if t <= WINDOWS["AM"]["close"]:  
        return "AM"
    if t <= WINDOWS["MID"]["close"]: 
        return "MID"
    return "EVE"

def previous_block(block: str) -> str:
    """
    Retorna el bloque anterior en el orden diario.
    Si es AM, el anterior es EVE del día previo.
    """
    order = ["AM", "MID", "EVE"]
    i = order.index(block)
    return order[i-1] if i > 0 else "EVE"  # si es AM, el anterior es EVE del día previo

def next_block(block: str) -> str:
    """
    Retorna el siguiente bloque en el orden diario.
    Si es EVE, el siguiente es AM del día siguiente.
    """
    order = ["AM", "MID", "EVE"]
    i = order.index(block)
    return order[i+1] if i < len(order)-1 else "AM"  # si es EVE, el siguiente es AM del día siguiente

def is_window_open(block: str, now: datetime) -> bool:
    """
    Verifica si una ventana está abierta en el momento actual.
    """
    current = current_block(now)
    return current == block

def get_window_status(now: datetime) -> Dict[str, any]:
    """
    Retorna el estado de todas las ventanas en el momento actual.
    """
    current = current_block(now)
    
    status = {}
    for block, config in WINDOWS.items():
        status[block] = {
            "is_current": block == current,
            "is_open": block == current,
            "close_time": config["close"],
            "previous": previous_block(block),
            "next": next_block(block)
        }
    
    return {
        "current_block": current,
        "windows": status,
        "timestamp": now.isoformat()
    }

def get_operational_schedule() -> Dict[str, any]:
    """
    Retorna el horario operativo de las ventanas.
    """
    return {
        "AM": {
            "open": "06:00",
            "close": "06:30",
            "description": "Primer tiro del día"
        },
        "MID": {
            "open": "13:35", 
            "close": "14:10",
            "description": "Sorteo del mediodía"
        },
        "EVE": {
            "open": "21:40",
            "close": "22:20", 
            "description": "Sorteo de la noche"
        }
    }


