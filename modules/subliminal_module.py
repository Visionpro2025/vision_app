# modules/subliminal_module.py
"""
MÓDULO DE DETECCIÓN DE MENSAJES SUBLIMINALES
Detecta patrones subliminales en datos de sorteos y genera palabras clave para búsqueda.
"""

import streamlit as st
import re
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SubliminalPattern:
    """Patrón subliminal detectado."""
    pattern_type: str
    confidence: float
    description: str
    keywords: List[str]

class SubliminalDetector:
    """Detector de mensajes subliminales en datos de sorteos."""
    
    def __init__(self):
        self.base_keywords = {
            'powerball': ['lottery', 'jackpot', 'winner', 'numbers', 'draw', 'prize'],
            'gematria': ['hebrew', 'numerology', 'sacred', 'divine', 'spiritual'],
            'subliminal': ['hidden', 'message', 'pattern', 'symbol', 'meaning'],
            'news': ['breaking', 'update', 'announcement', 'report', 'story']
        }
    
    def detect_subliminal_patterns(self, gematria_analysis: Dict[str, Any], 
                                 draw_data: Dict[str, Any]) -> str:
        """Detecta patrones subliminales en los datos del sorteo."""
        try:
            numbers = draw_data.get('winning_numbers', [])
            powerball = draw_data.get('powerball', 0)
            jackpot = draw_data.get('jackpot', 0)
            
            # Detectar patrones básicos
            patterns = []
            
            # Patrón de secuencia
            if len(numbers) >= 2:
                consecutive = sum(1 for i in range(len(numbers)-1) if numbers[i+1] == numbers[i] + 1)
                if consecutive >= 2:
                    patterns.append(f"Secuencia consecutiva detectada ({consecutive} números)")
            
            # Patrón de suma
            total_sum = sum(numbers) + powerball
            if total_sum in [21, 33, 42, 69, 88, 111, 222, 333, 444, 555, 666, 777, 888, 999]:
                patterns.append(f"Suma significativa detectada ({total_sum})")
            
            # Patrón de jackpot
            if jackpot >= 1000000000:
                patterns.append("Jackpot histórico (más de $1B)")
            
            # Generar mensaje
            if patterns:
                message = f"Patrón subliminal detectado: {'; '.join(patterns)}"
            else:
                message = "No se detectaron patrones subliminales significativos"
            
            return message
            
        except Exception as e:
            return f"Error detectando patrones: {str(e)}"
    
    def analyze_message(self, message: str) -> Dict[str, Any]:
        """Analiza un mensaje para detectar patrones subliminales."""
        try:
            # Detectar patrones en el mensaje
            patterns = []
            confidence = 0.0
            
            # Análisis de longitud
            if len(message) > 50:
                patterns.append("Mensaje extenso")
                confidence += 0.1
            
            # Análisis de palabras clave
            keywords_found = []
            for category, words in self.base_keywords.items():
                for word in words:
                    if word.lower() in message.lower():
                        keywords_found.append(word)
                        confidence += 0.05
            
            # Análisis de patrones numéricos
            numbers = re.findall(r'\d+', message)
            if numbers:
                patterns.append(f"Números encontrados: {numbers}")
                confidence += 0.1
            
            # Análisis de repeticiones
            words = re.findall(r'\b\w+\b', message.lower())
            word_counts = {}
            for word in words:
                if len(word) > 3:
                    word_counts[word] = word_counts.get(word, 0) + 1
            
            repeated_words = [word for word, count in word_counts.items() if count > 1]
            if repeated_words:
                patterns.append(f"Palabras repetidas: {repeated_words}")
                confidence += 0.15
            
            # Calcular fuerza del mensaje
            strength = min(confidence, 1.0)
            
            return {
                "success": True,
                "patterns": patterns,
                "confidence": confidence,
                "strength": strength,
                "keywords_found": keywords_found,
                "repeated_words": repeated_words,
                "numbers_found": numbers
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "patterns": [],
                "confidence": 0.0,
                "strength": 0.0
            }
    
    def detect_hidden_patterns(self, message: str) -> Dict[str, Any]:
        """Detecta patrones ocultos en un mensaje."""
        try:
            patterns = []
            confidence = 0.0
            
            # Detectar patrones de repetición
            words = message.lower().split()
            word_counts = {}
            for word in words:
                if len(word) > 3:
                    word_counts[word] = word_counts.get(word, 0) + 1
            
            repeated_words = [word for word, count in word_counts.items() if count > 1]
            if repeated_words:
                patterns.append(f"Palabras repetidas: {repeated_words}")
                confidence += 0.2
            
            # Detectar patrones numéricos
            import re
            numbers = re.findall(r'\d+', message)
            if numbers:
                patterns.append(f"Números encontrados: {numbers}")
                confidence += 0.15
            
            # Detectar patrones de longitud
            if len(message) > 100:
                patterns.append("Mensaje extenso")
                confidence += 0.1
            
            return {
                "success": True,
                "patterns": patterns,
                "confidence": min(confidence, 1.0),
                "repeated_words": repeated_words,
                "numbers_found": numbers
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "patterns": [],
                "confidence": 0.0
            }
    
    def analyze_subliminal_emotions(self, message: str) -> Dict[str, Any]:
        """Analiza las emociones subliminales en un mensaje."""
        try:
            # Palabras clave emocionales
            emotional_keywords = {
                'positive': ['creatividad', 'expresión', 'sabiduría', 'perfección', 'completitud'],
                'negative': ['conflicto', 'desafío', 'miedo', 'ansiedad', 'dolor'],
                'neutral': ['trinidad', 'espiritualidad', 'finalización', 'vida', 'equilibrio']
            }
            
            # Analizar el mensaje
            message_lower = message.lower()
            emotions_found = []
            emotional_score = 0.0
            
            for emotion_type, keywords in emotional_keywords.items():
                for keyword in keywords:
                    if keyword in message_lower:
                        emotions_found.append({
                            'emotion': emotion_type,
                            'keyword': keyword,
                            'intensity': 0.8 if emotion_type == 'positive' else 0.6 if emotion_type == 'negative' else 0.5
                        })
                        emotional_score += 0.1 if emotion_type == 'positive' else -0.05 if emotion_type == 'negative' else 0.0
            
            # Calcular confianza
            confidence = min(len(emotions_found) * 0.2, 1.0)
            
            # Determinar tema emocional dominante
            if emotional_score > 0.3:
                dominant_emotion = "positive"
            elif emotional_score < -0.1:
                dominant_emotion = "negative"
            else:
                dominant_emotion = "neutral"
            
            return {
                "success": True,
                "emotions_found": emotions_found,
                "emotional_score": emotional_score,
                "confidence": confidence,
                "dominant_emotion": dominant_emotion,
                "subliminal_strength": min(confidence + abs(emotional_score), 1.0)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "emotions_found": [],
                "emotional_score": 0.0,
                "confidence": 0.0,
                "dominant_emotion": "unknown"
            }
    
    def extract_keywords(self, subliminal_message: str) -> List[str]:
        """Extrae palabras clave del mensaje subliminal."""
        try:
            keywords = ['powerball', 'lottery', 'subliminal', 'pattern']
            
            # Extraer palabras del mensaje
            words = re.findall(r'\b\w+\b', subliminal_message.lower())
            significant_words = [word for word in words if len(word) > 3]
            
            keywords.extend(significant_words[:5])
            
            # Agregar palabras contextuales
            if 'secuencia' in subliminal_message.lower():
                keywords.extend(['sequence', 'consecutive'])
            if 'suma' in subliminal_message.lower():
                keywords.extend(['sum', 'total', 'mathematical'])
            if 'jackpot' in subliminal_message.lower():
                keywords.extend(['jackpot', 'prize', 'money'])
            
            return list(set(keywords))[:10]
            
        except Exception as e:
            return ['powerball', 'lottery', 'subliminal', 'pattern']

