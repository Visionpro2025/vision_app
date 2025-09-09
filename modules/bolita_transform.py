from __future__ import annotations
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class FLDraw:
    date: str            # 'YYYY-MM-DD'
    block: str           # 'MID' | 'EVE'
    pick3: Tuple[int,int,int]         # (d1,d2,d3)
    pick4: Optional[Tuple[int,int,int,int]] = None  # (d1,d2,d3,d4) si está
    fireball: Optional[int] = None     # 0..9 si está

def _val_2d(x: int) -> str:
    return f"{x:02d}"

def _last2_from_tuple(t: Tuple[int,...]) -> str:
    # últimos dos dígitos del arreglo
    return _val_2d(t[-2]*10 + t[-1])

def _sum_mod10_of_2d(two: str) -> str:
    a, b = int(two[0]), int(two[1])
    return f"{(a+b)%10}{(a+b)%10}"  # "empuje": XX

def derive_bolita(
    focus: FLDraw,
    other_block_pick3_last2: Optional[str] = None,   # 'NN' del otro bloque (opcional)
    force_min_candado: bool = True                   # si True, exige >=2 elementos reales o lanza
) -> Dict[str, Any]:
    """
    Regla fija de CANDADO:
      - FIJO_2D = últimos 2 del Pick3 (bloque focus)
      - CORRIDO_2D = últimos 2 del Pick4 (mismo bloque), si existe
      - TERCERO opcional = últimos 2 del Pick3 del otro bloque (si lo pasas)
    Parlés = todas las combinaciones 2-a-2 de los 2D disponibles.
    """
    # 1) FIJO (Pick3 del bloque)
    fijo3 = "".join(str(d) for d in focus.pick3)
    fijo2 = _last2_from_tuple(focus.pick3)

    # 2) CORRIDO (Pick4 del mismo bloque, si existe)
    corrido_bloque = _last2_from_tuple(focus.pick4) if focus.pick4 else None

    # 3) TERCERO (Pick3 del otro bloque, si lo pasas)
    corrido_otro = None
    if other_block_pick3_last2:
        s = str(other_block_pick3_last2).strip()
        if len(s) == 2 and s.isdigit():
            corrido_otro = s

    # 4) Construcción del set 2D base (en orden de prioridad)
    base2d: List[str] = [fijo2]
    if corrido_bloque: base2d.append(corrido_bloque)
    if corrido_otro:   base2d.append(corrido_otro)

    # Deduplicar manteniendo orden
    seen = set()
    base2d = [x for x in base2d if (x not in seen and not seen.add(x))]

    # 5) Validación mínima del candado
    if force_min_candado and len(base2d) < 2:
        # FIJO está siempre; si no hay ningún corrido real, lanza para que la app lo trate como "insumo insuficiente"
        raise ValueError("Candado insuficiente: falta Pick4 del bloque y no se aportó 'other_block_pick3_last2' válido.")

    # 6) CANDADO = primeros 2 o 3 según disponibilidad; PARLÉS = combinaciones 2 a 2
    candado = base2d[:3]
    parles: List[Tuple[str,str]] = []
    for i in range(len(base2d)):
        for j in range(i+1, len(base2d)):
            parles.append((base2d[i], base2d[j]))

    return {
        "date": focus.date,
        "block": focus.block,
        "fijo": {"3d": fijo3, "2d": fijo2},
        "corridos": [c for c in [corrido_bloque, corrido_otro] if c],
        "parles": parles,
        "candado": candado,
        "origen": {
            "pick3_block": focus.pick3,
            "pick4_block": focus.pick4,
            "other_pick3_last2": corrido_otro
        }
    }
