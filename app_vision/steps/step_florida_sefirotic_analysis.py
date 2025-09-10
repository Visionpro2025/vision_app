# app_vision/steps/step_florida_sefirotic_analysis.py
"""
PASO 6: Análisis Sefirótico de Últimos 5 Sorteos
Adaptado para Florida Pick 3 → Bolita Cubana
"""

from __future__ import annotations
from typing import Dict, Any, List, Tuple
from datetime import datetime
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.guardrails import apply_basic_guardrails

@register_step("FloridaSefiroticAnalysisStep")
class FloridaSefiroticAnalysisStep(Step):
    """
    PASO 6: Análisis Sefirótico de Últimos 5 Sorteos
    - Cargar últimos 5 sorteos de Florida Pick 3
    - Aplicar análisis sefirótico a cada sorteo
    - Generar números candidatos basados en sefirot
    - Correlacionar con números priorizados
    - Crear perfil para series cuánticas
    """
    
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        lottery_config = data.get("lottery_config", {})
        last_5_draws = data.get("last_5_draws", [])
        apply_sefirotic = data.get("apply_sefirotic", True)
        generate_candidates = data.get("generate_candidates", True)
        
        results = {
            "step": 6,
            "step_name": "FloridaSefiroticAnalysisStep",
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "sefirotic_analysis": {}
        }
        
        try:
            # 6.1 Cargar últimos 5 sorteos si no se proporcionan
            if not last_5_draws:
                last_5_draws = self._load_last_5_draws(lottery_config)
            
            if len(last_5_draws) < 3:
                raise StepError("InsufficientData", f"Se necesitan al menos 3 sorteos para análisis sefirótico, se tienen {len(last_5_draws)}")
            
            # 6.2 Análisis sefirótico de cada sorteo
            sefirot_analysis = self._analyze_last_5_draws_sefirotically(last_5_draws)
            
            # 6.3 Generar números candidatos
            candidate_numbers = {}
            if generate_candidates:
                candidate_numbers = self._generate_candidate_numbers(sefirot_analysis)
            
            # 6.4 Correlacionar con números priorizados (si están disponibles)
            correlation_analysis = self._correlate_with_prioritized_numbers(
                candidate_numbers, 
                data.get("prioritized_numbers", {})
            )
            
            # 6.5 Crear perfil para series
            series_profile = self._create_series_profile(correlation_analysis, sefirot_analysis)
            
            # 6.6 Análisis de flujo energético
            energy_flow = self._analyze_energy_flow(sefirot_analysis)
            
            # 6.7 Significancia espiritual
            spiritual_significance = self._analyze_spiritual_significance(sefirot_analysis)
            
            results["sefirotic_analysis"] = {
                "last_5_draws": last_5_draws,
                "draw_analyses": sefirot_analysis["draw_analyses"],
                "overall_patterns": sefirot_analysis["overall_patterns"],
                "candidate_numbers": candidate_numbers,
                "correlation_analysis": correlation_analysis,
                "series_profile": series_profile,
                "energy_flow": energy_flow,
                "spiritual_significance": spiritual_significance,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            # Validar output con guardrails
            apply_basic_guardrails(
                step_name="FloridaSefiroticAnalysisStep",
                input_data=data,
                output_data=results,
                required_output_keys=["step", "step_name", "timestamp", "status", "sefirotic_analysis"]
            )
            
            return results
            
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
            raise StepError("SefiroticError", f"Error en análisis sefirótico: {e}")
    
    def _load_last_5_draws(self, lottery_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Carga los últimos 5 sorteos de Florida Pick 3"""
        # En implementación real, esto obtendría datos reales
        # Por ahora, retorna datos de ejemplo
        return [
            {"date": "2025-09-07", "block": "EVE", "pick3": [8, 8, 1], "pick4": [1, 2, 3, 4]},
            {"date": "2025-09-07", "block": "MID", "pick3": [6, 9, 8], "pick4": [7, 7, 0, 2]},
            {"date": "2025-09-06", "block": "EVE", "pick3": [0, 7, 3], "pick4": [5, 9, 1, 2]},
            {"date": "2025-09-06", "block": "MID", "pick3": [4, 2, 1], "pick4": [3, 8, 9, 0]},
            {"date": "2025-09-05", "block": "EVE", "pick3": [9, 5, 7], "pick4": [2, 4, 6, 8]}
        ]
    
    def _analyze_last_5_draws_sefirotically(self, last_5_draws: List[Dict]) -> Dict[str, Any]:
        """Analiza los últimos 5 sorteos usando análisis sefirótico"""
        sefirot_analysis = {
            "draw_analyses": [],
            "overall_patterns": {},
            "energy_flow": {},
            "spiritual_significance": {}
        }
        
        # Analizar cada sorteo individualmente
        for draw in last_5_draws:
            draw_analysis = self._analyze_single_draw_sefirotically(draw)
            sefirot_analysis["draw_analyses"].append(draw_analysis)
        
        # Análisis de patrones generales
        sefirot_analysis["overall_patterns"] = self._analyze_overall_sefirot_patterns(sefirot_analysis["draw_analyses"])
        
        return sefirot_analysis
    
    def _analyze_single_draw_sefirotically(self, draw: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza un sorteo individual usando sefirot"""
        pick3 = draw.get("pick3", [])
        pick4 = draw.get("pick4", [])
        date = draw.get("date", "")
        block = draw.get("block", "")
        
        # Mapeo de números a sefirot
        sefirot_map = {
            0: "Kether", 1: "Chokmah", 2: "Binah", 3: "Chesed", 4: "Geburah",
            5: "Tiphareth", 6: "Netzach", 7: "Hod", 8: "Yesod", 9: "Malkuth"
        }
        
        # Análisis de Pick 3
        pick3_sefirot = [sefirot_map.get(num, "Unknown") for num in pick3]
        pick3_energy = self._calculate_sefirot_energy(pick3_sefirot)
        
        # Análisis de Pick 4
        pick4_sefirot = [sefirot_map.get(num, "Unknown") for num in pick4] if pick4 else []
        pick4_energy = self._calculate_sefirot_energy(pick4_sefirot) if pick4 else 0
        
        # Números de alta energía
        high_energy_numbers = []
        for i, num in enumerate(pick3):
            if pick3_energy > 7:  # Umbral de alta energía
                high_energy_numbers.append(num)
        
        # Análisis de patrones
        patterns = self._identify_sefirot_patterns(pick3_sefirot, pick4_sefirot)
        
        return {
            "date": date,
            "block": block,
            "pick3": pick3,
            "pick4": pick4,
            "pick3_sefirot": pick3_sefirot,
            "pick4_sefirot": pick4_sefirot,
            "pick3_energy": pick3_energy,
            "pick4_energy": pick4_energy,
            "total_energy": pick3_energy + pick4_energy,
            "high_energy_numbers": high_energy_numbers,
            "patterns": patterns,
            "spiritual_significance": self._calculate_spiritual_significance(pick3_sefirot, pick4_sefirot)
        }
    
    def _calculate_sefirot_energy(self, sefirot_list: List[str]) -> int:
        """Calcula la energía total de una lista de sefirot"""
        energy_map = {
            "Kether": 10, "Chokmah": 9, "Binah": 8, "Chesed": 7, "Geburah": 6,
            "Tiphareth": 5, "Netzach": 4, "Hod": 3, "Yesod": 2, "Malkuth": 1
        }
        return sum(energy_map.get(sef, 0) for sef in sefirot_list)
    
    def _identify_sefirot_patterns(self, pick3_sefirot: List[str], pick4_sefirot: List[str]) -> Dict[str, Any]:
        """Identifica patrones sefiróticos en los sorteos"""
        patterns = {
            "triple_sefirot": len(set(pick3_sefirot)) == 1,  # Mismo sefirot en Pick 3
            "ascending_energy": False,
            "descending_energy": False,
            "balanced_energy": False,
            "spiritual_dominance": False,
            "material_dominance": False
        }
        
        # Verificar si hay ascenso energético
        if len(pick3_sefirot) >= 2:
            energies = [self._calculate_sefirot_energy([sef]) for sef in pick3_sefirot]
            patterns["ascending_energy"] = energies == sorted(energies)
            patterns["descending_energy"] = energies == sorted(energies, reverse=True)
            patterns["balanced_energy"] = abs(energies[0] - energies[-1]) <= 2
        
        # Verificar dominancia espiritual vs material
        spiritual_sefirot = ["Kether", "Chokmah", "Binah", "Chesed", "Geburah", "Tiphareth"]
        material_sefirot = ["Netzach", "Hod", "Yesod", "Malkuth"]
        
        spiritual_count = sum(1 for sef in pick3_sefirot if sef in spiritual_sefirot)
        material_count = sum(1 for sef in pick3_sefirot if sef in material_sefirot)
        
        patterns["spiritual_dominance"] = spiritual_count > material_count
        patterns["material_dominance"] = material_count > spiritual_count
        
        return patterns
    
    def _calculate_spiritual_significance(self, pick3_sefirot: List[str], pick4_sefirot: List[str]) -> Dict[str, Any]:
        """Calcula la significancia espiritual del sorteo"""
        all_sefirot = pick3_sefirot + pick4_sefirot
        
        # Contar frecuencias
        sefirot_freq = {}
        for sef in all_sefirot:
            sefirot_freq[sef] = sefirot_freq.get(sef, 0) + 1
        
        # Sefirot más frecuente
        most_frequent = max(sefirot_freq.items(), key=lambda x: x[1]) if sefirot_freq else ("None", 0)
        
        # Significancia espiritual
        spiritual_sefirot = ["Kether", "Chokmah", "Binah", "Chesed", "Geburah", "Tiphareth"]
        spiritual_count = sum(1 for sef in all_sefirot if sef in spiritual_sefirot)
        total_count = len(all_sefirot)
        
        return {
            "most_frequent_sefirot": most_frequent[0],
            "frequency": most_frequent[1],
            "spiritual_ratio": spiritual_count / total_count if total_count > 0 else 0,
            "spiritual_dominance": spiritual_count > total_count / 2,
            "energy_level": self._calculate_sefirot_energy(all_sefirot)
        }
    
    def _analyze_overall_sefirot_patterns(self, draw_analyses: List[Dict]) -> Dict[str, Any]:
        """Analiza patrones generales de todos los sorteos"""
        if not draw_analyses:
            return {}
        
        # Recopilar datos de todos los sorteos
        all_high_energy = []
        all_patterns = []
        all_spiritual = []
        
        for analysis in draw_analyses:
            all_high_energy.extend(analysis.get("high_energy_numbers", []))
            all_patterns.append(analysis.get("patterns", {}))
            all_spiritual.append(analysis.get("spiritual_significance", {}))
        
        # Análisis de frecuencias
        number_freq = {}
        for num in all_high_energy:
            number_freq[num] = number_freq.get(num, 0) + 1
        
        # Patrones más comunes
        pattern_counts = {
            "triple_sefirot": sum(1 for p in all_patterns if p.get("triple_sefirot", False)),
            "ascending_energy": sum(1 for p in all_patterns if p.get("ascending_energy", False)),
            "descending_energy": sum(1 for p in all_patterns if p.get("descending_energy", False)),
            "balanced_energy": sum(1 for p in all_patterns if p.get("balanced_energy", False)),
            "spiritual_dominance": sum(1 for p in all_patterns if p.get("spiritual_dominance", False)),
            "material_dominance": sum(1 for p in all_patterns if p.get("material_dominance", False))
        }
        
        # Números espirituales más frecuentes
        spiritual_numbers = []
        for s in all_spiritual:
            if s.get("spiritual_dominance", False):
                spiritual_numbers.extend([num for num in range(10) if self._is_spiritual_number(num)])
        
        return {
            "total_draws_analyzed": len(draw_analyses),
            "number_frequencies": number_freq,
            "pattern_counts": pattern_counts,
            "spiritual_numbers": list(set(spiritual_numbers)),
            "most_common_pattern": max(pattern_counts.items(), key=lambda x: x[1])[0] if pattern_counts else "none",
            "spiritual_dominance_ratio": sum(1 for s in all_spiritual if s.get("spiritual_dominance", False)) / len(all_spiritual)
        }
    
    def _is_spiritual_number(self, num: int) -> bool:
        """Determina si un número tiene significancia espiritual"""
        spiritual_numbers = [0, 1, 2, 3, 4, 5]  # Kether a Tiphareth
        return num in spiritual_numbers
    
    def _generate_candidate_numbers(self, sefirot_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Genera números candidatos basados en el análisis sefirótico"""
        draw_analyses = sefirot_analysis.get("draw_analyses", [])
        overall_patterns = sefirot_analysis.get("overall_patterns", {})
        
        candidate_numbers = {
            "high_energy_numbers": [],
            "medium_energy_numbers": [],
            "low_energy_numbers": [],
            "spiritual_numbers": [],
            "material_numbers": [],
            "pattern_numbers": []
        }
        
        # Extraer números de alta energía
        for draw_analysis in draw_analyses:
            high_energy = draw_analysis.get("high_energy_numbers", [])
            candidate_numbers["high_energy_numbers"].extend(high_energy)
        
        # Extraer números espirituales
        spiritual_numbers = overall_patterns.get("spiritual_numbers", [])
        candidate_numbers["spiritual_numbers"] = spiritual_numbers
        
        # Generar números basados en patrones
        pattern_numbers = self._generate_pattern_based_numbers(overall_patterns)
        candidate_numbers["pattern_numbers"] = pattern_numbers
        
        # Clasificar números por energía
        all_numbers = set()
        for category in ["high_energy_numbers", "spiritual_numbers", "pattern_numbers"]:
            all_numbers.update(candidate_numbers[category])
        
        for num in all_numbers:
            if num in candidate_numbers["high_energy_numbers"]:
                candidate_numbers["high_energy_numbers"].append(num)
            elif num in candidate_numbers["spiritual_numbers"]:
                candidate_numbers["medium_energy_numbers"].append(num)
            else:
                candidate_numbers["low_energy_numbers"].append(num)
        
        # Eliminar duplicados
        for category in candidate_numbers:
            candidate_numbers[category] = list(set(candidate_numbers[category]))
        
        return candidate_numbers
    
    def _generate_pattern_based_numbers(self, overall_patterns: Dict[str, Any]) -> List[int]:
        """Genera números basados en patrones sefiróticos"""
        pattern_numbers = []
        
        # Si hay dominancia espiritual, incluir números espirituales
        if overall_patterns.get("spiritual_dominance_ratio", 0) > 0.5:
            pattern_numbers.extend([0, 1, 2, 3, 4, 5])
        
        # Si hay patrones de energía ascendente, incluir números altos
        if overall_patterns.get("pattern_counts", {}).get("ascending_energy", 0) > 0:
            pattern_numbers.extend([6, 7, 8, 9])
        
        # Si hay patrones de energía descendente, incluir números bajos
        if overall_patterns.get("pattern_counts", {}).get("descending_energy", 0) > 0:
            pattern_numbers.extend([0, 1, 2, 3])
        
        return list(set(pattern_numbers))
    
    def _correlate_with_prioritized_numbers(self, candidate_numbers: Dict[str, Any], prioritized_numbers: Dict[str, Any]) -> Dict[str, Any]:
        """Correlaciona números candidatos con números priorizados"""
        correlation = {
            "high_correlation": [],
            "medium_correlation": [],
            "low_correlation": [],
            "correlation_scores": {}
        }
        
        if not prioritized_numbers:
            return correlation
        
        # Obtener números priorizados
        prioritized = prioritized_numbers.get("prioritized_numbers", [])
        
        # Calcular correlaciones
        for category, numbers in candidate_numbers.items():
            for num in numbers:
                if num in prioritized:
                    correlation["high_correlation"].append(num)
                    correlation["correlation_scores"][num] = 1.0
                else:
                    correlation["low_correlation"].append(num)
                    correlation["correlation_scores"][num] = 0.3
        
        # Eliminar duplicados
        for category in ["high_correlation", "medium_correlation", "low_correlation"]:
            correlation[category] = list(set(correlation[category]))
        
        return correlation
    
    def _create_series_profile(self, correlation_analysis: Dict[str, Any], sefirot_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Crea perfil para generación de series"""
        return {
            "high_priority_numbers": correlation_analysis.get("high_correlation", []),
            "medium_priority_numbers": correlation_analysis.get("medium_correlation", []),
            "low_priority_numbers": correlation_analysis.get("low_correlation", []),
            "spiritual_numbers": sefirot_analysis.get("overall_patterns", {}).get("spiritual_numbers", []),
            "energy_level": self._calculate_overall_energy_level(sefirot_analysis),
            "pattern_preferences": self._extract_pattern_preferences(sefirot_analysis),
            "series_guidelines": self._generate_series_guidelines(correlation_analysis, sefirot_analysis)
        }
    
    def _calculate_overall_energy_level(self, sefirot_analysis: Dict[str, Any]) -> str:
        """Calcula el nivel energético general"""
        draw_analyses = sefirot_analysis.get("draw_analyses", [])
        if not draw_analyses:
            return "unknown"
        
        total_energy = sum(analysis.get("total_energy", 0) for analysis in draw_analyses)
        avg_energy = total_energy / len(draw_analyses)
        
        if avg_energy >= 20:
            return "very_high"
        elif avg_energy >= 15:
            return "high"
        elif avg_energy >= 10:
            return "medium"
        else:
            return "low"
    
    def _extract_pattern_preferences(self, sefirot_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae preferencias de patrones para series"""
        overall_patterns = sefirot_analysis.get("overall_patterns", {})
        pattern_counts = overall_patterns.get("pattern_counts", {})
        
        preferences = {
            "prefer_spiritual": pattern_counts.get("spiritual_dominance", 0) > pattern_counts.get("material_dominance", 0),
            "prefer_ascending": pattern_counts.get("ascending_energy", 0) > pattern_counts.get("descending_energy", 0),
            "prefer_balanced": pattern_counts.get("balanced_energy", 0) > 0,
            "prefer_triple": pattern_counts.get("triple_sefirot", 0) > 0
        }
        
        return preferences
    
    def _generate_series_guidelines(self, correlation_analysis: Dict[str, Any], sefirot_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Genera directrices para la creación de series"""
        return {
            "min_spiritual_numbers": 1,
            "max_material_numbers": 2,
            "prefer_high_energy": True,
            "balance_required": True,
            "spiritual_dominance_preferred": sefirot_analysis.get("overall_patterns", {}).get("spiritual_dominance_ratio", 0) > 0.5
        }
    
    def _analyze_energy_flow(self, sefirot_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza el flujo energético entre sorteos"""
        draw_analyses = sefirot_analysis.get("draw_analyses", [])
        if len(draw_analyses) < 2:
            return {"flow_type": "insufficient_data"}
        
        energies = [analysis.get("total_energy", 0) for analysis in draw_analyses]
        
        # Calcular tendencia energética
        energy_changes = [energies[i] - energies[i-1] for i in range(1, len(energies))]
        avg_change = sum(energy_changes) / len(energy_changes)
        
        return {
            "flow_type": "ascending" if avg_change > 0 else "descending" if avg_change < 0 else "stable",
            "energy_changes": energy_changes,
            "average_change": avg_change,
            "current_energy": energies[-1],
            "energy_volatility": max(energies) - min(energies)
        }
    
    def _analyze_spiritual_significance(self, sefirot_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza la significancia espiritual general"""
        draw_analyses = sefirot_analysis.get("draw_analyses", [])
        if not draw_analyses:
            return {"significance": "unknown"}
        
        spiritual_ratios = [analysis.get("spiritual_significance", {}).get("spiritual_ratio", 0) for analysis in draw_analyses]
        avg_spiritual_ratio = sum(spiritual_ratios) / len(spiritual_ratios)
        
        return {
            "significance": "high" if avg_spiritual_ratio > 0.6 else "medium" if avg_spiritual_ratio > 0.4 else "low",
            "average_spiritual_ratio": avg_spiritual_ratio,
            "spiritual_trend": "increasing" if spiritual_ratios[-1] > spiritual_ratios[0] else "decreasing" if spiritual_ratios[-1] < spiritual_ratios[0] else "stable",
            "spiritual_dominance_count": sum(1 for analysis in draw_analyses if analysis.get("spiritual_significance", {}).get("spiritual_dominance", False))
        }