# ============================================================================
# INTEGRACIÓN CON SUBLIMINAL V1.2 PARA FLORIDA PICK 3
# ============================================================================

# Importar las funciones del módulo v1.2
from .subliminal_v12 import (
    GameConfig, PICK3_FL, MEGA, POWER,
    GEMATRIA_CORE, AUX_LEXICON,
    num_to_symbols, merge_keywords, enrich_topics, compose_poem,
    SubliminalOutput, subliminal_from_pick3, subliminal_from_candidates
)

# Importar el módulo guardado
from .subliminal_guarded import (
    SubliminalGuarded, subliminal_guarded_from_pick3, ONTOLOGY
)

class SubliminalDetectorGuarded:
    """Detector subliminal en modo guardado (determinista, trazable)."""
    
    def __init__(self):
        self.ontology = ONTOLOGY
    
    def analyze_pick3_guarded(self, prev_draw: Tuple[int, int, int], 
                             draw_label: str = "PM",
                             date_str: Optional[str] = None) -> SubliminalGuarded:
        """
        Analiza un sorteo anterior de Florida Pick 3 usando modo guardado.
        
        Args:
            prev_draw: Tupla con los 3 números del sorteo anterior (d1, d2, d3)
            draw_label: "AM" o "PM" para identificar el tipo de sorteo
            date_str: Fecha específica (opcional)
            
        Returns:
            SubliminalGuarded con análisis determinista y trazable
        """
        try:
            return subliminal_guarded_from_pick3(prev_draw, draw_label, date_str)
        except Exception as e:
            # Fallback en caso de error
            return SubliminalGuarded(
                game="Pick3_FL",
                draw_label=draw_label,
                input_draw=prev_draw,
                hebrew_labels=["-", "-", "-"],
                families_used=["error", "fallback"],
                keywords_used=["error", "fallback"],
                poem="Error en análisis guardado",
                topics=["error", "fallback"],
                trace=[f"error: {str(e)}"]
            )
    
    def get_guarded_news_criteria(self, guarded_output: SubliminalGuarded) -> Dict[str, Any]:
        """
        Genera criterios de búsqueda de noticias basados en el análisis guardado.
        
        Args:
            guarded_output: Resultado del análisis guardado
            
        Returns:
            Diccionario con criterios de búsqueda deterministas
        """
        return {
            "primary_keywords": guarded_output.keywords_used,
            "news_topics": guarded_output.topics,
            "hebrew_context": guarded_output.hebrew_labels,
            "families_used": guarded_output.families_used,
            "poem_guidance": guarded_output.poem,
            "trace": guarded_output.trace,
            "search_priority": len(guarded_output.topics),
            "temporal_focus": "current_day",
            "geographic_focus": "Florida_USA",
            "deterministic": True,
            "traceable": True
        }

