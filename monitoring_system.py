#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MONITORING SYSTEM - Sistema de monitoreo avanzado para VISION PREMIUM
Incluye métricas en tiempo real, alertas automáticas y dashboard de análisis
"""

import os
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import psutil
import requests

# Importar sistemas existentes
try:
    from cache_manager import get_cache_stats
    from validation_system import get_validation_summary
    from ia_providers import get_provider_info
    SYSTEMS_AVAILABLE = True
except ImportError:
    SYSTEMS_AVAILABLE = False
    print("⚠️ Sistemas de caché y validación no disponibles")

@dataclass
class SystemMetrics:
    """Métricas del sistema en tiempo real"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io: Dict[str, float]
    active_connections: int
    cache_stats: Dict[str, Any]
    validation_stats: Dict[str, Any]
    ai_provider_status: Dict[str, Any]
    error_count: int
    warning_count: int
    performance_score: float

@dataclass
class Alert:
    """Alerta del sistema"""
    id: str
    timestamp: str
    level: str  # info, warning, error, critical
    category: str
    message: str
    details: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[str] = None

@dataclass
class PerformanceLog:
    """Log de rendimiento"""
    timestamp: str
    operation: str
    duration_ms: float
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

class MonitoringSystem:
    """Sistema de monitoreo avanzado para VISION PREMIUM"""
    
    def __init__(self, log_retention_days: int = 30, alert_threshold: float = 0.8):
        self.log_retention_days = log_retention_days
        self.alert_threshold = alert_threshold
        
        # Almacenamiento de métricas
        self.metrics_history = deque(maxlen=1000)  # Últimas 1000 métricas
        self.alerts_history = deque(maxlen=500)    # Últimas 500 alertas
        self.performance_logs = deque(maxlen=2000) # Últimos 2000 logs
        
        # Contadores en tiempo real
        self.error_counter = defaultdict(int)
        self.warning_counter = defaultdict(int)
        self.operation_counter = defaultdict(int)
        
        # Umbrales de alerta
        self.alert_thresholds = {
            "cpu_high": 80.0,           # CPU > 80%
            "memory_high": 85.0,        # Memoria > 85%
            "disk_high": 90.0,          # Disco > 90%
            "error_rate": 0.1,          # Tasa de errores > 10%
            "response_time": 5000.0,    # Tiempo de respuesta > 5s
            "cache_miss": 0.3           # Cache miss > 30%
        }
        
        # Estado del sistema
        self.system_status = "healthy"
        self.last_check = datetime.now()
        self.monitoring_active = False
        
        # Iniciar monitoreo automático
        self.start_monitoring()
    
    def start_monitoring(self):
        """Inicia el monitoreo automático en segundo plano"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()
            print("✅ Monitoreo automático iniciado")
    
    def stop_monitoring(self):
        """Detiene el monitoreo automático"""
        self.monitoring_active = False
        print("⏹️ Monitoreo automático detenido")
    
    def _monitoring_loop(self):
        """Bucle principal de monitoreo"""
        while self.monitoring_active:
            try:
                # Recolectar métricas
                metrics = self.collect_system_metrics()
                self.metrics_history.append(metrics)
                
                # Verificar alertas
                self.check_alerts(metrics)
                
                # Limpiar logs antiguos
                self.cleanup_old_logs()
                
                # Esperar 30 segundos antes de la siguiente verificación
                time.sleep(30)
                
            except Exception as e:
                print(f"❌ Error en monitoreo: {e}")
                time.sleep(60)  # Esperar más tiempo si hay error
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Recolecta métricas del sistema en tiempo real"""
        try:
            # Métricas del sistema
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Métricas de red
            network_io = psutil.net_io_counters()
            network_stats = {
                'bytes_sent': network_io.bytes_sent,
                'bytes_recv': network_io.bytes_recv,
                'packets_sent': network_io.packets_sent,
                'packets_recv': network_io.packets_recv
            }
            
            # Conexiones activas
            try:
                active_connections = len(psutil.net_connections())
            except:
                active_connections = 0
            
            # Métricas de caché
            cache_stats = {}
            if SYSTEMS_AVAILABLE:
                try:
                    cache_stats = get_cache_stats()
                except:
                    cache_stats = {"error": "No disponible"}
            
            # Métricas de validación
            validation_stats = {}
            if SYSTEMS_AVAILABLE:
                try:
                    # Simular estadísticas de validación
                    validation_stats = {
                        "total_validations": sum(self.error_counter.values()) + sum(self.warning_counter.values()),
                        "errors": sum(self.error_counter.values()),
                        "warnings": sum(self.warning_counter.values())
                    }
                except:
                    validation_stats = {"error": "No disponible"}
            
            # Estado del proveedor de IA
            ai_provider_status = {}
            if SYSTEMS_AVAILABLE:
                try:
                    ai_provider_status = get_provider_info()
                except:
                    ai_provider_status = {"error": "No disponible"}
            
            # Calcular score de rendimiento
            performance_score = self._calculate_performance_score(
                cpu_percent, memory.percent, disk.percent
            )
            
            return SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage_percent=disk.percent,
                network_io=network_stats,
                active_connections=active_connections,
                cache_stats=cache_stats,
                validation_stats=validation_stats,
                ai_provider_status=ai_provider_status,
                error_count=sum(self.error_counter.values()),
                warning_count=sum(self.warning_counter.values()),
                performance_score=performance_score
            )
            
        except Exception as e:
            print(f"❌ Error recolectando métricas: {e}")
            # Retornar métricas básicas en caso de error
            return SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_usage_percent=0.0,
                network_io={},
                active_connections=0,
                cache_stats={"error": str(e)},
                validation_stats={"error": str(e)},
                ai_provider_status={"error": str(e)},
                error_count=1,
                warning_count=0,
                performance_score=0.0
            )
    
    def _calculate_performance_score(self, cpu: float, memory: float, disk: float) -> float:
        """Calcula un score de rendimiento del 0 al 100"""
        try:
            # Score base: 100
            score = 100.0
            
            # Penalizaciones por uso alto de recursos
            if cpu > 80:
                score -= (cpu - 80) * 0.5
            if memory > 80:
                score -= (memory - 80) * 0.5
            if disk > 80:
                score -= (disk - 80) * 0.5
            
            # Asegurar que el score esté entre 0 y 100
            return max(0.0, min(100.0, score))
            
        except:
            return 50.0  # Score neutral en caso de error
    
    def check_alerts(self, metrics: SystemMetrics):
        """Verifica y genera alertas basadas en las métricas"""
        try:
            # Alerta por CPU alto
            if metrics.cpu_percent > self.alert_thresholds["cpu_high"]:
                self.create_alert(
                    level="warning",
                    category="performance",
                    message=f"CPU alto: {metrics.cpu_percent:.1f}%",
                    details={"cpu_percent": metrics.cpu_percent, "threshold": self.alert_thresholds["cpu_high"]}
                )
            
            # Alerta por memoria alta
            if metrics.memory_percent > self.alert_thresholds["memory_high"]:
                self.create_alert(
                    level="warning",
                    category="performance",
                    message=f"Memoria alta: {metrics.memory_percent:.1f}%",
                    details={"memory_percent": metrics.memory_percent, "threshold": self.alert_thresholds["memory_high"]}
                )
            
            # Alerta por disco alto
            if metrics.disk_usage_percent > self.alert_thresholds["disk_high"]:
                self.create_alert(
                    level="warning",
                    category="storage",
                    message=f"Disco alto: {metrics.disk_usage_percent:.1f}%",
                    details={"disk_percent": metrics.disk_usage_percent, "threshold": self.alert_thresholds["disk_high"]}
                )
            
            # Alerta por score de rendimiento bajo
            if metrics.performance_score < 50:
                self.create_alert(
                    level="error",
                    category="performance",
                    message=f"Rendimiento crítico: {metrics.performance_score:.1f}/100",
                    details={"performance_score": metrics.performance_score}
                )
            
            # Alerta por muchos errores
            if metrics.error_count > 10:
                self.create_alert(
                    level="error",
                    category="errors",
                    message=f"Muchos errores: {metrics.error_count}",
                    details={"error_count": metrics.error_count}
                )
            
        except Exception as e:
            print(f"❌ Error verificando alertas: {e}")
    
    def create_alert(self, level: str, category: str, message: str, details: Dict[str, Any]):
        """Crea una nueva alerta"""
        try:
            alert = Alert(
                id=f"alert_{int(time.time())}_{len(self.alerts_history)}",
                timestamp=datetime.now().isoformat(),
                level=level,
                category=category,
                message=message,
                details=details
            )
            
            self.alerts_history.append(alert)
            
            # Incrementar contadores
            self.error_counter[category] += 1 if level in ["error", "critical"] else 0
            self.warning_counter[category] += 1 if level == "warning" else 0
            
            # Log de alerta
            print(f"🚨 ALERTA [{level.upper()}] {category}: {message}")
            
        except Exception as e:
            print(f"❌ Error creando alerta: {e}")
    
    def log_operation(self, operation: str, duration_ms: float, success: bool, 
                     error_message: str = None, metadata: Dict[str, Any] = None):
        """Registra una operación para análisis de rendimiento"""
        try:
            log = PerformanceLog(
                timestamp=datetime.now().isoformat(),
                operation=operation,
                duration_ms=duration_ms,
                success=success,
                error_message=error_message,
                metadata=metadata or {}
            )
            
            self.performance_logs.append(log)
            self.operation_counter[operation] += 1
            
        except Exception as e:
            print(f"❌ Error registrando operación: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtiene el estado general del sistema"""
        try:
            if not self.metrics_history:
                return {"status": "unknown", "message": "No hay métricas disponibles"}
            
            latest_metrics = self.metrics_history[-1]
            
            # Determinar estado del sistema
            if latest_metrics.performance_score >= 80:
                status = "healthy"
                message = "Sistema funcionando correctamente"
            elif latest_metrics.performance_score >= 60:
                status = "warning"
                message = "Sistema con advertencias"
            else:
                status = "critical"
                message = "Sistema con problemas críticos"
            
            return {
                "status": status,
                "message": message,
                "performance_score": latest_metrics.performance_score,
                "last_check": latest_metrics.timestamp,
                "active_alerts": len([a for a in self.alerts_history if not a.resolved])
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Error obteniendo estado: {e}"}
    
    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Obtiene un resumen de métricas de las últimas N horas"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Filtrar métricas por tiempo
            recent_metrics = [
                m for m in self.metrics_history
                if datetime.fromisoformat(m.timestamp) > cutoff_time
            ]
            
            if not recent_metrics:
                return {"message": f"No hay métricas en las últimas {hours} horas"}
            
            # Calcular promedios
            avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
            avg_disk = sum(m.disk_usage_percent for m in recent_metrics) / len(recent_metrics)
            avg_performance = sum(m.performance_score for m in recent_metrics) / len(recent_metrics)
            
            # Contar alertas
            alerts_by_level = defaultdict(int)
            for alert in self.alerts_history:
                if datetime.fromisoformat(alert.timestamp) > cutoff_time:
                    alerts_by_level[alert.level] += 1
            
            return {
                "period_hours": hours,
                "metrics_count": len(recent_metrics),
                "averages": {
                    "cpu_percent": round(avg_cpu, 2),
                    "memory_percent": round(avg_memory, 2),
                    "disk_percent": round(avg_disk, 2),
                    "performance_score": round(avg_performance, 2)
                },
                "alerts": dict(alerts_by_level),
                "operations": dict(self.operation_counter)
            }
            
        except Exception as e:
            return {"error": f"Error calculando resumen: {e}"}
    
    def resolve_alert(self, alert_id: str):
        """Marca una alerta como resuelta"""
        try:
            for alert in self.alerts_history:
                if alert.id == alert_id:
                    alert.resolved = True
                    alert.resolved_at = datetime.now().isoformat()
                    print(f"✅ Alerta resuelta: {alert.message}")
                    return True
            return False
        except Exception as e:
            print(f"❌ Error resolviendo alerta: {e}")
            return False
    
    def cleanup_old_logs(self):
        """Limpia logs antiguos según la retención configurada"""
        try:
            cutoff_time = datetime.now() - timedelta(days=self.log_retention_days)
            
            # Limpiar métricas antiguas
            self.metrics_history = deque(
                [m for m in self.metrics_history 
                 if datetime.fromisoformat(m.timestamp) > cutoff_time],
                maxlen=1000
            )
            
            # Limpiar logs de rendimiento antiguos
            self.performance_logs = deque(
                [log for log in self.performance_logs
                 if datetime.fromisoformat(log.timestamp) > cutoff_time],
                maxlen=2000
            )
            
        except Exception as e:
            print(f"❌ Error limpiando logs: {e}")
    
    def export_metrics(self, format: str = "json") -> str:
        """Exporta métricas en diferentes formatos"""
        try:
            if format.lower() == "json":
                data = {
                    "export_timestamp": datetime.now().isoformat(),
                    "system_status": self.get_system_status(),
                    "metrics_summary": self.get_metrics_summary(24),
                    "recent_alerts": [asdict(a) for a in list(self.alerts_history)[-10:]],
                    "performance_logs": [asdict(log) for log in list(self.performance_logs)[-50:]]
                }
                return json.dumps(data, indent=2, ensure_ascii=False)
            
            elif format.lower() == "csv":
                # Implementar exportación CSV si es necesario
                return "Formato CSV no implementado aún"
            
            else:
                return f"Formato {format} no soportado"
                
        except Exception as e:
            return f"Error exportando métricas: {e}"

# Instancia global del sistema de monitoreo
monitoring_system = MonitoringSystem()

# Funciones de conveniencia
def start_monitoring():
    """Inicia el monitoreo automático"""
    monitoring_system.start_monitoring()

def stop_monitoring():
    """Detiene el monitoreo automático"""
    monitoring_system.stop_monitoring()

def get_system_status():
    """Obtiene el estado del sistema"""
    return monitoring_system.get_system_status()

def get_metrics_summary(hours: int = 24):
    """Obtiene resumen de métricas"""
    return monitoring_system.get_metrics_summary(hours)

def log_operation(operation: str, duration_ms: float, success: bool, 
                 error_message: str = None, metadata: Dict[str, Any] = None):
    """Registra una operación"""
    monitoring_system.log_operation(operation, duration_ms, success, error_message, metadata)

def create_alert(level: str, category: str, message: str, details: Dict[str, Any]):
    """Crea una alerta"""
    monitoring_system.create_alert(level, category, message, details)

def export_metrics(format: str = "json"):
    """Exporta métricas"""
    return monitoring_system.export_metrics(format)

if __name__ == "__main__":
    # Prueba del sistema de monitoreo
    print("📊 VISION PREMIUM - Sistema de Monitoreo Avanzado")
    print("=" * 60)
    
    # Iniciar monitoreo
    start_monitoring()
    
    # Esperar un momento para recolectar métricas
    print("⏳ Recolectando métricas iniciales...")
    time.sleep(5)
    
    # Mostrar estado del sistema
    status = get_system_status()
    print(f"📊 Estado del sistema: {status['status']}")
    print(f"💬 Mensaje: {status['message']}")
    print(f"🎯 Score de rendimiento: {status.get('performance_score', 'N/A')}")
    
    # Mostrar resumen de métricas
    summary = get_metrics_summary(1)  # Última hora
    if "averages" in summary:
        print(f"\n📈 Métricas promedio (última hora):")
        print(f"   CPU: {summary['averages']['cpu_percent']}%")
        print(f"   Memoria: {summary['averages']['memory_percent']}%")
        print(f"   Disco: {summary['disk_percent']}%")
        print(f"   Rendimiento: {summary['averages']['performance_score']}/100")
    
    # Simular algunas operaciones
    print(f"\n🧪 Simulando operaciones...")
    log_operation("test_operation", 150.5, True, metadata={"test": True})
    log_operation("cache_operation", 25.0, True)
    log_operation("validation_operation", 100.0, False, error_message="Error de prueba")
    
    # Crear alerta de prueba
    create_alert("info", "test", "Alerta de prueba del sistema", {"test": True})
    
    # Esperar un poco más
    time.sleep(3)
    
    # Mostrar estado final
    final_status = get_system_status()
    print(f"\n🎯 Estado final: {final_status['status']}")
    print(f"🚨 Alertas activas: {final_status['active_alerts']}")
    
    # Exportar métricas
    print(f"\n📤 Exportando métricas...")
    exported = export_metrics("json")
    print(f"✅ Métricas exportadas ({len(exported)} caracteres)")
    
    # Detener monitoreo
    stop_monitoring()
    
    print("\n🎉 Sistema de monitoreo probado exitosamente!")






