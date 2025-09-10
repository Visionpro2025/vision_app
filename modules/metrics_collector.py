# modules/metrics_collector.py
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import streamlit as st
import pandas as pd
import json

@dataclass
class PerformanceMetric:
    """Métrica de rendimiento del sistema."""
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    category: str

@dataclass
class KPISummary:
    """Resumen de KPIs del sistema."""
    total_executions: int
    success_rate: float
    avg_execution_time: float
    total_news_processed: int
    total_series_generated: int
    system_uptime: float
    last_execution: Optional[datetime]

class MetricsCollector:
    """Módulo para recolección y análisis de KPIs del sistema."""
    
    def __init__(self):
        self.performance_metrics = []
        self.execution_history = []
        self.start_time = datetime.now()
        
    def record_execution(self, execution_type: str, duration: float, success: bool, 
                        details: Dict[str, Any] = None):
        """Registra una ejecución del sistema."""
        execution_record = {
            "timestamp": datetime.now(),
            "type": execution_type,
            "duration": duration,
            "success": success,
            "details": details or {}
        }
        
        self.execution_history.append(execution_record)
        
        # Mantener solo los últimos 1000 registros
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-1000:]
    
    def record_performance_metric(self, metric_name: str, value: float, unit: str, category: str):
        """Registra una métrica de rendimiento."""
        metric = PerformanceMetric(
            timestamp=datetime.now(),
            metric_name=metric_name,
            value=value,
            unit=unit,
            category=category
        )
        
        self.performance_metrics.append(metric)
        
        # Mantener solo los últimos 500 métricas
        if len(self.performance_metrics) > 500:
            self.performance_metrics = self.performance_metrics[-500:]
    
    def get_kpi_summary(self) -> KPISummary:
        """Obtiene un resumen de los KPIs del sistema."""
        try:
            total_executions = len(self.execution_history)
            
            if total_executions == 0:
                return KPISummary(
                    total_executions=0,
                    success_rate=0.0,
                    avg_execution_time=0.0,
                    total_news_processed=0,
                    total_series_generated=0,
                    system_uptime=0.0,
                    last_execution=None
                )
            
            # Calcular tasa de éxito
            successful_executions = len([e for e in self.execution_history if e["success"]])
            success_rate = successful_executions / total_executions
            
            # Calcular tiempo promedio de ejecución
            execution_times = [e["duration"] for e in self.execution_history]
            avg_execution_time = sum(execution_times) / len(execution_times)
            
            # Calcular noticias procesadas
            total_news = 0
            for execution in self.execution_history:
                if "news_count" in execution["details"]:
                    total_news += execution["details"]["news_count"]
            
            # Calcular series generadas
            total_series = 0
            for execution in self.execution_history:
                if "series_count" in execution["details"]:
                    total_series += execution["details"]["series_count"]
            
            # Calcular tiempo de actividad
            system_uptime = (datetime.now() - self.start_time).total_seconds() / 3600  # Horas
            
            # Última ejecución
            last_execution = max([e["timestamp"] for e in self.execution_history]) if self.execution_history else None
            
            return KPISummary(
                total_executions=total_executions,
                success_rate=success_rate,
                avg_execution_time=avg_execution_time,
                total_news_processed=total_news,
                total_series_generated=total_series,
                system_uptime=system_uptime,
                last_execution=last_execution
            )
            
        except Exception as e:
            st.error(f"Error obteniendo KPIs: {e}")
            return KPISummary(0, 0.0, 0.0, 0, 0, 0.0, None)
    
    def get_performance_trends(self, hours: int = 24) -> Dict[str, List[float]]:
        """Obtiene tendencias de rendimiento en las últimas horas."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Filtrar métricas recientes
            recent_metrics = [
                m for m in self.performance_metrics
                if m.timestamp > cutoff_time
            ]
            
            trends = {}
            
            # Agrupar por categoría
            for metric in recent_metrics:
                if metric.category not in trends:
                    trends[metric.category] = []
                trends[metric.category].append(metric.value)
            
            # Calcular promedios por categoría
            for category in trends:
                if trends[category]:
                    trends[category] = sum(trends[category]) / len(trends[category])
                else:
                    trends[category] = 0.0
            
            return trends
            
        except Exception as e:
            st.error(f"Error obteniendo tendencias: {e}")
            return {}
    
    def render_metrics_dashboard(self):
        """Renderiza el dashboard de métricas en Streamlit."""
        st.subheader("📊 **DASHBOARD DE MÉTRICAS Y KPIs**")
        
        # Obtener resumen de KPIs
        kpi_summary = self.get_kpi_summary()
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Ejecuciones",
                kpi_summary.total_executions,
                "Del sistema"
            )
        
        with col2:
            st.metric(
                "Tasa de Éxito",
                f"{kpi_summary.success_rate:.1%}",
                "Operaciones exitosas"
            )
        
        with col3:
            st.metric(
                "Tiempo Promedio",
                f"{kpi_summary.avg_execution_time:.1f}s",
                "Por ejecución"
            )
        
        with col4:
            st.metric(
                "Tiempo Activo",
                f"{kpi_summary.system_uptime:.1f}h",
                "Sistema funcionando"
            )
        
        # Métricas de procesamiento
        st.subheader("⚙️ **Métricas de Procesamiento**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Noticias Procesadas",
                kpi_summary.total_news_processed,
                "Total acumulado"
            )
        
        with col2:
            st.metric(
                "Series Generadas",
                kpi_summary.total_series_generated,
                "Total acumulado"
            )
        
        # Tendencias de rendimiento
        st.subheader("📈 **Tendencias de Rendimiento**)
        
        trends = self.get_performance_trends(24)  # Últimas 24 horas
        
        if trends:
            trends_df = pd.DataFrame([
                {"Categoría": category, "Valor Promedio": value}
                for category, value in trends.items()
            ])
            
            st.bar_chart(trends_df.set_index("Categoría"))
        else:
            st.info("No hay métricas de rendimiento disponibles")
        
        # Historial de ejecuciones
        st.subheader("📋 **Historial de Ejecuciones**")
        
        if self.execution_history:
            # Crear DataFrame del historial
            history_data = []
            for execution in self.execution_history[-20:]:  # Últimas 20 ejecuciones
                history_data.append({
                    "Timestamp": execution["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                    "Tipo": execution["type"],
                    "Duración": f"{execution['duration']:.1f}s",
                    "Estado": "✅ Exitoso" if execution["success"] else "❌ Fallido",
                    "Detalles": str(execution["details"])
                })
            
            history_df = pd.DataFrame(history_data)
            st.dataframe(history_df, use_container_width=True, hide_index=True)
        else:
            st.info("No hay historial de ejecuciones disponible")
        
        # Controles
        st.subheader("🎛️ **Controles**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Actualizar Métricas", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("📊 Exportar KPIs", use_container_width=True):
                self._export_kpis()
    
    def _export_kpis(self):
        """Exporta los KPIs del sistema."""
        try:
            kpi_summary = self.get_kpi_summary()
            
            # Preparar datos para exportación
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "kpi_summary": {
                    "total_executions": kpi_summary.total_executions,
                    "success_rate": kpi_summary.success_rate,
                    "avg_execution_time": kpi_summary.avg_execution_time,
                    "total_news_processed": kpi_summary.total_news_processed,
                    "total_series_generated": kpi_summary.total_series_generated,
                    "system_uptime": kpi_summary.system_uptime,
                    "last_execution": kpi_summary.last_execution.isoformat() if kpi_summary.last_execution else None
                },
                "performance_trends": self.get_performance_trends(24),
                "execution_history": [
                    {
                        "timestamp": e["timestamp"].isoformat(),
                        "type": e["type"],
                        "duration": e["duration"],
                        "success": e["success"],
                        "details": e["details"]
                    }
                    for e in self.execution_history[-100:]  # Últimas 100 ejecuciones
                ]
            }
            
            # Crear archivo JSON para descarga
            json_str = json.dumps(export_data, indent=2, default=str)
            st.download_button(
                label="⬇️ Descargar KPIs (JSON)",
                data=json_str,
                file_name=f"kpis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.error(f"Error exportando KPIs: {str(e)}")

# Instancia global
metrics_collector = MetricsCollector()