class SubliminalDetectorV12:
    """Detector subliminal v1.2 integrado para Florida Pick 3."""
    
    def __init__(self):
        self.game_config = PICK3_FL
    
    def analyze_pick3_draw(self, prev_draw: Tuple[int, int, int], 
                          draw_label: str = "PM") -> SubliminalOutput:
        """
        Analiza un sorteo anterior de Florida Pick 3 y genera análisis subliminal completo.
        
        Args:
            prev_draw: Tupla con los 3 números del sorteo anterior (d1, d2, d3)
            draw_label: "AM" o "PM" para identificar el tipo de sorteo
            
        Returns:
            SubliminalOutput con análisis completo incluyendo poema y temas de noticias
        """
        try:
            return subliminal_from_pick3(prev_draw, draw_label)
        except Exception as e:
            # Fallback en caso de error
            return SubliminalOutput(
                game="Pick3_FL",
                draw_label=draw_label,
                input_draw=prev_draw,
                hebrew_labels=["-", "-", "-"],
                base_keywords=["error", "fallback"],
                news_topics=["error", "fallback"],
                poem="Error en análisis subliminal",
                hinted_numbers=[]
            )
    
    def analyze_candidates(self, candidates: List[int], 
                          game_type: str = "MegaMillions",
                          draw_label: str = "NOCHE") -> SubliminalOutput:
        """
        Analiza candidatos de números para otros juegos (MegaMillions, Powerball).
        
        Args:
            candidates: Lista de números candidatos
            game_type: Tipo de juego ("MegaMillions" o "Powerball")
            draw_label: Etiqueta del sorteo
            
        Returns:
            SubliminalOutput con análisis completo
        """
        try:
            game_config = MEGA if game_type == "MegaMillions" else POWER
            return subliminal_from_candidates(candidates, game_config, draw_label)
        except Exception as e:
            # Fallback en caso de error
            return SubliminalOutput(
                game=game_type,
                draw_label=draw_label,
                input_draw=(0, 0, 0),
                hebrew_labels=["-"],
                base_keywords=["error", "fallback"],
                news_topics=["error", "fallback"],
                poem="Error en análisis de candidatos",
                hinted_numbers=[]
            )
    
    def get_news_search_criteria(self, subliminal_output: SubliminalOutput) -> Dict[str, Any]:
        """
        Genera criterios de búsqueda de noticias basados en el análisis subliminal.
        
        Args:
            subliminal_output: Resultado del análisis subliminal
            
        Returns:
            Diccionario con criterios de búsqueda para noticias
        """
        return {
            "primary_keywords": subliminal_output.base_keywords,
            "news_topics": subliminal_output.news_topics,
            "hebrew_context": subliminal_output.hebrew_labels,
            "poem_guidance": subliminal_output.poem,
            "search_priority": len(subliminal_output.news_topics),
            "temporal_focus": "current_day",
            "geographic_focus": "Florida_USA",
            "emotional_tone": "neutral_to_positive",
            "spiritual_context": "basic"
        }

# Instancias globales
subliminal_detector = SubliminalDetector()
subliminal_detector_v12 = SubliminalDetectorV12()
subliminal_detector_guarded = SubliminalDetectorGuarded()