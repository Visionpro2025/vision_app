# modules/historical_analysis.py — Análisis Histórico y Arrastre
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timedelta
import json
import pandas as pd
import streamlit as st
from typing import List, Dict, Tuple, Optional
import re

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "__RUNS"
HISTORICAL_DIR = RUNS / "HISTORICAL"
HISTORICAL_DIR.mkdir(parents=True, exist_ok=True)

class HistoricalAnalyzer:
    def __init__(self):
        self.historical_data = {}
        self.drag_patterns = {}
        self.previous_draw_analysis = {}
        
    def _load_historical_news(self, days_back: int = 30) -> pd.DataFrame:
        """Carga noticias históricas de los últimos N días."""
        historical_news = []
        
        # Buscar archivos de noticias históricas
        news_dir = RUNS / "NEWS"
        if not news_dir.exists():
            return pd.DataFrame()
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        for news_file in news_dir.glob("*.csv"):
            try:
                # Extraer fecha del nombre del archivo o contenido
                file_date = self._extract_date_from_filename(news_file)
                if file_date and file_date >= cutoff_date:
                    df = pd.read_csv(news_file, dtype=str, encoding="utf-8")
                    df['_file_date'] = file_date
                    historical_news.append(df)
            except Exception:
                continue
        
        if historical_news:
            return pd.concat(historical_news, ignore_index=True)
        return pd.DataFrame()
    
    def _extract_date_from_filename(self, file_path: Path) -> Optional[datetime]:
        """Extrae fecha del nombre del archivo."""
        try:
            # Buscar patrones de fecha en el nombre
            filename = file_path.stem
            date_patterns = [
                r'(\d{4}-\d{2}-\d{2})',
                r'(\d{2}-\d{2}-\d{4})',
                r'(\d{8})'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, filename)
                if match:
                    date_str = match.group(1)
                    if len(date_str) == 8:  # YYYYMMDD
                        return datetime.strptime(date_str, '%Y%m%d')
                    elif len(date_str) == 10:  # YYYY-MM-DD
                        return datetime.strptime(date_str, '%Y-%m-%d')
                    elif len(date_str) == 8:  # MM-DD-YYYY
                        return datetime.strptime(date_str, '%m-%d-%Y')
        except Exception:
            pass
        return None
    
    def analyze_news_drag(self, current_news: pd.DataFrame, days_back: int = 30) -> Dict:
        """Analiza arrastre histórico de noticias."""
        historical_news = self._load_historical_news(days_back)
        
        if historical_news.empty:
            return {
                "drag_detected": False,
                "drag_strength": 0.0,
                "historical_patterns": [],
                "correlation_score": 0.0,
                "message": "No hay datos históricos disponibles"
            }
        
        # Analizar correlaciones entre noticias actuales e históricas
        drag_analysis = self._calculate_drag_correlation(current_news, historical_news)
        
        # Detectar patrones históricos
        historical_patterns = self._detect_historical_patterns(historical_news)
        
        # Calcular fuerza del arrastre
        drag_strength = self._calculate_drag_strength(drag_analysis, historical_patterns)
        
        return {
            "drag_detected": drag_strength > 0.3,
            "drag_strength": drag_strength,
            "historical_patterns": historical_patterns,
            "correlation_score": drag_analysis.get("overall_correlation", 0.0),
            "message": f"Arrastre detectado: {drag_strength:.2f}" if drag_strength > 0.3 else "Sin arrastre significativo"
        }
    
    def _calculate_drag_correlation(self, current: pd.DataFrame, historical: pd.DataFrame) -> Dict:
        """Calcula correlación entre noticias actuales e históricas."""
        if current.empty or historical.empty:
            return {"overall_correlation": 0.0}
        
        correlations = []
        
        # Comparar categorías emocionales
        if "_categoria_emocional" in current.columns and "_categoria_emocional" in historical.columns:
            current_cats = current["_categoria_emocional"].value_counts()
            historical_cats = historical["_categoria_emocional"].value_counts()
            
            # Normalizar y calcular correlación
            all_cats = set(current_cats.index) | set(historical_cats.index)
            current_norm = {cat: current_cats.get(cat, 0) / len(current) for cat in all_cats}
            historical_norm = {cat: historical_cats.get(cat, 0) / len(historical) for cat in all_cats}
            
            # Correlación de Pearson simplificada
            correlation = self._pearson_correlation(list(current_norm.values()), list(historical_norm.values()))
            correlations.append(("categorias", correlation))
        
        # Comparar fuentes
        if "fuente" in current.columns and "fuente" in historical.columns:
            current_sources = current["fuente"].value_counts()
            historical_sources = historical["fuente"].value_counts()
            
            all_sources = set(current_sources.index) | set(historical_sources.index)
            current_norm = {src: current_sources.get(src, 0) / len(current) for src in all_sources}
            historical_norm = {src: historical_sources.get(src, 0) / len(historical) for src in all_sources}
            
            correlation = self._pearson_correlation(list(current_norm.values()), list(historical_norm.values()))
            correlations.append(("fuentes", correlation))
        
        # Correlación general
        overall_correlation = sum(corr[1] for corr in correlations) / len(correlations) if correlations else 0.0
        
        return {
            "overall_correlation": overall_correlation,
            "detailed_correlations": correlations
        }
    
    def _pearson_correlation(self, x: List[float], y: List[float]) -> float:
        """Calcula correlación de Pearson simplificada."""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        sum_y2 = sum(y[i] ** 2 for i in range(n))
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def _detect_historical_patterns(self, historical_news: pd.DataFrame) -> List[Dict]:
        """Detecta patrones históricos en las noticias."""
        patterns = []
        
        if historical_news.empty:
            return patterns
        
        # Patrón 1: Ciclos temporales
        if "_file_date" in historical_news.columns:
            temporal_patterns = self._detect_temporal_patterns(historical_news)
            patterns.extend(temporal_patterns)
        
        # Patrón 2: Secuencias de categorías
        if "_categoria_emocional" in historical_news.columns:
            category_patterns = self._detect_category_patterns(historical_news)
            patterns.extend(category_patterns)
        
        # Patrón 3: Fluctuaciones de impacto
        if "_nivel_impacto" in historical_news.columns:
            impact_patterns = self._detect_impact_patterns(historical_news)
            patterns.extend(impact_patterns)
        
        return patterns
    
    def _detect_temporal_patterns(self, historical_news: pd.DataFrame) -> List[Dict]:
        """Detecta patrones temporales."""
        patterns = []
        
        # Agrupar por día
        daily_counts = historical_news.groupby("_file_date").size()
        
        if len(daily_counts) > 1:
            # Detectar tendencias
            values = list(daily_counts.values)
            if len(values) >= 3:
                # Tendencia creciente
                if all(values[i] <= values[i+1] for i in range(len(values)-1)):
                    patterns.append({
                        "type": "temporal_trend",
                        "description": "Tendencia creciente en volumen de noticias",
                        "strength": min(1.0, len(values) / 10.0)
                    })
                # Tendencia decreciente
                elif all(values[i] >= values[i+1] for i in range(len(values)-1)):
                    patterns.append({
                        "type": "temporal_trend",
                        "description": "Tendencia decreciente en volumen de noticias",
                        "strength": min(1.0, len(values) / 10.0)
                    })
        
        return patterns
    
    def _detect_category_patterns(self, historical_news: pd.DataFrame) -> List[Dict]:
        """Detecta patrones en categorías emocionales."""
        patterns = []
        
        # Agrupar por día y categoría
        daily_categories = historical_news.groupby(["_file_date", "_categoria_emocional"]).size().unstack(fill_value=0)
        
        if not daily_categories.empty:
            # Detectar categorías dominantes
            category_totals = daily_categories.sum()
            dominant_categories = category_totals[category_totals > category_totals.mean() * 1.5]
            
            for cat in dominant_categories.index:
                patterns.append({
                    "type": "category_dominance",
                    "description": f"Categoría dominante: {cat}",
                    "strength": min(1.0, dominant_categories[cat] / category_totals.max()),
                    "category": cat
                })
        
        return patterns
    
    def _detect_impact_patterns(self, historical_news: pd.DataFrame) -> List[Dict]:
        """Detecta patrones en niveles de impacto."""
        patterns = []
        
        # Agrupar por día y nivel de impacto
        daily_impact = historical_news.groupby(["_file_date", "_nivel_impacto"]).size().unstack(fill_value=0)
        
        if not daily_impact.empty:
            # Detectar días de alto impacto
            high_impact_days = daily_impact.get(5, pd.Series(dtype=int))
            if not high_impact_days.empty:
                high_impact_count = (high_impact_days > 0).sum()
                if high_impact_count > len(high_impact_days) * 0.3:  # Más del 30% de días
                    patterns.append({
                        "type": "high_impact_frequency",
                        "description": "Alta frecuencia de noticias de impacto máximo",
                        "strength": min(1.0, high_impact_count / len(high_impact_days)),
                        "frequency": high_impact_count
                    })
        
        return patterns
    
    def _calculate_drag_strength(self, correlation: Dict, patterns: List[Dict]) -> float:
        """Calcula la fuerza del arrastre basada en correlación y patrones."""
        base_strength = correlation.get("overall_correlation", 0.0)
        
        # Ajustar por patrones detectados
        pattern_bonus = 0.0
        for pattern in patterns:
            pattern_bonus += pattern.get("strength", 0.0) * 0.1  # Cada patrón añade hasta 0.1
        
        total_strength = min(1.0, base_strength + pattern_bonus)
        return total_strength
    
    def analyze_previous_draw(self, lottery_name: str = "default") -> Dict:
        """Analiza el sorteo anterior completo."""
        # Buscar archivos de resultados anteriores
        results_dir = RUNS / "RESULTS"
        if not results_dir.exists():
            return {
                "analysis_available": False,
                "message": "No hay resultados anteriores disponibles"
            }
        
        # Buscar el archivo más reciente
        result_files = list(results_dir.glob("result_*.json"))
        if not result_files:
            return {
                "analysis_available": False,
                "message": "No se encontraron archivos de resultados"
            }
        
        latest_result = max(result_files, key=lambda x: x.stat().st_mtime)
        
        try:
            with open(latest_result, 'r', encoding='utf-8') as f:
                previous_result = json.load(f)
            
            # Análisis gematría del sorteo anterior
            gematria_analysis = self._analyze_previous_draw_gematria(previous_result)
            
            # Análisis subliminal del sorteo anterior
            subliminal_analysis = self._analyze_previous_draw_subliminal(previous_result)
            
            return {
                "analysis_available": True,
                "previous_draw_date": previous_result.get("draw_date", "desconocida"),
                "previous_numbers": previous_result.get("numbers", []),
                "gematria_analysis": gematria_analysis,
                "subliminal_analysis": subliminal_analysis,
                "continuity_patterns": self._detect_continuity_patterns(previous_result)
            }
            
        except Exception as e:
            return {
                "analysis_available": False,
                "message": f"Error al analizar resultado anterior: {str(e)}"
            }
    
    def _analyze_previous_draw_gematria(self, previous_result: Dict) -> Dict:
        """Analiza gematría del sorteo anterior."""
        numbers = previous_result.get("numbers", [])
        
        if not numbers:
            return {"available": False, "message": "No hay números para analizar"}
        
        # Cálculos gematría básicos
        total_sum = sum(numbers)
        product = 1
        for num in numbers:
            product *= num
        
        # Análisis de patrones
        patterns = []
        if len(numbers) >= 2:
            # Secuencias
            sorted_nums = sorted(numbers)
            consecutive_count = 1
            for i in range(1, len(sorted_nums)):
                if sorted_nums[i] == sorted_nums[i-1] + 1:
                    consecutive_count += 1
                else:
                    if consecutive_count > 1:
                        patterns.append(f"Secuencia de {consecutive_count} números consecutivos")
                    consecutive_count = 1
            
            if consecutive_count > 1:
                patterns.append(f"Secuencia de {consecutive_count} números consecutivos")
        
        return {
            "available": True,
            "total_sum": total_sum,
            "product": product,
            "average": total_sum / len(numbers),
            "patterns": patterns,
            "gematria_value": total_sum % 70 + 1
        }
    
    def _analyze_previous_draw_subliminal(self, previous_result: Dict) -> Dict:
        """Analiza mensajes subliminales del sorteo anterior."""
        # Buscar contexto del sorteo anterior
        context = previous_result.get("context", {})
        news_context = context.get("news_context", "")
        
        if not news_context:
            return {"available": False, "message": "No hay contexto de noticias disponible"}
        
        # Análisis básico de sentimiento
        positive_words = ["ganar", "éxito", "victoria", "fortuna", "suerte", "prosperidad"]
        negative_words = ["pérdida", "fracaso", "derrota", "mala suerte", "pobreza"]
        
        positive_count = sum(1 for word in positive_words if word.lower() in news_context.lower())
        negative_count = sum(1 for word in negative_words if word.lower() in news_context.lower())
        
        # Sentimiento general
        if positive_count > negative_count:
            sentiment = "positivo"
            sentiment_strength = positive_count / (positive_count + negative_count + 1)
        elif negative_count > positive_count:
            sentiment = "negativo"
            sentiment_strength = negative_count / (positive_count + negative_count + 1)
        else:
            sentiment = "neutral"
            sentiment_strength = 0.5
        
        return {
            "available": True,
            "sentiment": sentiment,
            "sentiment_strength": sentiment_strength,
            "positive_indicators": positive_count,
            "negative_indicators": negative_count,
            "context_length": len(news_context)
        }
    
    def _detect_continuity_patterns(self, previous_result: Dict) -> List[Dict]:
        """Detecta patrones de continuidad hacia el sorteo actual."""
        patterns = []
        
        # Buscar indicadores de continuidad en el contexto
        context = previous_result.get("context", {})
        
        # Patrón 1: Continuidad temporal
        if "draw_date" in previous_result:
            try:
                prev_date = datetime.fromisoformat(previous_result["draw_date"])
                days_since = (datetime.now() - prev_date).days
                
                if days_since <= 7:
                    patterns.append({
                        "type": "temporal_continuity",
                        "description": f"Sorteo anterior hace {days_since} días",
                        "strength": max(0.1, 1.0 - (days_since / 7.0))
                    })
            except Exception:
                pass
        
        # Patrón 2: Continuidad numérica
        numbers = previous_result.get("numbers", [])
        if numbers:
            # Números que aparecen frecuentemente
            patterns.append({
                "type": "numerical_continuity",
                "description": f"Números del sorteo anterior: {numbers}",
                "strength": 0.6,
                "numbers": numbers
            })
        
        return patterns
    
    def generate_historical_report(self, current_news: pd.DataFrame) -> Dict:
        """Genera reporte completo de análisis histórico."""
        # Análisis de arrastre
        drag_analysis = self.analyze_news_drag(current_news)
        
        # Análisis del sorteo anterior
        previous_analysis = self.analyze_previous_draw()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "drag_analysis": drag_analysis,
            "previous_draw_analysis": previous_analysis,
            "recommendations": self._generate_recommendations(drag_analysis, previous_analysis)
        }
    
    def _generate_recommendations(self, drag_analysis: Dict, previous_analysis: Dict) -> List[str]:
        """Genera recomendaciones basadas en el análisis histórico."""
        recommendations = []
        
        # Recomendaciones basadas en arrastre
        if drag_analysis.get("drag_detected", False):
            drag_strength = drag_analysis.get("drag_strength", 0.0)
            if drag_strength > 0.7:
                recommendations.append("⚠️ ARRASTRE FUERTE DETECTADO: Considerar influencia significativa de patrones históricos")
            elif drag_strength > 0.5:
                recommendations.append("⚠️ ARRASTRE MODERADO: Patrones históricos pueden influir en el análisis actual")
            else:
                recommendations.append("ℹ️ Arrastre leve detectado, influencia mínima esperada")
        
        # Recomendaciones basadas en sorteo anterior
        if previous_analysis.get("analysis_available", False):
            gematria = previous_analysis.get("gematria_analysis", {})
            subliminal = previous_analysis.get("subliminal_analysis", {})
            
            if gematria.get("available", False):
                patterns = gematria.get("patterns", [])
                if patterns:
                    recommendations.append(f"🔢 PATRONES GEMÁTRICOS ANTERIORES: {', '.join(patterns[:3])}")
            
            if subliminal.get("available", False):
                sentiment = subliminal.get("sentiment", "neutral")
                if sentiment != "neutral":
                    recommendations.append(f"🧠 SENTIMIENTO ANTERIOR: {sentiment.capitalize()} - puede influir en continuidad")
        
        if not recommendations:
            recommendations.append("ℹ️ No se detectaron patrones históricos significativos")
        
        return recommendations

# Instancia global
historical_analyzer = HistoricalAnalyzer()

