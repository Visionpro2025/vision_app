# modules/protocol_metrics.py
"""
SISTEMA DE MÉTRICAS Y RENDIMIENTO PARA PROTOCOLO UNIVERSAL OFICIAL
==================================================================

Sistema completo de métricas para monitorear el rendimiento del protocolo universal oficial.
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class StepMetrics:
    """Métricas de un paso específico del protocolo."""
    step_number: int
    step_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    success: bool = False
    error_message: Optional[str] = None
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    data_processed: Optional[int] = None
    confidence_score: Optional[float] = None

@dataclass
class ProtocolMetrics:
    """Métricas completas del protocolo."""
    protocol_version: str
    execution_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration_seconds: Optional[float] = None
    total_steps: int = 9
    successful_steps: int = 0
    failed_steps: int = 0
    success_rate: Optional[float] = None
    average_step_duration: Optional[float] = None
    peak_memory_usage_mb: Optional[float] = None
    average_cpu_usage: Optional[float] = None
    total_data_processed: Optional[int] = None
    overall_confidence: Optional[float] = None
    lottery_type: Optional[str] = None
    user_satisfaction: Optional[float] = None

class ProtocolMetricsCollector:
    """
    Recolector de métricas para el protocolo universal oficial.
    """
    
    def __init__(self):
        """Inicializa el recolector de métricas."""
        self.current_execution_id = None
        self.step_metrics: List[StepMetrics] = []
        self.protocol_metrics: Optional[ProtocolMetrics] = None
        self.metrics_history: List[ProtocolMetrics] = []
        
        # Crear directorio de métricas
        self.metrics_dir = Path("metrics")
        self.metrics_dir.mkdir(exist_ok=True)
        
        logger.info("Sistema de Métricas del Protocolo inicializado")
    
    def start_protocol_execution(self, lottery_type: str = "powerball") -> str:
        """
        Inicia el tracking de una ejecución del protocolo.
        
        Args:
            lottery_type: Tipo de lotería siendo analizada
            
        Returns:
            ID único de la ejecución
        """
        try:
            self.current_execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self.protocol_metrics = ProtocolMetrics(
                protocol_version="1.0",
                execution_id=self.current_execution_id,
                start_time=datetime.now(),
                lottery_type=lottery_type
            )
            
            self.step_metrics = []
            
            logger.info(f"Iniciado tracking de ejecución: {self.current_execution_id}")
            return self.current_execution_id
            
        except Exception as e:
            logger.error(f"Error iniciando tracking: {e}")
            return None
    
    def start_step_tracking(self, step_number: int, step_name: str) -> bool:
        """
        Inicia el tracking de un paso específico.
        
        Args:
            step_number: Número del paso
            step_name: Nombre del paso
            
        Returns:
            True si se inició correctamente
        """
        try:
            step_metric = StepMetrics(
                step_number=step_number,
                step_name=step_name,
                start_time=datetime.now()
            )
            
            self.step_metrics.append(step_metric)
            
            logger.info(f"Iniciado tracking del paso {step_number}: {step_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error iniciando tracking del paso {step_number}: {e}")
            return False
    
    def end_step_tracking(self, step_number: int, success: bool, 
                         error_message: str = None, confidence_score: float = None,
                         data_processed: int = None) -> bool:
        """
        Finaliza el tracking de un paso específico.
        
        Args:
            step_number: Número del paso
            success: Si el paso fue exitoso
            error_message: Mensaje de error si falló
            confidence_score: Puntuación de confianza (0-1)
            data_processed: Cantidad de datos procesados
            
        Returns:
            True si se finalizó correctamente
        """
        try:
            # Buscar el paso en la lista
            step_metric = None
            for step in self.step_metrics:
                if step.step_number == step_number and step.end_time is None:
                    step_metric = step
                    break
            
            if step_metric is None:
                logger.warning(f"No se encontró paso {step_number} para finalizar")
                return False
            
            # Finalizar métricas del paso
            step_metric.end_time = datetime.now()
            step_metric.duration_seconds = (step_metric.end_time - step_metric.start_time).total_seconds()
            step_metric.success = success
            step_metric.error_message = error_message
            step_metric.confidence_score = confidence_score
            step_metric.data_processed = data_processed
            
            # Obtener métricas del sistema
            step_metric.memory_usage_mb = self._get_memory_usage()
            step_metric.cpu_usage_percent = self._get_cpu_usage()
            
            logger.info(f"Finalizado tracking del paso {step_number}: {step_metric.duration_seconds:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Error finalizando tracking del paso {step_number}: {e}")
            return False
    
    def end_protocol_execution(self, user_satisfaction: float = None) -> bool:
        """
        Finaliza el tracking de la ejecución completa del protocolo.
        
        Args:
            user_satisfaction: Puntuación de satisfacción del usuario (0-1)
            
        Returns:
            True si se finalizó correctamente
        """
        try:
            if self.protocol_metrics is None:
                logger.warning("No hay ejecución activa para finalizar")
                return False
            
            # Finalizar métricas del protocolo
            self.protocol_metrics.end_time = datetime.now()
            self.protocol_metrics.total_duration_seconds = (
                self.protocol_metrics.end_time - self.protocol_metrics.start_time
            ).total_seconds()
            
            # Calcular métricas agregadas
            self._calculate_aggregate_metrics()
            
            # Agregar satisfacción del usuario
            self.protocol_metrics.user_satisfaction = user_satisfaction
            
            # Guardar en historial
            self.metrics_history.append(self.protocol_metrics)
            
            # Guardar métricas en archivo
            self._save_metrics_to_file()
            
            logger.info(f"Finalizada ejecución {self.current_execution_id}: {self.protocol_metrics.total_duration_seconds:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Error finalizando ejecución: {e}")
            return False
    
    def _calculate_aggregate_metrics(self):
        """Calcula métricas agregadas del protocolo."""
        try:
            if not self.step_metrics:
                return
            
            # Contar pasos exitosos y fallidos
            successful_steps = sum(1 for step in self.step_metrics if step.success)
            failed_steps = len(self.step_metrics) - successful_steps
            
            self.protocol_metrics.successful_steps = successful_steps
            self.protocol_metrics.failed_steps = failed_steps
            self.protocol_metrics.success_rate = successful_steps / len(self.step_metrics)
            
            # Calcular duración promedio por paso
            durations = [step.duration_seconds for step in self.step_metrics if step.duration_seconds]
            if durations:
                self.protocol_metrics.average_step_duration = sum(durations) / len(durations)
            
            # Calcular uso máximo de memoria
            memory_usages = [step.memory_usage_mb for step in self.step_metrics if step.memory_usage_mb]
            if memory_usages:
                self.protocol_metrics.peak_memory_usage_mb = max(memory_usages)
            
            # Calcular uso promedio de CPU
            cpu_usages = [step.cpu_usage_percent for step in self.step_metrics if step.cpu_usage_percent]
            if cpu_usages:
                self.protocol_metrics.average_cpu_usage = sum(cpu_usages) / len(cpu_usages)
            
            # Calcular datos totales procesados
            data_processed = [step.data_processed for step in self.step_metrics if step.data_processed]
            if data_processed:
                self.protocol_metrics.total_data_processed = sum(data_processed)
            
            # Calcular confianza general
            confidence_scores = [step.confidence_score for step in self.step_metrics if step.confidence_score]
            if confidence_scores:
                self.protocol_metrics.overall_confidence = sum(confidence_scores) / len(confidence_scores)
                
        except Exception as e:
            logger.error(f"Error calculando métricas agregadas: {e}")
    
    def _get_memory_usage(self) -> float:
        """Obtiene el uso actual de memoria en MB."""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.rss / 1024 / 1024  # Convertir a MB
        except Exception:
            return 0.0
    
    def _get_cpu_usage(self) -> float:
        """Obtiene el uso actual de CPU en porcentaje."""
        try:
            import psutil
            return psutil.cpu_percent()
        except Exception:
            return 0.0
    
    def _save_metrics_to_file(self):
        """Guarda las métricas en archivo JSON."""
        try:
            if self.protocol_metrics is None:
                return
            
            # Preparar datos para guardar
            metrics_data = {
                "protocol_metrics": asdict(self.protocol_metrics),
                "step_metrics": [asdict(step) for step in self.step_metrics],
                "saved_at": datetime.now().isoformat()
            }
            
            # Convertir datetime a string para JSON
            def datetime_converter(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
            
            # Guardar archivo
            filename = f"metrics_{self.current_execution_id}.json"
            filepath = self.metrics_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(metrics_data, f, indent=2, default=datetime_converter)
            
            logger.info(f"Métricas guardadas en: {filepath}")
            
        except Exception as e:
            logger.error(f"Error guardando métricas: {e}")
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Obtiene las métricas actuales de la ejecución."""
        try:
            if self.protocol_metrics is None:
                return {"status": "no_active_execution"}
            
            current_metrics = {
                "execution_id": self.current_execution_id,
                "protocol_version": self.protocol_metrics.protocol_version,
                "lottery_type": self.protocol_metrics.lottery_type,
                "start_time": self.protocol_metrics.start_time.isoformat(),
                "current_duration": (datetime.now() - self.protocol_metrics.start_time).total_seconds(),
                "steps_completed": len([s for s in self.step_metrics if s.end_time is not None]),
                "total_steps": self.protocol_metrics.total_steps,
                "successful_steps": self.protocol_metrics.successful_steps,
                "failed_steps": self.protocol_metrics.failed_steps,
                "current_step": self.step_metrics[-1].step_number if self.step_metrics else 0,
                "current_step_name": self.step_metrics[-1].step_name if self.step_metrics else "None"
            }
            
            return current_metrics
            
        except Exception as e:
            logger.error(f"Error obteniendo métricas actuales: {e}")
            return {"error": str(e)}
    
    def get_historical_metrics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtiene métricas históricas de ejecuciones anteriores."""
        try:
            historical_data = []
            
            for metrics in self.metrics_history[-limit:]:
                historical_data.append({
                    "execution_id": metrics.execution_id,
                    "lottery_type": metrics.lottery_type,
                    "start_time": metrics.start_time.isoformat(),
                    "total_duration": metrics.total_duration_seconds,
                    "success_rate": metrics.success_rate,
                    "successful_steps": metrics.successful_steps,
                    "failed_steps": metrics.failed_steps,
                    "overall_confidence": metrics.overall_confidence,
                    "user_satisfaction": metrics.user_satisfaction
                })
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Error obteniendo métricas históricas: {e}")
            return []
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Genera un reporte de rendimiento completo."""
        try:
            if not self.metrics_history:
                return {"error": "No hay datos históricos disponibles"}
            
            # Calcular estadísticas generales
            total_executions = len(self.metrics_history)
            avg_duration = sum(m.total_duration_seconds for m in self.metrics_history if m.total_duration_seconds) / total_executions
            avg_success_rate = sum(m.success_rate for m in self.metrics_history if m.success_rate) / total_executions
            avg_confidence = sum(m.overall_confidence for m in self.metrics_history if m.overall_confidence) / total_executions
            
            # Encontrar mejor y peor ejecución
            best_execution = max(self.metrics_history, key=lambda m: m.success_rate or 0)
            worst_execution = min(self.metrics_history, key=lambda m: m.success_rate or 0)
            
            performance_report = {
                "summary": {
                    "total_executions": total_executions,
                    "average_duration_seconds": avg_duration,
                    "average_success_rate": avg_success_rate,
                    "average_confidence": avg_confidence
                },
                "best_execution": {
                    "execution_id": best_execution.execution_id,
                    "success_rate": best_execution.success_rate,
                    "duration": best_execution.total_duration_seconds,
                    "confidence": best_execution.overall_confidence
                },
                "worst_execution": {
                    "execution_id": worst_execution.execution_id,
                    "success_rate": worst_execution.success_rate,
                    "duration": worst_execution.total_duration_seconds,
                    "confidence": worst_execution.overall_confidence
                },
                "recommendations": self._generate_recommendations(),
                "generated_at": datetime.now().isoformat()
            }
            
            return performance_report
            
        except Exception as e:
            logger.error(f"Error generando reporte de rendimiento: {e}")
            return {"error": str(e)}
    
    def _generate_recommendations(self) -> List[str]:
        """Genera recomendaciones basadas en métricas históricas."""
        recommendations = []
        
        try:
            if not self.metrics_history:
                return ["No hay datos suficientes para generar recomendaciones"]
            
            # Analizar patrones
            avg_duration = sum(m.total_duration_seconds for m in self.metrics_history if m.total_duration_seconds) / len(self.metrics_history)
            avg_success_rate = sum(m.success_rate for m in self.metrics_history if m.success_rate) / len(self.metrics_history)
            
            if avg_duration > 300:  # Más de 5 minutos
                recommendations.append("Considerar optimizar pasos que toman más tiempo")
            
            if avg_success_rate < 0.8:  # Menos del 80% de éxito
                recommendations.append("Revisar pasos con mayor tasa de fallo")
            
            if not recommendations:
                recommendations.append("El protocolo está funcionando dentro de parámetros normales")
            
            return recommendations
            
        except Exception as e:
            return [f"Error generando recomendaciones: {e}"]


# =================== INSTANCIA GLOBAL ===================

# Instancia global del recolector de métricas
protocol_metrics_collector = ProtocolMetricsCollector()

def get_metrics_collector() -> ProtocolMetricsCollector:
    """Obtiene la instancia global del recolector de métricas."""
    return protocol_metrics_collector






