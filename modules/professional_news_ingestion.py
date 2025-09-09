# modules/professional_news_ingestion.py — Sistema Profesional de Ingestión de Noticias
# - Orientación social/económica real (USA)
# - Fuentes confiables y verificadas
# - Análisis emocional con NLP
# - Filtros temáticos y de calidad

from __future__ import annotations
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import requests
import feedparser
import logging
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

# =================== Configuración de Logging ===================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class NewsItem:
    """Estructura de datos para noticias procesadas."""
    titulo: str
    medio: str
    fecha: str
    url: str
    emocion: str
    impact_score: float
    tema: str
    contenido: str = ""
    resumen: str = ""

class ProfessionalNewsIngestion:
    """Sistema profesional de ingestión de noticias con orientación social/económica (USA)."""
    
    def __init__(self):
        # APIs disponibles (requieren keys)
        self.news_api_key = st.secrets.get("NEWS_API_KEY", "")
        self.gnews_api_key = st.secrets.get("GNEWS_API_KEY", "")
        self.bing_api_key = st.secrets.get("BING_API_KEY", "")
        
        # Fuentes confiables (medios de alto impacto)
        self.trusted_sources = {
            "reuters.com": "Reuters",
            "ap.org": "Associated Press", 
            "bloomberg.com": "Bloomberg",
            "politico.com": "Politico",
            "npr.org": "NPR",
            "theguardian.com": "The Guardian",
            "wsj.com": "Wall Street Journal",
            "nytimes.com": "The New York Times",
            "washingtonpost.com": "The Washington Post",
            "cnn.com": "CNN",
            "abcnews.go.com": "ABC News",
            "cbsnews.com": "CBS News",
            "nbcnews.com": "NBC News",
            "foxnews.com": "Fox News",
            "usatoday.com": "USA Today"
        }
        
        # Temas prioritarios con palabras clave
        self.priority_topics = {
            "economia_dinero": [
                "inflation", "recession", "unemployment", "wages", "salaries", "crisis",
                "markets", "stocks", "economy", "financial", "banking", "debt",
                "housing", "real estate", "mortgage", "interest rates", "fed", "federal reserve"
            ],
            "politica_justicia": [
                "protest", "demonstration", "civil rights", "voting rights", "election",
                "supreme court", "congress", "senate", "house", "legislation", "law",
                "justice", "police", "reform", "policy", "government", "administration"
            ],
            "seguridad_social": [
                "crime", "violence", "protest", "migration", "immigration", "border",
                "security", "threat", "attack", "shooting", "riot", "unrest",
                "social unrest", "civil unrest", "disorder", "chaos", "emergency"
            ]
        }
        
        # Temas a ignorar (noticias neutras)
        self.ignore_topics = [
            "weather", "climate", "sports", "entertainment", "celebrity", "gossip",
            "movie", "music", "tv show", "game", "recipe", "travel", "lifestyle"
        ]
        
        # Configuración de análisis emocional
        self.emotion_keywords = {
            "ira": ["anger", "furious", "outrage", "rage", "fury", "wrath", "hostile"],
            "miedo": ["fear", "terror", "panic", "horror", "dread", "anxiety", "worry"],
            "esperanza": ["hope", "optimism", "confidence", "trust", "faith", "belief"],
            "tristeza": ["sadness", "grief", "sorrow", "despair", "melancholy", "depression"],
            "orgullo": ["pride", "dignity", "honor", "respect", "achievement", "success"]
        }
    
    def fetch_profiled_news(self, keywords: List[str], date: str = None) -> List[Dict]:
        """
        Busca noticias sociales/económicas/políticas de alto impacto (USA).
        
        Args:
            keywords: Lista de palabras clave para búsqueda
            date: Fecha en formato YYYY-MM-DD (por defecto: ayer)
        
        Returns:
            Lista de diccionarios con noticias procesadas
        """
        try:
            # Configurar fecha (últimas 24 horas)
            if date is None:
                target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            else:
                target_date = date
            
            logger.info(f"Iniciando búsqueda de noticias para fecha: {target_date}")
            
            # Recolectar noticias de múltiples fuentes
            all_news = []
            
            # 1. NewsAPI (si está disponible)
            if self.news_api_key:
                news_api_results = self._fetch_from_newsapi(keywords, target_date)
                all_news.extend(news_api_results)
                logger.info(f"NewsAPI: {len(news_api_results)} noticias recolectadas")
            
            # 2. GNews (si está disponible)
            if self.gnews_api_key:
                gnews_results = self._fetch_from_gnews(keywords, target_date)
                all_news.extend(gnews_results)
                logger.info(f"GNews: {len(gnews_results)} noticias recolectadas")
            
            # 3. Bing News (si está disponible)
            if self.bing_api_key:
                bing_results = self._fetch_from_bing(keywords, target_date)
                all_news.extend(bing_results)
                logger.info(f"Bing News: {len(bing_results)} noticias recolectadas")
            
            # 4. RSS feeds como fallback
            if not all_news:
                rss_results = self._fetch_from_rss(keywords, target_date)
                all_news.extend(rss_results)
                logger.info(f"RSS: {len(rss_results)} noticias recolectadas")
            
            # Procesar y filtrar noticias
            processed_news = self._process_and_filter_news(all_news)
            
            # Ordenar por impacto y relevancia
            processed_news.sort(key=lambda x: x["impact_score"], reverse=True)
            
            logger.info(f"Total de noticias procesadas: {len(processed_news)}")
            
            return processed_news
            
        except Exception as e:
            logger.error(f"Error en fetch_profiled_news: {str(e)}")
            return []
    
    def _fetch_from_newsapi(self, keywords: List[str], date: str) -> List[Dict]:
        """Recolecta noticias desde NewsAPI."""
        try:
            news_items = []
            
            for keyword in keywords[:5]:  # Limitar a 5 keywords principales
                url = "https://newsapi.org/v2/everything"
                params = {
                    "q": keyword,
                    "from": date,
                    "to": date,
                    "language": "en",
                    "sortBy": "relevancy",
                    "apiKey": self.news_api_key,
                    "pageSize": 20
                }
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    for article in data.get("articles", []):
                        if self._is_valid_source(article.get("source", {}).get("domain", "")):
                            news_items.append({
                                "title": article.get("title", ""),
                                "source": article.get("source", {}).get("name", ""),
                                "publishedAt": article.get("publishedAt", ""),
                                "url": article.get("url", ""),
                                "content": article.get("content", ""),
                                "description": article.get("description", "")
                            })
            
            return news_items
            
        except Exception as e:
            logger.error(f"Error en NewsAPI: {str(e)}")
            return []
    
    def _fetch_from_gnews(self, keywords: List[str], date: str) -> List[Dict]:
        """Recolecta noticias desde GNews."""
        try:
            news_items = []
            
            for keyword in keywords[:5]:
                url = "https://gnews.io/api/v4/search"
                params = {
                    "q": keyword,
                    "lang": "en",
                    "country": "us",
                    "max": 20,
                    "apikey": self.gnews_api_key
                }
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    for article in data.get("articles", []):
                        if self._is_valid_source(article.get("source", {}).get("url", "")):
                            news_items.append({
                                "title": article.get("title", ""),
                                "source": article.get("source", {}).get("name", ""),
                                "publishedAt": article.get("publishedAt", ""),
                                "url": article.get("url", ""),
                                "content": article.get("content", ""),
                                "description": article.get("description", "")
                            })
            
            return news_items
            
        except Exception as e:
            logger.error(f"Error en GNews: {str(e)}")
            return []
    
    def _fetch_from_bing(self, keywords: List[str], date: str) -> List[Dict]:
        """Recolecta noticias desde Bing News Search."""
        try:
            news_items = []
            
            for keyword in keywords[:5]:
                url = "https://api.bing.microsoft.com/v7.0/news/search"
                headers = {
                    "Ocp-Apim-Subscription-Key": self.bing_api_key
                }
                params = {
                    "q": keyword,
                    "count": 20,
                    "mkt": "en-US",
                    "freshness": "Day"
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    for article in data.get("value", []):
                        if self._is_valid_source(article.get("url", "")):
                            news_items.append({
                                "title": article.get("name", ""),
                                "source": article.get("provider", [{}])[0].get("name", ""),
                                "publishedAt": article.get("datePublished", ""),
                                "url": article.get("url", ""),
                                "content": article.get("description", ""),
                                "description": article.get("description", "")
                            })
            
            return news_items
            
        except Exception as e:
            logger.error(f"Error en Bing News: {str(e)}")
            return []
    
    def _fetch_from_rss(self, keywords: List[str], date: str) -> List[Dict]:
        """Recolecta noticias desde RSS feeds como fallback."""
        try:
            news_items = []
            
            # RSS feeds de fuentes confiables
            rss_feeds = [
                "https://www.reuters.com/rssFeed/usNews",
                "https://feeds.npr.org/1001/rss.xml",
                "https://www.theguardian.com/us-news/rss",
                "https://rss.nytimes.com/services/xml/rss/nyt/US.xml",
                "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml"
            ]
            
            for feed_url in rss_feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries[:10]:  # Limitar a 10 por feed
                        # Verificar si la noticia es reciente
                        pub_date = self._parse_rss_date(entry.get("published", ""))
                        if pub_date and pub_date.strftime("%Y-%m-%d") == date:
                            # Verificar si contiene keywords relevantes
                            title = entry.get("title", "").lower()
                            if any(keyword.lower() in title for keyword in keywords):
                                news_items.append({
                                    "title": entry.get("title", ""),
                                    "source": feed.feed.get("title", ""),
                                    "publishedAt": entry.get("published", ""),
                                    "url": entry.get("link", ""),
                                    "content": entry.get("summary", ""),
                                    "description": entry.get("summary", "")
                                })
                
                except Exception as e:
                    logger.warning(f"Error procesando RSS {feed_url}: {str(e)}")
                    continue
            
            return news_items
            
        except Exception as e:
            logger.error(f"Error en RSS: {str(e)}")
            return []
    
    def _is_valid_source(self, source: str) -> bool:
        """Verifica si la fuente es confiable."""
        if not source:
            return False
        
        source_lower = source.lower()
        
        # Verificar si es una fuente confiable
        for trusted_domain in self.trusted_sources.keys():
            if trusted_domain in source_lower:
                return True
        
        # Excluir fuentes dudosas
        spam_indicators = ["blog", "wordpress", "tumblr", "medium.com", "substack.com"]
        for indicator in spam_indicators:
            if indicator in source_lower:
                return False
        
        return False
    
    def _parse_rss_date(self, date_str: str) -> Optional[datetime]:
        """Parsea fechas de RSS feeds."""
        try:
            # Intentar diferentes formatos de fecha
            date_formats = [
                "%a, %d %b %Y %H:%M:%S %z",
                "%a, %d %b %Y %H:%M:%S %Z",
                "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%d %H:%M:%S"
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            return None
            
        except Exception:
            return None
    
    def _process_and_filter_news(self, raw_news: List[Dict]) -> List[Dict]:
        """Procesa y filtra las noticias recolectadas."""
        processed_news = []
        
        for news in raw_news:
            try:
                # 1. Verificar que tenga contenido mínimo
                if not self._has_minimum_content(news):
                    continue
                
                # 2. Clasificar tema
                tema = self._classify_topic(news)
                if not tema:
                    continue  # Ignorar noticias sin tema relevante
                
                # 3. Analizar emoción
                emocion, impact_score = self._analyze_emotion_and_impact(news)
                
                # 4. Filtrar por score mínimo
                if impact_score < 0.6:
                    continue
                
                # 5. Crear item procesado
                processed_item = {
                    "titulo": news.get("title", ""),
                    "medio": news.get("source", ""),
                    "fecha": news.get("publishedAt", ""),
                    "url": news.get("url", ""),
                    "emocion": emocion,
                    "impact_score": round(impact_score, 3),
                    "tema": tema,
                    "contenido": news.get("content", ""),
                    "resumen": news.get("description", "")
                }
                
                processed_news.append(processed_item)
                
            except Exception as e:
                logger.warning(f"Error procesando noticia: {str(e)}")
                continue
        
        return processed_news
    
    def _has_minimum_content(self, news: Dict) -> bool:
        """Verifica que la noticia tenga contenido mínimo."""
        title = news.get("title", "")
        content = news.get("content", "")
        description = news.get("description", "")
        
        # Mínimo 10 caracteres en título
        if len(title.strip()) < 10:
            return False
        
        # Mínimo 50 caracteres en contenido o descripción
        total_content = (content + " " + description).strip()
        if len(total_content) < 50:
            return False
        
        return True
    
    def _classify_topic(self, news: Dict) -> Optional[str]:
        """Clasifica el tema de la noticia."""
        title = news.get("title", "").lower()
        content = news.get("content", "").lower()
        description = news.get("description", "").lower()
        
        full_text = f"{title} {content} {description}"
        
        # Verificar temas prioritarios
        for topic, keywords in self.priority_topics.items():
            if any(keyword in full_text for keyword in keywords):
                return topic
        
        # Verificar temas a ignorar
        for ignore_topic in self.ignore_topics:
            if ignore_topic in full_text:
                return None  # Ignorar esta noticia
        
        return None
    
    def _analyze_emotion_and_impact(self, news: Dict) -> Tuple[str, float]:
        """Analiza la emoción y calcula el score de impacto."""
        title = news.get("title", "").lower()
        content = news.get("content", "").lower()
        description = news.get("description", "").lower()
        
        full_text = f"{title} {content} {description}"
        
        # Análisis de emoción basado en palabras clave
        emotion_scores = {}
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in full_text)
            emotion_scores[emotion] = score
        
        # Emoción dominante
        if emotion_scores:
            dominant_emotion = max(emotion_scores, key=emotion_scores.get)
        else:
            dominant_emotion = "neutral"
        
        # Calcular score de impacto
        impact_score = self._calculate_impact_score(news, emotion_scores)
        
        return dominant_emotion, impact_score
    
    def _calculate_impact_score(self, news: Dict, emotion_scores: Dict) -> float:
        """Calcula el score de impacto de la noticia."""
        score = 0.0
        
        # 1. Emoción (40% del score)
        max_emotion_score = max(emotion_scores.values()) if emotion_scores else 0
        emotion_contribution = min(max_emotion_score / 3.0, 1.0) * 0.4
        score += emotion_contribution
        
        # 2. Longitud del contenido (20% del score)
        content_length = len(news.get("content", "") + news.get("description", ""))
        length_score = min(content_length / 1000.0, 1.0) * 0.2
        score += length_score
        
        # 3. Fuente confiable (20% del score)
        if self._is_highly_trusted_source(news.get("source", "")):
            score += 0.2
        
        # 4. Presencia de palabras clave críticas (20% del score)
        critical_keywords = [
            "crisis", "emergency", "urgent", "breaking", "exclusive",
            "protest", "riot", "violence", "attack", "threat",
            "recession", "inflation", "unemployment", "crisis"
        ]
        
        title = news.get("title", "").lower()
        critical_count = sum(1 for keyword in critical_keywords if keyword in title)
        critical_score = min(critical_count / 3.0, 1.0) * 0.2
        score += critical_score
        
        return min(score, 1.0)  # Normalizar a 0-1
    
    def _is_highly_trusted_source(self, source: str) -> bool:
        """Verifica si es una fuente altamente confiable."""
        highly_trusted = ["reuters.com", "ap.org", "bloomberg.com", "wsj.com", "nytimes.com"]
        
        source_lower = source.lower()
        return any(trusted in source_lower for trusted in highly_trusted)
    
    def get_news_summary(self, news_list: List[Dict]) -> Dict:
        """Genera un resumen estadístico de las noticias."""
        if not news_list:
            return {}
        
        summary = {
            "total_noticias": len(news_list),
            "por_tema": {},
            "por_emocion": {},
            "por_fuente": {},
            "score_promedio": 0.0,
            "fuentes_unicas": 0,
            "temas_unicos": 0,
            "emociones_unicas": 0
        }
        
        # Contar por tema
        for news in news_list:
            tema = news.get("tema", "sin_tema")
            summary["por_tema"][tema] = summary["por_tema"].get(tema, 0) + 1
        
        # Contar por emoción
        for news in news_list:
            emocion = news.get("emocion", "neutral")
            summary["por_emocion"][emocion] = summary["por_emocion"].get(emocion, 0) + 1
        
        # Contar por fuente
        for news in news_list:
            fuente = news.get("medio", "sin_fuente")
            summary["por_fuente"][fuente] = summary["por_fuente"].get(fuente, 0) + 1
        
        # Calcular promedios
        scores = [news.get("impact_score", 0) for news in news_list]
        summary["score_promedio"] = round(sum(scores) / len(scores), 3)
        
        # Contar únicos
        summary["fuentes_unicas"] = len(summary["por_fuente"])
        summary["temas_unicos"] = len(summary["por_tema"])
        summary["emociones_unicas"] = len(summary["por_emocion"])
        
        return summary

# Instancia global del sistema de ingestión profesional
professional_news_ingestion = ProfessionalNewsIngestion()

# =================== Función de Interfaz para Streamlit ===================

def fetch_profiled_news(keywords: List[str], date: str = None) -> List[Dict]:
    """
    Función de interfaz para buscar noticias sociales/económicas/políticas de alto impacto (USA).
    
    Args:
        keywords: Lista de palabras clave para búsqueda
        date: Fecha en formato YYYY-MM-DD (por defecto: ayer)
    
    Returns:
        Lista de diccionarios con campos:
        {
            "titulo": ...,
            "medio": ...,
            "fecha": ...,
            "url": ...,
            "emocion": ...,
            "impact_score": ...,
            "tema": ...
        }
    """
    return professional_news_ingestion.fetch_profiled_news(keywords, date)

def get_news_analysis_summary(news_list: List[Dict]) -> Dict:
    """
    Genera un resumen analítico de las noticias recolectadas.
    
    Args:
        news_list: Lista de noticias procesadas
    
    Returns:
        Diccionario con estadísticas y análisis
    """
    return professional_news_ingestion.get_news_summary(news_list)

# =================== Ejemplo de Uso ===================

if __name__ == "__main__":
    # Ejemplo de uso
    keywords = ["inflation", "protest", "crisis", "unemployment", "civil rights"]
    
    print("🔍 Iniciando búsqueda de noticias profesionales...")
    news = fetch_profiled_news(keywords)
    
    if news:
        print(f"✅ Se encontraron {len(news)} noticias relevantes")
        
        # Mostrar resumen
        summary = get_news_analysis_summary(news)
        print(f"📊 Resumen: {summary}")
        
        # Mostrar primeras noticias
        for i, item in enumerate(news[:3]):
            print(f"\n📰 Noticia {i+1}:")
            print(f"   Título: {item['titulo']}")
            print(f"   Medio: {item['medio']}")
            print(f"   Tema: {item['tema']}")
            print(f"   Emoción: {item['emocion']}")
            print(f"   Impacto: {item['impact_score']}")
    else:
        print("❌ No se encontraron noticias relevantes")







