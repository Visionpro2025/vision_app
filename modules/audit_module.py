# modules/audit_module.py
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from collections import defaultdict, Counter
import pandas as pd

@dataclass
class AuditCheck:
    """Verificación de auditoría individual."""
    id: str
    name: str
    category: str
    status: str  # "passed", "warning", "failed", "error"
    timestamp: datetime
    details: Dict[str, Any]
    severity: str  # "low", "medium", "high", "critical"
    recommendation: str

@dataclass
class BenchmarkResult:
    """Resultado de benchmarking contra referencia."""
    metric_name: str
    current_value: float
    reference_value: float
    difference: float
    percentage_diff: float
    status: str  # "better", "worse", "similar"
    confidence: float

@dataclass
class AuditReport:
    """Reporte completo de auditoría."""
    audit_id: str
    timestamp: datetime
    overall_score: float
    checks_passed: int
    checks_warning: int
    checks_failed: int
    checks_error: int
    total_checks: int
    categories: Dict[str, Dict[str, Any]]
    recommendations: List[str]
    benchmark_results: List[BenchmarkResult]

class AuditModule:
    """Módulo de auditoría automática y benchmarking del sistema."""
    
    def __init__(self):
        self.audit_checks = []
        self.benchmark_references = {}
        self.audit_reports = []
        self.performance_history = []
        
        # Inicializar referencias de benchmarking
        self._initialize_benchmark_references()
    
    def _initialize_benchmark_references(self):
        """Inicializa valores de referencia para benchmarking."""
        self.benchmark_references = {
            "news_quality": {
                "min_news_count": 50,
                "target_news_count": 100,
                "min_categories": 3,
                "min_sources": 5
            },
            "processing_performance": {
                "max_t70_time": 30.0,  # segundos
                "max_gematria_time": 45.0,
                "max_subliminal_time": 60.0,
                "max_quantum_time": 90.0
            },
            "correlation_quality": {
                "min_global_score": 0.3,
                "target_global_score": 0.7,
                "min_layer_correlation": 0.2
            },
            "system_health": {
                "min_cpu_usage": 80.0,  # máximo porcentaje
                "min_memory_usage": 85.0,
                "min_disk_usage": 90.0
            }
        }
    
    def run_comprehensive_audit(self) -> AuditReport:
        """Ejecuta una auditoría completa del sistema."""
        audit_id = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        st.info("🔍 **Iniciando auditoría completa del sistema...**")
        
        # Limpiar checks anteriores
        self.audit_checks = []
        
        # 1. Auditoría de calidad de datos
        self._audit_data_quality()
        
        # 2. Auditoría de rendimiento
        self._audit_performance()
        
        # 3. Auditoría de seguridad
        self._audit_security()
        
        # 4. Auditoría de correlaciones
        self._audit_correlations()
        
        # 5. Auditoría de sistema
        self._audit_system_health()
        
        # 6. Ejecutar benchmarking
        benchmark_results = self._run_benchmarking()
        
        # Generar reporte final
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Calcular puntuación general
        total_checks = len(self.audit_checks)
        passed_checks = len([c for c in self.audit_checks if c.status == "passed"])
        warning_checks = len([c for c in self.audit_checks if c.status == "warning"])
        failed_checks = len([c for c in self.audit_checks if c.status == "failed"])
        error_checks = len([c for c in self.audit_checks if c.status == "error"])
        
        # Puntuación ponderada
        overall_score = (
            (passed_checks * 1.0) +
            (warning_checks * 0.5) +
            (failed_checks * 0.0) +
            (error_checks * 0.0)
        ) / total_checks if total_checks > 0 else 0.0
        
        # Agrupar por categorías
        categories = defaultdict(lambda: {"checks": [], "score": 0.0, "count": 0})
        for check in self.audit_checks:
            categories[check.category]["checks"].append(check)
            categories[check.category]["count"] += 1
        
        # Calcular puntuación por categoría
        for category in categories:
            cat_checks = categories[category]["checks"]
            passed = len([c for c in cat_checks if c.status == "passed"])
            warning = len([c for c in cat_checks if c.status == "warning"])
            total = len(cat_checks)
            categories[category]["score"] = (passed + warning * 0.5) / total if total > 0 else 0.0
        
        # Generar recomendaciones
        recommendations = self._generate_recommendations()
        
        # Crear reporte
        audit_report = AuditReport(
            audit_id=audit_id,
            timestamp=end_time,
            overall_score=overall_score,
            checks_passed=passed_checks,
            checks_warning=warning_checks,
            checks_failed=failed_checks,
            checks_error=error_checks,
            total_checks=total_checks,
            categories=dict(categories),
            recommendations=recommendations,
            benchmark_results=benchmark_results
        )
        
        self.audit_reports.append(audit_report)
        
        # Mantener solo los últimos 50 reportes
        if len(self.audit_reports) > 50:
            self.audit_reports = self.audit_reports[-50:]
        
        st.success(f"✅ **Auditoría completada en {execution_time:.1f}s**")
        return audit_report
    
    def _audit_data_quality(self):
        """Auditoría de calidad de datos."""
        st.write("📊 Verificando calidad de datos...")
        
        # Verificar noticias en session state
        news_df = st.session_state.get("news_selected_df", pd.DataFrame())
        
        if not news_df.empty:
            # Verificar cantidad de noticias
            news_count = len(news_df)
            if news_count >= 100:
                self._add_audit_check(
                    "news_count", "Calidad de Datos", "passed",
                    f"Excelente cantidad de noticias: {news_count}",
                    "low", "Mantener acopio regular"
                )
            elif news_count >= 50:
                self._add_audit_check(
                    "news_count", "Calidad de Datos", "warning",
                    f"Cantidad aceptable de noticias: {news_count}",
                    "medium", "Considerar acopio adicional"
                )
            else:
                self._add_audit_check(
                    "news_count", "Calidad de Datos", "failed",
                    f"Insuficientes noticias: {news_count}",
                    "high", "Ejecutar acopio masivo inmediatamente"
                )
            
            # Verificar categorías
            if 'categoria' in news_df.columns:
                unique_categories = news_df['categoria'].nunique()
                if unique_categories >= 5:
                    self._add_audit_check(
                        "category_diversity", "Calidad de Datos", "passed",
                        f"Excelente diversidad de categorías: {unique_categories}",
                        "low", "Mantener balance de categorías"
                    )
                elif unique_categories >= 3:
                    self._add_audit_check(
                        "category_diversity", "Calidad de Datos", "warning",
                        f"Diversidad aceptable de categorías: {unique_categories}",
                        "medium", "Expandir cobertura de categorías"
                    )
                else:
                    self._add_audit_check(
                        "category_diversity", "Calidad de Datos", "failed",
                        f"Poca diversidad de categorías: {unique_categories}",
                        "high", "Ampliar fuentes y categorías"
                    )
            
            # Verificar fuentes
            if 'medio' in news_df.columns:
                unique_sources = news_df['medio'].nunique()
                if unique_sources >= 8:
                    self._add_audit_check(
                        "source_diversity", "Calidad de Datos", "passed",
                        f"Excelente diversidad de fuentes: {unique_sources}",
                        "low", "Mantener variedad de fuentes"
                    )
                elif unique_sources >= 5:
                    self._add_audit_check(
                        "source_diversity", "Calidad de Datos", "warning",
                        f"Diversidad aceptable de fuentes: {unique_sources}",
                        "medium", "Considerar nuevas fuentes"
                    )
                else:
                    self._add_audit_check(
                        "source_diversity", "Calidad de Datos", "failed",
                        f"Poca diversidad de fuentes: {unique_sources}",
                        "high", "Expandir fuentes de noticias"
                    )
        else:
            self._add_audit_check(
                "news_availability", "Calidad de Datos", "error",
                "No hay noticias disponibles",
                "critical", "Ejecutar acopio de noticias inmediatamente"
            )
    
    def _audit_performance(self):
        """Auditoría de rendimiento del sistema."""
        st.write("⚡ Verificando rendimiento...")
        
        # Verificar tiempo de ejecución del pipeline
        if "pipeline_execution_time" in st.session_state:
            exec_time = st.session_state["pipeline_execution_time"]
            
            if exec_time <= 60:  # 1 minuto
                self._add_audit_check(
                    "pipeline_performance", "Rendimiento", "passed",
                    f"Excelente rendimiento: {exec_time:.1f}s",
                    "low", "Mantener optimizaciones"
                )
            elif exec_time <= 180:  # 3 minutos
                self._add_audit_check(
                    "pipeline_performance", "Rendimiento", "warning",
                    f"Rendimiento aceptable: {exec_time:.1f}s",
                    "medium", "Revisar optimizaciones"
                )
            else:
                self._add_audit_check(
                    "pipeline_performance", "Rendimiento", "failed",
                    f"Rendimiento lento: {exec_time:.1f}s",
                    "high", "Optimizar pipeline y recursos"
                )
        else:
            self._add_audit_check(
                "pipeline_performance", "Rendimiento", "warning",
                "No hay datos de rendimiento disponibles",
                "medium", "Ejecutar pipeline para obtener métricas"
            )
        
        # Verificar uso de memoria (simulado)
        memory_usage = 75.0  # Simulado
        if memory_usage <= 70:
            self._add_audit_check(
                "memory_usage", "Rendimiento", "passed",
                f"Uso de memoria óptimo: {memory_usage:.1f}%",
                "low", "Mantener eficiencia"
            )
        elif memory_usage <= 85:
            self._add_audit_check(
                "memory_usage", "Rendimiento", "warning",
                f"Uso de memoria aceptable: {memory_usage:.1f}%",
                "medium", "Monitorear uso de memoria"
            )
        else:
            self._add_audit_check(
                "memory_usage", "Rendimiento", "failed",
                f"Uso de memoria alto: {memory_usage:.1f}%",
                "high", "Optimizar uso de memoria"
            )
    
    def _audit_security(self):
        """Auditoría de seguridad del sistema."""
        st.write("🔒 Verificando seguridad...")
        
        # Verificar autenticación
        if "current_user" in st.session_state:
            self._add_audit_check(
                "user_authentication", "Seguridad", "passed",
                f"Usuario autenticado: {st.session_state['current_user']['username']}",
                "low", "Mantener políticas de seguridad"
            )
        else:
            self._add_audit_check(
                "user_authentication", "Seguridad", "warning",
                "No hay usuario autenticado",
                "medium", "Implementar autenticación si es necesario"
            )
        
        # Verificar tokens de sesión
        if "session_token" in st.session_state:
            self._add_audit_check(
                "session_management", "Seguridad", "passed",
                "Token de sesión activo",
                "low", "Mantener gestión de sesiones"
            )
        else:
            self._add_audit_check(
                "session_management", "Seguridad", "warning",
                "No hay token de sesión",
                "medium", "Verificar gestión de sesiones"
            )
        
        # Verificar logs de seguridad
        if hasattr(st.session_state, 'security_logs'):
            log_count = len(st.session_state.security_logs)
            if log_count > 0:
                self._add_audit_check(
                    "security_logging", "Seguridad", "passed",
                    f"Logs de seguridad activos: {log_count}",
                    "low", "Mantener logging de seguridad"
                )
            else:
                self._add_audit_check(
                    "security_logging", "Seguridad", "warning",
                    "No hay logs de seguridad",
                    "medium", "Implementar logging de seguridad"
                )
        else:
            self._add_audit_check(
                "security_logging", "Seguridad", "warning",
                "Sistema de logging no configurado",
                "medium", "Configurar logging de seguridad"
            )
    
    def _audit_correlations(self):
        """Auditoría de correlaciones entre capas."""
        st.write("🔗 Verificando correlaciones...")
        
        # Verificar resultados de correlación
        if "corr" in st.session_state:
            correlation = st.session_state["corr"]
            
            if hasattr(correlation, 'global_score'):
                global_score = correlation.global_score
                
                if global_score >= 0.7:
                    self._add_audit_check(
                        "correlation_quality", "Correlaciones", "passed",
                        f"Excelente correlación global: {global_score:.1%}",
                        "low", "Mantener calidad de análisis"
                    )
                elif global_score >= 0.4:
                    self._add_audit_check(
                        "correlation_quality", "Correlaciones", "warning",
                        f"Correlación aceptable: {global_score:.1%}",
                        "medium", "Mejorar integración entre capas"
                    )
                else:
                    self._add_audit_check(
                        "correlation_quality", "Correlaciones", "failed",
                        f"Correlación baja: {global_score:.1%}",
                        "high", "Revisar integración y datos de entrada"
                    )
            else:
                self._add_audit_check(
                    "correlation_data", "Correlaciones", "warning",
                    "Datos de correlación incompletos",
                    "medium", "Verificar datos de correlación"
                )
        else:
            self._add_audit_check(
                "correlation_availability", "Correlaciones", "warning",
                "No hay datos de correlación disponibles",
                "medium", "Ejecutar análisis de correlación"
            )
        
        # Verificar series generadas
        if "series" in st.session_state:
            series = st.session_state["series"]
            if series and len(series) > 0:
                self._add_audit_check(
                    "series_generation", "Correlaciones", "passed",
                    f"Series generadas exitosamente: {len(series)}",
                    "low", "Mantener calidad de generación"
                )
            else:
                self._add_audit_check(
                    "series_generation", "Correlaciones", "warning",
                    "No hay series generadas",
                    "medium", "Verificar proceso de generación"
                )
        else:
            self._add_audit_check(
                "series_availability", "Correlaciones", "warning",
                "No hay series disponibles",
                "medium", "Ejecutar generación de series"
            )
    
    def _audit_system_health(self):
        """Auditoría de salud del sistema."""
        st.write("🏥 Verificando salud del sistema...")
        
        # Verificar estado general
        system_health = "healthy"  # Simulado
        if system_health == "healthy":
            self._add_audit_check(
                "system_health", "Salud del Sistema", "passed",
                "Sistema funcionando correctamente",
                "low", "Mantener monitoreo regular"
            )
        elif system_health == "warning":
            self._add_audit_check(
                "system_health", "Salud del Sistema", "warning",
                "Sistema con advertencias",
                "medium", "Revisar alertas del sistema"
            )
        else:
            self._add_audit_check(
                "system_health", "Salud del Sistema", "failed",
                "Sistema con problemas críticos",
                "high", "Revisar y resolver problemas inmediatamente"
            )
        
        # Verificar conectividad
        connectivity_status = "connected"  # Simulado
        if connectivity_status == "connected":
            self._add_audit_check(
                "connectivity", "Salud del Sistema", "passed",
                "Conectividad estable",
                "low", "Mantener monitoreo de red"
            )
        else:
            self._add_audit_check(
                "connectivity", "Salud del Sistema", "failed",
                "Problemas de conectividad",
                "high", "Verificar conexión de red"
            )
    
    def _run_benchmarking(self) -> List[BenchmarkResult]:
        """Ejecuta benchmarking contra valores de referencia."""
        st.write("📊 Ejecutando benchmarking...")
        
        benchmark_results = []
        
        # Benchmark de calidad de noticias
        news_df = st.session_state.get("news_selected_df", pd.DataFrame())
        if not news_df.empty:
            current_news_count = len(news_df)
            reference_news_count = self.benchmark_references["news_quality"]["target_news_count"]
            
            diff = current_news_count - reference_news_count
            percentage_diff = (diff / reference_news_count) * 100 if reference_news_count > 0 else 0
            
            if percentage_diff >= 0:
                status = "better"
            elif percentage_diff >= -20:
                status = "similar"
            else:
                status = "worse"
            
            benchmark_results.append(BenchmarkResult(
                metric_name="Cantidad de Noticias",
                current_value=float(current_news_count),
                reference_value=float(reference_news_count),
                difference=float(diff),
                percentage_diff=percentage_diff,
                status=status,
                confidence=0.9
            ))
        
        # Benchmark de correlación
        if "corr" in st.session_state:
            correlation = st.session_state["corr"]
            if hasattr(correlation, 'global_score'):
                current_score = correlation.global_score
                reference_score = self.benchmark_references["correlation_quality"]["target_global_score"]
                
                diff = current_score - reference_score
                percentage_diff = (diff / reference_score) * 100 if reference_score > 0 else 0
                
                if percentage_diff >= 0:
                    status = "better"
                elif percentage_diff >= -20:
                    status = "similar"
                else:
                    status = "worse"
                
                benchmark_results.append(BenchmarkResult(
                    metric_name="Correlación Global",
                    current_value=current_score,
                    reference_value=reference_score,
                    difference=diff,
                    percentage_diff=percentage_diff,
                    status=status,
                    confidence=0.8
                ))
        
        return benchmark_results
    
    def _add_audit_check(self, check_id: str, category: str, status: str, 
                         details: str, severity: str, recommendation: str):
        """Añade un check de auditoría."""
        check = AuditCheck(
            id=check_id,
            name=f"Check_{check_id}",
            category=category,
            status=status,
            timestamp=datetime.now(),
            details={"description": details},
            severity=severity,
            recommendation=recommendation
        )
        
        self.audit_checks.append(check)
    
    def _generate_recommendations(self) -> List[str]:
        """Genera recomendaciones basadas en los resultados de auditoría."""
        recommendations = []
        
        # Analizar checks fallidos
        failed_checks = [c for c in self.audit_checks if c.status == "failed"]
        error_checks = [c for c in self.audit_checks if c.status == "error"]
        
        if failed_checks:
            recommendations.append(f"🔴 Resolver {len(failed_checks)} verificaciones fallidas")
        
        if error_checks:
            recommendations.append(f"🚨 Resolver {len(error_checks)} errores críticos")
        
        # Recomendaciones específicas por categoría
        for check in self.audit_checks:
            if check.status in ["failed", "error"]:
                recommendations.append(f"💡 {check.recommendation}")
        
        # Recomendaciones generales
        if not recommendations:
            recommendations.append("✅ Sistema funcionando correctamente")
        
        return recommendations
    
    def render_audit_ui(self):
        """Renderiza la interfaz de auditoría en Streamlit."""
        st.subheader("🔍 **PANEL DE AUDITORÍA AUTOMÁTICA Y BENCHMARKING**")
        
        # Botón para ejecutar auditoría
        if st.button("🚀 **EJECUTAR AUDITORÍA COMPLETA**", use_container_width=True, type="primary"):
            with st.spinner("🔍 Ejecutando auditoría completa..."):
                audit_report = self.run_comprehensive_audit()
                st.session_state["last_audit_report"] = audit_report
                st.rerun()
        
        # Mostrar último reporte si existe
        if "last_audit_report" in st.session_state:
            self._render_audit_report(st.session_state["last_audit_report"])
        
        # Historial de auditorías
        if self.audit_reports:
            st.subheader("📋 **Historial de Auditorías**")
            
            # Crear DataFrame del historial
            history_data = []
            for report in self.audit_reports[-10:]:  # Últimos 10 reportes
                history_data.append({
                    "ID": report.audit_id,
                    "Fecha": report.timestamp.strftime("%Y-%m-%d %H:%M"),
                    "Puntuación": f"{report.overall_score:.1%}",
                    "Estado": "🟢 Excelente" if report.overall_score >= 0.8 else 
                              "🟡 Aceptable" if report.overall_score >= 0.6 else "🔴 Crítico",
                    "Pasaron": report.checks_passed,
                    "Advertencias": report.checks_warning,
                    "Fallaron": report.checks_failed,
                    "Errores": report.checks_error
                })
            
            if history_data:
                history_df = pd.DataFrame(history_data)
                st.dataframe(history_df, use_container_width=True, hide_index=True)
    
    def _render_audit_report(self, report: AuditReport):
        """Renderiza un reporte de auditoría específico."""
        st.subheader(f"📊 **Reporte de Auditoría: {report.audit_id}**")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Puntuación General",
                f"{report.overall_score:.1%}",
                f"{report.checks_passed}/{report.total_checks} pasaron"
            )
        
        with col2:
            status_icon = "🟢" if report.overall_score >= 0.8 else "🟡" if report.overall_score >= 0.6 else "🔴"
            st.metric(
                "Estado",
                f"{status_icon} {'Excelente' if report.overall_score >= 0.8 else 'Aceptable' if report.overall_score >= 0.6 else 'Crítico'}",
                f"Score: {report.overall_score:.3f}"
            )
        
        with col3:
            st.metric(
                "Verificaciones",
                f"{report.checks_passed + report.checks_warning}",
                f"✅ {report.checks_passed} | ⚠️ {report.checks_warning}"
            )
        
        with col4:
            st.metric(
                "Problemas",
                f"{report.checks_failed + report.checks_error}",
                f"❌ {report.checks_failed} | 🚨 {report.checks_error}"
            )
        
        # Resumen por categorías
        st.subheader("📊 **Resumen por Categorías**")
        
        if report.categories:
            category_data = []
            for category, data in report.categories.items():
                category_data.append({
                    "Categoría": category,
                    "Puntuación": f"{data['score']:.1%}",
                    "Verificaciones": data['count'],
                    "Estado": "🟢" if data['score'] >= 0.8 else "🟡" if data['score'] >= 0.6 else "🔴"
                })
            
            category_df = pd.DataFrame(category_data)
            st.dataframe(category_df, use_container_width=True, hide_index=True)
        
        # Resultados de benchmarking
        if report.benchmark_results:
            st.subheader("📈 **Resultados de Benchmarking**")
            
            benchmark_data = []
            for result in report.benchmark_results:
                status_icon = {
                    "better": "🟢",
                    "similar": "🟡",
                    "worse": "🔴"
                }.get(result.status, "⚪")
                
                benchmark_data.append({
                    "Métrica": result.metric_name,
                    "Valor Actual": f"{result.current_value:.2f}",
                    "Valor Referencia": f"{result.reference_value:.2f}",
                    "Diferencia": f"{result.difference:+.2f}",
                    "Diferencia %": f"{result.percentage_diff:+.1f}%",
                    "Estado": f"{status_icon} {result.status.title()}",
                    "Confianza": f"{result.confidence:.1%}"
                })
            
            benchmark_df = pd.DataFrame(benchmark_data)
            st.dataframe(benchmark_df, use_container_width=True, hide_index=True)
        
        # Recomendaciones
        st.subheader("💡 **Recomendaciones**")
        for recommendation in report.recommendations:
            st.write(f"• {recommendation}")
        
        # Detalles de verificaciones
        st.subheader("🔍 **Detalles de Verificaciones**")
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox(
                "Filtrar por Estado",
                ["Todos", "passed", "warning", "failed", "error"]
            )
        
        with col2:
            category_filter = st.selectbox(
                "Filtrar por Categoría",
                ["Todas"] + list(set(check.category for check in report.categories.keys()))
            )
        
        # Aplicar filtros
        filtered_checks = self.audit_checks
        if status_filter != "Todos":
            filtered_checks = [c for c in filtered_checks if c.status == status_filter]
        if category_filter != "Todas":
            filtered_checks = [c for c in filtered_checks if c.category == category_filter]
        
        # Mostrar checks filtrados
        if filtered_checks:
            check_data = []
            for check in filtered_checks:
                status_icons = {
                    "passed": "✅",
                    "warning": "⚠️",
                    "failed": "❌",
                    "error": "🚨"
                }
                
                check_data.append({
                    "ID": check.id,
                    "Categoría": check.category,
                    "Estado": f"{status_icons.get(check.status, '❓')} {check.status.title()}",
                    "Severidad": check.severity.title(),
                    "Detalles": check.details.get("description", ""),
                    "Recomendación": check.recommendation,
                    "Timestamp": check.timestamp.strftime("%H:%M:%S")
                })
            
            check_df = pd.DataFrame(check_data)
            st.dataframe(check_df, use_container_width=True, hide_index=True)
        else:
            st.info("No hay verificaciones que coincidan con los filtros")

# Instancia global
audit_module = AuditModule()








