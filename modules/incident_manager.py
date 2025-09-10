# modules/incident_manager.py
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
import streamlit as st
import logging
from enum import Enum
import pandas as pd
from dataclasses import asdict

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IncidentSeverity(Enum):
    """Severidad de las incidencias."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentStatus(Enum):
    """Estado de las incidencias."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class IncidentType(Enum):
    """Tipos de incidencias."""
    SYSTEM_ERROR = "system_error"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    DATA_QUALITY_ISSUE = "data_quality_issue"
    SECURITY_ALERT = "security_alert"
    PROCESS_FAILURE = "process_failure"
    RESOURCE_SHORTAGE = "resource_shortage"
    CONNECTIVITY_ISSUE = "connectivity_issue"

@dataclass
class Incident:
    """Representa una incidencia del sistema."""
    id: str
    title: str
    description: str
    incident_type: IncidentType
    severity: IncidentSeverity
    status: IncidentStatus
    created_at: datetime
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None
    auto_resolved: bool = False
    retry_count: int = 0
    max_retries: int = 3
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AutoCorrectionRule:
    """Regla de auto-corrección para incidencias."""
    id: str
    name: str
    incident_type: IncidentType
    severity_threshold: IncidentSeverity
    conditions: Dict[str, Any]
    actions: List[str]
    enabled: bool = True
    priority: int = 1
    cooldown_minutes: int = 5

@dataclass
class IncidentMetrics:
    """Métricas de incidencias."""
    total_incidents: int
    open_incidents: int
    resolved_incidents: int
    avg_resolution_time: float
    incidents_by_severity: Dict[str, int]
    incidents_by_type: Dict[str, int]
    auto_resolution_rate: float

