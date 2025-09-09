# modules/monitoring_dashboard.py
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from collections import deque
import psutil
import json

@dataclass
class SystemMetric:
    """Métrica del sistema en tiempo real."""
    timestamp: datetime
    value: float
    unit: str
    category: str
    status: str  # "healthy", "warning", "critical"

@dataclass
class ProcessStatus:
    """Estado de un proceso del sistema."""
    name: str
    status: str  # "running", "stopped", "error", "warning"
    start_time: datetime
    last_heartbeat: datetime
    execution_time: float
    success_rate: float
    error_count: int
    warning_count: int

@dataclass
class Alert:
    """Alerta del sistema."""
    id: str
    timestamp: datetime
    severity: str  # "info", "warning", "error", "critical"
    category: str
    message: str
    resolved: bool = False
    resolved_time: Optional[datetime] = None

class MonitoringDashboard:
    """Dashboard NOC en tiempo real para monitorización del sistema."""
    
    def __init__(self):
        self.system_metrics = {
            "cpu_usage": deque(maxlen=100),
            "memory_usage": deque(maxlen=100),
            "disk_usage": deque(maxlen=100),
            "network_io": deque(maxlen=100)
        }
        self.process_statuses = {}
        self.alerts = []
        self.performance_history = deque(maxlen=1000)
        self.monitoring_active = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Inicia el monitoreo en tiempo real."""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Detiene el monitoreo."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_loop(self):
        """Loop principal de monitoreo."""
        while self.monitoring_active:
            try:
                self._collect_system_metrics()
                self._check_process_health()
                self._generate_alerts()
                time.sleep(2)  # Actualizar cada 2 segundos
            except Exception as e:
                self._add_alert("error", "monitoring", f"Error en monitoreo: {str(e)}")
    
    def _collect_system_metrics(self):
        """Recolecta métricas del sistema."""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self.system_metrics["cpu_usage"].append(
                SystemMetric(
                    timestamp=datetime.now(),
                    value=cpu_percent,
                    unit="%",
                    category="CPU",
                    status="critical" if cpu_percent > 90 else "warning" if cpu_percent > 70 else "healthy"
                )
            )
            
            # Memoria
            memory = psutil.virtual_memory()
            self.system_metrics["memory_usage"].append(
                SystemMetric(
                    timestamp=datetime.now(),
                    value=memory.percent,
                    unit="%",
                    category="Memory",
                    status="critical" if memory.percent > 90 else "warning" if memory.percent > 80 else "healthy"
                )
            )
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.system_metrics["disk_usage"].append(
                SystemMetric(
                    timestamp=datetime.now(),
                    value=disk_percent,
                    unit="%",
                    category="Disk",
                    status="critical" if disk_percent > 95 else "warning" if disk_percent > 85 else "healthy"
                )
            )
            
            # Red
            net_io = psutil.net_io_counters()
            network_mb = (net_io.bytes_sent + net_io.bytes_recv) / (1024 * 1024)
            self.system_metrics["network_io"].append(
                SystemMetric(
                    timestamp=datetime.now(),
                    value=network_mb,
                    unit="MB",
                    category="Network",
                    status="healthy"  # Red generalmente no es crítica
                )
            )
            
        except Exception as e:
            self._add_alert("error", "metrics", f"Error recolectando métricas: {str(e)}")
    
    def _check_process_health(self):
        """Verifica la salud de los procesos del sistema."""
        current_time = datetime.now()
        
        # Verificar procesos activos
        for process_name, status in self.process_statuses.items():
            # Verificar si el proceso está activo (último heartbeat hace menos de 30 segundos)
            if (current_time - status.last_heartbeat).total_seconds() > 30:
                status.status = "error"
                self._add_alert("warning", "process", f"Proceso {process_name} sin heartbeat")
            elif (current_time - status.last_heartbeat).total_seconds() > 10:
                status.status = "warning"
    
    def _generate_alerts(self):
        """Genera alertas basadas en métricas del sistema."""
        # Alertas de CPU
        if self.system_metrics["cpu_usage"]:
            latest_cpu = self.system_metrics["cpu_usage"][-1]
            if latest_cpu.status == "critical":
                self._add_alert("critical", "cpu", f"CPU crítico: {latest_cpu.value}%")
            elif latest_cpu.status == "warning":
                self._add_alert("warning", "cpu", f"CPU alto: {latest_cpu.value}%")
        
        # Alertas de memoria
        if self.system_metrics["memory_usage"]:
            latest_memory = self.system_metrics["memory_usage"][-1]
            if latest_memory.status == "critical":
                self._add_alert("critical", "memory", f"Memoria crítica: {latest_memory.value}%")
            elif latest_memory.status == "warning":
                self._add_alert("warning", "memory", f"Memoria alta: {latest_memory.value}%")
        
        # Alertas de disco
        if self.system_metrics["disk_usage"]:
            latest_disk = self.system_metrics["disk_usage"][-1]
            if latest_disk.status == "critical":
                self._add_alert("critical", "disk", f"Disco crítico: {latest_disk.value}%")
            elif latest_disk.status == "warning":
                self._add_alert("warning", "disk", f"Disco alto: {latest_disk.value}%")
    
    def _add_alert(self, severity: str, category: str, message: str):
        """Añade una nueva alerta."""
        alert = Alert(
            id=str(len(self.alerts) + 1),
            timestamp=datetime.now(),
            severity=severity,
            category=category,
            message=message
        )
        self.alerts.append(alert)
        
        # Mantener solo las últimas 100 alertas
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    def update_process_status(self, process_name: str, status: str, execution_time: float = 0.0):
        """Actualiza el estado de un proceso."""
        current_time = datetime.now()
        
        if process_name not in self.process_statuses:
            self.process_statuses[process_name] = ProcessStatus(
                name=process_name,
                status=status,
                start_time=current_time,
                last_heartbeat=current_time,
                execution_time=execution_time,
                success_rate=1.0,
                error_count=0,
                warning_count=0
            )
        else:
            process = self.process_statuses[process_name]
            process.status = status
            process.last_heartbeat = current_time
            process.execution_time = execution_time
            
            # Actualizar estadísticas
            if status == "error":
                process.error_count += 1
            elif status == "warning":
                process.warning_count += 1
            
            # Calcular tasa de éxito
            total_runs = process.error_count + process.warning_count + 1
            process.success_rate = 1.0 - (process.error_count / total_runs)
    
    def get_system_health(self) -> Dict[str, Any]:
        """Obtiene el estado general de salud del sistema."""
        # Calcular salud general basada en métricas
        health_scores = {}
        
        for metric_name, metrics in self.system_metrics.items():
            if metrics:
                latest = metrics[-1]
                if latest.status == "healthy":
                    health_scores[metric_name] = 1.0
                elif latest.status == "warning":
                    health_scores[metric_name] = 0.5
                else:
                    health_scores[metric_name] = 0.0
        
        # Salud general del sistema
        overall_health = sum(health_scores.values()) / len(health_scores) if health_scores else 0.0
        
        # Determinar estado general
        if overall_health >= 0.8:
            system_status = "healthy"
        elif overall_health >= 0.5:
            system_status = "warning"
        else:
            system_status = "critical"
        
        return {
            "system_health": system_status,
            "overall_score": overall_health,
            "component_scores": health_scores,
            "active_processes": len([p for p in self.process_statuses.values() if p.status == "running"]),
            "total_processes": len(self.process_statuses),
            "active_alerts": len([a for a in self.alerts if not a.resolved]),
            "last_update": datetime.now().isoformat()
        }
    
    def create_system_metrics_chart(self) -> go.Figure:
        """Crea gráfico de métricas del sistema en tiempo real."""
        fig = go.Figure()
        
        # Colores para diferentes estados
        colors = {"healthy": "#00FF00", "warning": "#FFFF00", "critical": "#FF0000"}
        
        for metric_name, metrics in self.system_metrics.items():
            if metrics:
                timestamps = [m.timestamp for m in metrics]
                values = [m.value for m in metrics]
                statuses = [m.status for m in metrics]
                
                # Color por estado
                line_colors = [colors.get(status, "#808080") for status in statuses]
                
                fig.add_trace(go.Scatter(
                    x=timestamps,
                    y=values,
                    mode="lines+markers",
                    name=metric_name.replace("_", " ").title(),
                    line=dict(color=line_colors[-1]),
                    marker=dict(color=line_colors, size=6),
                    hovertemplate="<b>%{x}</b><br>%{y:.2f}<extra></extra>"
                ))
        
        fig.update_layout(
            title="Métricas del Sistema en Tiempo Real",
            xaxis_title="Tiempo",
            yaxis_title="Valor",
            height=400,
            hovermode="x unified"
        )
        
        return fig
    
    def create_process_status_chart(self) -> go.Figure:
        """Crea gráfico del estado de los procesos."""
        if not self.process_statuses:
            return go.Figure()
        
        process_names = list(self.process_statuses.keys())
        success_rates = [p.success_rate * 100 for p in self.process_statuses.values()]
        error_counts = [p.error_count for p in self.process_statuses.values()]
        warning_counts = [p.warning_count for p in self.process_statuses.values()]
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Tasa de Éxito por Proceso", "Conteo de Errores y Advertencias"),
            specs=[[{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Tasa de éxito
        fig.add_trace(
            go.Bar(
                x=process_names,
                y=success_rates,
                name="Tasa de Éxito (%)",
                marker_color="green",
                text=[f"{rate:.1f}%" for rate in success_rates],
                textposition="auto"
            ),
            row=1, col=1
        )
        
        # Errores y advertencias
        fig.add_trace(
            go.Bar(
                x=process_names,
                y=error_counts,
                name="Errores",
                marker_color="red",
                text=error_counts,
                textposition="auto"
            ),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Bar(
                x=process_names,
                y=warning_counts,
                name="Advertencias",
                marker_color="orange",
                text=warning_counts,
                textposition="auto"
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title="Estado de Procesos del Sistema",
            height=400,
            showlegend=True
        )
        
        return fig
    
    def render_monitoring_dashboard(self):
        """Renderiza el dashboard de monitorización en Streamlit."""
        st.subheader("📊 **DASHBOARD NOC - MONITORIZACIÓN EN TIEMPO REAL**")
        
        # Iniciar monitoreo si no está activo
        if not self.monitoring_active:
            self.start_monitoring()
        
        # Estado general del sistema
        system_health = self.get_system_health()
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            health_color = {
                "healthy": "🟢",
                "warning": "🟡", 
                "critical": "🔴"
            }.get(system_health["system_health"], "⚪")
            
            st.metric(
                "Salud del Sistema",
                f"{health_color} {system_health['system_health'].upper()}",
                f"{system_health['overall_score']:.1%}"
            )
        
        with col2:
            st.metric(
                "Procesos Activos",
                f"{system_health['active_processes']}/{system_health['total_processes']}",
                "Ejecutándose"
            )
        
        with col3:
            st.metric(
                "Alertas Activas",
                system_health['active_alerts'],
                "Sin resolver"
            )
        
        with col4:
            st.metric(
                "Última Actualización",
                system_health['last_update'][11:19],  # Solo hora
                "En tiempo real"
            )
        
        # Gráficos de métricas
        st.subheader("📈 **Métricas del Sistema**")
        
        tab1, tab2 = st.tabs(["📊 Métricas en Tiempo Real", "⚙️ Estado de Procesos"])
        
        with tab1:
            metrics_chart = self.create_system_metrics_chart()
            st.plotly_chart(metrics_chart, use_container_width=True)
        
        with tab2:
            if self.process_statuses:
                process_chart = self.create_process_status_chart()
                st.plotly_chart(process_chart, use_container_width=True)
            else:
                st.info("No hay procesos registrados aún")
        
        # Tabla de estado de procesos
        st.subheader("🔍 **Estado Detallado de Procesos**")
        if self.process_statuses:
            process_data = []
            for process in self.process_statuses.values():
                process_data.append({
                    "Proceso": process.name,
                    "Estado": process.status,
                    "Tiempo de Ejecución": f"{process.execution_time:.1f}s",
                    "Tasa de Éxito": f"{process.success_rate:.1%}",
                    "Errores": process.error_count,
                    "Advertencias": process.warning_count,
                    "Último Heartbeat": process.last_heartbeat.strftime("%H:%M:%S")
                })
            
            import pandas as pd
            process_df = pd.DataFrame(process_data)
            st.dataframe(process_df, use_container_width=True, hide_index=True)
        
        # Alertas del sistema
        st.subheader("🚨 **Alertas del Sistema**")
        
        # Filtros de alertas
        col1, col2 = st.columns(2)
        with col1:
            severity_filter = st.selectbox(
                "Filtrar por Severidad",
                ["Todas", "info", "warning", "error", "critical"]
            )
        
        with col2:
            category_filter = st.selectbox(
                "Filtrar por Categoría",
                ["Todas"] + list(set(a.category for a in self.alerts))
            )
        
        # Filtrar alertas
        filtered_alerts = self.alerts
        if severity_filter != "Todas":
            filtered_alerts = [a for a in filtered_alerts if a.severity == severity_filter]
        if category_filter != "Todas":
            filtered_alerts = [a for a in filtered_alerts if a.category == category_filter]
        
        # Mostrar alertas
        if filtered_alerts:
            for alert in filtered_alerts[-10:]:  # Últimas 10 alertas
                severity_icons = {
                    "info": "ℹ️",
                    "warning": "⚠️", 
                    "error": "❌",
                    "critical": "🚨"
                }
                
                severity_colors = {
                    "info": "blue",
                    "warning": "orange",
                    "error": "red",
                    "critical": "darkred"
                }
                
                st.markdown(
                    f"""
                    <div style="
                        border-left: 4px solid {severity_colors.get(alert.severity, 'gray')};
                        padding-left: 10px;
                        margin: 5px 0;
                    ">
                        <strong>{severity_icons.get(alert.severity, '❓')} {alert.severity.upper()}</strong> - {alert.category}<br>
                        <small>{alert.message}</small><br>
                        <small style="color: gray;">{alert.timestamp.strftime('%H:%M:%S')}</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.success("✅ No hay alertas activas")
        
        # Controles de monitoreo
        st.subheader("⚙️ **Controles de Monitoreo**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Actualizar Dashboard", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("📊 Exportar Métricas", use_container_width=True):
                self._export_metrics()
    
    def _export_metrics(self):
        """Exporta métricas del sistema."""
        try:
            # Preparar datos para exportación
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "system_health": self.get_system_health(),
                "process_statuses": {
                    name: {
                        "status": status.status,
                        "success_rate": status.success_rate,
                        "error_count": status.error_count,
                        "warning_count": status.warning_count
                    }
                    for name, status in self.process_statuses.items()
                },
                "recent_alerts": [
                    {
                        "severity": alert.severity,
                        "category": alert.category,
                        "message": alert.message,
                        "timestamp": alert.timestamp.isoformat()
                    }
                    for alert in self.alerts[-20:]  # Últimas 20 alertas
                ]
            }
            
            # Crear archivo JSON para descarga
            json_str = json.dumps(export_data, indent=2, default=str)
            st.download_button(
                label="⬇️ Descargar Métricas (JSON)",
                data=json_str,
                file_name=f"system_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.error(f"Error exportando métricas: {str(e)}")

# Instancia global
monitoring_dashboard = MonitoringDashboard()







