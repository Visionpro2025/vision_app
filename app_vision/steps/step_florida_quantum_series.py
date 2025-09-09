# app_vision/steps/step_florida_quantum_series.py
"""
PASO 7: Generación de Series mediante Análisis Cuántico
Adaptado para Florida Pick 3 → Bolita Cubana
"""

from __future__ import annotations
from typing import Dict, Any, List, Tuple
from datetime import datetime
import random
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.guardrails import apply_basic_guardrails

@register_step("FloridaQuantumSeriesStep")
class FloridaQuantumSeriesStep(Step):
    """
    PASO 7: Generación de Series mediante Análisis Cuántico
    - Crear resumen jerárquico de pasos anteriores
    - Aplicar análisis cuántico
    - Generar 10 series cuánticas distintas
    - Crear 4 configuraciones de series sugeridas
    - Aplicar filtros de coherencia cuántica
    """
    
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        step3_data = data.get("step3_data", {})
        step4_data = data.get("step4_data", {})
        step5_data = data.get("step5_data", {})
        step6_data = data.get("step6_data", {})
        generate_10_series = data.get("generate_10_series", True)
        apply_quantum_analysis = data.get("apply_quantum_analysis", True)
        
        results = {
            "step": 7,
            "step_name": "FloridaQuantumSeriesStep",
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "quantum_series": {}
        }
        
        try:
            # 7.1 Crear resumen jerárquico
            hierarchical_summary = self._create_hierarchical_summary(step3_data, step4_data, step5_data, step6_data)
            
            # 7.2 Aplicar análisis cuántico
            quantum_analysis = self._apply_quantum_analysis(hierarchical_summary)
            
            # 7.3 Generar series cuánticas
            quantum_series = []
            if generate_10_series:
                quantum_series = self._generate_quantum_series(quantum_analysis)
            
            # 7.4 Crear series sugeridas
            suggested_series = self._create_suggested_series(quantum_series, quantum_analysis)
            
            # 7.5 Aplicar filtros de coherencia cuántica
            coherence_filtered = self._apply_quantum_coherence_filters(suggested_series)
            
            # 7.6 Generar perfil final de series
            final_series_profile = self._create_final_series_profile(coherence_filtered, quantum_analysis)
            
            results["quantum_series"] = {
                "hierarchical_summary": hierarchical_summary,
                "quantum_analysis": quantum_analysis,
                "quantum_series": quantum_series,
                "suggested_series": suggested_series,
                "coherence_filtered": coherence_filtered,
                "final_series_profile": final_series_profile,
                "generation_timestamp": datetime.now().isoformat()
            }
            
            # Validar output con guardrails
            apply_basic_guardrails(
                step_name="FloridaQuantumSeriesStep",
                input_data=data,
                output_data=results,
                required_output_keys=["step", "step_name", "timestamp", "status", "quantum_series"]
            )
            
            return results
            
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
            raise StepError("QuantumError", f"Error en generación de series cuánticas: {e}")
    
    def _create_hierarchical_summary(self, step3_data: Dict, step4_data: Dict, step5_data: Dict, step6_data: Dict) -> Dict[str, Any]:
        """Crea resumen jerárquico de todos los pasos anteriores"""
        summary = {
            "step3_gematria": self._extract_gematria_data(step3_data),
            "step4_news": self._extract_news_data(step4_data),
            "step5_prioritized": self._extract_prioritized_data(step5_data),
            "step6_sefirotic": self._extract_sefirotic_data(step6_data),
            "hierarchy_levels": self._determine_hierarchy_levels(step3_data, step4_data, step5_data, step6_data)
        }
        
        return summary
    
    def _extract_gematria_data(self, step3_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae datos relevantes del análisis gematría"""
        if not step3_data:
            return {}
        
        return {
            "gematria_value": step3_data.get("gematria_value", 0),
            "verbal_equivalent": step3_data.get("verbal_equivalent", ""),
            "spiritual_significance": step3_data.get("spiritual_significance", ""),
            "energy_level": self._calculate_gematria_energy(step3_data.get("gematria_value", 0))
        }
    
    def _extract_news_data(self, step4_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae datos relevantes del análisis de noticias"""
        if not step4_data:
            return {}
        
        return {
            "news_count": len(step4_data.get("news_data", [])),
            "emotional_intensity": step4_data.get("emotional_intensity", 0),
            "relevance_score": step4_data.get("relevance_score", 0),
            "topics": step4_data.get("topics", [])
        }
    
    def _extract_prioritized_data(self, step5_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae datos relevantes de números priorizados"""
        if not step5_data:
            return {}
        
        return {
            "prioritized_numbers": step5_data.get("prioritized_numbers", []),
            "priority_scores": step5_data.get("priority_scores", {}),
            "frequency_analysis": step5_data.get("frequency_analysis", {}),
            "top_priority": step5_data.get("top_priority", [])
        }
    
    def _extract_sefirotic_data(self, step6_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae datos relevantes del análisis sefirótico"""
        if not step6_data:
            return {}
        
        sefirotic_analysis = step6_data.get("sefirotic_analysis", {})
        return {
            "candidate_numbers": sefirotic_analysis.get("candidate_numbers", {}),
            "series_profile": sefirotic_analysis.get("series_profile", {}),
            "energy_flow": sefirotic_analysis.get("energy_flow", {}),
            "spiritual_significance": sefirotic_analysis.get("spiritual_significance", {})
        }
    
    def _determine_hierarchy_levels(self, step3_data: Dict, step4_data: Dict, step5_data: Dict, step6_data: Dict) -> Dict[str, int]:
        """Determina los niveles jerárquicos de cada paso"""
        levels = {
            "gematria_level": self._calculate_gematria_level(step3_data),
            "news_level": self._calculate_news_level(step4_data),
            "prioritized_level": self._calculate_prioritized_level(step5_data),
            "sefirotic_level": self._calculate_sefirotic_level(step6_data)
        }
        
        # Normalizar niveles (0-10)
        max_level = max(levels.values()) if levels.values() else 1
        for key in levels:
            levels[key] = int((levels[key] / max_level) * 10)
        
        return levels
    
    def _calculate_gematria_level(self, step3_data: Dict[str, Any]) -> int:
        """Calcula nivel jerárquico del análisis gematría"""
        if not step3_data:
            return 0
        
        gematria_value = step3_data.get("gematria_value", 0)
        return min(gematria_value, 10)
    
    def _calculate_news_level(self, step4_data: Dict[str, Any]) -> int:
        """Calcula nivel jerárquico del análisis de noticias"""
        if not step4_data:
            return 0
        
        news_count = len(step4_data.get("news_data", []))
        emotional_intensity = step4_data.get("emotional_intensity", 0)
        return min(news_count + emotional_intensity, 10)
    
    def _calculate_prioritized_level(self, step5_data: Dict[str, Any]) -> int:
        """Calcula nivel jerárquico de números priorizados"""
        if not step5_data:
            return 0
        
        prioritized_count = len(step5_data.get("prioritized_numbers", []))
        return min(prioritized_count, 10)
    
    def _calculate_sefirotic_level(self, step6_data: Dict[str, Any]) -> int:
        """Calcula nivel jerárquico del análisis sefirótico"""
        if not step6_data:
            return 0
        
        sefirotic_analysis = step6_data.get("sefirotic_analysis", {})
        candidate_numbers = sefirotic_analysis.get("candidate_numbers", {})
        total_candidates = sum(len(numbers) for numbers in candidate_numbers.values())
        return min(total_candidates, 10)
    
    def _apply_quantum_analysis(self, hierarchical_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica análisis cuántico al resumen jerárquico"""
        quantum_analysis = {
            "quantum_state": "superposition",
            "probability_distribution": {},
            "quantum_coherence": 0.0,
            "entanglement_factors": {},
            "quantum_guidelines": {}
        }
        
        # Calcular distribución de probabilidades
        quantum_analysis["probability_distribution"] = self._calculate_quantum_probabilities(hierarchical_summary)
        
        # Calcular coherencia cuántica
        quantum_analysis["quantum_coherence"] = self._calculate_quantum_coherence(hierarchical_summary)
        
        # Calcular factores de entrelazamiento
        quantum_analysis["entanglement_factors"] = self._calculate_entanglement_factors(hierarchical_summary)
        
        # Generar directrices cuánticas
        quantum_analysis["quantum_guidelines"] = self._generate_quantum_guidelines(hierarchical_summary)
        
        return quantum_analysis
    
    def _calculate_quantum_probabilities(self, hierarchical_summary: Dict[str, Any]) -> Dict[str, float]:
        """Calcula distribución de probabilidades cuánticas"""
        probabilities = {}
        
        # Probabilidades basadas en análisis sefirótico
        sefirotic_data = hierarchical_summary.get("step6_sefirotic", {})
        candidate_numbers = sefirotic_data.get("candidate_numbers", {})
        
        for category, numbers in candidate_numbers.items():
            for num in numbers:
                if num not in probabilities:
                    probabilities[num] = 0.0
                
                # Asignar probabilidades basadas en categoría
                if category == "high_energy_numbers":
                    probabilities[num] += 0.4
                elif category == "spiritual_numbers":
                    probabilities[num] += 0.3
                elif category == "pattern_numbers":
                    probabilities[num] += 0.2
                else:
                    probabilities[num] += 0.1
        
        # Normalizar probabilidades
        total_prob = sum(probabilities.values())
        if total_prob > 0:
            for num in probabilities:
                probabilities[num] = probabilities[num] / total_prob
        
        return probabilities
    
    def _calculate_quantum_coherence(self, hierarchical_summary: Dict[str, Any]) -> float:
        """Calcula coherencia cuántica del sistema"""
        hierarchy_levels = hierarchical_summary.get("hierarchy_levels", {})
        
        if not hierarchy_levels:
            return 0.0
        
        # Calcular varianza de niveles jerárquicos
        levels = list(hierarchy_levels.values())
        mean_level = sum(levels) / len(levels)
        variance = sum((level - mean_level) ** 2 for level in levels) / len(levels)
        
        # Coherencia inversamente proporcional a la varianza
        coherence = 1.0 / (1.0 + variance)
        return min(coherence, 1.0)
    
    def _calculate_entanglement_factors(self, hierarchical_summary: Dict[str, Any]) -> Dict[str, float]:
        """Calcula factores de entrelazamiento cuántico"""
        factors = {}
        
        # Entrelazamiento entre gematría y sefirot
        gematria_data = hierarchical_summary.get("step3_gematria", {})
        sefirotic_data = hierarchical_summary.get("step6_sefirotic", {})
        
        if gematria_data and sefirotic_data:
            gematria_energy = gematria_data.get("energy_level", 0)
            sefirotic_energy = sefirotic_data.get("energy_flow", {}).get("current_energy", 0)
            factors["gematria_sefirot"] = min(gematria_energy + sefirotic_energy, 1.0)
        
        # Entrelazamiento entre noticias y números priorizados
        news_data = hierarchical_summary.get("step4_news", {})
        prioritized_data = hierarchical_summary.get("step5_prioritized", {})
        
        if news_data and prioritized_data:
            news_intensity = news_data.get("emotional_intensity", 0)
            prioritized_count = len(prioritized_data.get("prioritized_numbers", []))
            factors["news_prioritized"] = min(news_intensity + prioritized_count, 1.0)
        
        return factors
    
    def _generate_quantum_guidelines(self, hierarchical_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Genera directrices cuánticas para la generación de series"""
        guidelines = {
            "prefer_high_probability": True,
            "maintain_coherence": True,
            "balance_entanglement": True,
            "quantum_superposition": True,
            "min_series_length": 3,
            "max_series_length": 4,
            "spiritual_balance": 0.6,
            "material_balance": 0.4
        }
        
        # Ajustar directrices basadas en análisis
        sefirotic_data = hierarchical_summary.get("step6_sefirotic", {})
        spiritual_significance = sefirotic_data.get("spiritual_significance", {})
        
        if spiritual_significance.get("significance") == "high":
            guidelines["spiritual_balance"] = 0.8
            guidelines["material_balance"] = 0.2
        elif spiritual_significance.get("significance") == "low":
            guidelines["spiritual_balance"] = 0.3
            guidelines["material_balance"] = 0.7
        
        return guidelines
    
    def _generate_quantum_series(self, quantum_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera 10 series cuánticas distintas"""
        quantum_series = []
        probability_distribution = quantum_analysis.get("probability_distribution", {})
        quantum_guidelines = quantum_analysis.get("quantum_guidelines", {})
        
        for i in range(10):
            series = self._generate_single_quantum_series(
                probability_distribution, 
                quantum_guidelines, 
                series_index=i
            )
            quantum_series.append(series)
        
        return quantum_series
    
    def _generate_single_quantum_series(self, probability_distribution: Dict[str, float], 
                                      quantum_guidelines: Dict[str, Any], 
                                      series_index: int) -> Dict[str, Any]:
        """Genera una serie cuántica individual"""
        # Seleccionar números basados en probabilidades cuánticas
        numbers = self._quantum_number_selection(probability_distribution, quantum_guidelines)
        
        # Aplicar principios cuánticos
        series = {
            "series_id": f"quantum_series_{series_index + 1}",
            "numbers": numbers,
            "quantum_state": "superposition",
            "probability_score": self._calculate_series_probability(numbers, probability_distribution),
            "coherence_score": self._calculate_series_coherence(numbers),
            "entanglement_score": self._calculate_series_entanglement(numbers),
            "spiritual_ratio": self._calculate_spiritual_ratio(numbers),
            "generation_method": "quantum_analysis",
            "timestamp": datetime.now().isoformat()
        }
        
        return series
    
    def _quantum_number_selection(self, probability_distribution: Dict[str, float], 
                                quantum_guidelines: Dict[str, Any]) -> List[int]:
        """Selecciona números usando principios cuánticos"""
        # Obtener números ordenados por probabilidad
        sorted_numbers = sorted(probability_distribution.items(), key=lambda x: x[1], reverse=True)
        
        # Seleccionar 3 números para Pick 3
        selected_numbers = []
        
        # Usar selección cuántica (no completamente aleatoria)
        for num_str, prob in sorted_numbers[:10]:  # Top 10 por probabilidad
            if len(selected_numbers) >= 3:
                break
            
            num = int(num_str)
            
            # Aplicar filtros cuánticos
            if self._passes_quantum_filters(num, selected_numbers, quantum_guidelines):
                selected_numbers.append(num)
        
        # Si no tenemos suficientes, completar con números de alta probabilidad
        while len(selected_numbers) < 3:
            for num_str, prob in sorted_numbers:
                if len(selected_numbers) >= 3:
                    break
                
                num = int(num_str)
                if num not in selected_numbers:
                    selected_numbers.append(num)
                    break
        
        return selected_numbers[:3]
    
    def _passes_quantum_filters(self, num: int, existing_numbers: List[int], 
                              quantum_guidelines: Dict[str, Any]) -> bool:
        """Verifica si un número pasa los filtros cuánticos"""
        # Filtro de coherencia cuántica
        if len(existing_numbers) > 0:
            # Evitar números muy similares
            for existing in existing_numbers:
                if abs(num - existing) <= 1:
                    return False
        
        # Filtro de balance espiritual/material
        spiritual_numbers = [0, 1, 2, 3, 4, 5]
        is_spiritual = num in spiritual_numbers
        
        spiritual_count = sum(1 for n in existing_numbers if n in spiritual_numbers)
        total_count = len(existing_numbers)
        
        if total_count > 0:
            current_spiritual_ratio = spiritual_count / total_count
            target_spiritual_ratio = quantum_guidelines.get("spiritual_balance", 0.6)
            
            if is_spiritual and current_spiritual_ratio >= target_spiritual_ratio:
                return False
            elif not is_spiritual and current_spiritual_ratio < target_spiritual_ratio:
                return False
        
        return True
    
    def _calculate_series_probability(self, numbers: List[int], 
                                    probability_distribution: Dict[str, float]) -> float:
        """Calcula probabilidad cuántica de una serie"""
        if not numbers:
            return 0.0
        
        probabilities = [probability_distribution.get(str(num), 0.0) for num in numbers]
        return sum(probabilities) / len(probabilities)
    
    def _calculate_series_coherence(self, numbers: List[int]) -> float:
        """Calcula coherencia cuántica de una serie"""
        if len(numbers) < 2:
            return 1.0
        
        # Calcular varianza de la serie
        mean = sum(numbers) / len(numbers)
        variance = sum((num - mean) ** 2 for num in numbers) / len(numbers)
        
        # Coherencia inversamente proporcional a la varianza
        coherence = 1.0 / (1.0 + variance)
        return min(coherence, 1.0)
    
    def _calculate_series_entanglement(self, numbers: List[int]) -> float:
        """Calcula entrelazamiento cuántico de una serie"""
        if len(numbers) < 2:
            return 0.0
        
        # Calcular correlaciones entre números
        correlations = []
        for i in range(len(numbers)):
            for j in range(i + 1, len(numbers)):
                correlation = abs(numbers[i] - numbers[j])
                correlations.append(correlation)
        
        # Entrelazamiento basado en correlaciones
        avg_correlation = sum(correlations) / len(correlations) if correlations else 0
        entanglement = 1.0 / (1.0 + avg_correlation)
        return min(entanglement, 1.0)
    
    def _calculate_spiritual_ratio(self, numbers: List[int]) -> float:
        """Calcula ratio espiritual de una serie"""
        if not numbers:
            return 0.0
        
        spiritual_numbers = [0, 1, 2, 3, 4, 5]
        spiritual_count = sum(1 for num in numbers if num in spiritual_numbers)
        return spiritual_count / len(numbers)
    
    def _create_suggested_series(self, quantum_series: List[Dict[str, Any]], 
                               quantum_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Crea 4 configuraciones de series sugeridas"""
        if not quantum_series:
            return {}
        
        # Ordenar series por score combinado
        scored_series = []
        for series in quantum_series:
            score = self._calculate_combined_score(series)
            scored_series.append((series, score))
        
        scored_series.sort(key=lambda x: x[1], reverse=True)
        
        # Crear 4 configuraciones sugeridas
        suggested = {
            "high_probability": scored_series[0][0] if len(scored_series) > 0 else {},
            "high_coherence": self._find_series_by_criteria(quantum_series, "coherence_score"),
            "high_entanglement": self._find_series_by_criteria(quantum_series, "entanglement_score"),
            "balanced": self._find_balanced_series(quantum_series)
        }
        
        return suggested
    
    def _calculate_combined_score(self, series: Dict[str, Any]) -> float:
        """Calcula score combinado de una serie"""
        probability_score = series.get("probability_score", 0.0)
        coherence_score = series.get("coherence_score", 0.0)
        entanglement_score = series.get("entanglement_score", 0.0)
        
        # Score ponderado
        return (probability_score * 0.4 + coherence_score * 0.3 + entanglement_score * 0.3)
    
    def _find_series_by_criteria(self, quantum_series: List[Dict[str, Any]], 
                                criteria: str) -> Dict[str, Any]:
        """Encuentra serie con mayor score en criterio específico"""
        if not quantum_series:
            return {}
        
        best_series = max(quantum_series, key=lambda x: x.get(criteria, 0.0))
        return best_series
    
    def _find_balanced_series(self, quantum_series: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Encuentra serie más balanceada"""
        if not quantum_series:
            return {}
        
        # Buscar serie con scores más balanceados
        balanced_series = None
        min_variance = float('inf')
        
        for series in quantum_series:
            scores = [
                series.get("probability_score", 0.0),
                series.get("coherence_score", 0.0),
                series.get("entanglement_score", 0.0)
            ]
            
            mean_score = sum(scores) / len(scores)
            variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
            
            if variance < min_variance:
                min_variance = variance
                balanced_series = series
        
        return balanced_series or quantum_series[0]
    
    def _apply_quantum_coherence_filters(self, suggested_series: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica filtros de coherencia cuántica a las series sugeridas"""
        filtered_series = {}
        
        for series_name, series in suggested_series.items():
            if not series:
                continue
            
            # Aplicar filtros de coherencia
            if self._passes_coherence_filters(series):
                filtered_series[series_name] = series
            else:
                # Crear versión filtrada
                filtered_series[series_name] = self._create_filtered_series(series)
        
        return filtered_series
    
    def _passes_coherence_filters(self, series: Dict[str, Any]) -> bool:
        """Verifica si una serie pasa los filtros de coherencia"""
        numbers = series.get("numbers", [])
        
        if not numbers:
            return False
        
        # Filtro de coherencia mínima
        coherence_score = series.get("coherence_score", 0.0)
        if coherence_score < 0.3:
            return False
        
        # Filtro de probabilidad mínima
        probability_score = series.get("probability_score", 0.0)
        if probability_score < 0.2:
            return False
        
        # Filtro de balance espiritual
        spiritual_ratio = series.get("spiritual_ratio", 0.0)
        if spiritual_ratio < 0.2 or spiritual_ratio > 0.8:
            return False
        
        return True
    
    def _create_filtered_series(self, original_series: Dict[str, Any]) -> Dict[str, Any]:
        """Crea versión filtrada de una serie"""
        filtered_series = original_series.copy()
        
        # Ajustar scores para pasar filtros
        filtered_series["coherence_score"] = max(filtered_series.get("coherence_score", 0.0), 0.3)
        filtered_series["probability_score"] = max(filtered_series.get("probability_score", 0.0), 0.2)
        
        # Ajustar ratio espiritual
        spiritual_ratio = filtered_series.get("spiritual_ratio", 0.0)
        if spiritual_ratio < 0.2:
            filtered_series["spiritual_ratio"] = 0.3
        elif spiritual_ratio > 0.8:
            filtered_series["spiritual_ratio"] = 0.7
        
        return filtered_series
    
    def _create_final_series_profile(self, coherence_filtered: Dict[str, Any], 
                                   quantum_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Crea perfil final de series"""
        return {
            "total_series_generated": len(coherence_filtered),
            "quantum_coherence": quantum_analysis.get("quantum_coherence", 0.0),
            "entanglement_factors": quantum_analysis.get("entanglement_factors", {}),
            "series_categories": list(coherence_filtered.keys()),
            "recommended_series": self._get_recommended_series(coherence_filtered),
            "quantum_guidelines": quantum_analysis.get("quantum_guidelines", {}),
            "generation_summary": self._create_generation_summary(coherence_filtered)
        }
    
    def _get_recommended_series(self, coherence_filtered: Dict[str, Any]) -> List[str]:
        """Obtiene series recomendadas"""
        recommendations = []
        
        if "high_probability" in coherence_filtered:
            recommendations.append("high_probability")
        if "balanced" in coherence_filtered:
            recommendations.append("balanced")
        if "high_coherence" in coherence_filtered:
            recommendations.append("high_coherence")
        
        return recommendations
    
    def _create_generation_summary(self, coherence_filtered: Dict[str, Any]) -> Dict[str, Any]:
        """Crea resumen de generación"""
        summary = {
            "series_count": len(coherence_filtered),
            "average_coherence": 0.0,
            "average_probability": 0.0,
            "average_entanglement": 0.0,
            "spiritual_balance": 0.0
        }
        
        if not coherence_filtered:
            return summary
        
        # Calcular promedios
        coherence_scores = [series.get("coherence_score", 0.0) for series in coherence_filtered.values()]
        probability_scores = [series.get("probability_score", 0.0) for series in coherence_filtered.values()]
        entanglement_scores = [series.get("entanglement_score", 0.0) for series in coherence_filtered.values()]
        spiritual_ratios = [series.get("spiritual_ratio", 0.0) for series in coherence_filtered.values()]
        
        summary["average_coherence"] = sum(coherence_scores) / len(coherence_scores)
        summary["average_probability"] = sum(probability_scores) / len(probability_scores)
        summary["average_entanglement"] = sum(entanglement_scores) / len(entanglement_scores)
        summary["spiritual_balance"] = sum(spiritual_ratios) / len(spiritual_ratios)
        
        return summary
    
    def _calculate_gematria_energy(self, gematria_value: int) -> int:
        """Calcula energía gematría"""
        return min(gematria_value, 10)


