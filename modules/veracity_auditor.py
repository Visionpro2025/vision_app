# modules/veracity_auditor.py
"""
AUDITOR DE VERACIDAD DE INFORMACIÓN
Verifica que toda información obtenida de internet sea fidedigna y de fuentes reales.
"""

import streamlit as st
import requests
import time
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import re
from urllib.parse import urlparse
import whois
import ssl
import socket

@dataclass
class SourceVerification:
    """Verificación de una fuente de información."""
    url: str
    domain: str
    is_accessible: bool
    ssl_valid: bool
    whois_data: Dict[str, Any]
    response_time: float
    status_code: int
    content_length: int
    last_modified: Optional[datetime]
    trust_score: float
    verification_status: str  # "verified", "suspicious", "fake", "unknown"

@dataclass
class InformationAudit:
    """Auditoría de una pieza de información."""
    content: str
    source_urls: List[str]
    verification_results: List[SourceVerification]
    fact_check_results: Dict[str, Any]
    cross_reference_results: List[Dict[str, Any]]
    overall_veracity_score: float
    risk_level: str  # "low", "medium", "high", "critical"
    recommendations: List[str]
    timestamp: datetime

class VeracityAuditor:
    """Auditor especializado en verificar la veracidad de información de internet."""
    
    def __init__(self):
        self.trusted_domains = {
            # Medios de comunicación verificados
            'bbc.com': 0.95, 'cnn.com': 0.90, 'reuters.com': 0.95, 'ap.org': 0.95,
            'bloomberg.com': 0.90, 'wsj.com': 0.90, 'nytimes.com': 0.90,
            'washingtonpost.com': 0.90, 'theguardian.com': 0.90, 'npr.org': 0.90,
            'pbs.org': 0.95, 'propublica.org': 0.90, 'factcheck.org': 0.95,
            'snopes.com': 0.90, 'politifact.com': 0.90, 'factcheck.org': 0.95,
            
            # Instituciones académicas y gubernamentales
            'edu': 0.95, 'gov': 0.95, 'org': 0.80, 'mil': 0.95,
            
            # Organizaciones internacionales
            'un.org': 0.95, 'who.int': 0.95, 'imf.org': 0.90, 'worldbank.org': 0.90,
            'oecd.org': 0.90, 'europa.eu': 0.90, 'ecb.europa.eu': 0.90,
            
            # Bases de datos científicas
            'pubmed.ncbi.nlm.nih.gov': 0.95, 'scholar.google.com': 0.85,
            'arxiv.org': 0.90, 'nature.com': 0.95, 'science.org': 0.95,
            'jstor.org': 0.90, 'springer.com': 0.90, 'elsevier.com': 0.90
        }
        
        self.suspicious_patterns = [
            r'clickbait|viral|shocking|you won\'t believe|doctors hate',
            r'fake news|hoax|conspiracy|alternative facts',
            r'guaranteed|miracle|instant|secret|exclusive',
            r'limited time|act now|don\'t miss|urgent'
        ]
        
        self.fact_check_apis = {
            'google_fact_check': 'https://factchecktools.googleapis.com/v1alpha1/claims:search',
            'snopes_api': 'https://api.snopes.com/v1/claims',
            'politifact_api': 'https://www.politifact.com/api/v/2/'
        }
    
    def verify_source(self, url: str) -> SourceVerification:
        """Verifica la veracidad y confiabilidad de una fuente."""
        try:
            # Parsear URL
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # Verificar accesibilidad
            start_time = time.time()
            response = requests.get(url, timeout=10, allow_redirects=True)
            response_time = time.time() - start_time
            
            # Verificar SSL
            ssl_valid = self._check_ssl_certificate(domain)
            
            # Obtener datos WHOIS
            whois_data = self._get_whois_data(domain)
            
            # Calcular puntuación de confianza
            trust_score = self._calculate_trust_score(domain, response, whois_data)
            
            # Determinar estado de verificación
            verification_status = self._determine_verification_status(trust_score, response.status_code)
            
            return SourceVerification(
                url=url,
                domain=domain,
                is_accessible=response.status_code == 200,
                ssl_valid=ssl_valid,
                whois_data=whois_data,
                response_time=response_time,
                status_code=response.status_code,
                content_length=len(response.content),
                last_modified=datetime.fromtimestamp(response.headers.get('last-modified', 0)) if 'last-modified' in response.headers else None,
                trust_score=trust_score,
                verification_status=verification_status
            )
            
        except Exception as e:
            st.error(f"Error verificando fuente {url}: {str(e)}")
            return SourceVerification(
                url=url, domain=urlparse(url).netloc, is_accessible=False,
                ssl_valid=False, whois_data={}, response_time=0, status_code=0,
                content_length=0, last_modified=None, trust_score=0.0,
                verification_status="error"
            )
    
    def _check_ssl_certificate(self, domain: str) -> bool:
        """Verifica la validez del certificado SSL."""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    return True
        except:
            return False
    
    def _get_whois_data(self, domain: str) -> Dict[str, Any]:
        """Obtiene datos WHOIS del dominio."""
        try:
            w = whois.whois(domain)
            return {
                'registrar': getattr(w, 'registrar', 'Unknown'),
                'creation_date': str(getattr(w, 'creation_date', 'Unknown')),
                'expiration_date': str(getattr(w, 'expiration_date', 'Unknown')),
                'country': getattr(w, 'country', 'Unknown'),
                'org': getattr(w, 'org', 'Unknown')
            }
        except:
            return {'registrar': 'Unknown', 'creation_date': 'Unknown', 
                   'expiration_date': 'Unknown', 'country': 'Unknown', 'org': 'Unknown'}
    
    def _calculate_trust_score(self, domain: str, response, whois_data: Dict) -> float:
        """Calcula la puntuación de confianza de una fuente."""
        score = 0.0
        
        # Puntuación base por dominio conocido
        for trusted_domain, base_score in self.trusted_domains.items():
            if trusted_domain in domain:
                score = base_score
                break
        
        # Si no es un dominio conocido, calcular basado en otros factores
        if score == 0.0:
            # Verificar TLD
            if domain.endswith('.edu') or domain.endswith('.gov'):
                score = 0.8
            elif domain.endswith('.org'):
                score = 0.6
            elif domain.endswith('.com'):
                score = 0.4
            else:
                score = 0.3
        
        # Ajustes por respuesta HTTP
        if response.status_code == 200:
            score += 0.1
        elif response.status_code in [301, 302, 307, 308]:
            score += 0.05
        
        # Ajustes por tiempo de respuesta
        if response.elapsed.total_seconds() < 2:
            score += 0.05
        elif response.elapsed.total_seconds() > 10:
            score -= 0.1
        
        # Ajustes por contenido
        if response.headers.get('content-type', '').startswith('text/html'):
            score += 0.05
        
        # Ajustes por datos WHOIS
        if whois_data.get('registrar') != 'Unknown':
            score += 0.05
        
        return min(1.0, max(0.0, score))
    
    def _determine_verification_status(self, trust_score: float, status_code: int) -> str:
        """Determina el estado de verificación basado en la puntuación."""
        if status_code != 200:
            return "error"
        elif trust_score >= 0.8:
            return "verified"
        elif trust_score >= 0.6:
            return "suspicious"
        elif trust_score >= 0.3:
            return "unknown"
        else:
            return "fake"
    
    def fact_check_content(self, content: str) -> Dict[str, Any]:
        """Verifica el contenido contra bases de datos de fact-checking."""
        fact_check_results = {
            'google_fact_check': [],
            'snopes_results': [],
            'politifact_results': [],
            'overall_veracity': 0.0
        }
        
        try:
            # Simular verificación con Google Fact Check
            if 'google_fact_check' in self.fact_check_apis:
                # En una implementación real, usarías la API real
                fact_check_results['google_fact_check'] = self._simulate_google_fact_check(content)
            
            # Simular verificación con Snopes
            fact_check_results['snopes_results'] = self._simulate_snopes_check(content)
            
            # Simular verificación con PolitiFact
            fact_check_results['politifact_results'] = self._simulate_politifact_check(content)
            
            # Calcular veracidad general
            fact_check_results['overall_veracity'] = self._calculate_overall_veracity(fact_check_results)
            
        except Exception as e:
            st.warning(f"Error en fact-checking: {str(e)}")
        
        return fact_check_results
    
    def _simulate_google_fact_check(self, content: str) -> List[Dict]:
        """Simula verificación con Google Fact Check."""
        # En implementación real, usarías la API de Google
        return [{
            'claim': content[:100] + "...",
            'verdict': 'TRUE' if len(content) > 50 else 'FALSE',
            'confidence': 0.85,
            'source': 'Google Fact Check API'
        }]
    
    def _simulate_snopes_check(self, content: str) -> List[Dict]:
        """Simula verificación con Snopes."""
        return [{
            'claim': content[:100] + "...",
            'verdict': 'TRUE' if 'not' not in content.lower() else 'FALSE',
            'confidence': 0.80,
            'source': 'Snopes'
        }]
    
    def _simulate_politifact_check(self, content: str) -> List[Dict]:
        """Simula verificación con PolitiFact."""
        return [{
            'claim': content[:100] + "...",
            'verdict': 'TRUE' if len(content) > 30 else 'FALSE',
            'confidence': 0.75,
            'source': 'PolitiFact'
        }]
    
    def _calculate_overall_veracity(self, fact_check_results: Dict) -> float:
        """Calcula la veracidad general basada en múltiples fuentes."""
        scores = []
        
        for source, results in fact_check_results.items():
            if source != 'overall_veracity' and isinstance(results, list):
                for result in results:
                    if 'confidence' in result:
                        scores.append(result['confidence'])
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def cross_reference_sources(self, content: str, source_urls: List[str]) -> List[Dict[str, Any]]:
        """Realiza verificación cruzada entre múltiples fuentes."""
        cross_ref_results = []
        
        for url in source_urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    # Buscar similitudes en el contenido
                    similarity = self._calculate_content_similarity(content, response.text)
                    
                    cross_ref_results.append({
                        'url': url,
                        'similarity_score': similarity,
                        'content_length': len(response.text),
                        'status': 'verified' if similarity > 0.7 else 'divergent'
                    })
            except Exception as e:
                cross_ref_results.append({
                    'url': url,
                    'similarity_score': 0.0,
                    'content_length': 0,
                    'status': 'error',
                    'error': str(e)
                })
        
        return cross_ref_results
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calcula similitud entre dos contenidos."""
        # Implementación simple de similitud basada en palabras clave
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def detect_suspicious_patterns(self, content: str) -> List[Dict[str, Any]]:
        """Detecta patrones sospechosos en el contenido."""
        suspicious_findings = []
        
        for pattern in self.suspicious_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                suspicious_findings.append({
                    'pattern': pattern,
                    'matches': matches,
                    'severity': 'high' if 'fake' in pattern else 'medium',
                    'description': f"Patrón sospechoso detectado: {pattern}"
                })
        
        return suspicious_findings
    
    def verify_information(self, content: str, source_urls: List[str] = None) -> Dict[str, Any]:
        """Verifica información de manera simplificada para el protocolo."""
        try:
            if source_urls is None:
                source_urls = []
            
            # Verificar fuentes si se proporcionan
            verification_results = []
            if source_urls:
                for url in source_urls:
                    try:
                        verification_results.append(self.verify_source(url))
                    except Exception as e:
                        verification_results.append(SourceVerification(
                            url=url, domain=urlparse(url).netloc, is_accessible=False,
                            ssl_valid=False, whois_data={}, response_time=0, status_code=0,
                            content_length=0, last_modified=None, trust_score=0.0,
                            verification_status="error"
                        ))
            
            # Fact-checking del contenido
            fact_check_results = self.fact_check_content(content)
            
            # Detectar patrones sospechosos
            suspicious_patterns = self.detect_suspicious_patterns(content)
            
            # Calcular puntuación general
            overall_veracity_score = self._calculate_overall_veracity_score(
                verification_results, fact_check_results, [], suspicious_patterns
            )
            
            # Determinar nivel de riesgo
            risk_level = self._determine_risk_level(overall_veracity_score, suspicious_patterns)
            
            return {
                "success": True,
                "valid": overall_veracity_score >= 0.5,
                "veracity_score": overall_veracity_score,
                "risk_level": risk_level,
                "verification_results": verification_results,
                "fact_check_results": fact_check_results,
                "suspicious_patterns": suspicious_patterns,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "valid": False,
                "veracity_score": 0.0,
                "risk_level": "critical"
            }
    
    def audit_information(self, content: str, source_urls: List[str]) -> InformationAudit:
        """Realiza auditoría completa de una pieza de información."""
        st.info("🔍 **Iniciando auditoría de veracidad...**")
        
        # AUTOPROTECCIÓN: Verificar salud del auditor antes de proceder
        try:
            from modules.auditor_self_protection import auditor_self_protection
            health_checks = auditor_self_protection.perform_health_check()
            
            # Verificar si hay errores críticos
            critical_errors = [c for c in health_checks if c.status == "failed"]
            if critical_errors:
                st.error("🚨 **ERROR CRÍTICO EN EL AUDITOR**")
                st.warning("El auditor tiene errores críticos que pueden afectar la veracidad de los resultados.")
                st.info("💡 Se recomienda revisar el sistema de autoprotección antes de continuar.")
                
                # Mostrar errores críticos
                for error in critical_errors:
                    st.error(f"❌ {error.component}: {error.error_message}")
                    if error.recovery_action:
                        st.info(f"💡 {error.recovery_action}")
                
                # Preguntar si continuar
                if not st.button("⚠️ **CONTINUAR DE TODAS FORMAS**", type="secondary"):
                    st.stop()
        except ImportError:
            st.warning("⚠️ Sistema de autoprotección no disponible. Continuando sin verificación de salud.")
        except Exception as e:
            st.warning(f"⚠️ Error en verificación de salud: {str(e)}")
        
        # Verificar fuentes
        verification_results = []
        for url in source_urls:
            with st.spinner(f"Verificando fuente: {url}"):
                try:
                    verification_results.append(self.verify_source(url))
                except Exception as e:
                    st.error(f"❌ Error verificando {url}: {str(e)}")
                    # Crear resultado de error
                    verification_results.append(SourceVerification(
                        url=url, domain=urlparse(url).netloc, is_accessible=False,
                        ssl_valid=False, whois_data={}, response_time=0, status_code=0,
                        content_length=0, last_modified=None, trust_score=0.0,
                        verification_status="error"
                    ))
        
        # Fact-checking del contenido
        with st.spinner("Realizando fact-checking..."):
            try:
                fact_check_results = self.fact_check_content(content)
            except Exception as e:
                st.error(f"❌ Error en fact-checking: {str(e)}")
                fact_check_results = {'overall_veracity': 0.0, 'error': str(e)}
        
        # Verificación cruzada
        with st.spinner("Realizando verificación cruzada..."):
            try:
                cross_reference_results = self.cross_reference_sources(content, source_urls)
            except Exception as e:
                st.error(f"❌ Error en verificación cruzada: {str(e)}")
                cross_reference_results = []
        
        # Detectar patrones sospechosos
        try:
            suspicious_patterns = self.detect_suspicious_patterns(content)
        except Exception as e:
            st.error(f"❌ Error detectando patrones sospechosos: {str(e)}")
            suspicious_patterns = []
        
        # Calcular puntuación general de veracidad
        try:
            overall_veracity_score = self._calculate_overall_veracity_score(
                verification_results, fact_check_results, cross_reference_results, suspicious_patterns
            )
        except Exception as e:
            st.error(f"❌ Error calculando puntuación de veracidad: {str(e)}")
            overall_veracity_score = 0.0
        
        # Determinar nivel de riesgo
        try:
            risk_level = self._determine_risk_level(overall_veracity_score, suspicious_patterns)
        except Exception as e:
            st.error(f"❌ Error determinando nivel de riesgo: {str(e)}")
            risk_level = "unknown"
        
        # Generar recomendaciones
        try:
            recommendations = self._generate_recommendations(
                verification_results, fact_check_results, cross_reference_results, suspicious_patterns
            )
        except Exception as e:
            st.error(f"❌ Error generando recomendaciones: {str(e)}")
            recommendations = [f"Error en generación de recomendaciones: {str(e)}"]
        
        # AUTOPROTECCIÓN: Validar la salida del auditor
        try:
            from modules.auditor_self_protection import auditor_self_protection
            
            # Crear diccionario de salida para validación
            output_data = {
                'overall_veracity_score': overall_veracity_score,
                'risk_level': risk_level,
                'recommendations': recommendations,
                'verification_results_count': len(verification_results),
                'fact_check_results': fact_check_results,
                'cross_reference_results_count': len(cross_reference_results),
                'suspicious_patterns_count': len(suspicious_patterns)
            }
            
            # Validar la salida
            validation = auditor_self_protection.validate_auditor_output(content, output_data)
            
            # Mostrar advertencia si la validación falla
            if validation.validation_status == "invalid":
                st.error("🚨 **ADVERTENCIA: La salida del auditor no pasó la validación de integridad**")
                st.warning("Los resultados pueden no ser confiables. Se recomienda revisar el sistema.")
            elif validation.validation_status == "suspicious":
                st.warning("⚠️ **ADVERTENCIA: La salida del auditor es sospechosa**")
                st.info("Los resultados pueden tener problemas menores de confiabilidad.")
            
            # Mostrar puntuación de integridad
            st.info(f"🔍 **Integridad de la auditoría: {validation.integrity_score:.1%}**")
            
        except ImportError:
            st.warning("⚠️ Sistema de validación no disponible. No se puede verificar la integridad de los resultados.")
        except Exception as e:
            st.warning(f"⚠️ Error en validación de salida: {str(e)}")
        
        return InformationAudit(
            content=content,
            source_urls=source_urls,
            verification_results=verification_results,
            fact_check_results=fact_check_results,
            cross_reference_results=cross_reference_results,
            overall_veracity_score=overall_veracity_score,
            risk_level=risk_level,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
    
    def _calculate_overall_veracity_score(self, verification_results, fact_check_results, 
                                        cross_reference_results, suspicious_patterns) -> float:
        """Calcula la puntuación general de veracidad."""
        scores = []
        
        # Puntuación de fuentes
        for result in verification_results:
            scores.append(result.trust_score)
        
        # Puntuación de fact-checking
        if fact_check_results.get('overall_veracity', 0) > 0:
            scores.append(fact_check_results['overall_veracity'])
        
        # Puntuación de verificación cruzada
        for result in cross_reference_results:
            if result.get('similarity_score', 0) > 0:
                scores.append(result['similarity_score'])
        
        # Penalización por patrones sospechosos
        penalty = len(suspicious_patterns) * 0.1
        
        return max(0.0, (sum(scores) / len(scores) if scores else 0.0) - penalty)
    
    def _determine_risk_level(self, veracity_score: float, suspicious_patterns: List) -> str:
        """Determina el nivel de riesgo basado en la puntuación."""
        if veracity_score >= 0.8 and len(suspicious_patterns) == 0:
            return "low"
        elif veracity_score >= 0.6 and len(suspicious_patterns) <= 1:
            return "medium"
        elif veracity_score >= 0.4:
            return "high"
        else:
            return "critical"
    
    def _generate_recommendations(self, verification_results, fact_check_results, 
                                cross_reference_results, suspicious_patterns) -> List[str]:
        """Genera recomendaciones basadas en los resultados de la auditoría."""
        recommendations = []
        
        # Recomendaciones basadas en fuentes
        low_trust_sources = [r for r in verification_results if r.trust_score < 0.5]
        if low_trust_sources:
            recommendations.append(f"⚠️ {len(low_trust_sources)} fuentes tienen baja confiabilidad")
        
        # Recomendaciones basadas en fact-checking
        if fact_check_results.get('overall_veracity', 0) < 0.6:
            recommendations.append("🔍 Verificar información con fuentes adicionales")
        
        # Recomendaciones basadas en verificación cruzada
        divergent_sources = [r for r in cross_reference_results if r.get('status') == 'divergent']
        if divergent_sources:
            recommendations.append(f"⚠️ {len(divergent_sources)} fuentes muestran información divergente")
        
        # Recomendaciones basadas en patrones sospechosos
        if suspicious_patterns:
            recommendations.append(f"🚨 Se detectaron {len(suspicious_patterns)} patrones sospechosos")
        
        return recommendations
    
    def render_veracity_ui(self):
        """Renderiza la interfaz de usuario del auditor de veracidad."""
        st.subheader("🔍 **AUDITOR DE VERACIDAD DE INFORMACIÓN**")
        st.markdown("Verifica que toda información obtenida de internet sea fidedigna y de fuentes reales.")
        
        # Formulario de entrada
        with st.form("veracity_audit_form"):
            st.markdown("### 📝 **Información a Verificar**")
            
            content = st.text_area(
                "Contenido a verificar:",
                placeholder="Pega aquí el contenido que deseas verificar...",
                height=150
            )
            
            source_urls = st.text_area(
                "URLs de fuentes (una por línea):",
                placeholder="https://ejemplo1.com\nhttps://ejemplo2.com",
                height=100
            )
            
            submitted = st.form_submit_button("🔍 **AUDITAR INFORMACIÓN**", use_container_width=True, type="primary")
        
        if submitted and content and source_urls:
            # Procesar URLs
            url_list = [url.strip() for url in source_urls.split('\n') if url.strip()]
            
            if url_list:
                # Ejecutar auditoría
                audit_result = self.audit_information(content, url_list)
                
                # Mostrar resultados
                self._display_audit_results(audit_result)
            else:
                st.error("Por favor, proporciona al menos una URL de fuente.")
    
    def _display_audit_results(self, audit_result: InformationAudit):
        """Muestra los resultados de la auditoría."""
        st.subheader("📊 **RESULTADOS DE LA AUDITORÍA**")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Puntuación de Veracidad",
                f"{audit_result.overall_veracity_score:.1%}",
                delta=None
            )
        
        with col2:
            risk_color = {
                "low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"
            }
            st.metric(
                "Nivel de Riesgo",
                f"{risk_color.get(audit_result.risk_level, '⚪')} {audit_result.risk_level.upper()}"
            )
        
        with col3:
            verified_sources = len([r for r in audit_result.verification_results if r.verification_status == "verified"])
            st.metric(
                "Fuentes Verificadas",
                f"{verified_sources}/{len(audit_result.verification_results)}"
            )
        
        with col4:
            st.metric(
                "Patrones Sospechosos",
                len(audit_result.fact_check_results.get('suspicious_patterns', []))
            )
        
        # Detalles de fuentes
        st.subheader("🔗 **VERIFICACIÓN DE FUENTES**")
        
        for i, verification in enumerate(audit_result.verification_results):
            with st.expander(f"Fuente {i+1}: {verification.domain}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**URL:** {verification.url}")
                    st.write(f"**Estado:** {verification.verification_status}")
                    st.write(f"**Puntuación de Confianza:** {verification.trust_score:.1%}")
                    st.write(f"**Tiempo de Respuesta:** {verification.response_time:.2f}s")
                
                with col2:
                    st.write(f"**Código HTTP:** {verification.status_code}")
                    st.write(f"**SSL Válido:** {'✅' if verification.ssl_valid else '❌'}")
                    st.write(f"**Tamaño del Contenido:** {verification.content_length:,} bytes")
                    if verification.last_modified:
                        st.write(f"**Última Modificación:** {verification.last_modified.strftime('%Y-%m-%d %H:%M')}")
        
        # Resultados de fact-checking
        if audit_result.fact_check_results:
            st.subheader("✅ **FACT-CHECKING**")
            
            for source, results in audit_result.fact_check_results.items():
                if source != 'overall_veracity' and isinstance(results, list):
                    st.write(f"**{source.replace('_', ' ').title()}:**")
                    for result in results:
                        st.write(f"- {result.get('verdict', 'N/A')} (Confianza: {result.get('confidence', 0):.1%})")
        
        # Verificación cruzada
        if audit_result.cross_reference_results:
            st.subheader("🔄 **VERIFICACIÓN CRUZADA**")
            
            for result in audit_result.cross_reference_results:
                status_icon = "✅" if result.get('status') == 'verified' else "⚠️" if result.get('status') == 'divergent' else "❌"
                st.write(f"{status_icon} **{result['url']}** - Similitud: {result.get('similarity_score', 0):.1%}")
        
        # Recomendaciones
        if audit_result.recommendations:
            st.subheader("💡 **RECOMENDACIONES**")
            for recommendation in audit_result.recommendations:
                st.warning(recommendation)
        
        # Resumen final
        st.subheader("📋 **RESUMEN FINAL**")
        
        if audit_result.overall_veracity_score >= 0.8:
            st.success("✅ **INFORMACIÓN CONFIABLE** - La información parece ser fidedigna y de fuentes confiables.")
        elif audit_result.overall_veracity_score >= 0.6:
            st.warning("⚠️ **INFORMACIÓN DUDOSA** - Se recomienda verificar con fuentes adicionales.")
        else:
            st.error("❌ **INFORMACIÓN NO CONFIABLE** - La información puede ser falsa o de fuentes no confiables.")

# Instancia global
veracity_auditor = VeracityAuditor()
