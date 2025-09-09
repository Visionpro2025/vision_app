# ============================================
# 📌 MÓDULO DE VERIFICACIÓN DE CONTENIDO AVANZADA
# Detecta información ilegítima, falsa y generada por IA
# ============================================

from __future__ import annotations
import re, hashlib, json
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class ContentVerificationResult:
    is_legitimate: bool
    confidence_score: float
    verification_reasons: List[str]
    ai_detection: bool
    temporal_coherence: bool
    metadata_integrity: bool
    source_reliability: float

class ContentVerificationEngine:
    """
    Motor de verificación de contenido que detecta:
    - Contenido generado por IA
    - Información falsa o inventada
    - Inconsistencias temporales
    - Metadatos corruptos o faltantes
    - Fuentes no confiables
    """
    
    def __init__(self):
        # Patrones de contenido generado por IA
        self.ai_patterns = [
            r"as an ai", r"i cannot", r"i don't have access",
            r"based on my training", r"i'm not able to",
            r"i don't have real-time", r"i cannot provide",
            r"as a language model", r"i don't have the ability",
            r"i cannot generate", r"i cannot create",
            r"i don't have personal", r"i cannot access",
            r"i don't have specific", r"i cannot verify",
            r"i don't have current", r"i cannot confirm"
        ]
        
        # Patrones de contenido sospechoso
        self.suspicious_patterns = [
            r"according to sources", r"unconfirmed reports",
            r"rumors suggest", r"it is believed",
            r"some say", r"allegedly",
            r"supposedly", r"reportedly",
            r"it has been said", r"word has it"
        ]
        
        # Patrones de contenido inventado
        self.fabricated_patterns = [
            r"breaking news", r"exclusive report",
            r"insider sources", r"confidential information",
            r"leaked documents", r"anonymous sources",
            r"undisclosed sources", r"reliable sources"
        ]
    
    def detect_ai_generated_content(self, text: str) -> Tuple[bool, float, List[str]]:
        """
        Detecta si el contenido fue generado por IA.
        
        Returns:
            (is_ai_generated, confidence, reasons)
        """
        text_lower = text.lower()
        reasons = []
        ai_hits = 0
        
        # Contar patrones de IA
        for pattern in self.ai_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                ai_hits += len(matches)
                reasons.append(f"Patrón IA detectado: '{pattern}'")
        
        # Calcular confianza
        confidence = min(ai_hits / 10.0, 1.0)  # Normalizar a 0-1
        is_ai_generated = confidence > 0.3  # Umbral de 30%
        
        return is_ai_generated, confidence, reasons
    
    def detect_suspicious_content(self, text: str) -> Tuple[bool, float, List[str]]:
        """
        Detecta contenido sospechoso o no verificado.
        
        Returns:
            (is_suspicious, confidence, reasons)
        """
        text_lower = text.lower()
        reasons = []
        suspicious_hits = 0
        
        # Contar patrones sospechosos
        for pattern in self.suspicious_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                suspicious_hits += len(matches)
                reasons.append(f"Contenido sospechoso: '{pattern}'")
        
        # Calcular confianza
        confidence = min(suspicious_hits / 5.0, 1.0)
        is_suspicious = confidence > 0.4  # Umbral de 40%
        
        return is_suspicious, confidence, reasons
    
    def detect_fabricated_content(self, text: str) -> Tuple[bool, float, List[str]]:
        """
        Detecta contenido inventado o fabricado.
        
        Returns:
            (is_fabricated, confidence, reasons)
        """
        text_lower = text.lower()
        reasons = []
        fabricated_hits = 0
        
        # Contar patrones de fabricación
        for pattern in self.fabricated_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                fabricated_hits += len(matches)
                reasons.append(f"Contenido inventado: '{pattern}'")
        
        # Calcular confianza
        confidence = min(fabricated_hits / 3.0, 1.0)
        is_fabricated = confidence > 0.5  # Umbral de 50%
        
        return is_fabricated, confidence, reasons
    
    def verify_temporal_coherence(self, articles: List[Dict[str, Any]]) -> Tuple[bool, float, List[str]]:
        """
        Verifica coherencia temporal entre artículos.
        
        Returns:
            (is_coherent, confidence, reasons)
        """
        if len(articles) < 2:
            return True, 1.0, ["Solo un artículo, coherencia temporal no aplicable"]
        
        reasons = []
        dates = []
        
        # Extraer fechas válidas
        for article in articles:
            if 'date_iso' in article and article['date_iso']:
                try:
                    date_obj = datetime.fromisoformat(article['date_iso'])
                    dates.append(date_obj)
                except:
                    reasons.append(f"Fecha inválida en artículo: {article.get('title', 'Sin título')}")
        
        if len(dates) < 2:
            return False, 0.0, ["Fechas insuficientes para verificar coherencia temporal"]
        
        # Verificar coherencia temporal
        dates.sort()
        time_span = (dates[-1] - dates[0]).days
        
        # Si el rango temporal es muy amplio, es sospechoso
        if time_span > 30:  # Más de 30 días
            reasons.append(f"Rango temporal muy amplio: {time_span} días")
            return False, 0.3, reasons
        
        # Verificar distribución temporal
        gaps = []
        for i in range(1, len(dates)):
            gap = (dates[i] - dates[i-1]).days
            gaps.append(gap)
        
        avg_gap = sum(gaps) / len(gaps) if gaps else 0
        
        if avg_gap > 7:  # Promedio de más de 7 días entre artículos
            reasons.append(f"Gap temporal promedio alto: {avg_gap:.1f} días")
            return False, 0.5, reasons
        
        return True, 0.9, ["Coherencia temporal verificada"]
    
    def verify_metadata_integrity(self, article: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
        """
        Verifica integridad de metadatos del artículo.
        
        Returns:
            (is_integrity_ok, confidence, reasons)
        """
        reasons = []
        missing_fields = []
        invalid_fields = []
        
        # Campos requeridos
        required_fields = ['title', 'date_iso', 'final_url', 'content_sha256']
        
        # Verificar campos faltantes
        for field in required_fields:
            if field not in article or not article[field]:
                missing_fields.append(field)
        
        if missing_fields:
            reasons.append(f"Campos faltantes: {', '.join(missing_fields)}")
        
        # Verificar formato de fecha
        if 'date_iso' in article and article['date_iso']:
            try:
                datetime.fromisoformat(article['date_iso'])
            except:
                invalid_fields.append('date_iso')
                reasons.append("Formato de fecha inválido")
        
        # Verificar URL válida
        if 'final_url' in article and article['final_url']:
            if not article['final_url'].startswith(('http://', 'https://')):
                invalid_fields.append('final_url')
                reasons.append("URL inválida")
        
        # Verificar SHA256
        if 'content_sha256' in article and article['content_sha256']:
            if len(article['content_sha256']) != 64:
                invalid_fields.append('content_sha256')
                reasons.append("SHA256 inválido")
        
        # Calcular confianza
        total_fields = len(required_fields)
        valid_fields = total_fields - len(missing_fields) - len(invalid_fields)
        confidence = valid_fields / total_fields
        
        is_integrity_ok = confidence >= 0.75  # 75% de campos válidos
        
        return is_integrity_ok, confidence, reasons
    
    def calculate_source_reliability(self, domain: str, article_count: int) -> float:
        """
        Calcula confiabilidad de la fuente basada en dominio y cantidad de artículos.
        
        Returns:
            reliability_score (0.0 - 1.0)
        """
        # Fuentes de alta confiabilidad
        high_reliability = {
            'bbc.com', 'reuters.com', 'apnews.com', 'nytimes.com',
            'washingtonpost.com', 'theguardian.com', 'cnn.com'
        }
        
        # Fuentes de confiabilidad media
        medium_reliability = {
            'elpais.com', 'infobae.com', 'bloomberg.com',
            '14ymedio.com', 'cibercuba.com', 'americateve.com'
        }
        
        if domain in high_reliability:
            base_score = 0.9
        elif domain in medium_reliability:
            base_score = 0.7
        else:
            base_score = 0.5
        
        # Ajustar por cantidad de artículos (más artículos = más confiable)
        article_bonus = min(article_count / 10.0, 0.1)  # Máximo 10% de bonus
        
        return min(base_score + article_bonus, 1.0)
    
    def verify_content(self, articles: List[Dict[str, Any]]) -> List[ContentVerificationResult]:
        """
        Verifica contenido completo de una lista de artículos.
        
        Returns:
            Lista de resultados de verificación
        """
        results = []
        
        for article in articles:
            text = f"{article.get('title', '')} {article.get('text', '')}"
            domain = article.get('domain', '')
            
            # Detectar IA
            is_ai, ai_confidence, ai_reasons = self.detect_ai_generated_content(text)
            
            # Detectar sospechoso
            is_suspicious, suspicious_confidence, suspicious_reasons = self.detect_suspicious_content(text)
            
            # Detectar fabricado
            is_fabricated, fabricated_confidence, fabricated_reasons = self.detect_fabricated_content(text)
            
            # Verificar metadatos
            is_metadata_ok, metadata_confidence, metadata_reasons = self.verify_metadata_integrity(article)
            
            # Calcular confiabilidad de fuente
            source_reliability = self.calculate_source_reliability(domain, len(articles))
            
            # Verificar coherencia temporal (se hace sobre toda la lista)
            is_temporal_ok, temporal_confidence, temporal_reasons = self.verify_temporal_coherence(articles)
            
            # Combinar todas las razones
            all_reasons = ai_reasons + suspicious_reasons + fabricated_reasons + metadata_reasons + temporal_reasons
            
            # Calcular score final
            final_confidence = (
                (1.0 - ai_confidence) * 0.3 +
                (1.0 - suspicious_confidence) * 0.2 +
                (1.0 - fabricated_confidence) * 0.2 +
                metadata_confidence * 0.15 +
                temporal_confidence * 0.1 +
                source_reliability * 0.05
            )
            
            # Determinar si es legítimo
            is_legitimate = (
                not is_ai and
                not is_fabricated and
                is_metadata_ok and
                final_confidence > 0.6
            )
            
            result = ContentVerificationResult(
                is_legitimate=is_legitimate,
                confidence_score=final_confidence,
                verification_reasons=all_reasons,
                ai_detection=is_ai,
                temporal_coherence=is_temporal_ok,
                metadata_integrity=is_metadata_ok,
                source_reliability=source_reliability
            )
            
            results.append(result)
        
        return results



