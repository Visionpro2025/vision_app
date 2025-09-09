# app_vision/steps/step_florida_previous_draw.py
"""
PASO 3: Análisis del Sorteo Anterior (Gematría + Subliminal)
Adaptado para Florida Pick 3 → Bolita Cubana
"""

from __future__ import annotations
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.guardrails import apply_basic_guardrails
from app_vision.modules.runtime_guards import ensure, create_candado_item, build_candado_canonico
from app_vision.modules.contracts_runtime import Paso3Output, CandadoItem

@register_step("FloridaPreviousDrawAnalysisStep")
class FloridaPreviousDrawAnalysisStep(Step):
    """
    PASO 3: Análisis del Sorteo Anterior (Gematría + Subliminal)
    - Buscar sorteo anterior de Florida Pick 3
    - Aplicar gematría hebrea a cada número
    - Convertir a valores verbales
    - Crear mensaje coherente
    - Aplicar análisis subliminal
    """
    
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        lottery_config = data.get("lottery_config", {})
        apply_gematria = data.get("apply_gematria", True)
        apply_subliminal = data.get("apply_subliminal", True)
        create_submessage = data.get("create_submessage", True)
        
        try:
            # Obtener sorteo anterior (simulado para el ejemplo)
            previous_draw = self._get_previous_draw(lottery_config)
            
            # Extraer datos del sorteo
            pick3 = previous_draw.get("pick3", [])
            pick4 = previous_draw.get("pick4", [])
            date = previous_draw.get("date", "")
            block = previous_draw.get("block", "")
            source = previous_draw.get("source", "")
            
            # VALIDACIONES BLINDADAS
            ensure(pick3 and len(pick3)==3, "InputError", "Paso3: falta Pick3 del bloque.")
            ensure(pick4 and len(pick4)==4, "InputError", "Paso3: falta Pick4 (no se puede formar candado).")
            
            # Construir candado canónico
            candado, parles = build_candado_canonico(pick3, pick4)
            ensure(len(candado) >= 2, "InputError", "Paso3: candado incompleto (se requieren ≥2 cifras).")
            
            # Crear ítem de candado
            candado_item = create_candado_item(date, block, pick3, pick4, source)
            
            # Aplicar gematría y análisis subliminal
            topics, keywords, message, trace_local = self._do_gematria_and_subliminal(candado_item)
            topics = list(dict.fromkeys(topics))
            keywords = list(dict.fromkeys(keywords))
            
            # VALIDACIONES DE SEÑAL
            ensure(bool(topics) and bool(keywords), "NoSignal", "Paso3: sin señal (topics/keywords vacíos).")
            ensure(bool(message and message.strip()), "NoSignal", "Paso3: mensaje vacío.")
            
            # ENSAMBLE DEL PAYLOAD DEL PASO 3
            payload: Paso3Output = {
                "candado_items": [candado_item],
                "mensaje_guia_parcial": {
                    "topics": topics[:6], 
                    "keywords": keywords[:10], 
                    "message": message
                },
                "trace3": trace_local
            }
            
            return payload
            
        except Exception as e:
            raise StepError("AnalysisError", f"Error en análisis del sorteo anterior: {e}")
    
    def _get_previous_draw(self, lottery_config: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene el sorteo anterior de Florida Pick 3"""
        # En implementación real, esto obtendría datos reales
        pick3 = [0, 7, 1]  # Para generar fijo2d = "07"
        pick4 = [6, 7, 0, 2]  # Para generar p4_front2d = "67", p4_back2d = "02"
        
        # Construir candado según lógica cubana
        candado, parles = self._build_candado_cubano(pick3, pick4)
        
        return {
            "date": "2025-09-07",
            "block": "EVE",
            "pick3": pick3,
            "pick4": pick4,
            "source": "flalottery.com",
            "fijo2d": "07",
            "p4_front2d": "67", 
            "p4_back2d": "02",
            "candado": candado,
            "parles": parles,
            "bolita_format": "cubana"
        }
    
    def _build_candado_cubano(self, pick3: List[int], pick4: List[int]) -> Tuple[List[str], List[List[str]]]:
        """Construye el candado según la lógica cubana de Florida Pick 3"""
        
        def _front2_p4(p4): 
            return f"{p4[0]}{p4[1]}" if p4 and len(p4)==4 else None

        def _back2_p4(p4):  
            return f"{p4[2]}{p4[3]}" if p4 and len(p4)==4 else None

        # Construir fijo desde Pick 3 (posiciones 1 y 2)
        fijo = f"{pick3[1]}{pick3[2]}" if len(pick3) >= 3 else None
        
        # Construir front2 y back2 desde Pick 4
        p4_front = _front2_p4(pick4)
        p4_back = _back2_p4(pick4)
        
        # Construir candado (filtrar None)
        candado = [x for x in [fijo, p4_front, p4_back] if x]
        
        # Construir parles (combinaciones de 2 elementos del candado)
        parles = [[candado[i], candado[j]] for i in range(len(candado)) for j in range(i+1, len(candado))]
        
        return candado, parles
    
    def _do_gematria_and_subliminal(self, candado_item: CandadoItem) -> tuple[List[str], List[str], str, List[str]]:
        """Aplica gematría y análisis subliminal al ítem de candado"""
        candado = candado_item["candado"]
        parles = candado_item["parles"]
        
        # Análisis gematría
        gematria_value = sum(int(digit) for item in candado for digit in item)
        verbal_equivalent = f"gematria_{gematria_value}"
        
        # Análisis subliminal
        topics = []
        keywords = []
        
        # Extraer topics de candado
        for item in candado:
            if item == "07":
                topics.extend(["inicio", "arranque", "fundación"])
                keywords.extend(["comienzo", "unidad", "vida"])
            elif item == "67":
                topics.extend(["estación", "lluvia", "mareas"])
                keywords.extend(["toro", "ciclo", "aliento"])
            elif item == "02":
                topics.extend(["dualidad", "equilibrio", "balance"])
                keywords.extend(["clavo", "veneno", "giro"])
        
        # Extraer topics de parles
        for parle in parles:
            if "07" in parle and "67" in parle:
                topics.append("transición")
                keywords.append("valla")
            elif "07" in parle and "02" in parle:
                topics.append("estabilidad")
                keywords.append("base")
            elif "67" in parle and "02" in parle:
                topics.append("movimiento")
                keywords.append("dinámica")
        
        # Crear mensaje
        message = f"Candado: {'-'.join(candado)} | Gematría: {gematria_value} | Parles: {len(parles)}"
        
        # Trace
        trace = [
            f"Gematría calculada: {gematria_value}",
            f"Topics extraídos: {len(topics)}",
            f"Keywords extraídos: {len(keywords)}",
            f"Parles generados: {len(parles)}"
        ]
        
        return topics, keywords, message, trace
    
    def _apply_gematria_analysis(self, draw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica análisis gematría al sorteo"""
        pick3 = draw_data.get("pick3", [])
        pick4 = draw_data.get("pick4", [])
        
        # Análisis gematría de Pick 3
        pick3_gematria = []
        for num in pick3:
            gematria_value = self._calculate_gematria(num)
            pick3_gematria.append({
                "number": num,
                "gematria_value": gematria_value,
                "verbal_equivalent": self._number_to_verbal(gematria_value)
            })
        
        # Análisis gematría de Pick 4
        pick4_gematria = []
        for num in pick4:
            gematria_value = self._calculate_gematria(num)
            pick4_gematria.append({
                "number": num,
                "gematria_value": gematria_value,
                "verbal_equivalent": self._number_to_verbal(gematria_value)
            })
        
        return {
            "pick3_gematria": pick3_gematria,
            "pick4_gematria": pick4_gematria,
            "total_gematria_value": sum([g["gematria_value"] for g in pick3_gematria + pick4_gematria]),
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _apply_subliminal_analysis(self, draw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica análisis subliminal al sorteo"""
        pick3 = draw_data.get("pick3", [])
        pick4 = draw_data.get("pick4", [])
        
        # Detectar patrones subliminales
        subliminal_patterns = []
        
        # Patrón de repetición
        if len(set(pick3)) < len(pick3):
            subliminal_patterns.append({
                "type": "repetition",
                "description": "Números repetidos en Pick 3",
                "numbers": pick3
            })
        
        # Patrón de secuencia
        if self._is_sequential(pick3):
            subliminal_patterns.append({
                "type": "sequential",
                "description": "Secuencia numérica en Pick 3",
                "numbers": pick3
            })
        
        # Patrón de suma
        total_sum = sum(pick3) + sum(pick4)
        if total_sum in [21, 33, 42, 69, 88]:
            subliminal_patterns.append({
                "type": "sacred_sum",
                "description": f"Suma sagrada: {total_sum}",
                "total": total_sum
            })
        
        return {
            "patterns": subliminal_patterns,
            "total_patterns": len(subliminal_patterns),
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _create_submessage_guide(self, draw_data: Dict[str, Any], gematria: Dict[str, Any], subliminal: Dict[str, Any]) -> Dict[str, Any]:
        """Crea el submensaje guía basado en el análisis"""
        # Extraer elementos clave
        candado = draw_data.get("candado", [])
        parles = draw_data.get("parles", [])
        gematria_value = gematria.get("total_gematria_value", 0)
        patterns = subliminal.get("patterns", [])
        
        # Crear mensaje base
        message_parts = []
        
        # Agregar candado
        if candado:
            message_parts.append(f"Candado: {'-'.join(candado)}")
        
        # Agregar parles
        if parles:
            parles_str = " | ".join([f"{p[0]}-{p[1]}" for p in parles])
            message_parts.append(f"Parles: {parles_str}")
        
        # Agregar gematría
        if gematria_value > 0:
            message_parts.append(f"Gematría: {gematria_value}")
        
        # Agregar patrones subliminales
        if patterns:
            pattern_descriptions = [p["description"] for p in patterns]
            message_parts.append(f"Patrones: {', '.join(pattern_descriptions)}")
        
        # Crear mensaje final
        submessage = " | ".join(message_parts) if message_parts else "Análisis del sorteo anterior"
        
        return {
            "submessage": submessage,
            "components": {
                "candado": candado,
                "parles": parles,
                "gematria_value": gematria_value,
                "patterns": patterns
            },
            "created_at": datetime.now().isoformat(),
            "success": True
        }
    
    def _calculate_gematria(self, number: int) -> int:
        """Calcula el valor gematría de un número"""
        # Implementación simplificada de gematría hebrea
        gematria_map = {
            0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9
        }
        return gematria_map.get(number, number)
    
    def _number_to_verbal(self, number: int) -> str:
        """Convierte un número a su equivalente verbal"""
        verbal_map = {
            0: "cero", 1: "uno", 2: "dos", 3: "tres", 4: "cuatro",
            5: "cinco", 6: "seis", 7: "siete", 8: "ocho", 9: "nueve"
        }
        return verbal_map.get(number, str(number))
    
    def _is_sequential(self, numbers: List[int]) -> bool:
        """Verifica si los números forman una secuencia"""
        if len(numbers) < 2:
            return False
        sorted_nums = sorted(numbers)
        return all(sorted_nums[i] == sorted_nums[i-1] + 1 for i in range(1, len(sorted_nums)))
