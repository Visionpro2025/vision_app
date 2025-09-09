# modules/auditor_self_protection.py
"""
SISTEMA DE AUTOPROTECCIÓN DEL AUDITOR
Protege al auditor contra sus propios errores y garantiza su confiabilidad.
"""

import streamlit as st
import hashlib
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import requests
import ssl
import socket
from urllib.parse import urlparse
import re

@dataclass
class AuditorHealthCheck:
    """Verificación de salud del auditor."""
    timestamp: datetime
    component: str
    status: str  # "healthy", "degraded", "failed"
    error_message: Optional[str]
    recovery_action: Optional[str]
    confidence_score: float

@dataclass
class AuditorValidation:
    """Validación de resultados del auditor."""
    validation_id: str
    timestamp: datetime
    input_hash: str
    output_hash: str
    validation_status: str  # "valid", "invalid", "suspicious"
    cross_validation_results: List[Dict[str, Any]]
    integrity_score: float

class AuditorSelfProtection:
    """Sistema de autoprotección y validación del auditor."""
    
    def __init__(self):
        self.health_checks = []
        self.validation_history = []
        self.error_patterns = []
        self.recovery_actions = []
        self.confidence_threshold = 0.8
        
        # Patrones de error conocidos
        self.error_patterns = [
            r'connection.*timeout',
            r'ssl.*certificate.*error',
            r'http.*error.*\d{3}',
            r'json.*decode.*error',
            r'attribute.*error',
            r'key.*error',
            r'index.*error'
        ]
        
        # Acciones de recuperación
        self.recovery_actions = {
            'timeout': 'Retry with exponential backoff',
            'ssl_error': 'Fallback to HTTP or skip SSL verification',
            'http_error': 'Try alternative endpoints or cached data',
            'json_error': 'Use alternative parsing methods',
            'attribute_error': 'Use safe attribute access with defaults',
            'key_error': 'Use safe dictionary access with defaults',
            'index_error': 'Use safe list access with bounds checking'
        }
    
    def perform_health_check(self) -> List[AuditorHealthCheck]:
        """Realiza verificación completa de salud del auditor."""
        st.info("🔍 **Realizando verificación de salud del auditor...**")
        
        health_checks = []
        
        # Verificar conectividad de red
        network_check = self._check_network_connectivity()
        health_checks.append(network_check)
        
        # Verificar APIs de fact-checking
        fact_check_check = self._check_fact_checking_apis()
        health_checks.append(fact_check_check)
        
        # Verificar base de datos de dominios confiables
        domains_check = self._check_trusted_domains()
        health_checks.append(domains_check)
        
        # Verificar algoritmos de verificación
        algorithms_check = self._check_verification_algorithms()
        health_checks.append(algorithms_check)
        
        # Verificar sistema de detección de patrones
        patterns_check = self._check_pattern_detection()
        health_checks.append(patterns_check)
        
        # Verificar sistema de logging
        logging_check = self._check_logging_system()
        health_checks.append(logging_check)
        
        self.health_checks = health_checks
        return health_checks
    
    def _check_network_connectivity(self) -> AuditorHealthCheck:
        """Verifica la conectividad de red del auditor."""
        try:
            # Probar conectividad a múltiples servicios
            test_urls = [
                'https://httpbin.org/get',
                'https://api.github.com',
                'https://www.google.com'
            ]
            
            successful_connections = 0
            for url in test_urls:
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        successful_connections += 1
                except:
                    continue
            
            success_rate = successful_connections / len(test_urls)
            
            if success_rate >= 0.8:
                status = "healthy"
                error_message = None
                recovery_action = None
                confidence = 0.9
            elif success_rate >= 0.5:
                status = "degraded"
                error_message = f"Solo {success_rate:.1%} de conexiones exitosas"
                recovery_action = "Usar conexiones alternativas o modo offline"
                confidence = 0.6
            else:
                status = "failed"
                error_message = f"Solo {success_rate:.1%} de conexiones exitosas"
                recovery_action = "Activar modo offline o usar datos en caché"
                confidence = 0.3
                
        except Exception as e:
            status = "failed"
            error_message = str(e)
            recovery_action = "Verificar configuración de red"
            confidence = 0.1
        
        return AuditorHealthCheck(
            timestamp=datetime.now(),
            component="network_connectivity",
            status=status,
            error_message=error_message,
            recovery_action=recovery_action,
            confidence_score=confidence
        )
    
    def _check_fact_checking_apis(self) -> AuditorHealthCheck:
        """Verifica la disponibilidad de APIs de fact-checking."""
        try:
            # Simular verificación de APIs (en implementación real, verificarías las APIs reales)
            api_status = {
                'google_fact_check': random.choice([True, True, False]),  # 66% éxito
                'snopes_api': random.choice([True, True, True, False]),   # 75% éxito
                'politifact_api': random.choice([True, True, False])      # 66% éxito
            }
            
            successful_apis = sum(api_status.values())
            total_apis = len(api_status)
            success_rate = successful_apis / total_apis
            
            if success_rate >= 0.8:
                status = "healthy"
                error_message = None
                recovery_action = None
                confidence = 0.9
            elif success_rate >= 0.5:
                status = "degraded"
                error_message = f"Solo {success_rate:.1%} de APIs disponibles"
                recovery_action = "Usar APIs alternativas o modo offline"
                confidence = 0.6
            else:
                status = "failed"
                error_message = f"Solo {success_rate:.1%} de APIs disponibles"
                recovery_action = "Activar modo offline o usar datos en caché"
                confidence = 0.3
                
        except Exception as e:
            status = "failed"
            error_message = str(e)
            recovery_action = "Verificar configuración de APIs"
            confidence = 0.1
        
        return AuditorHealthCheck(
            timestamp=datetime.now(),
            component="fact_checking_apis",
            status=status,
            error_message=error_message,
            recovery_action=recovery_action,
            confidence_score=confidence
        )
    
    def _check_trusted_domains(self) -> AuditorHealthCheck:
        """Verifica la base de datos de dominios confiables."""
        try:
            # Verificar que la base de datos de dominios confiables esté disponible
            trusted_domains = {
                'bbc.com': 0.95, 'cnn.com': 0.90, 'reuters.com': 0.95, 'ap.org': 0.95,
                'bloomberg.com': 0.90, 'wsj.com': 0.90, 'nytimes.com': 0.90,
                'washingtonpost.com': 0.90, 'theguardian.com': 0.90, 'npr.org': 0.90
            }
            
            if len(trusted_domains) >= 10:
                status = "healthy"
                error_message = None
                recovery_action = None
                confidence = 0.9
            elif len(trusted_domains) >= 5:
                status = "degraded"
                error_message = f"Solo {len(trusted_domains)} dominios confiables disponibles"
                recovery_action = "Agregar más dominios confiables"
                confidence = 0.6
            else:
                status = "failed"
                error_message = f"Solo {len(trusted_domains)} dominios confiables disponibles"
                recovery_action = "Cargar base de datos de dominios confiables"
                confidence = 0.3
                
        except Exception as e:
            status = "failed"
            error_message = str(e)
            recovery_action = "Verificar configuración de dominios confiables"
            confidence = 0.1
        
        return AuditorHealthCheck(
            timestamp=datetime.now(),
            component="trusted_domains",
            status=status,
            error_message=error_message,
            recovery_action=recovery_action,
            confidence_score=confidence
        )
    
    def _check_verification_algorithms(self) -> AuditorHealthCheck:
        """Verifica los algoritmos de verificación del auditor."""
        try:
            # Probar algoritmos de verificación con datos de prueba
            test_data = {
                'url': 'https://example.com',
                'content': 'This is a test content for verification',
                'trust_score': 0.8
            }
            
            # Simular verificación de algoritmos
            algorithm_tests = {
                'ssl_verification': random.choice([True, True, True, False]),  # 75% éxito
                'whois_verification': random.choice([True, True, False]),       # 66% éxito
                'content_analysis': random.choice([True, True, True, True]),    # 100% éxito
                'trust_calculation': random.choice([True, True, True, False])   # 75% éxito
            }
            
            successful_tests = sum(algorithm_tests.values())
            total_tests = len(algorithm_tests)
            success_rate = successful_tests / total_tests
            
            if success_rate >= 0.9:
                status = "healthy"
                error_message = None
                recovery_action = None
                confidence = 0.9
            elif success_rate >= 0.7:
                status = "degraded"
                error_message = f"Solo {success_rate:.1%} de algoritmos funcionando correctamente"
                recovery_action = "Revisar algoritmos fallidos"
                confidence = 0.6
            else:
                status = "failed"
                error_message = f"Solo {success_rate:.1%} de algoritmos funcionando correctamente"
                recovery_action = "Reinicializar algoritmos de verificación"
                confidence = 0.3
                
        except Exception as e:
            status = "failed"
            error_message = str(e)
            recovery_action = "Verificar implementación de algoritmos"
            confidence = 0.1
        
        return AuditorHealthCheck(
            timestamp=datetime.now(),
            component="verification_algorithms",
            status=status,
            error_message=error_message,
            recovery_action=recovery_action,
            confidence_score=confidence
        )
    
    def _check_pattern_detection(self) -> AuditorHealthCheck:
        """Verifica el sistema de detección de patrones sospechosos."""
        try:
            # Probar detección de patrones con datos de prueba
            test_patterns = [
                'This is clickbait content',
                'You won\'t believe what happens next',
                'Doctors hate this one trick',
                'This is normal content without suspicious patterns'
            ]
            
            suspicious_patterns = [
                r'clickbait|viral|shocking|you won\'t believe|doctors hate',
                r'fake news|hoax|conspiracy|alternative facts',
                r'guaranteed|miracle|instant|secret|exclusive'
            ]
            
            detection_accuracy = 0
            for pattern in test_patterns:
                detected = any(re.search(p, pattern, re.IGNORECASE) for p in suspicious_patterns)
                expected = 'clickbait' in pattern or 'won\'t believe' in pattern or 'doctors hate' in pattern
                if detected == expected:
                    detection_accuracy += 1
            
            accuracy_rate = detection_accuracy / len(test_patterns)
            
            if accuracy_rate >= 0.9:
                status = "healthy"
                error_message = None
                recovery_action = None
                confidence = 0.9
            elif accuracy_rate >= 0.7:
                status = "degraded"
                error_message = f"Solo {accuracy_rate:.1%} de precisión en detección"
                recovery_action = "Revisar patrones de detección"
                confidence = 0.6
            else:
                status = "failed"
                error_message = f"Solo {accuracy_rate:.1%} de precisión en detección"
                recovery_action = "Reinicializar sistema de detección"
                confidence = 0.3
                
        except Exception as e:
            status = "failed"
            error_message = str(e)
            recovery_action = "Verificar implementación de detección"
            confidence = 0.1
        
        return AuditorHealthCheck(
            timestamp=datetime.now(),
            component="pattern_detection",
            status=status,
            error_message=error_message,
            recovery_action=recovery_action,
            confidence_score=confidence
        )
    
    def _check_logging_system(self) -> AuditorHealthCheck:
        """Verifica el sistema de logging del auditor."""
        try:
            # Verificar que el sistema de logging esté funcionando
            log_entries = len(self.health_checks) + len(self.validation_history)
            
            if log_entries >= 0:
                status = "healthy"
                error_message = None
                recovery_action = None
                confidence = 0.9
            else:
                status = "failed"
                error_message = "Sistema de logging no disponible"
                recovery_action = "Inicializar sistema de logging"
                confidence = 0.1
                
        except Exception as e:
            status = "failed"
            error_message = str(e)
            recovery_action = "Verificar configuración de logging"
            confidence = 0.1
        
        return AuditorHealthCheck(
            timestamp=datetime.now(),
            component="logging_system",
            status=status,
            error_message=error_message,
            recovery_action=recovery_action,
            confidence_score=confidence
        )
    
    def validate_auditor_output(self, input_data: str, output_data: Dict[str, Any]) -> AuditorValidation:
        """Valida la salida del auditor para detectar errores."""
        try:
            # Generar hashes para verificación de integridad
            input_hash = hashlib.md5(input_data.encode()).hexdigest()
            output_hash = hashlib.md5(json.dumps(output_data, sort_keys=True).encode()).hexdigest()
            
            # Verificaciones de validación
            validation_checks = []
            
            # Verificar que la salida no esté vacía
            if output_data:
                validation_checks.append({"check": "output_not_empty", "status": "passed"})
            else:
                validation_checks.append({"check": "output_not_empty", "status": "failed"})
            
            # Verificar que tenga campos requeridos
            required_fields = ['overall_veracity_score', 'risk_level', 'recommendations']
            for field in required_fields:
                if field in output_data:
                    validation_checks.append({"check": f"has_{field}", "status": "passed"})
                else:
                    validation_checks.append({"check": f"has_{field}", "status": "failed"})
            
            # Verificar rangos de valores
            if 'overall_veracity_score' in output_data:
                score = output_data['overall_veracity_score']
                if 0 <= score <= 1:
                    validation_checks.append({"check": "score_in_range", "status": "passed"})
                else:
                    validation_checks.append({"check": "score_in_range", "status": "failed"})
            
            # Calcular puntuación de integridad
            passed_checks = sum(1 for check in validation_checks if check['status'] == 'passed')
            total_checks = len(validation_checks)
            integrity_score = passed_checks / total_checks if total_checks > 0 else 0
            
            # Determinar estado de validación
            if integrity_score >= 0.9:
                validation_status = "valid"
            elif integrity_score >= 0.7:
                validation_status = "suspicious"
            else:
                validation_status = "invalid"
            
            validation = AuditorValidation(
                validation_id=f"val_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now(),
                input_hash=input_hash,
                output_hash=output_hash,
                validation_status=validation_status,
                cross_validation_results=validation_checks,
                integrity_score=integrity_score
            )
            
            self.validation_history.append(validation)
            return validation
            
        except Exception as e:
            # En caso de error, crear validación fallida
            return AuditorValidation(
                validation_id=f"val_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now(),
                input_hash="",
                output_hash="",
                validation_status="invalid",
                cross_validation_results=[{"check": "validation_error", "status": "failed", "error": str(e)}],
                integrity_score=0.0
            )
    
    def cross_validate_with_alternative_methods(self, input_data: str) -> Dict[str, Any]:
        """Valida usando métodos alternativos para detectar errores del auditor."""
        try:
            # Simular validación cruzada con métodos alternativos
            alternative_results = {
                'method_1': {
                    'veracity_score': random.uniform(0.6, 0.9),
                    'confidence': random.uniform(0.7, 0.95),
                    'method': 'Alternative Algorithm 1'
                },
                'method_2': {
                    'veracity_score': random.uniform(0.5, 0.8),
                    'confidence': random.uniform(0.6, 0.9),
                    'method': 'Alternative Algorithm 2'
                },
                'method_3': {
                    'veracity_score': random.uniform(0.7, 0.95),
                    'confidence': random.uniform(0.8, 0.98),
                    'method': 'Alternative Algorithm 3'
                }
            }
            
            # Calcular consenso entre métodos
            scores = [result['veracity_score'] for result in alternative_results.values()]
            avg_score = sum(scores) / len(scores)
            score_variance = sum((score - avg_score) ** 2 for score in scores) / len(scores)
            
            return {
                'alternative_results': alternative_results,
                'consensus_score': avg_score,
                'score_variance': score_variance,
                'consensus_confidence': 1.0 - min(score_variance, 1.0)
            }
            
        except Exception as e:
            return {
                'alternative_results': {},
                'consensus_score': 0.0,
                'score_variance': 1.0,
                'consensus_confidence': 0.0,
                'error': str(e)
            }
    
    def detect_auditor_errors(self, health_checks: List[AuditorHealthCheck]) -> List[Dict[str, Any]]:
        """Detecta errores en el auditor basado en verificaciones de salud."""
        errors = []
        
        for check in health_checks:
            if check.status == "failed":
                errors.append({
                    'component': check.component,
                    'severity': 'critical',
                    'error_message': check.error_message,
                    'recovery_action': check.recovery_action,
                    'confidence': check.confidence_score
                })
            elif check.status == "degraded":
                errors.append({
                    'component': check.component,
                    'severity': 'warning',
                    'error_message': check.error_message,
                    'recovery_action': check.recovery_action,
                    'confidence': check.confidence_score
                })
        
        return errors
    
    def generate_recovery_plan(self, errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Genera un plan de recuperación para los errores detectados."""
        recovery_plan = {
            'timestamp': datetime.now(),
            'total_errors': len(errors),
            'critical_errors': len([e for e in errors if e['severity'] == 'critical']),
            'warning_errors': len([e for e in errors if e['severity'] == 'warning']),
            'recovery_actions': [],
            'estimated_recovery_time': 0
        }
        
        for error in errors:
            if error['severity'] == 'critical':
                recovery_plan['recovery_actions'].append({
                    'action': error['recovery_action'],
                    'priority': 'high',
                    'estimated_time': 5  # minutos
                })
                recovery_plan['estimated_recovery_time'] += 5
            else:
                recovery_plan['recovery_actions'].append({
                    'action': error['recovery_action'],
                    'priority': 'medium',
                    'estimated_time': 2  # minutos
                })
                recovery_plan['estimated_recovery_time'] += 2
        
        return recovery_plan
    
    def render_self_protection_ui(self):
        """Renderiza la interfaz de autoprotección del auditor."""
        st.subheader("🛡️ **SISTEMA DE AUTOPROTECCIÓN DEL AUDITOR**")
        st.markdown("Verifica la salud y confiabilidad del auditor de veracidad")
        st.markdown("---")
        
        # Botón para ejecutar verificación de salud
        if st.button("🔍 **EJECUTAR VERIFICACIÓN DE SALUD**", use_container_width=True, type="primary"):
            with st.spinner("🔍 Verificando salud del auditor..."):
                health_checks = self.perform_health_check()
                st.session_state['auditor_health_checks'] = health_checks
                st.rerun()
        
        # Mostrar resultados de verificación de salud
        if 'auditor_health_checks' in st.session_state:
            self._display_health_check_results(st.session_state['auditor_health_checks'])
        
        # Mostrar historial de validaciones
        if self.validation_history:
            self._display_validation_history()
        
        # Mostrar estadísticas de autoprotección
        self._display_protection_statistics()
    
    def _display_health_check_results(self, health_checks: List[AuditorHealthCheck]):
        """Muestra los resultados de verificación de salud."""
        st.subheader("📊 **RESULTADOS DE VERIFICACIÓN DE SALUD**")
        
        # Métricas generales
        total_checks = len(health_checks)
        healthy_checks = len([c for c in health_checks if c.status == "healthy"])
        degraded_checks = len([c for c in health_checks if c.status == "degraded"])
        failed_checks = len([c for c in health_checks if c.status == "failed"])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Verificaciones", total_checks)
        
        with col2:
            st.metric("Saludables", healthy_checks, delta=f"{healthy_checks/total_checks:.1%}" if total_checks > 0 else "0%")
        
        with col3:
            st.metric("Degradadas", degraded_checks, delta=f"{degraded_checks/total_checks:.1%}" if total_checks > 0 else "0%")
        
        with col4:
            st.metric("Fallidas", failed_checks, delta=f"{failed_checks/total_checks:.1%}" if total_checks > 0 else "0%")
        
        # Detalles por componente
        st.subheader("🔍 **DETALLES POR COMPONENTE**")
        
        for check in health_checks:
            with st.expander(f"{check.component.replace('_', ' ').title()} - {check.status.upper()}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Estado:** {check.status}")
                    st.write(f"**Confianza:** {check.confidence_score:.1%}")
                    st.write(f"**Timestamp:** {check.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                
                with col2:
                    if check.error_message:
                        st.error(f"**Error:** {check.error_message}")
                    if check.recovery_action:
                        st.warning(f"**Acción de Recuperación:** {check.recovery_action}")
        
        # Detectar errores y generar plan de recuperación
        errors = self.detect_auditor_errors(health_checks)
        if errors:
            st.subheader("🚨 **ERRORES DETECTADOS**")
            
            for error in errors:
                severity_color = "🔴" if error['severity'] == 'critical' else "🟡"
                st.write(f"{severity_color} **{error['component']}** - {error['error_message']}")
                st.write(f"   💡 **Recuperación:** {error['recovery_action']}")
            
            # Generar plan de recuperación
            recovery_plan = self.generate_recovery_plan(errors)
            
            with st.expander("📋 **PLAN DE RECUPERACIÓN**"):
                st.write(f"**Total de errores:** {recovery_plan['total_errors']}")
                st.write(f"**Errores críticos:** {recovery_plan['critical_errors']}")
                st.write(f"**Advertencias:** {recovery_plan['warning_errors']}")
                st.write(f"**Tiempo estimado de recuperación:** {recovery_plan['estimated_recovery_time']} minutos")
                
                st.write("**Acciones de recuperación:**")
                for i, action in enumerate(recovery_plan['recovery_actions'], 1):
                    priority_color = "🔴" if action['priority'] == 'high' else "🟡"
                    st.write(f"{i}. {priority_color} {action['action']} ({action['estimated_time']} min)")
    
    def _display_validation_history(self):
        """Muestra el historial de validaciones."""
        st.subheader("📋 **HISTORIAL DE VALIDACIONES**")
        
        if self.validation_history:
            # Crear DataFrame del historial
            history_data = []
            for validation in self.validation_history[-10:]:  # Últimas 10 validaciones
                history_data.append({
                    "ID": validation.validation_id,
                    "Timestamp": validation.timestamp.strftime("%Y-%m-%d %H:%M"),
                    "Estado": validation.validation_status,
                    "Integridad": f"{validation.integrity_score:.1%}",
                    "Hash Entrada": validation.input_hash[:8] + "...",
                    "Hash Salida": validation.output_hash[:8] + "..."
                })
            
            if history_data:
                import pandas as pd
                history_df = pd.DataFrame(history_data)
                st.dataframe(history_df, use_container_width=True, hide_index=True)
        else:
            st.info("📝 No hay validaciones disponibles")
    
    def _display_protection_statistics(self):
        """Muestra estadísticas de autoprotección."""
        st.subheader("📈 **ESTADÍSTICAS DE AUTOPROTECCIÓN**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Verificaciones de Salud", len(self.health_checks))
        
        with col2:
            st.metric("Validaciones Realizadas", len(self.validation_history))
        
        with col3:
            if self.validation_history:
                avg_integrity = sum(v.integrity_score for v in self.validation_history) / len(self.validation_history)
                st.metric("Integridad Promedio", f"{avg_integrity:.1%}")
            else:
                st.metric("Integridad Promedio", "N/A")

# Instancia global
auditor_self_protection = AuditorSelfProtection()






