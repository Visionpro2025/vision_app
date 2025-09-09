# ============================================
# 🚀 MÓDULO: UTILIDADES PARA SORTEOS
# Funciones auxiliares para manejo de sorteos
# Selección del sorteo más reciente y validación
# ============================================

import os, re
from datetime import datetime
from typing import List, Dict, Any, Tuple

def _parse_date(d: str) -> datetime:
    """
    Admite 'YYYY-MM-DD' o 'YYYY-MM-DDTHH:MM:SS' o 'YYYY/MM/DD' y variantes sencillas.
    Si hay hora aparte (draw_time), se usa para la comparación si es necesario.
    """
    d = d.strip().replace("/", "-")
    # Cortar a fecha si llegó con T
    if "T" in d:
        d = d.split("T", 1)[0]
    return datetime.strptime(d, "%Y-%m-%d")

def select_latest_draw(draws: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Recibe una lista de draws con al menos:
      - draw_date: 'YYYY-MM-DD' (obligatorio)
      - numbers: [d1,d2,d3] para Pick3
      - lottery, draw_time (opcionales)
    Devuelve el draw MÁS RECIENTE por fecha (y si hay empate, por draw_time si es comparable).
    Determinista e idempotente.
    """
    if not draws:
        raise ValueError("No hay draws para seleccionar.")
    # Normalizar y ordenar DESC por fecha; si empatan, usar draw_time si es HH:MM
    def _key(d):
        dt = _parse_date(str(d.get("draw_date")))
        tm = str(d.get("draw_time", "00:00"))
        # hh:mm seguro, si no, 00:00
        if re.fullmatch(r"\d{1,2}:\d{2}", tm.strip()):
            h, m = tm.split(":")
            aux = int(h)*60 + int(m)
        else:
            aux = -1  # pone al final en empates
        return (dt, aux)
    # Ordenar DESC
    sorted_draws = sorted(draws, key=_key, reverse=True)
    return sorted_draws[0]

def validate_pick3_numbers(nums: Any) -> Tuple[int,int,int]:
    """
    Acepta lista/tupla de 3 enteros 0..9 o string 'd1d2d3'.
    Retorna tupla (d1,d2,d3). Lanza ValueError si no cumple.
    """
    if isinstance(nums, (list, tuple)) and len(nums) == 3:
        d1, d2, d3 = nums
    elif isinstance(nums, str) and len(nums) == 3 and nums.isdigit():
        d1, d2, d3 = int(nums[0]), int(nums[1]), int(nums[2])
    else:
        raise ValueError(f"Formato inválido de Pick3: {nums}")
    if not all(isinstance(x, int) and 0 <= x <= 9 for x in (d1,d2,d3)):
        raise ValueError(f"Dígitos fuera de rango 0..9: {nums}")
    return (d1, d2, d3)