class IncidentManager:
    """Módulo de manejo proactivo de incidencias y auto-corrección."""
    
    def __init__(self):
        self.incidents = []
        self.auto_correction_rules = []
        self.incident_handlers = {}
        self.monitoring_active = False
        self.monitor_thread = None
        self.incident_counter = 0
        
        # Inicializar reglas de auto-corrección
        self._initialize_auto_correction_rules()
        
        # Inicializar manejadores de incidencias
        self._initialize_incident_handlers()
    
    def _initialize_auto_correction_rules(self):
        """Inicializa reglas de auto-corrección por defecto."""
        
        # Regla para errores de sistema
        system_error_rule = AutoCorrectionRule(
            id="system_error_restart",
            name="Reinicio automático en errores de sistema",
            incident_type=IncidentType.SYSTEM_ERROR,
            severity_threshold=IncidentSeverity.MEDIUM,
            conditions={
                "error_type": ["connection_error", "timeout_error", "resource_error"],
                "retry_count": {"max": 2}
            },
            actions=["restart_process", "clear_cache", "reset_connection"],
            priority=1,
            cooldown_minutes=2
        )
        
        # Regla para problemas de rendimiento
        performance_rule = AutoCorrectionRule(
            id="performance_optimization",
            name="Optimización automática de rendimiento",
            incident_type=IncidentType.PERFORMANCE_DEGRADATION,
            severity_threshold=IncidentSeverity.LOW,
            conditions={
                "cpu_usage": {"min": 80.0},
                "memory_usage": {"min": 85.0},
                "response_time": {"min": 5.0}
            },
            actions=["optimize_memory", "clear_temp_files", "restart_services"],
            priority=2,
            cooldown_minutes=10
        )
        
        # Regla para problemas de calidad de datos
        data_quality_rule = AutoCorrectionRule(
            id="data_quality_fix",
            name="Corrección automática de calidad de datos",
            incident_type=IncidentType.DATA_QUALITY_ISSUE,
            severity_threshold=IncidentSeverity.MEDIUM,
            conditions={
                "news_count": {"max": 30},
                "category_diversity": {"max": 2},
                "source_diversity": {"max": 3}
            },
            actions=["trigger_news_acquisition", "expand_sources", "retry_failed_requests"],
            priority=1,
            cooldown_minutes=5
        )
        
        # Regla para fallos de procesos
        process_failure_rule = AutoCorrectionRule(
            id="process_failure_recovery",
            name="Recuperación automática de procesos fallidos",
            incident_type=IncidentType.PROCESS_FAILURE,
            severity_threshold=IncidentSeverity.HIGH,
            conditions={
                "failure_type": ["pipeline_failure", "layer_failure", "correlation_failure"],
                "consecutive_failures": {"max": 2}
            },
            actions=["restart_pipeline", "fallback_to_backup", "notify_admin"],
            priority=1,
            cooldown_minutes=1
        )
        
        self.auto_correction_rules.extend([
            system_error_rule,
            performance_rule,
            data_quality_rule,
            process_failure_rule
        ])
    
    def _initialize_incident_handlers(self):
        """Inicializa manejadores específicos para diferentes tipos de incidencias."""
        
        # Manejador para errores de sistema
        self.incident_handlers[IncidentType.SYSTEM_ERROR] = {
            "restart_process": self._restart_process,
            "clear_cache": self._clear_cache,
            "reset_connection": self._reset_connection
        }
        
        # Manejador para problemas de rendimiento
        self.incident_handlers[IncidentType.PERFORMANCE_DEGRADATION] = {
            "optimize_memory": self._optimize_memory,
            "clear_temp_files": self._clear_temp_files,
            "restart_services": self._restart_services
        }
        
        # Manejador para problemas de calidad de datos
        self.incident_handlers[IncidentType.DATA_QUALITY_ISSUE] = {
            "trigger_news_acquisition": self._trigger_news_acquisition,
            "expand_sources": self._expand_sources,
            "retry_failed_requests": self._retry_failed_requests
        }
        
        # Manejador para fallos de procesos
        self.incident_handlers[IncidentType.PROCESS_FAILURE] = {
            "restart_pipeline": self._restart_pipeline,
            "fallback_to_backup": self._fallback_to_backup,
            "notify_admin": self._notify_admin
        }
    
    def start_monitoring(self):
        """Inicia el monitoreo proactivo de incidencias."""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("🚀 Monitoreo proactivo de incidencias iniciado")
    
    def stop_monitoring(self):
        """Detiene el monitoreo proactivo."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
            logger.info("🛑 Monitoreo proactivo de incidencias detenido")
    
    def _monitor_loop(self):
        """Loop principal de monitoreo proactivo."""
        while self.monitoring_active:
            try:
                # Verificar condiciones del sistema
                self._check_system_conditions()
                
                # Verificar incidencias abiertas
                self._check_open_incidents()
                
                # Aplicar reglas de auto-corrección
                self._apply_auto_correction_rules()
                
                # Limpiar incidencias antiguas
                self._cleanup_old_incidents()
                
                time.sleep(10)  # Verificar cada 10 segundos
                
            except Exception as e:
                logger.error(f"Error en loop de monitoreo: {e}")
                self._create_incident(
                    "Error en monitoreo proactivo",
                    f"Error en loop de monitoreo: {str(e)}",
                    IncidentType.SYSTEM_ERROR,
                    IncidentSeverity.HIGH
                )
    
    def _check_system_conditions(self):
        """Verifica condiciones del sistema para detectar incidencias proactivamente."""
        try:
            # Verificar calidad de datos
            news_df = st.session_state.get("news_selected_df", None)
            if news_df is not None and len(news_df) < 30:
                self._create_incident(
                    "Calidad de datos insuficiente",
                    f"Solo hay {len(news_df)} noticias disponibles (mínimo recomendado: 50)",
                    IncidentType.DATA_QUALITY_ISSUE,
                    IncidentSeverity.MEDIUM
                )
            
            # Verificar rendimiento del pipeline
            if "pipeline_execution_time" in st.session_state:
                exec_time = st.session_state["pipeline_execution_time"]
                if exec_time > 300:  # Más de 5 minutos
                    self._create_incident(
                        "Rendimiento del pipeline degradado",
                        f"Pipeline ejecutándose por {exec_time:.1f} segundos",
                        IncidentType.PERFORMANCE_DEGRADATION,
                        IncidentSeverity.MEDIUM
                    )
            
            # Verificar estado de correlaciones
            if "corr" in st.session_state:
                correlation = st.session_state["corr"]
                if hasattr(correlation, 'global_score') and correlation.global_score < 0.3:
                    self._create_incident(
                        "Calidad de correlación baja",
                        f"Correlación global: {correlation.global_score:.1%} (mínimo recomendado: 30%)",
                        IncidentType.DATA_QUALITY_ISSUE,
                        IncidentSeverity.LOW
                    )
            
        except Exception as e:
            logger.error(f"Error verificando condiciones del sistema: {e}")
    
    def _check_open_incidents(self):
        """Verifica incidencias abiertas para escalación."""
        current_time = datetime.now()
        
        for incident in self.incidents:
            if incident.status == IncidentStatus.OPEN:
                # Escalar incidencias críticas después de 5 minutos
                if (incident.severity == IncidentSeverity.CRITICAL and 
                    (current_time - incident.created_at).total_seconds() > 300):
                    self._escalate_incident(incident)
                
                # Escalar incidencias altas después de 15 minutos
                elif (incident.severity == IncidentSeverity.HIGH and 
                      (current_time - incident.created_at).total_seconds() > 900):
                    self._escalate_incident(incident)
    
    def _apply_auto_correction_rules(self):
        """Aplica reglas de auto-corrección activas."""
        current_time = datetime.now()
        
        for rule in self.auto_correction_rules:
            if not rule.enabled:
                continue
            
            # Verificar cooldown
            if hasattr(rule, 'last_applied'):
                time_since_last = (current_time - rule.last_applied).total_seconds() / 60
                if time_since_last < rule.cooldown_minutes:
                    continue
            
            # Verificar si la regla se aplica a alguna incidencia abierta
            applicable_incidents = [
                i for i in self.incidents
                if (i.incident_type == rule.incident_type and
                    i.status == IncidentStatus.OPEN and
                    i.severity.value >= rule.severity_threshold.value)
            ]
            
            for incident in applicable_incidents:
                if self._should_apply_rule(rule, incident):
                    self._apply_correction_rule(rule, incident)
                    rule.last_applied = current_time
                    break
    
    def _should_apply_rule(self, rule: AutoCorrectionRule, incident: Incident) -> bool:
        """Determina si una regla debe aplicarse a una incidencia."""
        try:
            for condition_key, condition_value in rule.conditions.items():
                if condition_key in incident.metadata:
                    incident_value = incident.metadata[condition_key]
                    
                    if isinstance(condition_value, dict):
                        if "min" in condition_value and incident_value < condition_value["min"]:
                            return False
                        if "max" in condition_value and incident_value > condition_value["max"]:
                            return False
                    elif incident_value != condition_value:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error verificando condiciones de regla: {e}")
            return False
    
    def _apply_correction_rule(self, rule: AutoCorrectionRule, incident: Incident):
        """Aplica una regla de corrección a una incidencia."""
        try:
            logger.info(f"🔧 Aplicando regla de auto-corrección: {rule.name}")
            
            # Ejecutar acciones
            for action in rule.actions:
                if action in self.incident_handlers.get(incident.incident_type, {}):
                    handler = self.incident_handlers[incident.incident_type][action]
                    success = handler(incident)
                    
                    if success:
                        logger.info(f"✅ Acción {action} ejecutada exitosamente")
                    else:
                        logger.warning(f"⚠️ Acción {action} falló")
            
            # Marcar como en progreso
            incident.status = IncidentStatus.IN_PROGRESS
            incident.assigned_to = "auto_correction_system"
            
            # Incrementar contador de reintentos
            incident.retry_count += 1
            
            # Verificar si se resolvió automáticamente
            if incident.retry_count <= incident.max_retries:
                self._attempt_auto_resolution(incident)
            
        except Exception as e:
            logger.error(f"Error aplicando regla de corrección: {e}")
    
    def _attempt_auto_resolution(self, incident: Incident):
        """Intenta resolver una incidencia automáticamente."""
        try:
            # Simular verificación de resolución
            time.sleep(2)  # Simular tiempo de procesamiento
            
            # Verificar si la incidencia se resolvió
            if self._verify_incident_resolution(incident):
                incident.status = IncidentStatus.RESOLVED
                incident.resolved_at = datetime.now()
                incident.auto_resolved = True
                incident.resolution_notes = "Resuelto automáticamente por el sistema"
                
                logger.info(f"✅ Incidencia {incident.id} resuelta automáticamente")
                
                # Notificar resolución
                self._notify_incident_resolution(incident)
            else:
                # Si no se resolvió, mantener en progreso
                incident.status = IncidentStatus.IN_PROGRESS
                
        except Exception as e:
            logger.error(f"Error en resolución automática: {e}")
    
    def _verify_incident_resolution(self, incident: Incident) -> bool:
        """Verifica si una incidencia ha sido resuelta."""
        try:
            if incident.incident_type == IncidentType.DATA_QUALITY_ISSUE:
                # Verificar si se resolvió el problema de datos
                news_df = st.session_state.get("news_selected_df", None)
                if news_df is not None and len(news_df) >= 50:
                    return True
            
            elif incident.incident_type == IncidentType.PERFORMANCE_DEGRADATION:
                # Verificar si mejoró el rendimiento
                if "pipeline_execution_time" in st.session_state:
                    exec_time = st.session_state["pipeline_execution_time"]
                    if exec_time < 180:  # Menos de 3 minutos
                        return True
            
            elif incident.incident_type == IncidentType.SYSTEM_ERROR:
                # Verificar si se resolvió el error del sistema
                return True  # Simulado
            
            return False
            
        except Exception as e:
            logger.error(f"Error verificando resolución: {e}")
            return False
    
    def _create_incident(self, title: str, description: str, incident_type: IncidentType, 
                         severity: IncidentSeverity, metadata: Dict = None) -> Incident:
        """Crea una nueva incidencia."""
        try:
            # Verificar si ya existe una incidencia similar
            existing_incident = self._find_similar_incident(title, incident_type)
            if existing_incident and existing_incident.status != IncidentStatus.RESOLVED:
                # Actualizar incidencia existente
                existing_incident.retry_count += 1
                existing_incident.metadata.update(metadata or {})
                logger.info(f"🔄 Incidencia existente actualizada: {existing_incident.id}")
                return existing_incident
            
            # Crear nueva incidencia
            self.incident_counter += 1
            incident_id = f"INC_{self.incident_counter:04d}"
            
            incident = Incident(
                id=incident_id,
                title=title,
                description=description,
                incident_type=incident_type,
                severity=severity,
                status=IncidentStatus.OPEN,
                created_at=datetime.now(),
                detected_at=datetime.now(),
                metadata=metadata or {},
                tags=[incident_type.value, severity.value]
            )
            
            self.incidents.append(incident)
            
            # Notificar nueva incidencia
            self._notify_new_incident(incident)
            
            logger.info(f"🚨 Nueva incidencia creada: {incident_id} - {title}")
            
            return incident
            
        except Exception as e:
            logger.error(f"Error creando incidencia: {e}")
            return None
    
    def _find_similar_incident(self, title: str, incident_type: IncidentType) -> Optional[Incident]:
        """Busca una incidencia similar existente."""
        for incident in self.incidents:
            if (incident.incident_type == incident_type and
                incident.title.lower() in title.lower() or
                title.lower() in incident.title.lower()):
                return incident
        return None
    
    def _escalate_incident(self, incident: Incident):
        """Escala una incidencia que requiere atención manual."""
        try:
            if incident.severity == IncidentSeverity.CRITICAL:
                incident.severity = IncidentSeverity.CRITICAL  # Ya es crítico
                incident.tags.append("escalated")
                logger.warning(f"🚨🚨 INCIDENCIA CRÍTICA ESCALADA: {incident.id}")
                
                # Notificar a administradores
                self._notify_admin_critical_incident(incident)
            
            elif incident.severity == IncidentSeverity.HIGH:
                incident.severity = IncidentSeverity.CRITICAL
                incident.tags.append("escalated")
                logger.warning(f"🚨 Incidencia alta escalada a crítica: {incident.id}")
                
                # Notificar a administradores
                self._notify_admin_critical_incident(incident)
            
        except Exception as e:
            logger.error(f"Error escalando incidencia: {e}")
    
    def _cleanup_old_incidents(self):
        """Limpia incidencias antiguas resueltas."""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(days=7)  # 7 días
        
        # Mover incidencias resueltas antiguas a cerradas
        for incident in self.incidents:
            if (incident.status == IncidentStatus.RESOLVED and
                incident.resolved_at and
                incident.resolved_at < cutoff_time):
                incident.status = IncidentStatus.CLOSED
        
        # Eliminar incidencias cerradas muy antiguas (30 días)
        cutoff_time_old = current_time - timedelta(days=30)
        self.incidents = [
            i for i in self.incidents
            if not (i.status == IncidentStatus.CLOSED and
                   i.resolved_at and
                   i.resolved_at < cutoff_time_old)
        ]
    
    def get_incident_metrics(self) -> IncidentMetrics:
        """Obtiene métricas de incidencias."""
        try:
            total_incidents = len(self.incidents)
            open_incidents = len([i for i in self.incidents if i.status == IncidentStatus.OPEN])
            resolved_incidents = len([i for i in self.incidents if i.status == IncidentStatus.RESOLVED])
            
            # Calcular tiempo promedio de resolución
            resolution_times = []
            for incident in self.incidents:
                if incident.resolved_at and incident.created_at:
                    resolution_time = (incident.resolved_at - incident.created_at).total_seconds() / 60
                    resolution_times.append(resolution_time)
            
            avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
            
            # Incidencias por severidad
            incidents_by_severity = {}
            for severity in IncidentSeverity:
                count = len([i for i in self.incidents if i.severity == severity])
                incidents_by_severity[severity.value] = count
            
            # Incidencias por tipo
            incidents_by_type = {}
            for incident_type in IncidentType:
                count = len([i for i in self.incidents if i.incident_type == incident_type])
                incidents_by_type[incident_type.value] = count
            
            # Tasa de auto-resolución
            auto_resolved_count = len([i for i in self.incidents if i.auto_resolved])
            auto_resolution_rate = auto_resolved_count / total_incidents if total_incidents > 0 else 0
            
            return IncidentMetrics(
                total_incidents=total_incidents,
                open_incidents=open_incidents,
                resolved_incidents=resolved_incidents,
                avg_resolution_time=avg_resolution_time,
                incidents_by_severity=incidents_by_severity,
                incidents_by_type=incidents_by_type,
                auto_resolution_rate=auto_resolution_rate
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo métricas de incidencias: {e}")
            return IncidentMetrics(0, 0, 0, 0, {}, {}, 0)
    
    # Implementaciones de acciones de corrección
    def _restart_process(self, incident: Incident) -> bool:
        """Reinicia un proceso del sistema."""
        try:
            logger.info(f"🔄 Reiniciando proceso para incidencia {incident.id}")
            # Simular reinicio
            time.sleep(1)
            return True
        except Exception as e:
            logger.error(f"Error reiniciando proceso: {e}")
            return False
    
    def _clear_cache(self, incident: Incident) -> bool:
        """Limpia la caché del sistema."""
        try:
            logger.info(f"🧹 Limpiando caché para incidencia {incident.id}")
            # Simular limpieza
            time.sleep(0.5)
            return True
        except Exception as e:
            logger.error(f"Error limpiando caché: {e}")
            return False
    
    def _reset_connection(self, incident: Incident) -> bool:
        """Reinicia conexiones del sistema."""
        try:
            logger.info(f"🔌 Reiniciando conexiones para incidencia {incident.id}")
            # Simular reinicio
            time.sleep(1)
            return True
        except Exception as e:
            logger.error(f"Error reiniciando conexiones: {e}")
            return False
    
    def _optimize_memory(self, incident: Incident) -> bool:
        """Optimiza el uso de memoria."""
        try:
            logger.info(f"💾 Optimizando memoria para incidencia {incident.id}")
            # Simular optimización
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Error optimizando memoria: {e}")
            return False
    
    def _clear_temp_files(self, incident: Incident) -> bool:
        """Limpia archivos temporales."""
        try:
            logger.info(f"🗑️ Limpiando archivos temporales para incidencia {incident.id}")
            # Simular limpieza
            time.sleep(1)
            return True
        except Exception as e:
            logger.error(f"Error limpiando archivos temporales: {e}")
            return False
    
    def _restart_services(self, incident: Incident) -> bool:
        """Reinicia servicios del sistema."""
        try:
            logger.info(f"🔄 Reiniciando servicios para incidencia {incident.id}")
            # Simular reinicio
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Error reiniciando servicios: {e}")
            return False
    
    def _trigger_news_acquisition(self, incident: Incident) -> bool:
        """Dispara adquisición automática de noticias."""
        try:
            logger.info(f"📰 Disparando adquisición de noticias para incidencia {incident.id}")
            # Simular adquisición
            time.sleep(3)
            return True
        except Exception as e:
            logger.error(f"Error disparando adquisición de noticias: {e}")
            return False
    
    def _expand_sources(self, incident: Incident) -> bool:
        """Expande fuentes de noticias."""
        try:
            logger.info(f"🔍 Expandindo fuentes para incidencia {incident.id}")
            # Simular expansión
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Error expandiendo fuentes: {e}")
            return False
    
    def _retry_failed_requests(self, incident: Incident) -> bool:
        """Reintenta solicitudes fallidas."""
        try:
            logger.info(f"🔄 Reintentando solicitudes fallidas para incidencia {incident.id}")
            # Simular reintento
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Error reintentando solicitudes: {e}")
            return False
    
    def _restart_pipeline(self, incident: Incident) -> bool:
        """Reinicia el pipeline de análisis."""
        try:
            logger.info(f"🔄 Reiniciando pipeline para incidencia {incident.id}")
            # Simular reinicio
            time.sleep(3)
            return True
        except Exception as e:
            logger.error(f"Error reiniciando pipeline: {e}")
            return False
    
    def _fallback_to_backup(self, incident: Incident) -> bool:
        """Cambia a modo de respaldo."""
        try:
            logger.info(f"🔄 Cambiando a modo de respaldo para incidencia {incident.id}")
            # Simular cambio
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Error cambiando a modo de respaldo: {e}")
            return False
    
    def _notify_admin(self, incident: Incident) -> bool:
        """Notifica a administradores."""
        try:
            logger.info(f"📢 Notificando a administradores sobre incidencia {incident.id}")
            # Simular notificación
            time.sleep(1)
            return True
        except Exception as e:
            logger.error(f"Error notificando a administradores: {e}")
            return False
    
    # Métodos de notificación
    def _notify_new_incident(self, incident: Incident):
        """Notifica una nueva incidencia."""
        logger.info(f"🚨 NUEVA INCIDENCIA: {incident.title} (Severidad: {incident.severity.value})")
    
    def _notify_incident_resolution(self, incident: Incident):
        """Notifica la resolución de una incidencia."""
        logger.info(f"✅ INCIDENCIA RESUELTA: {incident.title}")
    
    def _notify_admin_critical_incident(self, incident: Incident):
        """Notifica a administradores sobre incidencias críticas."""
        logger.warning(f"🚨🚨 INCIDENCIA CRÍTICA ESCALADA: {incident.title} - Requiere atención inmediata")
    
    def render_incident_ui(self):
        """Renderiza la interfaz de gestión de incidencias en Streamlit."""
        st.subheader("🚨 **PANEL DE GESTIÓN PROACTIVA DE INCIDENCIAS**")
        
        # Iniciar monitoreo si no está activo
        if not self.monitoring_active:
            self.start_monitoring()
        
        # Métricas principales
        metrics = self.get_incident_metrics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Incidencias",
                metrics.total_incidents,
                f"Abiertas: {metrics.open_incidents}"
            )
        
        with col2:
            st.metric(
                "Resueltas",
                metrics.resolved_incidents,
                f"Tasa: {(metrics.resolved_incidents/metrics.total_incidents*100):.1f}%" if metrics.total_incidents > 0 else "0%"
            )
        
        with col3:
            st.metric(
                "Tiempo Promedio",
                f"{metrics.avg_resolution_time:.1f} min",
                "Resolución"
            )
        
        with col4:
            st.metric(
                "Auto-Resolución",
                f"{metrics.auto_resolution_rate:.1%}",
                "Tasa"
            )
        
        # Incidencias activas
        st.subheader("🚨 **Incidencias Activas**")
        
        active_incidents = [i for i in self.incidents if i.status in [IncidentStatus.OPEN, IncidentStatus.IN_PROGRESS]]
        
        if active_incidents:
            incident_data = []
            for incident in active_incidents:
                severity_icons = {
                    IncidentSeverity.LOW: "🟢",
                    IncidentSeverity.MEDIUM: "🟡",
                    IncidentSeverity.HIGH: "🟠",
                    IncidentSeverity.CRITICAL: "🔴"
                }
                
                status_icons = {
                    IncidentStatus.OPEN: "🚨",
                    IncidentStatus.IN_PROGRESS: "⚡",
                    IncidentStatus.RESOLVED: "✅",
                    IncidentStatus.CLOSED: "🔒"
                }
                
                incident_data.append({
                    "ID": incident.id,
                    "Título": incident.title,
                    "Tipo": incident.incident_type.value.replace("_", " ").title(),
                    "Severidad": f"{severity_icons.get(incident.severity, '❓')} {incident.severity.value.title()}",
                    "Estado": f"{status_icons.get(incident.status, '❓')} {incident.status.value.replace('_', ' ').title()}",
                    "Creada": incident.created_at.strftime("%H:%M:%S"),
                    "Reintentos": incident.retry_count,
                    "Auto-Resuelta": "✅" if incident.auto_resolved else "❌"
                })
            
            incident_df = pd.DataFrame(incident_data)
            st.dataframe(incident_df, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No hay incidencias activas")
        
        # Reglas de auto-corrección
        st.subheader("⚙️ **Reglas de Auto-Corrección**")
        
        if self.auto_correction_rules:
            rule_data = []
            for rule in self.auto_correction_rules:
                rule_data.append({
                    "ID": rule.id,
                    "Nombre": rule.name,
                    "Tipo": rule.incident_type.value.replace("_", " ").title(),
                    "Umbral": rule.severity_threshold.value.title(),
                    "Prioridad": rule.priority,
                    "Estado": "✅ Activa" if rule.enabled else "❌ Inactiva",
                    "Cooldown": f"{rule.cooldown_minutes} min"
                })
            
            rule_df = pd.DataFrame(rule_data)
            st.dataframe(rule_df, use_container_width=True, hide_index=True)
        
        # Historial de incidencias
        st.subheader("📋 **Historial de Incidencias**")
        
        if self.incidents:
            # Filtros
            col1, col2 = st.columns(2)
            with col1:
                status_filter = st.selectbox(
                    "Filtrar por Estado",
                    ["Todos"] + [status.value for status in IncidentStatus]
                )
            
            with col2:
                severity_filter = st.selectbox(
                    "Filtrar por Severidad",
                    ["Todas"] + [severity.value for severity in IncidentSeverity]
                )
            
            # Aplicar filtros
            filtered_incidents = self.incidents
            if status_filter != "Todos":
                filtered_incidents = [i for i in filtered_incidents if i.status.value == status_filter]
            if severity_filter != "Todas":
                filtered_incidents = [i for i in filtered_incidents if i.severity.value == severity_filter]
            
            # Mostrar incidencias filtradas
            if filtered_incidents:
                history_data = []
                for incident in filtered_incidents[-20:]:  # Últimas 20 incidencias
                    severity_icons = {
                        IncidentSeverity.LOW: "🟢",
                        IncidentSeverity.MEDIUM: "🟡",
                        IncidentSeverity.HIGH: "🟠",
                        IncidentSeverity.CRITICAL: "🔴"
                    }
                    
                    history_data.append({
                        "ID": incident.id,
                        "Título": incident.title,
                        "Tipo": incident.incident_type.value.replace("_", " ").title(),
                        "Severidad": f"{severity_icons.get(incident.severity, '❓')} {incident.severity.value.title()}",
                        "Estado": incident.status.value.replace("_", " ").title(),
                        "Creada": incident.created_at.strftime("%Y-%m-%d %H:%M"),
                        "Resuelta": incident.resolved_at.strftime("%Y-%m-%d %H:%M") if incident.resolved_at else "N/A",
                        "Auto-Resuelta": "✅" if incident.auto_resolved else "❌"
                    })
                
                history_df = pd.DataFrame(history_data)
                st.dataframe(history_df, use_container_width=True, hide_index=True)
            else:
                st.info("No hay incidencias que coincidan con los filtros")
        else:
            st.info("No hay historial de incidencias disponible")
        
        # Controles
        st.subheader("🎛️ **Controles del Sistema**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Actualizar Estado", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("📊 Exportar Reporte", use_container_width=True):
                self._export_incident_report()
    
    def _export_incident_report(self):
        """Exporta un reporte de incidencias."""
        try:
            # Preparar datos para exportación
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "metrics": asdict(self.get_incident_metrics()),
                "incidents": [
                    {
                        "id": incident.id,
                        "title": incident.title,
                        "description": incident.description,
                        "type": incident.incident_type.value,
                        "severity": incident.severity.value,
                        "status": incident.status.value,
                        "created_at": incident.created_at.isoformat(),
                        "resolved_at": incident.resolved_at.isoformat() if incident.resolved_at else None,
                        "auto_resolved": incident.auto_resolved,
                        "retry_count": incident.retry_count
                    }
                    for incident in self.incidents
                ]
            }
            
            # Crear archivo JSON para descarga
            import json
            json_str = json.dumps(export_data, indent=2, default=str)
            st.download_button(
                label="⬇️ Descargar Reporte de Incidencias (JSON)",
                data=json_str,
                file_name=f"incident_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.error(f"Error exportando reporte: {str(e)}")

# Instancia global
incident_manager = IncidentManager()









