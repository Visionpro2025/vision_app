#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enriquecedor de noticias usando léxicos del corpus de VISIÓN Premium
Expande queries, rerankea noticias y detecta frames subliminales
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsEnricher:
    """Enriquecedor de noticias usando léxicos especializados"""
    
    def __init__(self, lexicon_service=None):
        self.lexicon_service = lexicon_service
        
        # Patrones de detección de frames
        self.frame_patterns = {
            "priming": [
                r"\b(primero|primera|inicial|comenzar|empezar|inicio)\b",
                r"\b(anterior|previo|pasado|histórico|tradicional)\b",
                r"\b(experiencia|memoria|recuerdo|familiar|conocido)\b"
            ],
            "framing": [
                r"\b(marco|contexto|perspectiva|enfoque|óptica|punto de vista)\b",
                r"\b(interpretación|lectura|significado|sentido|valor)\b",
                r"\b(agenda|prioridad|importancia|relevancia|urgencia)\b"
            ],
            "nudge": [
                r"\b(sugerencia|recomendación|consejo|opción|alternativa)\b",
                r"\b(fácil|simple|rápido|conveniente|accesible)\b",
                r"\b(mejor|óptimo|ideal|perfecto|excelente)\b"
            ],
            "double_bind": [
                r"\b(o bien|o si no|de lo contrario|alternativamente)\b",
                r"\b(entre|elegir|decidir|seleccionar|optar)\b",
                r"\b(ambos|ninguno|todos|cada|cualquier)\b"
            ]
        }
        
        # Patrones de clickbait
        self.clickbait_patterns = [
            r"\b(increíble|increible|sorprendente|impactante|escalofriante)\b",
            r"\b(lo que|esto es|descubre|revela|expone)\b",
            r"\b(nunca|siempre|todos|nadie|jamás)\b",
            r"\b(secreto|oculto|escondido|misterioso|enigmático)\b",
            r"\b(choque|conflicto|polémica|escándalo|controversia)\b"
        ]
    
    def expand_query(self, base_query: str, domain: str = None, 
                    max_expansions: int = 5) -> Dict[str, Any]:
        """
        Expande una query base usando léxicos del corpus
        
        Args:
            base_query: Query original
            domain: Dominio específico (jung, subliminal, gematria)
            max_expansions: Máximo número de términos a agregar
        
        Returns:
            Dict con query expandida y metadatos
        """
        try:
            if not self.lexicon_service:
                logger.warning("Servicio de léxicos no disponible, retornando query original")
                return {
                    "original_query": base_query,
                    "expanded_query": base_query,
                    "expansions": [],
                    "domain": domain
                }
            
            # Obtener léxico del dominio
            if domain:
                domain_terms = self.lexicon_service.get_domain_lexicon(domain)
            else:
                # Buscar en todos los dominios
                search_results = self.lexicon_service.search_terms(base_query)
                domain_terms = []
                for d, terms in search_results.items():
                    domain_terms.extend(terms)
            
            # Filtrar términos relevantes
            relevant_terms = self._filter_relevant_terms(base_query, domain_terms, max_expansions)
            
            # Construir query expandida
            expanded_query = base_query
            if relevant_terms:
                expanded_query += " " + " ".join(relevant_terms)
            
            return {
                "original_query": base_query,
                "expanded_query": expanded_query,
                "expansions": relevant_terms,
                "domain": domain,
                "expansion_count": len(relevant_terms)
            }
            
        except Exception as e:
            logger.error(f"Error expandiendo query: {e}")
            return {
                "original_query": base_query,
                "expanded_query": base_query,
                "expansions": [],
                "domain": domain,
                "error": str(e)
            }
    
    def _filter_relevant_terms(self, base_query: str, candidate_terms: List[str], 
                             max_terms: int) -> List[str]:
        """Filtra términos relevantes para la expansión"""
        try:
            if not candidate_terms:
                return []
            
            # Calcular relevancia basada en similitud semántica simple
            scored_terms = []
            base_words = set(base_query.lower().split())
            
            for term in candidate_terms:
                term_words = set(term.lower().split())
                
                # Calcular overlap de palabras
                overlap = len(base_words.intersection(term_words))
                score = overlap / max(len(base_words), 1)
                
                # Bonus por longitud similar
                length_diff = abs(len(term) - len(base_query))
                if length_diff < 10:
                    score += 0.1
                
                scored_terms.append((term, score))
            
            # Ordenar por score y tomar los mejores
            scored_terms.sort(key=lambda x: x[1], reverse=True)
            selected_terms = [term for term, score in scored_terms[:max_terms] if score > 0]
            
            return selected_terms
            
        except Exception as e:
            logger.error(f"Error filtrando términos relevantes: {e}")
            return []
    
    def rerank_news(self, news_items: List[Dict[str, Any]], 
                    lexicons: Dict[str, List[str]] = None,
                    frame_classifier = None) -> List[Dict[str, Any]]:
        """
        Rerankea noticias basado en léxicos del corpus y detección de frames
        
        Args:
            news_items: Lista de noticias a rerankear
            lexicons: Léxicos especializados (opcional)
            frame_classifier: Clasificador de frames (opcional)
        
        Returns:
            Lista de noticias rerankeada
        """
        try:
            if not news_items:
                return []
            
            # Calcular scores para cada noticia
            scored_items = []
            
            for item in news_items:
                score = self._calculate_news_score(item, lexicons, frame_classifier)
                
                scored_item = item.copy()
                scored_item["_lexicon_score"] = score["lexicon_score"]
                scored_item["_frame_score"] = score["frame_score"]
                scored_item["_clickbait_penalty"] = score["clickbait_penalty"]
                scored_item["_total_score"] = score["total_score"]
                
                scored_items.append(scored_item)
            
            # Ordenar por score total
            scored_items.sort(key=lambda x: x.get("_total_score", 0), reverse=True)
            
            logger.info(f"Rerankeadas {len(news_items)} noticias")
            return scored_items
            
        except Exception as e:
            logger.error(f"Error rerankeando noticias: {e}")
            return news_items
    
    def _calculate_news_score(self, news_item: Dict[str, Any], 
                            lexicons: Dict[str, List[str]] = None,
                            frame_classifier = None) -> Dict[str, float]:
        """Calcula score para una noticia individual"""
        try:
            # Extraer texto de la noticia
            title = news_item.get("title", "")
            content = news_item.get("content", "")
            summary = news_item.get("summary", "")
            
            searchable_text = " ".join([title, content, summary]).lower()
            
            # Score por léxicos
            lexicon_score = self._calculate_lexicon_score(searchable_text, lexicons)
            
            # Score por frames
            frame_score = self._calculate_frame_score(searchable_text, frame_classifier)
            
            # Penalización por clickbait
            clickbait_penalty = self._calculate_clickbait_penalty(searchable_text)
            
            # Score total (ponderado)
            total_score = (
                lexicon_score * 0.5 +
                frame_score * 0.3 +
                (1.0 - clickbait_penalty) * 0.2
            )
            
            return {
                "lexicon_score": lexicon_score,
                "frame_score": frame_score,
                "clickbait_penalty": clickbait_penalty,
                "total_score": total_score
            }
            
        except Exception as e:
            logger.error(f"Error calculando score de noticia: {e}")
            return {
                "lexicon_score": 0.0,
                "frame_score": 0.0,
                "clickbait_penalty": 0.0,
                "total_score": 0.0
            }
    
    def _calculate_lexicon_score(self, text: str, lexicons: Dict[str, List[str]] = None) -> float:
        """Calcula score basado en presencia de términos del léxico"""
        try:
            if not lexicons:
                return 0.5  # Score neutral si no hay léxicos
            
            total_matches = 0
            total_terms = 0
            
            for domain, terms in lexicons.items():
                if not terms:
                    continue
                
                domain_matches = 0
                for term in terms:
                    if term.lower() in text:
                        domain_matches += 1
                
                # Normalizar por dominio
                if len(terms) > 0:
                    domain_score = domain_matches / len(terms)
                    total_matches += domain_score
                    total_terms += 1
            
            # Score promedio
            if total_terms > 0:
                return total_matches / total_terms
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Error calculando score de léxico: {e}")
            return 0.0
    
    def _calculate_frame_score(self, text: str, frame_classifier = None) -> float:
        """Calcula score basado en detección de frames"""
        try:
            if frame_classifier:
                # Usar clasificador externo si está disponible
                try:
                    prediction = frame_classifier.predict([text])
                    return float(prediction[0]) if hasattr(prediction, '__iter__') else float(prediction)
                except Exception as e:
                    logger.warning(f"Error usando clasificador externo: {e}")
            
            # Detección basada en patrones
            frame_scores = {}
            
            for frame_type, patterns in self.frame_patterns.items():
                matches = 0
                for pattern in patterns:
                    if re.search(pattern, text, flags=re.IGNORECASE):
                        matches += 1
                
                # Normalizar por número de patrones
                if patterns:
                    frame_scores[frame_type] = matches / len(patterns)
                else:
                    frame_scores[frame_type] = 0.0
            
            # Score promedio de todos los frames
            if frame_scores:
                return sum(frame_scores.values()) / len(frame_scores)
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Error calculando score de frames: {e}")
            return 0.0
    
    def _calculate_clickbait_penalty(self, text: str) -> float:
        """Calcula penalización por clickbait"""
        try:
            matches = 0
            for pattern in self.clickbait_patterns:
                if re.search(pattern, text, flags=re.IGNORECASE):
                    matches += 1
            
            # Penalización proporcional al número de patrones detectados
            penalty = min(matches / len(self.clickbait_patterns), 1.0)
            
            return penalty
            
        except Exception as e:
            logger.error(f"Error calculando penalización de clickbait: {e}")
            return 0.0
    
    def detect_frames(self, text: str) -> Dict[str, Any]:
        """
        Detecta frames subliminales en un texto
        
        Args:
            text: Texto a analizar
        
        Returns:
            Dict con detección de frames
        """
        try:
            text_lower = text.lower()
            frame_detections = {}
            
            for frame_type, patterns in self.frame_patterns.items():
                detected_patterns = []
                
                for pattern in patterns:
                    if re.search(pattern, text_lower):
                        detected_patterns.append(pattern)
                
                frame_detections[frame_type] = {
                    "detected": len(detected_patterns) > 0,
                    "pattern_count": len(detected_patterns),
                    "patterns": detected_patterns,
                    "confidence": min(len(detected_patterns) / len(patterns), 1.0)
                }
            
            # Resumen general
            total_frames = sum(1 for f in frame_detections.values() if f["detected"])
            overall_confidence = sum(f["confidence"] for f in frame_detections.values()) / len(frame_detections)
            
            return {
                "frames": frame_detections,
                "total_frames_detected": total_frames,
                "overall_confidence": overall_confidence,
                "text_length": len(text),
                "analysis_timestamp": "2025-08-31T06:30:00Z"
            }
            
        except Exception as e:
            logger.error(f"Error detectando frames: {e}")
            return {"error": str(e)}
    
    def enrich_news_batch(self, news_batch: List[Dict[str, Any]], 
                         lexicons: Dict[str, List[str]] = None) -> List[Dict[str, Any]]:
        """
        Enriquece un lote completo de noticias
        
        Args:
            news_batch: Lote de noticias
            lexicons: Léxicos especializados
        
        Returns:
            Lista de noticias enriquecidas
        """
        try:
            enriched_batch = []
            
            for news_item in news_batch:
                # Detectar frames
                text = " ".join([
                    news_item.get("title", ""),
                    news_item.get("content", ""),
                    news_item.get("summary", "")
                ])
                
                frame_analysis = self.detect_frames(text)
                
                # Enriquecer item
                enriched_item = news_item.copy()
                enriched_item["frame_analysis"] = frame_analysis
                enriched_item["lexicon_terms"] = self._extract_lexicon_terms(text, lexicons)
                enriched_item["enrichment_score"] = self._calculate_enrichment_score(frame_analysis, enriched_item["lexicon_terms"])
                
                enriched_batch.append(enriched_item)
            
            # Ordenar por score de enriquecimiento
            enriched_batch.sort(key=lambda x: x.get("enrichment_score", 0), reverse=True)
            
            logger.info(f"Enriquecidas {len(enriched_batch)} noticias")
            return enriched_batch
            
        except Exception as e:
            logger.error(f"Error enriqueciendo lote de noticias: {e}")
            return news_batch
    
    def _extract_lexicon_terms(self, text: str, lexicons: Dict[str, List[str]] = None) -> Dict[str, List[str]]:
        """Extrae términos del léxico presentes en el texto"""
        try:
            if not lexicons:
                return {}
            
            found_terms = {}
            text_lower = text.lower()
            
            for domain, terms in lexicons.items():
                domain_terms = []
                for term in terms:
                    if term.lower() in text_lower:
                        domain_terms.append(term)
                
                if domain_terms:
                    found_terms[domain] = domain_terms
            
            return found_terms
            
        except Exception as e:
            logger.error(f"Error extrayendo términos del léxico: {e}")
            return {}
    
    def _calculate_enrichment_score(self, frame_analysis: Dict[str, Any], 
                                 lexicon_terms: Dict[str, List[str]]) -> float:
        """Calcula score de enriquecimiento general"""
        try:
            score = 0.0
            
            # Score por frames detectados
            if "total_frames_detected" in frame_analysis:
                frame_score = min(frame_analysis["total_frames_detected"] / 4.0, 1.0)
                score += frame_score * 0.4
            
            # Score por términos del léxico
            total_lexicon_terms = sum(len(terms) for terms in lexicon_terms.values())
            lexicon_score = min(total_lexicon_terms / 10.0, 1.0)
            score += lexicon_score * 0.6
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculando score de enriquecimiento: {e}")
            return 0.0

# Funciones de conveniencia
def expand_query(base_query: str, **kwargs) -> Dict[str, Any]:
    """Expande una query usando léxicos del corpus"""
    enricher = NewsEnricher()
    return enricher.expand_query(base_query, **kwargs)

def rerank_news(news_items: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
    """Rerankea noticias basado en léxicos y frames"""
    enricher = NewsEnricher()
    return enricher.rerank_news(news_items, **kwargs)

def detect_frames(text: str) -> Dict[str, Any]:
    """Detecta frames subliminales en un texto"""
    enricher = NewsEnricher()
    return enricher.detect_frames(text)







