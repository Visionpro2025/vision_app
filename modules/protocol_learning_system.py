# modules/protocol_learning_system.py
"""
SISTEMA DE APRENDIZAJE Y ADAPTACIÓN PARA PROTOCOLO UNIVERSAL OFICIAL
====================================================================

Sistema inteligente que aprende de cada ejecución del protocolo para optimizar
futuras ejecuciones y adaptarse a diferentes tipos de loterías.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

@dataclass
class ExecutionPattern:
    """Patrón de ejecución identificado."""
    pattern_id: str
    pattern_type: str
    frequency: int
    success_rate: float
    avg_duration: float
    lottery_types: List[str]
    characteristics: Dict[str, Any]
    last_seen: datetime

@dataclass
class OptimizationSuggestion:
    """Sugerencia de optimización."""
    suggestion_id: str
    category: str
    description: str
    expected_improvement: float
    implementation_difficulty: str
    priority: int
    evidence: List[str]

@dataclass
class LearningInsight:
    """Insight aprendido del análisis."""
    insight_id: str
    category: str
    description: str
    confidence: float
    supporting_evidence: List[str]
    discovered_at: datetime

class ProtocolLearningSystem:
    """
    Sistema de aprendizaje y adaptación para el protocolo universal oficial.
    """
    
    def __init__(self):
        """Inicializa el sistema de aprendizaje."""
        self.learning_data_dir = Path("learning_data")
        self.learning_data_dir.mkdir(exist_ok=True)
        
        # Almacenamiento de datos de aprendizaje
        self.execution_history: List[Dict] = []
        self.patterns: Dict[str, ExecutionPattern] = {}
        self.optimization_suggestions: List[OptimizationSuggestion] = []
        self.learning_insights: List[LearningInsight] = []
        
        # Métricas de aprendizaje
        self.learning_metrics = {
            "total_executions_analyzed": 0,
            "patterns_identified": 0,
            "suggestions_generated": 0,
            "insights_discovered": 0,
            "last_learning_session": None
        }
        
        # Cargar datos existentes
        self._load_learning_data()
        
        logger.info("Sistema de Aprendizaje del Protocolo inicializado")
    
    def learn_from_execution(self, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aprende de una ejecución del protocolo.
        
        Args:
            execution_data: Datos completos de la ejecución
            
        Returns:
            Dict con resultados del aprendizaje
        """
        try:
            # Validar datos de entrada
            if not self._validate_execution_data(execution_data):
                return {"error": "Datos de ejecución inválidos", "learned": False}
            
            # Agregar a historial
            self.execution_history.append(execution_data)
            
            # Analizar patrones
            patterns_found = self._analyze_execution_patterns(execution_data)
            
            # Generar insights
            insights_generated = self._generate_insights(execution_data)
            
            # Actualizar métricas
            self.learning_metrics["total_executions_analyzed"] += 1
            self.learning_metrics["patterns_identified"] += len(patterns_found)
            self.learning_metrics["insights_discovered"] += len(insights_generated)
            self.learning_metrics["last_learning_session"] = datetime.now().isoformat()
            
            # Guardar datos de aprendizaje
            self._save_learning_data()
            
            learning_result = {
                "learned": True,
                "patterns_found": len(patterns_found),
                "insights_generated": len(insights_generated),
                "execution_id": execution_data.get("execution_id"),
                "learning_timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Aprendizaje completado para ejecución {execution_data.get('execution_id')}")
            return learning_result
            
        except Exception as e:
            logger.error(f"Error en aprendizaje: {e}")
            return {"error": str(e), "learned": False}
    
    def suggest_optimizations(self, lottery_type: str = None) -> List[OptimizationSuggestion]:
        """
        Sugiere optimizaciones basadas en datos históricos.
        
        Args:
            lottery_type: Tipo de lotería específico (opcional)
            
        Returns:
            Lista de sugerencias de optimización
        """
        try:
            suggestions = []
            
            # Analizar rendimiento por paso
            step_performance = self._analyze_step_performance(lottery_type)
            suggestions.extend(self._generate_step_optimizations(step_performance))
            
            # Analizar patrones de error
            error_patterns = self._analyze_error_patterns(lottery_type)
            suggestions.extend(self._generate_error_optimizations(error_patterns))
            
            # Analizar eficiencia temporal
            time_efficiency = self._analyze_time_efficiency(lottery_type)
            suggestions.extend(self._generate_time_optimizations(time_efficiency))
            
            # Analizar precisión de resultados
            accuracy_analysis = self._analyze_result_accuracy(lottery_type)
            suggestions.extend(self._generate_accuracy_optimizations(accuracy_analysis))
            
            # Ordenar por prioridad
            suggestions.sort(key=lambda x: x.priority, reverse=True)
            
            # Actualizar métricas
            self.learning_metrics["suggestions_generated"] += len(suggestions)
            
            logger.info(f"Generadas {len(suggestions)} sugerencias de optimización")
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generando sugerencias: {e}")
            return []
    
    def get_adaptive_parameters(self, lottery_type: str, step_number: int) -> Dict[str, Any]:
        """
        Obtiene parámetros adaptativos para un paso específico.
        
        Args:
            lottery_type: Tipo de lotería
            step_number: Número del paso
            
        Returns:
            Dict con parámetros adaptativos
        """
        try:
            adaptive_params = {}
            
            # Analizar ejecuciones exitosas para este tipo de lotería
            successful_executions = self._get_successful_executions(lottery_type)
            
            if successful_executions:
                # Calcular parámetros óptimos
                optimal_params = self._calculate_optimal_parameters(
                    successful_executions, step_number
                )
                adaptive_params.update(optimal_params)
            
            # Aplicar ajustes basados en patrones
            pattern_adjustments = self._get_pattern_adjustments(lottery_type, step_number)
            adaptive_params.update(pattern_adjustments)
            
            return adaptive_params
            
        except Exception as e:
            logger.error(f"Error obteniendo parámetros adaptativos: {e}")
            return {}
    
    def predict_execution_success(self, lottery_type: str, current_step: int, 
                                step_data: Dict) -> Dict[str, Any]:
        """
        Predice la probabilidad de éxito de la ejecución actual.
        
        Args:
            lottery_type: Tipo de lotería
            current_step: Paso actual
            step_data: Datos del paso actual
            
        Returns:
            Dict con predicción de éxito
        """
        try:
            # Analizar patrones históricos similares
            similar_executions = self._find_similar_executions(
                lottery_type, current_step, step_data
            )
            
            if not similar_executions:
                return {
                    "success_probability": 0.5,
                    "confidence": 0.0,
                    "prediction_based_on": "insufficient_data"
                }
            
            # Calcular probabilidad de éxito
            success_rate = sum(1 for ex in similar_executions if ex.get("success", False)) / len(similar_executions)
            
            # Calcular confianza basada en cantidad de datos
            confidence = min(len(similar_executions) / 10.0, 1.0)
            
            # Identificar factores de riesgo
            risk_factors = self._identify_risk_factors(similar_executions, step_data)
            
            prediction = {
                "success_probability": success_rate,
                "confidence": confidence,
                "prediction_based_on": f"{len(similar_executions)} similar_executions",
                "risk_factors": risk_factors,
                "recommendations": self._generate_success_recommendations(risk_factors)
            }
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error prediciendo éxito: {e}")
            return {"error": str(e)}
    
    def _validate_execution_data(self, execution_data: Dict) -> bool:
        """Valida que los datos de ejecución sean válidos."""
        required_fields = ["execution_id", "lottery_type", "steps", "success_rate"]
        return all(field in execution_data for field in required_fields)
    
    def _analyze_execution_patterns(self, execution_data: Dict) -> List[ExecutionPattern]:
        """Analiza patrones en la ejecución."""
        patterns_found = []
        
        try:
            # Analizar patrones de duración
            duration_pattern = self._analyze_duration_pattern(execution_data)
            if duration_pattern:
                patterns_found.append(duration_pattern)
            
            # Analizar patrones de éxito
            success_pattern = self._analyze_success_pattern(execution_data)
            if success_pattern:
                patterns_found.append(success_pattern)
            
            # Analizar patrones de lotería
            lottery_pattern = self._analyze_lottery_pattern(execution_data)
            if lottery_pattern:
                patterns_found.append(lottery_pattern)
            
            return patterns_found
            
        except Exception as e:
            logger.error(f"Error analizando patrones: {e}")
            return []
    
    def _analyze_duration_pattern(self, execution_data: Dict) -> Optional[ExecutionPattern]:
        """Analiza patrones de duración."""
        try:
            total_duration = execution_data.get("total_duration_seconds", 0)
            lottery_type = execution_data.get("lottery_type", "unknown")
            
            # Clasificar duración
            if total_duration < 60:
                duration_category = "fast"
            elif total_duration < 300:
                duration_category = "normal"
            else:
                duration_category = "slow"
            
            pattern_id = f"duration_{duration_category}_{lottery_type}"
            
            if pattern_id in self.patterns:
                # Actualizar patrón existente
                pattern = self.patterns[pattern_id]
                pattern.frequency += 1
                pattern.avg_duration = (pattern.avg_duration + total_duration) / 2
                pattern.last_seen = datetime.now()
            else:
                # Crear nuevo patrón
                pattern = ExecutionPattern(
                    pattern_id=pattern_id,
                    pattern_type="duration",
                    frequency=1,
                    success_rate=execution_data.get("success_rate", 0.0),
                    avg_duration=total_duration,
                    lottery_types=[lottery_type],
                    characteristics={"duration_category": duration_category},
                    last_seen=datetime.now()
                )
                self.patterns[pattern_id] = pattern
            
            return pattern
            
        except Exception as e:
            logger.error(f"Error analizando patrón de duración: {e}")
            return None
    
    def _analyze_success_pattern(self, execution_data: Dict) -> Optional[ExecutionPattern]:
        """Analiza patrones de éxito."""
        try:
            success_rate = execution_data.get("success_rate", 0.0)
            lottery_type = execution_data.get("lottery_type", "unknown")
            
            # Clasificar éxito
            if success_rate >= 0.9:
                success_category = "excellent"
            elif success_rate >= 0.7:
                success_category = "good"
            elif success_rate >= 0.5:
                success_category = "fair"
            else:
                success_category = "poor"
            
            pattern_id = f"success_{success_category}_{lottery_type}"
            
            if pattern_id in self.patterns:
                # Actualizar patrón existente
                pattern = self.patterns[pattern_id]
                pattern.frequency += 1
                pattern.success_rate = (pattern.success_rate + success_rate) / 2
                pattern.last_seen = datetime.now()
            else:
                # Crear nuevo patrón
                pattern = ExecutionPattern(
                    pattern_id=pattern_id,
                    pattern_type="success",
                    frequency=1,
                    success_rate=success_rate,
                    avg_duration=execution_data.get("total_duration_seconds", 0),
                    lottery_types=[lottery_type],
                    characteristics={"success_category": success_category},
                    last_seen=datetime.now()
                )
                self.patterns[pattern_id] = pattern
            
            return pattern
            
        except Exception as e:
            logger.error(f"Error analizando patrón de éxito: {e}")
            return None
    
    def _analyze_lottery_pattern(self, execution_data: Dict) -> Optional[ExecutionPattern]:
        """Analiza patrones específicos de lotería."""
        try:
            lottery_type = execution_data.get("lottery_type", "unknown")
            steps_data = execution_data.get("steps", {})
            
            # Analizar pasos más problemáticos para esta lotería
            problematic_steps = []
            for step_num, step_data in steps_data.items():
                if step_data.get("success", False) == False:
                    problematic_steps.append(step_num)
            
            pattern_id = f"lottery_{lottery_type}_issues"
            
            if pattern_id in self.patterns:
                # Actualizar patrón existente
                pattern = self.patterns[pattern_id]
                pattern.frequency += 1
                pattern.characteristics["problematic_steps"] = problematic_steps
                pattern.last_seen = datetime.now()
            else:
                # Crear nuevo patrón
                pattern = ExecutionPattern(
                    pattern_id=pattern_id,
                    pattern_type="lottery_specific",
                    frequency=1,
                    success_rate=execution_data.get("success_rate", 0.0),
                    avg_duration=execution_data.get("total_duration_seconds", 0),
                    lottery_types=[lottery_type],
                    characteristics={"problematic_steps": problematic_steps},
                    last_seen=datetime.now()
                )
                self.patterns[pattern_id] = pattern
            
            return pattern
            
        except Exception as e:
            logger.error(f"Error analizando patrón de lotería: {e}")
            return None
    
    def _generate_insights(self, execution_data: Dict) -> List[LearningInsight]:
        """Genera insights basados en la ejecución."""
        insights = []
        
        try:
            # Insight sobre eficiencia
            if execution_data.get("total_duration_seconds", 0) < 120:
                insight = LearningInsight(
                    insight_id=f"efficiency_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    category="efficiency",
                    description="Ejecución muy eficiente detectada",
                    confidence=0.8,
                    supporting_evidence=[f"Duration: {execution_data.get('total_duration_seconds')}s"],
                    discovered_at=datetime.now()
                )
                insights.append(insight)
            
            # Insight sobre precisión
            if execution_data.get("success_rate", 0) >= 0.95:
                insight = LearningInsight(
                    insight_id=f"accuracy_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    category="accuracy",
                    description="Alta precisión en resultados",
                    confidence=0.9,
                    supporting_evidence=[f"Success rate: {execution_data.get('success_rate')}"],
                    discovered_at=datetime.now()
                )
                insights.append(insight)
            
            # Insight sobre lotería específica
            lottery_type = execution_data.get("lottery_type", "unknown")
            if lottery_type != "unknown":
                insight = LearningInsight(
                    insight_id=f"lottery_{lottery_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    category="lottery_specific",
                    description=f"Patrones específicos para {lottery_type} identificados",
                    confidence=0.7,
                    supporting_evidence=[f"Lottery type: {lottery_type}"],
                    discovered_at=datetime.now()
                )
                insights.append(insight)
            
            # Agregar a lista de insights
            self.learning_insights.extend(insights)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generando insights: {e}")
            return []
    
    def _analyze_step_performance(self, lottery_type: str = None) -> Dict[str, Any]:
        """Analiza rendimiento por paso."""
        try:
            step_performance = defaultdict(list)
            
            for execution in self.execution_history:
                if lottery_type and execution.get("lottery_type") != lottery_type:
                    continue
                
                steps_data = execution.get("steps", {})
                for step_num, step_data in steps_data.items():
                    step_performance[step_num].append({
                        "duration": step_data.get("duration_seconds", 0),
                        "success": step_data.get("success", False),
                        "confidence": step_data.get("confidence_score", 0.0)
                    })
            
            # Calcular métricas por paso
            performance_metrics = {}
            for step_num, step_data in step_performance.items():
                if step_data:
                    performance_metrics[step_num] = {
                        "avg_duration": sum(s["duration"] for s in step_data) / len(step_data),
                        "success_rate": sum(1 for s in step_data if s["success"]) / len(step_data),
                        "avg_confidence": sum(s["confidence"] for s in step_data) / len(step_data),
                        "total_executions": len(step_data)
                    }
            
            return performance_metrics
            
        except Exception as e:
            logger.error(f"Error analizando rendimiento por paso: {e}")
            return {}
    
    def _generate_step_optimizations(self, step_performance: Dict) -> List[OptimizationSuggestion]:
        """Genera optimizaciones basadas en rendimiento por paso."""
        suggestions = []
        
        try:
            for step_num, metrics in step_performance.items():
                # Sugerencia para pasos lentos
                if metrics["avg_duration"] > 30:
                    suggestion = OptimizationSuggestion(
                        suggestion_id=f"step_{step_num}_speed",
                        category="performance",
                        description=f"Optimizar velocidad del Paso {step_num}",
                        expected_improvement=0.2,
                        implementation_difficulty="medium",
                        priority=3,
                        evidence=[f"Avg duration: {metrics['avg_duration']:.2f}s"]
                    )
                    suggestions.append(suggestion)
                
                # Sugerencia para pasos con baja tasa de éxito
                if metrics["success_rate"] < 0.8:
                    suggestion = OptimizationSuggestion(
                        suggestion_id=f"step_{step_num}_reliability",
                        category="reliability",
                        description=f"Mejorar confiabilidad del Paso {step_num}",
                        expected_improvement=0.15,
                        implementation_difficulty="high",
                        priority=5,
                        evidence=[f"Success rate: {metrics['success_rate']:.2f}"]
                    )
                    suggestions.append(suggestion)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generando optimizaciones de paso: {e}")
            return []
    
    def _analyze_error_patterns(self, lottery_type: str = None) -> Dict[str, Any]:
        """Analiza patrones de error."""
        try:
            error_patterns = defaultdict(int)
            
            for execution in self.execution_history:
                if lottery_type and execution.get("lottery_type") != lottery_type:
                    continue
                
                steps_data = execution.get("steps", {})
                for step_num, step_data in steps_data.items():
                    if not step_data.get("success", True):
                        error_message = step_data.get("error_message", "unknown_error")
                        error_patterns[f"step_{step_num}_{error_message}"] += 1
            
            return dict(error_patterns)
            
        except Exception as e:
            logger.error(f"Error analizando patrones de error: {e}")
            return {}
    
    def _generate_error_optimizations(self, error_patterns: Dict) -> List[OptimizationSuggestion]:
        """Genera optimizaciones basadas en patrones de error."""
        suggestions = []
        
        try:
            for error_pattern, frequency in error_patterns.items():
                if frequency >= 3:  # Error recurrente
                    suggestion = OptimizationSuggestion(
                        suggestion_id=f"error_{error_pattern}",
                        category="error_handling",
                        description=f"Resolver error recurrente: {error_pattern}",
                        expected_improvement=0.3,
                        implementation_difficulty="medium",
                        priority=4,
                        evidence=[f"Frequency: {frequency} occurrences"]
                    )
                    suggestions.append(suggestion)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generando optimizaciones de error: {e}")
            return []
    
    def _analyze_time_efficiency(self, lottery_type: str = None) -> Dict[str, Any]:
        """Analiza eficiencia temporal."""
        try:
            durations = []
            for execution in self.execution_history:
                if lottery_type and execution.get("lottery_type") != lottery_type:
                    continue
                
                duration = execution.get("total_duration_seconds", 0)
                if duration > 0:
                    durations.append(duration)
            
            if not durations:
                return {}
            
            return {
                "avg_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "std_duration": np.std(durations) if len(durations) > 1 else 0,
                "total_executions": len(durations)
            }
            
        except Exception as e:
            logger.error(f"Error analizando eficiencia temporal: {e}")
            return {}
    
    def _generate_time_optimizations(self, time_efficiency: Dict) -> List[OptimizationSuggestion]:
        """Genera optimizaciones basadas en eficiencia temporal."""
        suggestions = []
        
        try:
            if not time_efficiency:
                return suggestions
            
            avg_duration = time_efficiency.get("avg_duration", 0)
            std_duration = time_efficiency.get("std_duration", 0)
            
            # Sugerencia para alta variabilidad
            if std_duration > avg_duration * 0.3:
                suggestion = OptimizationSuggestion(
                    suggestion_id="time_consistency",
                    category="performance",
                    description="Reducir variabilidad en tiempo de ejecución",
                    expected_improvement=0.25,
                    implementation_difficulty="high",
                    priority=3,
                    evidence=[f"Std deviation: {std_duration:.2f}s"]
                )
                suggestions.append(suggestion)
            
            # Sugerencia para duración promedio alta
            if avg_duration > 300:
                suggestion = OptimizationSuggestion(
                    suggestion_id="overall_speed",
                    category="performance",
                    description="Optimizar velocidad general del protocolo",
                    expected_improvement=0.3,
                    implementation_difficulty="medium",
                    priority=4,
                    evidence=[f"Avg duration: {avg_duration:.2f}s"]
                )
                suggestions.append(suggestion)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generando optimizaciones temporales: {e}")
            return []
    
    def _analyze_result_accuracy(self, lottery_type: str = None) -> Dict[str, Any]:
        """Analiza precisión de resultados."""
        try:
            success_rates = []
            confidence_scores = []
            
            for execution in self.execution_history:
                if lottery_type and execution.get("lottery_type") != lottery_type:
                    continue
                
                success_rate = execution.get("success_rate", 0)
                confidence = execution.get("overall_confidence", 0)
                
                if success_rate > 0:
                    success_rates.append(success_rate)
                if confidence > 0:
                    confidence_scores.append(confidence)
            
            if not success_rates:
                return {}
            
            return {
                "avg_success_rate": sum(success_rates) / len(success_rates),
                "avg_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
                "min_success_rate": min(success_rates),
                "max_success_rate": max(success_rates),
                "total_executions": len(success_rates)
            }
            
        except Exception as e:
            logger.error(f"Error analizando precisión: {e}")
            return {}
    
    def _generate_accuracy_optimizations(self, accuracy_analysis: Dict) -> List[OptimizationSuggestion]:
        """Genera optimizaciones basadas en precisión."""
        suggestions = []
        
        try:
            if not accuracy_analysis:
                return suggestions
            
            avg_success_rate = accuracy_analysis.get("avg_success_rate", 0)
            avg_confidence = accuracy_analysis.get("avg_confidence", 0)
            
            # Sugerencia para baja tasa de éxito
            if avg_success_rate < 0.8:
                suggestion = OptimizationSuggestion(
                    suggestion_id="success_rate_improvement",
                    category="accuracy",
                    description="Mejorar tasa de éxito general",
                    expected_improvement=0.2,
                    implementation_difficulty="high",
                    priority=5,
                    evidence=[f"Avg success rate: {avg_success_rate:.2f}"]
                )
                suggestions.append(suggestion)
            
            # Sugerencia para baja confianza
            if avg_confidence < 0.7:
                suggestion = OptimizationSuggestion(
                    suggestion_id="confidence_improvement",
                    category="accuracy",
                    description="Mejorar confianza en resultados",
                    expected_improvement=0.15,
                    implementation_difficulty="medium",
                    priority=4,
                    evidence=[f"Avg confidence: {avg_confidence:.2f}"]
                )
                suggestions.append(suggestion)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generando optimizaciones de precisión: {e}")
            return []
    
    def _get_successful_executions(self, lottery_type: str) -> List[Dict]:
        """Obtiene ejecuciones exitosas para un tipo de lotería."""
        successful = []
        
        for execution in self.execution_history:
            if execution.get("lottery_type") == lottery_type and execution.get("success_rate", 0) >= 0.8:
                successful.append(execution)
        
        return successful
    
    def _calculate_optimal_parameters(self, successful_executions: List[Dict], step_number: int) -> Dict[str, Any]:
        """Calcula parámetros óptimos basados en ejecuciones exitosas."""
        try:
            step_durations = []
            step_confidences = []
            
            for execution in successful_executions:
                steps_data = execution.get("steps", {})
                step_data = steps_data.get(str(step_number), {})
                
                if step_data.get("duration_seconds"):
                    step_durations.append(step_data["duration_seconds"])
                if step_data.get("confidence_score"):
                    step_confidences.append(step_data["confidence_score"])
            
            optimal_params = {}
            
            if step_durations:
                optimal_params["expected_duration"] = sum(step_durations) / len(step_durations)
            
            if step_confidences:
                optimal_params["target_confidence"] = sum(step_confidences) / len(step_confidences)
            
            return optimal_params
            
        except Exception as e:
            logger.error(f"Error calculando parámetros óptimos: {e}")
            return {}
    
    def _get_pattern_adjustments(self, lottery_type: str, step_number: int) -> Dict[str, Any]:
        """Obtiene ajustes basados en patrones identificados."""
        adjustments = {}
        
        # Buscar patrones relevantes
        for pattern in self.patterns.values():
            if lottery_type in pattern.lottery_types and pattern.pattern_type == "lottery_specific":
                problematic_steps = pattern.characteristics.get("problematic_steps", [])
                if str(step_number) in problematic_steps:
                    adjustments["requires_extra_validation"] = True
                    adjustments["expected_difficulty"] = "high"
        
        return adjustments
    
    def _find_similar_executions(self, lottery_type: str, current_step: int, step_data: Dict) -> List[Dict]:
        """Encuentra ejecuciones similares."""
        similar = []
        
        for execution in self.execution_history:
            if execution.get("lottery_type") == lottery_type:
                steps_data = execution.get("steps", {})
                step_execution = steps_data.get(str(current_step), {})
                
                # Comparar características similares
                if self._are_executions_similar(step_data, step_execution):
                    similar.append(execution)
        
        return similar
    
    def _are_executions_similar(self, data1: Dict, data2: Dict) -> bool:
        """Determina si dos ejecuciones son similares."""
        # Implementar lógica de similitud
        # Por ahora, consideramos similares si tienen características básicas parecidas
        return True  # Simplificado para el ejemplo
    
    def _identify_risk_factors(self, similar_executions: List[Dict], step_data: Dict) -> List[str]:
        """Identifica factores de riesgo."""
        risk_factors = []
        
        # Analizar patrones de fallo en ejecuciones similares
        failure_count = sum(1 for ex in similar_executions if ex.get("success_rate", 0) < 0.8)
        
        if failure_count > len(similar_executions) * 0.3:
            risk_factors.append("high_failure_rate_in_similar_executions")
        
        return risk_factors
    
    def _generate_success_recommendations(self, risk_factors: List[str]) -> List[str]:
        """Genera recomendaciones para mejorar éxito."""
        recommendations = []
        
        for risk_factor in risk_factors:
            if risk_factor == "high_failure_rate_in_similar_executions":
                recommendations.append("Considerar validación adicional en este paso")
                recommendations.append("Revisar parámetros de configuración")
        
        return recommendations
    
    def _load_learning_data(self):
        """Carga datos de aprendizaje existentes."""
        try:
            learning_file = self.learning_data_dir / "learning_data.json"
            
            if learning_file.exists():
                with open(learning_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.execution_history = data.get("execution_history", [])
                self.learning_metrics = data.get("learning_metrics", self.learning_metrics)
                
                # Cargar patrones
                patterns_data = data.get("patterns", {})
                for pattern_id, pattern_data in patterns_data.items():
                    pattern_data["last_seen"] = datetime.fromisoformat(pattern_data["last_seen"])
                    self.patterns[pattern_id] = ExecutionPattern(**pattern_data)
                
                logger.info("Datos de aprendizaje cargados exitosamente")
            
        except Exception as e:
            logger.error(f"Error cargando datos de aprendizaje: {e}")
    
    def _save_learning_data(self):
        """Guarda datos de aprendizaje."""
        try:
            learning_data = {
                "execution_history": self.execution_history,
                "patterns": {pid: asdict(pattern) for pid, pattern in self.patterns.items()},
                "learning_metrics": self.learning_metrics,
                "saved_at": datetime.now().isoformat()
            }
            
            learning_file = self.learning_data_dir / "learning_data.json"
            
            with open(learning_file, 'w', encoding='utf-8') as f:
                json.dump(learning_data, f, indent=2, default=str)
            
            logger.info("Datos de aprendizaje guardados exitosamente")
            
        except Exception as e:
            logger.error(f"Error guardando datos de aprendizaje: {e}")
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Obtiene resumen del sistema de aprendizaje."""
        return {
            "learning_metrics": self.learning_metrics,
            "total_patterns": len(self.patterns),
            "total_insights": len(self.learning_insights),
            "total_suggestions": len(self.optimization_suggestions),
            "system_status": "active" if self.learning_metrics["total_executions_analyzed"] > 0 else "learning"
        }


# =================== INSTANCIA GLOBAL ===================

# Instancia global del sistema de aprendizaje
protocol_learning_system = ProtocolLearningSystem()

def get_learning_system() -> ProtocolLearningSystem:
    """Obtiene la instancia global del sistema de aprendizaje."""
    return protocol_learning_system





