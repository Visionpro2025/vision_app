from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple, List, Dict

@dataclass(frozen=True)
class Candado:
    """
    Modelo de Candado con regla fija:
    - FIJO = last2(Pick3 del bloque)
    - CORRIDO = last2(Pick4 del bloque) si existe
    - EXTRA = last2(Pick3 del otro bloque) opcional
    """
    date: str          # 'YYYY-MM-DD'
    block: str         # 'AM' | 'MID' | 'EVE'
    fijo2d: str        # last2(Pick3 del bloque)
    corrido2d: Optional[str] = None   # last2(Pick4 del bloque)
    extra2d: Optional[str] = None     # last2(Pick3 del otro bloque), opcional
    pick3: Tuple[int,int,int] = (0,0,0)
    pick4: Optional[Tuple[int,int,int,int]] = None
    source_p3: Optional[str] = None
    source_p4: Optional[str] = None

    def trio(self) -> List[str]:
        """Retorna el trio del candado (FIJO + CORRIDO + EXTRA) sin duplicados"""
        base = [self.fijo2d]
        if self.corrido2d: 
            base.append(self.corrido2d)
        if self.extra2d:   
            base.append(self.extra2d)
        # dedup preservando orden
        seen = set()
        return [x for x in base if (x not in seen and not seen.add(x))]

    def parles(self) -> List[Tuple[str,str]]:
        """Retorna todas las combinaciones 2-a-2 del trio"""
        xs = self.trio()
        return [(xs[i], xs[j]) for i in range(len(xs)) for j in range(i+1, len(xs))]

    def to_dict(self) -> Dict[str, any]:
        """Convierte el candado a diccionario para serialización"""
        return {
            "date": self.date,
            "block": self.block,
            "fijo2d": self.fijo2d,
            "corrido2d": self.corrido2d,
            "extra2d": self.extra2d,
            "trio": self.trio(),
            "parles": self.parles(),
            "pick3": self.pick3,
            "pick4": self.pick4,
            "source_p3": self.source_p3,
            "source_p4": self.source_p4
        }

    @classmethod
    def from_draw(cls, draw: Dict[str, any], other_last2: Optional[str] = None) -> 'Candado':
        """Crea un Candado a partir de un draw y el last2 del otro bloque"""
        # Extraer last2 del Pick3
        pick3 = draw.get("numbers", [0, 0, 0])
        fijo2d = f"{pick3[1]}{pick3[2]}" if len(pick3) >= 3 else "00"
        
        # Extraer last2 del Pick4 si existe
        pick4 = draw.get("pick4")
        corrido2d = f"{pick4[2]}{pick4[3]}" if pick4 and len(pick4) >= 4 else None
        
        # Validar other_last2
        extra2d = None
        if other_last2 and len(str(other_last2)) == 2 and str(other_last2).isdigit():
            extra2d = str(other_last2)
        
        return cls(
            date=str(draw.get("date", "")),
            block=str(draw.get("block", "")).upper(),
            fijo2d=fijo2d,
            corrido2d=corrido2d,
            extra2d=extra2d,
            pick3=tuple(pick3) if len(pick3) >= 3 else (0, 0, 0),
            pick4=tuple(pick4) if pick4 and len(pick4) >= 4 else None,
            source_p3=draw.get("source"),
            source_p4=draw.get("source")
        )


