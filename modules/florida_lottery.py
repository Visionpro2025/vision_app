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
    focus: FLDraw,                    # bloque a publicar (ej. tirada del mediodía)
    other_block_pick3_last2: Optional[str] = None,   # terminal del otro bloque (si se quiere usar)
    use_empuxe: bool = False,         # incluir XX = (suma mod10 del FIJO-2D) duplicado
    prefer_pick4_as_corrido: bool = True # si hay Pick4 del mismo bloque, tomar sus últimos 2 como 1er corrido
) -> Dict[str, Any]:
    """
    Convierte los sorteos reales de Florida → Formato bolita:
      - FIJO (3D) = Pick3 tal cual.
      - FIJO_2D   = últimos dos del Pick3.
      - CORRIDOS  = [terminal Pick4 mismo bloque?, terminal Pick3 del otro bloque?] (según disponibilidad).
      - PARLÉS    = combinaciones 2 a 2 del conjunto {FIJO_2D, corridos...}.
      - CANDADO   = tríada base {FIJO_2D, corrido_bloque, corrido_día} (dedup).
    Nada se inventa: si falta un origen, simplemente no se agrega.
    """
    # 1) FIJO: tripleta Pick3 del bloque
    fijo3 = "".join(str(d) for d in focus.pick3)
    fijo2 = _last2_from_tuple(focus.pick3)

    # 2) Corridos candidatos (máximo 2, según tu práctica)
    corridos: List[str] = []

    # 2.1 terminal del Pick4 mismo bloque (si existe y está habilitado)
    if prefer_pick4_as_corrido and focus.pick4:
        corridos.append(_last2_from_tuple(focus.pick4))

    # 2.2 terminal del Pick3 del otro bloque (si viene por argumento)
    if other_block_pick3_last2:
        corridos.append(_val_2d(int(other_block_pick3_last2)))

    # deduplicar manteniendo orden
    seen = set(); corridos = [x for x in corridos if (x not in seen and not seen.add(x))]

    # 3) Empuje (opcional)
    empuje = _sum_mod10_of_2d(fijo2) if use_empuxe else None

    # 4) Conjunto base 2D para parlés/candado
    base2d: List[str] = [fijo2] + corridos
    if use_empuxe and empuje not in base2d:
        base2d.append(empuje)
    # dedup
    seen = set(); base2d = [x for x in base2d if (x not in seen and not seen.add(x))]

    # 5) CANDADO (tríada principal): tomar hasta 3 primeros del conjunto base
    candado = base2d[:3]

    # 6) PARLÉS: pares no ordenados del conjunto base (sin repetidos)
    parles = []
    for i in range(len(base2d)):
        for j in range(i+1, len(base2d)):
            parles.append((base2d[i], base2d[j]))

    # 7) Salida estructurada
    out: Dict[str, Any] = {
        "date": focus.date,
        "block": focus.block,
        "fijo": {
            "3d": fijo3,
            "2d": fijo2
        },
        "corridos": corridos,
        "empuje": empuje,           # puede ser None si no se usa
        "parles": parles,           # lista de tuplas 2D
        "candado": candado,         # hasta 3 ítems 2D
        "origen": {
            "pick3_block": focus.pick3,
            "pick4_block": focus.pick4,
            "other_pick3_last2": other_block_pick3_last2
        }
    }
    return out

class FloridaLotteryAnalyzer:
    """Analizador principal para lotería de Florida"""
    
    def __init__(self):
        self.recent_draws = []
        self.analysis_history = []
    
    def add_draw(self, draw: FLDraw):
        """Agrega un sorteo al historial"""
        self.recent_draws.append(draw)
        # Mantener solo los últimos 30 sorteos
        if len(self.recent_draws) > 30:
            self.recent_draws = self.recent_draws[-30:]
    
    def analyze_draw(self, draw: FLDraw, other_block_last2: Optional[str] = None) -> Dict[str, Any]:
        """Analiza un sorteo específico"""
        result = derive_bolita(
            focus=draw,
            other_block_pick3_last2=other_block_last2,
            use_empuxe=True,
            prefer_pick4_as_corrido=True
        )
        
        # Agregar análisis adicional
        result['analysis'] = self._generate_analysis(result)
        
        # Guardar en historial
        self.analysis_history.append({
            'timestamp': draw.date,
            'result': result
        })
        
        return result
    
    def _generate_analysis(self, bolita_result: Dict[str, Any]) -> Dict[str, Any]:
        """Genera análisis adicional basado en el resultado de bolita"""
        analysis = {
            'total_combinations': len(bolita_result['parles']),
            'candado_strength': len(bolita_result['candado']),
            'has_empuje': bolita_result['empuje'] is not None,
            'corridos_count': len(bolita_result['corridos']),
            'recommendations': []
        }
        
        # Recomendaciones basadas en el análisis
        if analysis['total_combinations'] > 10:
            analysis['recommendations'].append("Alto número de combinaciones - considerar filtros")
        
        if analysis['candado_strength'] == 3:
            analysis['recommendations'].append("Candado completo - alta confianza")
        
        if bolita_result['empuje']:
            analysis['recommendations'].append("Empuje disponible - incluir en análisis")
        
        return analysis
    
    def get_pattern_analysis(self) -> Dict[str, Any]:
        """Analiza patrones en el historial de sorteos"""
        if len(self.analysis_history) < 3:
            return {"error": "Insuficientes datos para análisis de patrones"}
        
        # Análisis de patrones básicos
        patterns = {
            'most_common_fijo2d': {},
            'most_common_corridos': {},
            'empuje_frequency': 0,
            'total_analyses': len(self.analysis_history)
        }
        
        for analysis in self.analysis_history:
            result = analysis['result']
            
            # Contar FIJO 2D más comunes
            fijo2d = result['fijo']['2d']
            patterns['most_common_fijo2d'][fijo2d] = patterns['most_common_fijo2d'].get(fijo2d, 0) + 1
            
            # Contar corridos más comunes
            for corrido in result['corridos']:
                patterns['most_common_corridos'][corrido] = patterns['most_common_corridos'].get(corrido, 0) + 1
            
            # Frecuencia de empuje
            if result['empuje']:
                patterns['empuje_frequency'] += 1
        
        return patterns




