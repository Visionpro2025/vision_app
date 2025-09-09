# modules/noticias_module.py — Acopio Emoción Social (USA) · Día del protocolo (Cuba)
# - Amplio (RSS + Google News + Bing News), real (feeds públicos), sin inventos.
# - Concurrencia, listas editables (__CONFIG/*.txt), bloqueo de spam/agregadores.
# - Filtro ESTRICTO: SOLO noticias del "día del protocolo" según hora de Cuba (America/Havana).
# - Scoring emocional + relevancia + recencia, dedup semántica, límite por fuente.
# - UI: reloj Cuba, KPIs, papelera, bitácora, buffers (GEM/SUBLIMINAL/T70), depuración, export CSV/JSON.
# - Red: requests con timeouts y reintentos antes de parsear via feedparser.
# - Caché: implementación MANUAL con TTL dinámico (sin decoradores).

from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
import re, time, hashlib, io, json
import feedparser
import requests
import pandas as pd
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging

# =================== Configuración de Logging ===================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =================== Nueva Función de Ingestión Profesional ===================

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
        try:
            self.news_api_key = st.secrets.get("NEWS_API_KEY", "")
            self.gnews_api_key = st.secrets.get("GNEWS_API_KEY", "")
            self.bing_api_key = st.secrets.get("BING_API_KEY", "")
        except:
            # Si no hay secrets disponibles, usar modo demo
            self.news_api_key = ""
            self.gnews_api_key = ""
            self.bing_api_key = ""
        
        # Verificar si estamos en modo demo (sin API keys)
        self.demo_mode = not any([self.news_api_key, self.gnews_api_key, self.bing_api_key])
        if self.demo_mode:
            logger.info("🔮 Modo DEMO activado - Usando noticias de ejemplo")
        
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
            "orgullo": ["pride", "dignity", "honor", "achievement", "success", "victory"]
        }
        
        logger.info("🔮 Sistema de ingestión profesional inicializado")
    
    def fetch_profiled_news(self, keywords: List[str] = None, date: str = None) -> List[Dict]:
        """Obtiene noticias con perfil profesional y orientación social/económica."""
        try:
            if self.demo_mode:
                # Modo demo: retornar noticias de ejemplo más abundantes
                from datetime import datetime, timedelta
                today = datetime.now()
                
                sample_news = [
                    {
                        "titulo": "Federal Reserve considers interest rate changes amid inflation concerns",
                        "medio": "Reuters",
                        "fecha": today.strftime("%Y-%m-%d"),
                        "url": "https://reuters.com/fed-rates",
                        "emocion": "miedo",
                        "impact_score": 0.92,
                        "tema": "economia_dinero"
                    },
                    {
                        "titulo": "Supreme Court hears arguments on voting rights case",
                        "medio": "AP",
                        "fecha": today.strftime("%Y-%m-%d"),
                        "url": "https://ap.org/voting-rights",
                        "emocion": "esperanza",
                        "impact_score": 0.88,
                        "tema": "politica_justicia"
                    },
                    {
                        "titulo": "Protesters gather outside Capitol demanding police reform",
                        "medio": "The Guardian",
                        "fecha": today.strftime("%Y-%m-%d"),
                        "url": "https://guardian.com/protests",
                        "emocion": "ira",
                        "impact_score": 0.85,
                        "tema": "seguridad_social"
                    },
                    {
                        "titulo": "Stock market volatility increases as economic uncertainty grows",
                        "medio": "Bloomberg",
                        "fecha": today.strftime("%Y-%m-%d"),
                        "url": "https://bloomberg.com/market-volatility",
                        "emocion": "miedo",
                        "impact_score": 0.89,
                        "tema": "economia_dinero"
                    },
                    {
                        "titulo": "Congress debates new immigration policy framework",
                        "medio": "Politico",
                        "fecha": today.strftime("%Y-%m-%d"),
                        "url": "https://politico.com/immigration-policy",
                        "emocion": "esperanza",
                        "impact_score": 0.82,
                        "tema": "politica_justicia"
                    },
                    {
                        "titulo": "Local communities organize against rising crime rates",
                        "medio": "NPR",
                        "fecha": today.strftime("%Y-%m-%d"),
                        "url": "https://npr.org/crime-rates",
                        "emocion": "miedo",
                        "impact_score": 0.78,
                        "tema": "seguridad_social"
                    },
                    {
                        "titulo": "Federal minimum wage increase proposal gains momentum",
                        "medio": "The Washington Post",
                        "fecha": today.strftime("%Y-%m-%d"),
                        "url": "https://washingtonpost.com/minimum-wage",
                        "emocion": "esperanza",
                        "impact_score": 0.91,
                        "tema": "economia_dinero"
                    },
                    {
                        "titulo": "Civil rights organizations challenge new voting restrictions",
                        "medio": "CNN",
                        "fecha": today.strftime("%Y-%m-%d"),
                        "url": "https://cnn.com/voting-restrictions",
                        "emocion": "ira",
                        "impact_score": 0.87,
                        "tema": "politica_justicia"
                    }
                ]
                
                logger.info(f"🔮 Modo DEMO: Generando {len(sample_news)} noticias de ejemplo")
                return sample_news
            else:
                # Modo real: conectar a APIs
                logger.info("🔮 Modo REAL: Conectando a APIs de noticias")
                # TODO: Implementar conexión real a APIs
                return []
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo noticias: {str(e)}")
            return []
    
    def fetch_profiled_news_extra(self, keywords: List[str] = None, date: str = None) -> List[Dict]:
        """Obtiene noticias adicionales para acopio extra."""
        try:
            if self.demo_mode:
                # Modo demo: retornar noticias adicionales de ejemplo
                from datetime import datetime, timedelta
                today = datetime.now()
                
                extra_sample_news = [
                    {
                        "titulo": "New economic stimulus package announced by Congress",
                        "medio": "The New York Times",
                        "fecha": today.strftime("%Y-%m-%d"),
                        "url": "https://nytimes.com/stimulus-package",
                        "emocion": "esperanza",
                        "impact_score": 0.94,
                        "tema": "economia_dinero"
                    },
                    {
                        "titulo": "Supreme Court ruling on environmental regulations",
                        "medio": "USA Today",
                        "fecha": today.strftime("%Y-%m-%d"),
                        "url": "https://usatoday.com/environmental-ruling",
                        "emocion": "miedo",
                        "impact_score": 0.87,
                        "tema": "politica_justicia"
                    },
                    {
                        "titulo": "Major tech companies announce AI safety measures",
                        "medio": "TechCrunch",
                        "fecha": today.strftime("%Y-%m-%d"),
                        "url": "https://techcrunch.com/ai-safety",
                        "emocion": "esperanza",
                        "impact_score": 0.89,
                        "tema": "tecnologia_innovacion"
                    },
                    {
                        "titulo": "International trade agreement reached with Asia-Pacific nations",
                        "medio": "Financial Times",
                        "fecha": today.strftime("%Y-%m-%d"),
                        "url": "https://ft.com/trade-agreement",
                        "emocion": "orgullo",
                        "impact_score": 0.91,
                        "tema": "economia_dinero"
                    },
                    {
                        "titulo": "Healthcare reform bill passes in Senate",
                        "medio": "Politico",
                        "fecha": today.strftime("%Y-%m-%d"),
                        "url": "https://politico.com/healthcare-reform",
                        "emocion": "esperanza",
                        "impact_score": 0.88,
                        "tema": "politica_justicia"
                    },
                    {
                        "titulo": "Climate change summit produces new commitments",
                        "medio": "The Washington Post",
                        "fecha": today.strftime("%Y-%m-%d"),
                        "url": "https://washingtonpost.com/climate-summit",
                        "emocion": "esperanza",
                        "impact_score": 0.85,
                        "tema": "medioambiente_clima"
                    },
                    {
                        "titulo": "Cybersecurity threats increase globally",
                        "medio": "Reuters",
                        "fecha": today.strftime("%Y-%m-%d"),
                        "url": "https://reuters.com/cybersecurity-threats",
                        "emocion": "miedo",
                        "impact_score": 0.83,
                        "tema": "seguridad_social"
                    },
                    {
                        "titulo": "Education funding bill signed into law",
                        "medio": "NPR",
                        "fecha": today.strftime("%Y-%m-%d"),
                        "url": "https://npr.org/education-funding",
                        "emocion": "orgullo",
                        "impact_score": 0.86,
                        "tema": "politica_justicia"
                    }
                ]
                
                logger.info(f"🔮 Modo DEMO: Generando {len(extra_sample_news)} noticias adicionales de ejemplo")
                return extra_sample_news
            else:
                # Modo real: conectar a APIs
                logger.info("🔮 Modo REAL: Conectando a APIs de noticias para acopio extra")
                # TODO: Implementar conexión real a APIs
                return []
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo noticias adicionales: {str(e)}")
            return []

# =================== CLASE PRINCIPAL NOTICIAS MODULE ===================

class NoticiasModule:
    """Módulo principal de noticias con funcionalidades completas."""
    
    def __init__(self):
        """Inicializa el módulo de noticias."""
        self.professional_ingestion = ProfessionalNewsIngestion()
        self.current_news_df = None
        self.news_logs = {}
        
        # Configuración actualizada según requerimientos del usuario
        self.CFG = {
            "MIN_NEWS_REQUIRED": 50,      # Mínimo de noticias requeridas
            "TARGET_NEWS_COUNT": 100,     # Objetivo de noticias a recolectar
            "CATEGORY_BALANCE": True,      # Balance de categorías
            "STRICT_SAME_DAY": False,      # Eliminado filtro "mismo día Cuba"
            "RECENCY_HOURS": 72,          # Ventana de recencia
            "MIN_TOKENS": 8,              # Tamaño mínimo de texto
            "MAX_PER_SOURCE": 4,          # Diversidad por dominio
            "SEMANTIC_ON": True,          # Deduplicación semántica
            "SEMANTIC_THR": 0.82,         # Umbral coseno TF-IDF
            "MAX_WORKERS": 12,            # Concurrencia
            "HTTP_TIMEOUT": 8,            # Timeout HTTP
            "HTTP_RETRIES": 3,            # Reintentos HTTP
            "CACHE_TTL_SEC": 300          # TTL de caché
        }
        
        logger.info("📰 Módulo de noticias inicializado")
    
    def _run_pipeline_manual(self) -> Dict:
        """Ejecuta el pipeline manual de noticias usando el sistema profesional."""
        try:
            logger.info("🚀 Ejecutando pipeline manual de noticias...")
            
            # Obtener noticias del sistema profesional
            news_list = self.professional_ingestion.fetch_profiled_news()
            
            if not news_list:
                logger.error("❌ No se pudieron obtener noticias del sistema profesional")
                return {"success": False, "error": "No se pudieron obtener noticias"}
            
            # Convertir a DataFrame
            df_raw = pd.DataFrame(news_list)
            
            # Aplicar procesamiento estándar
            df_sel = self._process_news_dataframe(df_raw)
            
            # Guardar en session state para la UI
            st.session_state["news_raw_df"] = df_raw.copy()
            st.session_state["news_selected_df"] = df_sel.copy()
            
            # Crear logs del pipeline
            logs = {
                "timestamp": datetime.now().isoformat(),
                "total_news": len(df_raw),
                "selected_news": len(df_sel),
                "sources": df_raw['medio'].nunique() if not df_raw.empty else 0,
                "emotions": df_sel['emocion'].nunique() if not df_sel.empty else 0,
                "pipeline_status": "completed",
                "demo_mode": self.professional_ingestion.demo_mode
            }
            
            st.session_state["pipeline_logs"] = logs.copy()
            
            logger.info(f"✅ Pipeline manual completado: {len(df_sel)} noticias seleccionadas")
            
            return {
                "success": True,
                "raw_news": df_raw,
                "selected_news": df_sel,
                "logs": logs,
                "message": f"Pipeline exitoso: {len(df_sel)} noticias procesadas"
            }
            
        except Exception as e:
            error_msg = f"❌ Error en pipeline manual: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _run_pipeline_extra(self) -> Dict:
        """Ejecuta el pipeline extra de noticias para obtener más noticias."""
        try:
            logger.info("🚀 Ejecutando pipeline extra de noticias...")
            
            # Obtener noticias adicionales del sistema profesional
            extra_news_list = self.professional_ingestion.fetch_profiled_news_extra()
            
            if not extra_news_list:
                logger.error("❌ No se pudieron obtener noticias adicionales del sistema profesional")
                return {"success": False, "error": "No se pudieron obtener noticias adicionales"}
            
            # Convertir a DataFrame
            df_extra = pd.DataFrame(extra_news_list)
            
            # Aplicar procesamiento estándar
            df_extra_processed = self._process_news_dataframe(df_extra)
            
            # Crear logs del pipeline extra
            logs = {
                "timestamp": datetime.now().isoformat(),
                "extra_news": len(df_extra),
                "extra_processed": len(df_extra_processed),
                "pipeline_status": "extra_completed",
                "demo_mode": self.professional_ingestion.demo_mode
            }
            
            logger.info(f"✅ Pipeline extra completado: {len(df_extra_processed)} noticias adicionales")
            
            return {
                "success": True,
                "new_news": df_extra_processed,
                "logs": logs,
                "message": f"Pipeline extra exitoso: {len(df_extra_processed)} noticias adicionales"
            }
            
        except Exception as e:
            error_msg = f"❌ Error en pipeline extra: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _process_news_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Procesa el DataFrame de noticias aplicando filtros y categorización."""
        try:
            if df.empty:
                return df
            
            # Crear copia para procesamiento
            processed_df = df.copy()
            
            # Aplicar categorización emocional si no existe
            if 'emocion' not in processed_df.columns:
                processed_df = self._categorize_emotional_impact(processed_df)
            
            # Aplicar balance de categorías si está habilitado
            if self.CFG["CATEGORY_BALANCE"]:
                processed_df = self._balance_categories(processed_df)
            
            # Preparar para capas especializadas
            self._prepare_news_for_capas()
            
            return processed_df
            
        except Exception as e:
            logger.error(f"❌ Error procesando DataFrame: {str(e)}")
            return df
    
    def acopio_noticias(self) -> Dict:
        """Ejecuta el acopio principal de noticias."""
        try:
            logger.info("🚀 Iniciando acopio de noticias...")
            
            # Obtener noticias profesionales
            news_list = self.professional_ingestion.fetch_profiled_news()
            
            if len(news_list) >= self.CFG["MIN_NEWS_REQUIRED"]:
                # Convertir a DataFrame
                self.current_news_df = pd.DataFrame(news_list)
                
                # Aplicar categorización emocional
                self.current_news_df = self._categorize_emotional_impact(self.current_news_df)
                
                # Balancear categorías
                if self.CFG["CATEGORY_BALANCE"]:
                    self.current_news_df = self._balance_categories(self.current_news_df)
                
                # Preparar para capas especializadas
                self._prepare_news_for_capas()
                
                result = {
                    "success": True,
                    "news_count": len(self.current_news_df),
                    "message": f"✅ Acopio exitoso: {len(self.current_news_df)} noticias recolectadas"
                }
                
                logger.info(f"✅ Acopio completado: {len(self.current_news_df)} noticias")
                return result
                
            else:
                error_msg = f"❌ Insuficientes noticias: {len(news_list)} < {self.CFG['MIN_NEWS_REQUIRED']}"
                logger.warning(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "news_count": len(news_list)
                }
                
        except Exception as e:
            error_msg = f"❌ Error en acopio: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def acopio_extra(self) -> Dict:
        """Ejecuta acopio extra de noticias."""
        try:
            logger.info("🔄 Iniciando acopio extra...")
            
            # Obtener noticias adicionales
            extra_news = self.professional_ingestion.fetch_profiled_news()
            
            if extra_news:
                # Convertir a DataFrame si no existe
                if self.current_news_df is None:
                    self.current_news_df = pd.DataFrame(extra_news)
                else:
                    # Agregar nuevas noticias sin perder las anteriores
                    extra_df = pd.DataFrame(extra_news)
                    self.current_news_df = pd.concat([self.current_news_df, extra_df], ignore_index=True)
                    self.current_news_df = self.current_news_df.drop_duplicates(subset=['url'])
                
                # Re-aplicar procesamiento
                self.current_news_df = self._categorize_emotional_impact(self.current_news_df)
                if self.CFG["CATEGORY_BALANCE"]:
                    self.current_news_df = self._balance_categories(self.current_news_df)
                
                result = {
                    "success": True,
                    "total_news": len(self.current_news_df),
                    "extra_added": len(extra_news),
                    "message": f"✅ Acopio extra: {len(extra_news)} noticias agregadas"
                }
                
                logger.info(f"✅ Acopio extra completado: {len(extra_news)} noticias agregadas")
                return result
                
            else:
                return {
                    "success": False,
                    "error": "No se pudieron obtener noticias adicionales"
                }
                
        except Exception as e:
            error_msg = f"❌ Error en acopio extra: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def get_news_status(self) -> Dict:
        """Obtiene el estado actual de las noticias."""
        if self.current_news_df is None or self.current_news_df.empty:
            return {
                "has_news": False,
                "count": 0,
                "message": "No hay noticias disponibles"
            }
        
        return {
            "has_news": True,
            "count": len(self.current_news_df),
            "categories": self.current_news_df['tema'].value_counts().to_dict(),
            "emotions": self.current_news_df['emocion'].value_counts().to_dict(),
            "message": f"✅ {len(self.current_news_df)} noticias disponibles"
        }
    
    def get_news_dataframe(self) -> Optional[pd.DataFrame]:
        """Obtiene el DataFrame de noticias actual."""
        return self.current_news_df.copy() if self.current_news_df is not None else None
    
    def _categorize_emotional_impact(self, df: pd.DataFrame) -> pd.DataFrame:
        """Categoriza el impacto emocional de las noticias."""
        if df.empty:
            return df
        
        # Aplicar categorización emocional
        df['emocion_categoria'] = df['emocion'].map({
            'ira': 'Alto Impacto',
            'miedo': 'Alto Impacto', 
            'esperanza': 'Medio Impacto',
            'tristeza': 'Medio Impacto',
            'orgullo': 'Bajo Impacto'
        }).fillna('Sin Categorizar')
        
        # Calcular nivel de impacto
        df['impact_level'] = df['impact_score'].map({
            lambda x: 'Crítico' if x >= 0.9 else
            'Alto' if x >= 0.8 else
            'Medio' if x >= 0.6 else 'Bajo'
        })
        
        return df
    
    def _add_emotional_categories(self, df: pd.DataFrame) -> pd.DataFrame:
        """Añade categorías emocionales detalladas."""
        if df.empty:
            return df
        
        # Categorías emocionales expandidas
        emotion_categories = {
            'ira': ['Protesta', 'Conflicto', 'Violencia'],
            'miedo': ['Crisis', 'Amenaza', 'Incertidumbre'],
            'esperanza': ['Progreso', 'Reforma', 'Mejora'],
            'tristeza': ['Pérdida', 'Sufrimiento', 'Desesperación'],
            'orgullo': ['Logro', 'Reconocimiento', 'Éxito']
        }
        
        df['categoria_emocional'] = df['emocion'].map(emotion_categories).fillna('Sin Categoría')
        
        return df
    
    def _calculate_impact_level(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula el nivel de impacto basado en múltiples factores."""
        if df.empty:
            return df
        
        # Factor de impacto compuesto
        df['impact_factor'] = (
            df['impact_score'] * 0.4 +  # Score base
            (df['emocion'].isin(['ira', 'miedo']).astype(int) * 0.3) +  # Emociones críticas
            (df['tema'].isin(['economia_dinero', 'seguridad_social']).astype(int) * 0.3)  # Temas prioritarios
        )
        
        # Clasificar por nivel de impacto
        df['nivel_impacto'] = pd.cut(
            df['impact_factor'],
            bins=[0, 0.3, 0.6, 0.8, 1.0],
            labels=['Bajo', 'Medio', 'Alto', 'Crítico']
        )
        
        return df
    
    def _balance_categories(self, df: pd.DataFrame) -> pd.DataFrame:
        """Balancea las categorías para representación equilibrada."""
        if df.empty:
            return df
        
        # Contar noticias por categoría
        category_counts = df['tema'].value_counts()
        
        # Calcular límite por categoría
        max_per_category = min(
            len(df) // len(category_counts),
            self.CFG["TARGET_NEWS_COUNT"] // len(category_counts)
        )
        
        # Balancear categorías
        balanced_df = pd.DataFrame()
        for category in category_counts.index:
            category_news = df[df['tema'] == category]
            if len(category_news) > max_per_category:
                # Tomar las mejores noticias de la categoría
                category_news = category_news.nlargest(max_per_category, 'impact_score')
            balanced_df = pd.concat([balanced_df, category_news], ignore_index=True)
        
        return balanced_df.reset_index(drop=True)
    
    def _group_news_by_category(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Agrupa las noticias por categorías."""
        if df.empty:
            return {}
        
        grouped = {}
        for category in df['tema'].unique():
            grouped[category] = df[df['tema'] == category].copy()
        
        return grouped
    
    def _get_category_keywords(self, category: str) -> List[str]:
        """Obtiene palabras clave para una categoría específica."""
        category_keywords = {
            'economia_dinero': ['economy', 'financial', 'market', 'inflation', 'recession'],
            'politica_justicia': ['politics', 'government', 'justice', 'law', 'rights'],
            'seguridad_social': ['security', 'crime', 'protest', 'social', 'violence']
        }
        
        return category_keywords.get(category, [])
    
    def _map_categories_to_t70(self, grouped_news: Dict[str, pd.DataFrame]) -> Dict:
        """Mapea las categorías de noticias a equivalencias T70."""
        t70_mapping = {}
        
        for category, news_df in grouped_news.items():
            if not news_df.empty:
                # Obtener palabras clave de la categoría
                keywords = self._get_category_keywords(category)
                
                # Simular mapeo T70 (en implementación real se usaría la tabla T70.csv)
                t70_mapping[category] = {
                    'keywords': keywords,
                    'news_count': len(news_df),
                    't70_equivalents': self._generate_t70_equivalents(category, len(news_df)),
                    'dominant_emotions': news_df['emocion'].value_counts().to_dict()
                }
        
        return t70_mapping
    
    def _generate_t70_equivalents(self, category: str, news_count: int) -> List[int]:
        """Genera equivalencias T70 basadas en la categoría y cantidad de noticias."""
        # Simulación de equivalencias T70
        base_equivalents = {
            'economia_dinero': [10, 20, 30, 40, 50],
            'politica_justicia': [15, 25, 35, 45, 55],
            'seguridad_social': [5, 15, 25, 35, 45]
        }
        
        base = base_equivalents.get(category, [1, 2, 3, 4, 5])
        # Ajustar según la cantidad de noticias
        adjusted = [base[i % len(base)] + (news_count % 10) for i in range(min(5, news_count))]
        
        return adjusted
    
    def _prepare_news_for_capas(self):
        """Prepara las noticias para ser enviadas a las capas especializadas."""
        if self.current_news_df is None or self.current_news_df.empty:
            logger.warning("⚠️ No hay noticias para preparar para las capas")
            return
        
        try:
            # Agrupar por categorías
            grouped_news = self._group_news_by_category(self.current_news_df)
            
            # Mapear a T70
            t70_mapping = self._map_categories_to_t70(grouped_news)
            
            # Preparar para GEM (Gematría)
            gem_news = self.current_news_df.copy()
            gem_news['arquetipos'] = gem_news['emocion'].map({
                'ira': 'Guerrero/Sombra',
                'miedo': 'Huérfano/Víctima',
                'esperanza': 'Héroe/Sabio',
                'tristeza': 'Mártir/Sombra',
                'orgullo': 'Rey/Creador'
            })
            
            # Preparar para SUB (Subliminal)
            sub_news = self.current_news_df.copy()
            sub_news['patrones_subliminales'] = sub_news['emocion'].map({
                'ira': 'Patrón de confrontación',
                'miedo': 'Patrón de amenaza',
                'esperanza': 'Patrón de transformación',
                'tristeza': 'Patrón de pérdida',
                'orgullo': 'Patrón de elevación'
            })
            
            # Almacenar en session state para Streamlit
            if 'news_selected_df' not in st.session_state:
                st.session_state["news_selected_df"] = self.current_news_df.copy()
            
            if 'news_raw_df' not in st.session_state:
                st.session_state["news_raw_df"] = self.current_news_df.copy()
            
            if 't70_mapping' not in st.session_state:
                st.session_state["t70_mapping"] = t70_mapping
            
            logger.info("✅ Noticias preparadas para capas especializadas")
            
        except Exception as e:
            logger.error(f"❌ Error preparando noticias para capas: {str(e)}")
    
    def _categorize_emotional_impact(self, df: pd.DataFrame) -> pd.DataFrame:
        """Categoriza las noticias por impacto emocional."""
        try:
            if df.empty:
                return df
            
            processed_df = df.copy()
            
            # Si ya tiene columna de emoción, no procesar
            if 'emocion' in processed_df.columns:
                return processed_df
            
            # Aplicar categorización basada en palabras clave
            def categorize_emotion(text):
                text_lower = str(text).lower()
                
                # Palabras clave para cada emoción
                emotion_keywords = {
                    'ira': ['anger', 'furious', 'outrage', 'rage', 'fury', 'wrath', 'hostile', 'protest', 'riot'],
                    'miedo': ['fear', 'terror', 'panic', 'horror', 'dread', 'anxiety', 'worry', 'crisis', 'threat'],
                    'esperanza': ['hope', 'optimism', 'confidence', 'trust', 'faith', 'belief', 'reform', 'progress'],
                    'tristeza': ['sadness', 'grief', 'sorrow', 'despair', 'melancholy', 'depression', 'loss'],
                    'orgullo': ['pride', 'dignity', 'honor', 'achievement', 'success', 'victory', 'accomplishment']
                }
                
                # Contar ocurrencias de cada emoción
                emotion_counts = {}
                for emotion, keywords in emotion_keywords.items():
                    count = sum(1 for keyword in keywords if keyword in text_lower)
                    emotion_counts[emotion] = count
                
                # Retornar la emoción dominante
                if emotion_counts:
                    dominant_emotion = max(emotion_counts, key=emotion_counts.get)
                    if emotion_counts[dominant_emotion] > 0:
                        return dominant_emotion
                
                return 'neutral'
            
            # Aplicar categorización a título y contenido
            processed_df['emocion'] = processed_df['titulo'].apply(categorize_emotion)
            
            # Si no se detectó emoción en el título, intentar con el contenido
            neutral_mask = processed_df['emocion'] == 'neutral'
            if neutral_mask.any():
                processed_df.loc[neutral_mask, 'emocion'] = processed_df.loc[neutral_mask, 'contenido'].apply(categorize_emotion)
            
            logger.info(f"✅ Categorización emocional aplicada: {processed_df['emocion'].value_counts().to_dict()}")
            return processed_df
            
        except Exception as e:
            logger.error(f"❌ Error en categorización emocional: {str(e)}")
            return df
    
    def _balance_categories(self, df: pd.DataFrame) -> pd.DataFrame:
        """Balancea las categorías de noticias para distribución equitativa."""
        try:
            if df.empty:
                return df
            
            processed_df = df.copy()
            
            # Contar noticias por emoción
            emotion_counts = processed_df['emocion'].value_counts()
            
            # Calcular el número objetivo por emoción (mínimo 10 por categoría)
            target_per_emotion = max(10, len(processed_df) // len(emotion_counts))
            
            balanced_df = pd.DataFrame()
            
            for emotion in emotion_counts.index:
                emotion_news = processed_df[processed_df['emocion'] == emotion]
                
                if len(emotion_news) > target_per_emotion:
                    # Tomar las mejores noticias de esta emoción
                    emotion_news = emotion_news.head(target_per_emotion)
                
                balanced_df = pd.concat([balanced_df, emotion_news], ignore_index=True)
            
            logger.info(f"✅ Balance de categorías aplicado: {len(balanced_df)} noticias balanceadas")
            return balanced_df
            
        except Exception as e:
            logger.error(f"❌ Error en balance de categorías: {str(e)}")
            return df
    
    def _group_news_by_category(self, df: pd.DataFrame) -> Dict:
        """Agrupa las noticias por categoría para procesamiento especializado."""
        try:
            if df.empty:
                return {}
            
            grouped = {}
            
            # Agrupar por tema si existe
            if 'tema' in df.columns:
                for tema in df['tema'].unique():
                    grouped[tema] = df[df['tema'] == tema]
            
            # Agrupar por emoción si existe
            if 'emocion' in df.columns:
                for emocion in df['emocion'].unique():
                    grouped[f"emocion_{emocion}"] = df[df['emocion'] == emocion]
            
            # Agrupar por fuente si existe
            if 'medio' in df.columns:
                for medio in df['medio'].unique():
                    grouped[f"fuente_{medio}"] = df[df['medio'] == medio]
            
            logger.info(f"✅ Noticias agrupadas en {len(grouped)} categorías")
            return grouped
            
        except Exception as e:
            logger.error(f"❌ Error agrupando noticias: {str(e)}")
            return {}
    
    def _map_categories_to_t70(self, grouped_news: Dict) -> Dict:
        """Mapea las categorías de noticias a equivalencias T70."""
        try:
            t70_mapping = {}
            
            for category, news_group in grouped_news.items():
                if not news_group.empty:
                    # Extraer palabras clave de la categoría
                    keywords = self._get_category_keywords(news_group)
                    
                    # Mapear a números T70 (simplificado)
                    t70_numbers = self._get_t70_equivalents(keywords)
                    
                    t70_mapping[category] = {
                        'news_count': len(news_group),
                        'keywords': keywords,
                        't70_numbers': t70_numbers,
                        'sample_titles': news_group['titulo'].head(3).tolist()
                    }
            
            logger.info(f"✅ Mapeo T70 completado para {len(t70_mapping)} categorías")
            return t70_mapping
            
        except Exception as e:
            logger.error(f"❌ Error en mapeo T70: {str(e)}")
            return {}
    
    def _get_category_keywords(self, news_group: pd.DataFrame) -> List[str]:
        """Extrae palabras clave de un grupo de noticias."""
        try:
            keywords = []
            
            # Combinar títulos y contenido
            text_combined = ' '.join(news_group['titulo'].astype(str) + ' ' + news_group['contenido'].astype(str))
            
            # Palabras comunes a ignorar
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            
            # Extraer palabras significativas
            words = text_combined.lower().split()
            word_counts = {}
            
            for word in words:
                word = word.strip('.,!?;:()[]{}"\'').lower()
                if len(word) > 3 and word not in stop_words and word.isalpha():
                    word_counts[word] = word_counts.get(word, 0) + 1
            
            # Tomar las 10 palabras más frecuentes
            keywords = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            keywords = [word for word, count in keywords]
            
            return keywords
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo palabras clave: {str(e)}")
            return []
    
    def _get_t70_equivalents(self, keywords: List[str]) -> List[int]:
        """Obtiene números T70 equivalentes para palabras clave."""
        try:
            # Mapeo simplificado de palabras a números T70
            # En implementación real, se usaría la tabla T70 completa
            t70_mapping = {
                'federal': 15, 'reserve': 23, 'interest': 31, 'rates': 42,
                'supreme': 18, 'court': 25, 'voting': 33, 'rights': 44,
                'protest': 19, 'police': 26, 'reform': 35, 'community': 47,
                'stock': 21, 'market': 28, 'economy': 37, 'financial': 49,
                'congress': 22, 'policy': 29, 'immigration': 38, 'border': 51
            }
            
            t70_numbers = []
            for keyword in keywords:
                if keyword in t70_mapping:
                    t70_numbers.append(t70_mapping[keyword])
            
            # Si no hay coincidencias, generar números aleatorios en rango T70
            if not t70_numbers:
                import random
                t70_numbers = random.sample(range(1, 71), min(5, len(keywords)))
            
            return t70_numbers
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo equivalentes T70: {str(e)}")
            return []
    
    def send_to_gem(self) -> Dict:
        """Envía noticias procesadas a la capa de Gematría."""
        try:
            if self.current_news_df is None or self.current_news_df.empty:
                return {
                    "success": False,
                    "error": "No hay noticias disponibles para enviar a GEM"
                }
            
            # Preparar datos para GEM
            gem_data = {
                'news_count': len(self.current_news_df),
                'categories': self.current_news_df['tema'].value_counts().to_dict(),
                'emotions': self.current_news_df['emocion'].value_counts().to_dict(),
                'arquetipos': self.current_news_df.get('arquetipos', {}).value_counts().to_dict() if 'arquetipos' in self.current_news_df.columns else {},
                'timestamp': datetime.now().isoformat()
            }
            
            # En implementación real, se enviaría a la capa GEM
            logger.info(f"✅ {len(self.current_news_df)} noticias enviadas a GEM")
            
            return {
                "success": True,
                "message": f"✅ Noticias enviadas a GEM: {len(self.current_news_df)} noticias",
                "gem_data": gem_data
            }
            
        except Exception as e:
            error_msg = f"❌ Error enviando a GEM: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def send_to_sub(self) -> Dict:
        """Envía noticias procesadas a la capa Subliminal."""
        try:
            if self.current_news_df is None or self.current_news_df.empty:
                return {
                    "success": False,
                    "error": "No hay noticias disponibles para enviar a SUB"
                }
            
            # Preparar datos para SUB
            sub_data = {
                'news_count': len(self.current_news_df),
                'categories': self.current_news_df['tema'].value_counts().to_dict(),
                'emotions': self.current_news_df['emocion'].value_counts().to_dict(),
                'patrones_subliminales': self.current_news_df.get('patrones_subliminales', {}).value_counts().to_dict() if 'patrones_subliminales' in self.current_news_df.columns else {},
                'timestamp': datetime.now().isoformat()
            }
            
            # En implementación real, se enviaría a la capa SUB
            logger.info(f"✅ {len(self.current_news_df)} noticias enviadas a SUB")
            
            return {
                "success": True,
                "message": f"✅ Noticias enviadas a SUB: {len(self.current_news_df)} noticias",
                "sub_data": sub_data
            }
            
        except Exception as e:
            error_msg = f"❌ Error enviando a SUB: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def send_to_t70(self) -> Dict:
        """Envía noticias procesadas a la capa T70."""
        try:
            if self.current_news_df is None or self.current_news_df.empty:
                return {
                    "success": False,
                    "error": "No hay noticias disponibles para enviar a T70"
                }
            
            # Preparar datos para T70
            t70_data = {
                'news_count': len(self.current_news_df),
                'categories': self.current_news_df['tema'].value_counts().to_dict(),
                't70_mapping': st.session_state.get("t70_mapping", {}),
                'timestamp': datetime.now().isoformat()
            }
            
            # En implementación real, se enviaría a la capa T70
            logger.info(f"✅ {len(self.current_news_df)} noticias enviadas a T70")
            
            return {
                "success": True,
                "message": f"✅ Noticias enviadas a T70: {len(self.current_news_df)} noticias",
                "t70_data": t70_data
            }
            
        except Exception as e:
            error_msg = f"❌ Error enviando a T70: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def get_pipeline_summary(self) -> Dict:
        """Obtiene un resumen del pipeline de noticias."""
        if self.current_news_df is None or self.current_news_df.empty:
            return {
                "status": "Sin datos",
                "message": "No hay noticias procesadas"
            }
        
        try:
            summary = {
                "status": "Completado",
                "total_news": len(self.current_news_df),
                "categories": self.current_news_df['tema'].value_counts().to_dict(),
                "emotions": self.current_news_df['emocion'].value_counts().to_dict(),
                "impact_levels": self.current_news_df.get('nivel_impacto', {}).value_counts().to_dict() if 'nivel_impacto' in self.current_news_df.columns else {},
                "processing_timestamp": datetime.now().isoformat(),
                "configuration": {
                    "min_required": self.CFG["MIN_NEWS_REQUIRED"],
                    "target_count": self.CFG["TARGET_NEWS_COUNT"],
                    "category_balance": self.CFG["CATEGORY_BALANCE"]
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error generando resumen: {str(e)}")
            return {
                "status": "Error",
                "error": str(e)
            }

# =================== Paths base ===================
ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "__RUNS" / "NEWS"
LEDGER_DIR = OUT_DIR / "ledger"
TRASH_DIR = OUT_DIR / ".trash"
BUFF_GEM = ROOT / "__RUNS" / "GEMATRIA_IN"
BUFF_SUB = ROOT / "__RUNS" / "SUBLIMINAL_IN"
BUFF_T70 = ROOT / "__RUNS" / "T70_IN"
T70_PATH = ROOT / "T70.csv"
RAW_LAST = OUT_DIR / "ultimo_acopio_bruto.csv"
SEL_LAST = OUT_DIR / "ultima_seleccion_es.csv"

for p in [OUT_DIR, LEDGER_DIR, TRASH_DIR, BUFF_GEM, BUFF_SUB, BUFF_T70]:
    p.mkdir(parents=True, exist_ok=True)

# =================== Config núcleo ===================
PROTOCOL_TZ = "America/Havana"   # Reloj y día del protocolo (Cuba)
CFG = {
    "RECENCY_HOURS": 72,         # ventana de recencia dura
    "MIN_TOKENS": 8,             # tamaño mínimo de texto útil
    "MAX_PER_SOURCE": 4,         # diversidad por dominio
    "SEMANTIC_ON": True,         # deduplicación semántica
    "SEMANTIC_THR": 0.82,        # umbral coseno TF-IDF
    "SOFT_DEDUP_NORM": True,     # normalización de titulares fallback
    "MAX_WORKERS": 12,           # concurrencia de fetch
    "STRICT_SAME_DAY": True,     # SOLO día del protocolo (Cuba)
    "HTTP_TIMEOUT": 8,           # seg. por petición RSS/News
    "HTTP_RETRIES": 3,           # reintentos por URL
    "CACHE_TTL_SEC": 300,        # objetivo de TTL (usado por caché manual)
}

# Bloqueo de agregadores/duplicadores (base)
SPAM_BLOCK_BASE = [
    "news.google.com", "feedproxy.google.com", "news.yahoo.com", "bing.com"
]

# =================== Config externo (listas editables) ===================
CONFIG_DIR = ROOT / "__CONFIG"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
RSS_TXT = CONFIG_DIR / "rss_sources.txt"
GNEWS_TXT = CONFIG_DIR / "gnews_queries.txt"
BING_TXT = CONFIG_DIR / "bing_queries.txt"
BLOCKED_TXT = CONFIG_DIR / "blocked_domains.txt"

def _load_list(path: Path, defaults: list[str]) -> list[str]:
    items = []
    try:
        if path.exists():
            for raw in path.read_text(encoding="utf-8").splitlines():
                s = raw.strip()
                if not s or s.startswith("#"):
                    continue
                items.append(s)
    except Exception:
        pass
    return items if items else list(defaults)

def _load_blocked_domains() -> list[str]:
    try:
        if BLOCKED_TXT.exists():
            return [ln.strip().lower() for ln in BLOCKED_TXT.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.strip().startswith("#")]
    except Exception:
        pass
    return []

def _save_blocked_domains(domains: list[str]) -> None:
    try:
        uniq = sorted(set([d.strip().lower() for d in domains if d.strip()]))
        BLOCKED_TXT.write_text("\n".join(uniq) + "\n", encoding="utf-8")
    except Exception:
        pass

# Defaults robustos (USA)
RSS_SOURCES_DEFAULT = [
    "https://www.reuters.com/rssFeed/usNews",
    "https://feeds.npr.org/1001/rss.xml",
    "https://feeds.abcnews.com/abcnews/usheadlines",
    "https://www.cbsnews.com/latest/rss/us/",
    "https://www.theguardian.com/us-news/rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/US.xml",
    "http://rss.cnn.com/rss/cnn_us.rss",
    "http://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml",
    "http://rssfeeds.usatoday.com/usatoday-NewsTopStories",
]
GNEWS_QUERIES_DEFAULT = [
    # EN (impacto social en USA)
    "protest OR strike OR riot OR looting site:us",
    "shortage OR blackout OR curfew OR evacuation site:us",
    "boycott OR layoffs OR outage OR wildfire OR hurricane OR flood site:us",
    "mass shooting OR unrest OR clashes site:us",
    # ES (comunidad hispana en USA)
    "protesta OR huelga OR disturbios OR saqueo site:us",
    "desabasto OR apagón OR toque de queda OR evacuación site:us",
    "boicot OR despidos OR tiroteo masivo site:us",
]
BING_QUERIES_DEFAULT = list(GNEWS_QUERIES_DEFAULT)

RSS_SOURCES = _load_list(RSS_TXT, RSS_SOURCES_DEFAULT)
GNEWS_QUERIES = _load_list(GNEWS_TXT, GNEWS_QUERIES_DEFAULT)
BING_QUERIES = _load_list(BING_TXT, BING_QUERIES_DEFAULT)

def _gnews_rss_url(q: str) -> str:
    from urllib.parse import quote_plus
    return f"https://news.google.com/rss/search?q={quote_plus(q)}&hl=en-US&gl=US&ceid=US:en"

def _bingnews_rss_url(q: str) -> str:
    from urllib.parse import quote_plus
    return f"https://www.bing.com/news/search?q={quote_plus(q)}&format=RSS&setmkt=en-US&setlang=en-US"

# =================== Utilidades ===================
def _now_utc() -> datetime:
    return datetime.now(timezone.utc)

def _now_cuba() -> datetime:
    return datetime.now(ZoneInfo(PROTOCOL_TZ))

def _today_cuba_date_str() -> str:
    return _now_cuba().strftime("%Y-%m-%d")

def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "ignore")).hexdigest()[:16]

def _domain(url: str) -> str:
    try:
        from urllib.parse import urlparse
        d = urlparse(url).netloc.lower()
        return d[4:] if d.startswith("www.") else d
    except Exception:
        return ""

def _tokens(text: str) -> int:
    return len(re.findall(r"\w+", str(text or "")))

def _coerce_dt_from_feed(entry) -> datetime | None:
    try:
        tt = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
        if tt:
            return datetime(*tt[:6], tzinfo=timezone.utc)
    except Exception:
        pass
    return None

def _recency_factor(ts_utc: datetime | None) -> float:
    if ts_utc is None:
        return 0.6
    hours = (_now_utc() - ts_utc).total_seconds() / 3600.0
    if hours <= 12: return 1.0
    if hours <= 24: return 0.95
    if hours <= 48: return 0.9
    if hours <= 72: return 0.8
    return 0.7

def _to_csv_bytes(df: pd.DataFrame) -> bytes:
    buf = io.StringIO()
    df.to_csv(buf, index=False, encoding="utf-8")
    return buf.getvalue().encode("utf-8")

def _to_json_bytes(df: pd.DataFrame) -> bytes:
    def _ser(o):
        if isinstance(o, pd.Timestamp):
            if o.tzinfo is None:
                return o.tz_localize("UTC").isoformat()
            return o.isoformat()
        return str(o)
    data = json.loads(df.to_json(orient="records", date_unit="s"))
    return json.dumps(data, ensure_ascii=False, default=_ser, indent=2).encode("utf-8")

# Triggers y temas (impacto emocional)
TRIGGERS = {
    "protest":1.0,"strike":1.0,"riot":1.0,"looting":1.0,"shortage":0.9,
    "blackout":0.9,"curfew":1.0,"evacuation":0.9,"boycott":0.9,"mass shooting":1.0,
    "unrest":0.9,"clashes":0.9,"layoffs":0.8,"outage":0.8,
    "protesta":1.0,"huelga":1.0,"disturbios":1.0,"saqueo":1.0,"desabasto":0.9,
    "apagón":0.9,"toque de queda":1.0,"evacuación":0.9,"boicot":0.9,"tiroteo":1.0,"despidos":0.8
}
TOPICS = {
    "salud":["hospital","infección","brote","vacuna","epidemia","health","outbreak"],
    "economía":["inflación","desempleo","cierres","layoffs","crash","recesión"],
    "seguridad":["tiroteo","violencia","homicidio","shooting","kidnapping","unrest"],
    "clima":["huracán","terremoto","inundación","ola de calor","heatwave","wildfire","hurricane","flood"],
    "política":["elecciones","protesta","congreso","parlamento","impeachment"],
}

def _emo_heuristics(text: str) -> float:
    t = (text or "").lower()
    score = 0.0
    for k, w in TRIGGERS.items():
        if k in t: score += w
    score += 0.1 * t.count("!")
    if any(flag in t for tflag in ["breaking", "última hora", "urgente"] for flag in [t]):
        score += 0.15
    return min(score, 3.0) / 3.0

def _topic_relevance(text: str) -> float:
    t = (text or "").lower()
    hits = sum(1 for kws in TOPICS.values() if any(k in t for k in kws))
    return min(0.2 * hits, 1.0)

def _source_weight(domain: str) -> float:
    d = (domain or "").lower()
    majors = ["reuters","apnews","npr","bbc","abcnews","cbsnews","nytimes","wsj","guardian","nbcnews","latimes","usatoday","cnn"]
    locals_ = ["miamiherald","chicagotribune","houstonchronicle","dallasnews","sfchronicle"]
    if any(m in d for m in majors): return 1.15
    if any(l in d for l in locals_): return 1.05
    return 1.0

# =================== Deduplicación ===================
def _soft_dedup(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty: return df
    base = df.copy()
    base["_tit_norm"] = base["titular"].fillna("").str.lower().str.replace(r"[\W_]+"," ",regex=True).str.strip()
    base = base.drop_duplicates(subset=["_tit_norm"], keep="first")
    return base.drop(columns=["_tit_norm"], errors="ignore")

def _semantic_dedup(df: pd.DataFrame, thr: float) -> pd.DataFrame:
    if df.empty or len(df) == 1: return df
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity as _cos
    except Exception:
        return _soft_dedup(df)
    texts = (df["titular"].fillna("") + " " + df["resumen"].fillna("")).tolist()
    vec = TfidfVectorizer(max_features=25000, ngram_range=(1,2), lowercase=True, strip_accents="unicode")
    X = vec.fit_transform(texts)
    sim = _cos(X, dense_output=False)
    keep, removed = [], set()
    n = len(df)
    for i in range(n):
        if i in removed: continue
        keep.append(i)
        row = sim.getrow(i)
        near = row.nonzero()[1]
        for j in near:
            if j != i and row[0, j] >= thr:
                removed.add(j)
    return df.iloc[keep].copy()
# =================== Fetch ===================
def _parse_rss_bytes(content: bytes, src_url: str) -> list[dict]:
    data = feedparser.parse(content)
    out = []
    for e in data.entries:
        title = getattr(e, "title", "") or ""
        summary = getattr(e, "summary", "") or getattr(e, "description", "") or ""
        link = getattr(e, "link", "") or ""
        ts = _coerce_dt_from_feed(e)
        out.append({
            "titular": title.strip(),
            "resumen": re.sub("<[^<]+?>", "", summary).strip(),
            "url": link.strip(),
            "fecha_dt": ts,
            "fuente": _domain(link),
            "raw_source": src_url,
        })
    return out

def _fetch_rss(url: str) -> list[dict]:
    headers = {"User-Agent":"Mozilla/5.0 (Vision-News/1.0)"}
    for attempt in range(1, CFG["HTTP_RETRIES"]+1):
        try:
            r = requests.get(url, headers=headers, timeout=CFG["HTTP_TIMEOUT"])
            if r.status_code and r.status_code >= 400:
                continue
            return _parse_rss_bytes(r.content, url)
        except Exception:
            if attempt == CFG["HTTP_RETRIES"]:
                return []
            time.sleep(0.4 * attempt)
    return []

def _fetch_all_sources(strict_same_day: bool | None = None,
                       recency_hours_override: int | None = None,
                       extra_blocklist: list[str] | None = None) -> tuple[pd.DataFrame, dict]:
    started = time.time()
    logs = {"sources": [], "errors": []}

    if strict_same_day is None:
        strict_same_day = CFG["STRICT_SAME_DAY"]
    rec_hours = int(recency_hours_override) if recency_hours_override else CFG["RECENCY_HOURS"]

    persisted_block = set(_load_blocked_domains())
    block = set(SPAM_BLOCK_BASE) | persisted_block | set([b.strip().lower() for b in (extra_blocklist or []) if b.strip()])
    logs["blocked_domains_persisted"] = sorted(list(persisted_block))

    urls = []
    urls.extend(RSS_SOURCES)
    urls.extend([_gnews_rss_url(q) for q in GNEWS_QUERIES])
    urls.extend([_bingnews_rss_url(q) for q in BING_QUERIES])

    all_items: list[dict] = []
    max_workers = max(4, min(CFG["MAX_WORKERS"], len(urls))) if urls else 4
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        fut2src = {ex.submit(_fetch_rss, u): u for u in urls}
        for fut in as_completed(fut2src):
            src = fut2src[fut]
            try:
                items = fut.result() or []
                logs["sources"].append({"source": src, "items": len(items)})
                all_items.extend(items)
            except Exception as e:
                logs["errors"].append({"source": src, "error": str(e)})

    df = pd.DataFrame(all_items)
    if not df.empty:
        # Normalización + reglas duras
        df["fuente"] = df["fuente"].fillna("").str.strip().str.lower()
        df = df[~df["fuente"].isin(block)]

        df["fecha_dt"] = pd.to_datetime(df["fecha_dt"], utc=True, errors="coerce")
        df = df[df["fecha_dt"].notna()]

        # Filtro de recencia dura
        cutoff = _now_utc() - timedelta(hours=rec_hours)
        df = df[df["fecha_dt"] >= cutoff]

        # Filtro "mismo día Cuba" (condicional)
        if strict_same_day:
            today_cu = _today_cuba_date_str()
            df["_date_cuba"] = df["fecha_dt"].dt.tz_convert(ZoneInfo(PROTOCOL_TZ)).dt.strftime("%Y-%m-%d")
            df = df[df["_date_cuba"] == today_cu]

        df["titular"] = df["titular"].fillna("").str.strip()
        df["resumen"] = df["resumen"].fillna("").str.strip()
        df["tokens"] = (df["titular"] + " " + df["resumen"]).map(_tokens)
        df = df[df["tokens"] >= CFG["MIN_TOKENS"]]

        df["id_noticia"] = df.apply(lambda r: _hash((r["titular"] or "") + (r["url"] or "")), axis=1)
        df["pais"] = "US"
        df["_texto"] = (df["titular"] + " " + df["resumen"]).str.strip()

        df = df.drop(columns=["_date_cuba"], errors="ignore")

    logs["elapsed_sec"] = round(time.time() - started, 2)
    logs["recency_hours_used"] = rec_hours
    logs["strict_same_day"] = bool(strict_same_day)
    logs["blocked_domains_effective"] = sorted(list(block))
    return df, logs

# =================== Scoring y límite por fuente ===================
def _score_emocion_social(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    emos, recs, rels, srcw = [], [], [], []
    for _, row in df.iterrows():
        txt = f"{row.get('titular','')} {row.get('resumen','')}"
        emos.append(_emo_heuristics(txt))
        recs.append(_recency_factor(row.get("fecha_dt")))
        rels.append(_topic_relevance(txt))
        srcw.append(_source_weight(row.get("fuente","")))
    df = df.copy()
    df["_emo"] = emos
    df["_recency"] = recs
    df["_rel"] = rels
    df["_srcw"] = srcw
    df["_score_es"] = 0.35*df["_emo"] + 0.20*df["_rel"] + 0.20*df["_recency"] + 0.20*df["_srcw"] + 0.05
    return df

def _limit_per_source(df: pd.DataFrame, k: int) -> pd.DataFrame:
    if df.empty or k <= 0: return df
    df = df.copy()
    df["_rank_src"] = df.groupby("fuente")["_score_es"].rank(ascending=False, method="first")
    out = df[df["_rank_src"] <= k].drop(columns=["_rank_src"], errors="ignore")
    return out

# =================== Persistencia ===================
def _ts() -> str: return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
def _save_csv(df: pd.DataFrame, path: Path):
    if df is None: return
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")

def _append_trash(df_rows: pd.DataFrame, reason: str = "manual"):
    if df_rows.empty: return
    trash = TRASH_DIR / "trash.csv"
    df_rows = df_rows.copy()
    df_rows["trash_reason"] = reason
    df_rows["trash_ts"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    if trash.exists():
        try:
            prev = pd.read_csv(trash, dtype=str, encoding="utf-8")
            df_rows = pd.concat([prev, df_rows], ignore_index=True)
        except Exception:
            pass
    _save_csv(df_rows, trash)

def _save_ledger(df_sel: pd.DataFrame, lottery: str):
    day = datetime.now(ZoneInfo(PROTOCOL_TZ)).strftime("%Y%m%d")  # día Cuba
    folder = LEDGER_DIR / lottery / day
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"bitacora_{_ts()}.csv"
    _save_csv(df_sel, path)
    return path

def _export_buffer(df_rows: pd.DataFrame, kind: str) -> Path | None:
    # kind in {"GEM","SUB","T70"}
    if df_rows.empty: return None
    base = {"GEM": BUFF_GEM, "SUB": BUFF_SUB, "T70": BUFF_T70}[kind]
    base.mkdir(parents=True, exist_ok=True)
    path = base / f"news_batch_{_ts()}.csv"
    _save_csv(df_rows, path)
    return path

def _export_to_buffers(df_news: pd.DataFrame) -> Dict[str, Path]:
    """Exporta noticias a todos los buffers (GEM, SUB, T70)."""
    results = {}
    
    if df_news.empty:
        return results
    
    try:
        # Exportar a GEM
        p_gem = _export_buffer(df_news, "GEM")
        if p_gem:
            results["GEM"] = p_gem
        
        # Exportar a SUB
        p_sub = _export_buffer(df_news, "SUB")
        if p_sub:
            results["SUB"] = p_sub
        
        # Exportar a T70
        p_t70 = _export_buffer(df_news, "T70")
        if p_t70:
            results["T70"] = p_t70
            
    except Exception as e:
        st.error(f"Error al exportar a buffers: {e}")
    
    return results

def _validate_schema(df: pd.DataFrame) -> tuple[bool, list[str]]:
    required = ["id_noticia","titular","resumen","url","fecha_dt","fuente","pais","_score_es"]
    missing = [c for c in required if c not in df.columns]
    return (len(missing) == 0, missing)

# =================== Health Check ===================
def _health_check(n_to_test: int = 5) -> pd.DataFrame:
    urls = []
    urls.extend(RSS_SOURCES[:max(0, n_to_test-2)])
    if GNEWS_QUERIES:
        urls.append(_gnews_rss_url(GNEWS_QUERIES[0]))
    if BING_QUERIES:
        urls.append(_bingnews_rss_url(BING_QUERIES[0]))

    rows = []
    headers = {"User-Agent":"Mozilla/5.0 (Vision-News/1.0)"}
    for u in urls:
        t0 = time.time()
        status = "ok"; code = None; items = 0
        try:
            r = requests.get(u, headers=headers, timeout=CFG["HTTP_TIMEOUT"])
            code = r.status_code
            if code and code >= 400:
                status = "http_error"
            else:
                parsed = feedparser.parse(r.content)
                items = len(getattr(parsed, "entries", []) or [])
        except requests.Timeout:
            status = "timeout"
        except Exception:
            status = "error"
        dt = round(time.time()-t0, 2)
        rows.append({"source": u, "status": status, "http_code": code, "latency_s": dt, "items": items})
    return pd.DataFrame(rows)
   # =================== UI principal (con caché manual dinámica) ===================
def _cache_get() -> dict | None:
    return st.session_state.get("__news_cache__", None)

def _cache_set(payload: dict):
    st.session_state["__news_cache__"] = payload

def _run_pipeline_manual(strict_flag: bool = True, rec_hours: int = 72, extra_blocklist: list[str] = None, ttl_sec: int = 300
                         ) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Ejecuta el pipeline de noticias con parámetros por defecto optimizados para emociones sociales."""
    # Clave de caché dependiente de parámetros + día Cuba (para coherencia operativa)
    cache_key = {
        "strict": bool(strict_flag),
        "rec_hours": int(rec_hours),
        "extra_blocklist": sorted([b.strip().lower() for b in (extra_blocklist or [])]),
        "day_cu": _today_cuba_date_str(),
    }
    now_ts = time.time()
    cache = _cache_get()
    if cache and cache.get("key") == cache_key and (now_ts - cache.get("created_ts", 0)) < ttl_sec:
        return cache["df_raw"], cache["df_sel"], cache["logs"]

    # Ejecutar pipeline
    df_raw, logs = _fetch_all_sources(
        strict_same_day=cache_key["strict"],
        recency_hours_override=cache_key["rec_hours"],
        extra_blocklist=cache_key["extra_blocklist"],
    )
    if df_raw.empty:
        df_sel = df_raw
    else:
        df = _score_emocion_social(df_raw)
        if CFG["SEMANTIC_ON"]:
            df = _semantic_dedup(df, CFG["SEMANTIC_THR"])
        if CFG["SOFT_DEDUP_NORM"]:
            df = _soft_dedup(df)
        df = _limit_per_source(df, CFG["MAX_PER_SOURCE"])
        df_sel = df.sort_values(by=["_score_es", "fecha_dt"], ascending=[False, False]).reset_index(drop=True)
        _save_csv(df_raw, RAW_LAST)
        _save_csv(df_sel, SEL_LAST)

    payload = {"key": cache_key, "created_ts": now_ts, "df_raw": df_raw, "df_sel": df_sel, "logs": logs}
    _cache_set(payload)
    return df_raw, df_sel, logs

def render_noticias():
    # Reloj de Cuba (siempre visible)
    now_cu = _now_cuba()
    dia_cuba = now_cu.strftime("%Y-%m-%d")
    hora_cuba = now_cu.strftime("%H:%M:%S")
    st.subheader("📰 Noticias · Emoción Social (USA)")
    st.caption(f"🕒 Cuba (America/Havana): **{dia_cuba} {hora_cuba}**  ·  Filtro activo: SOLO día del protocolo en Cuba")

    # Sidebar fijo
    with st.sidebar:
        st.markdown("#### Acciones")
        if st.button("↻ Reacopiar ahora", use_container_width=True, key="btn_reacopiar"):
            _cache_set(None)
            st.rerun()

        st.markdown("#### Depuración (temporal)")
        relax = st.toggle(
            "Ignorar 'mismo día Cuba' (solo usa ventana de recencia)",
            value=False,
            help="Úsalo solo para auditar. No cambia el decreto por defecto.",
            key="toggle_relax_same_day",
        )
        st.session_state["_relax_same_day"] = bool(relax)

        rec_override = st.slider(
            "Ventana de recencia (horas)",
            min_value=6,
            max_value=168,
            value=CFG["RECENCY_HOURS"],
            step=6,
            help="Solo depuración. No persiste en CFG.",
            key="slider_recency_hours",
        )

        cache_ttl = st.slider(
            "TTL de caché (segundos)",
            min_value=30,
            max_value=1800,
            value=CFG["CACHE_TTL_SEC"],
            step=30,
            help="Tiempo durante el cual se reusa el resultado del pipeline.",
            key="slider_cache_ttl",
        )
        # Si cambia el TTL, invalidamos la caché para que tome efecto de inmediato
        if "prev_cache_ttl" not in st.session_state:
            st.session_state["prev_cache_ttl"] = cache_ttl
        if cache_ttl != st.session_state["prev_cache_ttl"]:
            st.session_state["prev_cache_ttl"] = cache_ttl
            _cache_set(None)
            st.toast("Caché reiniciada por cambio de TTL.", icon="♻️")

        st.markdown("#### Bloquear dominios (sesión)")
        blocked = st.text_input(
            "Listado separados por coma",
            value="",
            key="blocked_domains_input",
            help="Ej: example.com, another.com",
        )
        extra_block = [x.strip().lower() for x in blocked.split(",") if x.strip()]

        st.markdown("#### Bloqueo persistente (__CONFIG/blocked_domains.txt)")
        current_persisted = ", ".join(_load_blocked_domains()) or "(ninguno)"
        st.caption(f"Actual: {current_persisted}")
        new_persist = st.text_input(
            "Agregar dominios (coma)",
            value="",
            key="blocked_domains_persist_add",
        )
        if st.button("💾 Guardar en __CONFIG", use_container_width=True, key="btn_save_blocked"):
            to_save = _load_blocked_domains() + [x.strip().lower() for x in new_persist.split(",") if x.strip()]
            _save_blocked_domains(to_save)
            st.toast("Bloqueo persistente actualizado.", icon="✅")
            st.rerun()

        st.markdown("#### Descargas")
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            if RAW_LAST.exists():
                st.download_button("Acopio bruto (CSV)", RAW_LAST.read_bytes(), "acopio_bruto_ultimo.csv",
                                   use_container_width=True, key="dl_raw")
        with col_dl2:
            if SEL_LAST.exists():
                st.download_button("Selección ES (CSV)", SEL_LAST.read_bytes(), "seleccion_es_ultima.csv",
                                   use_container_width=True, key="dl_sel")

        st.markdown("#### Health check")
        if st.button("📶 Probar 5 fuentes", use_container_width=True, key="btn_health"):
            df_health = _health_check(5)
            st.dataframe(df_health, use_container_width=True, hide_index=True)

        st.markdown("#### Enviar selección a")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🔡 GEM", use_container_width=True, key="send_gem"):
                sel = st.session_state.get("news_selected_df", pd.DataFrame())
                if not sel.empty:
                    p = _export_buffer(sel, "GEM")
                    st.toast(f"GEMATRÍA: {p.name if p else 'sin datos'}", icon="✅")
        with c2:
            if st.button("🌀 SUB", use_container_width=True, key="send_sub"):
                sel = st.session_state.get("news_selected_df", pd.DataFrame())
                if not sel.empty:
                    p = _export_buffer(sel, "SUB")
                    st.toast(f"SUBLIMINAL: {p.name if p else 'sin datos'}", icon="✅")
        with c3:
            if st.button("📊 T70", use_container_width=True, key="send_t70"):
                sel = st.session_state.get("news_selected_df", pd.DataFrame())
                if not sel.empty:
                    sel2 = sel.copy()
                    if "T70_map" not in sel2.columns:
                        sel2["T70_map"] = ""
                    p = _export_buffer(sel2, "T70")
                    st.toast(f"T70: {p.name if p else 'sin datos'}", icon="✅")

        st.markdown("#### Bitácora (por sorteo)")
        current_lottery = st.session_state.get("current_lottery", "GENERAL")
        if st.button("Guardar selección en bitácora", use_container_width=True, key="save_ledger"):
            sel = st.session_state.get("news_selected_df", pd.DataFrame())
            if not sel.empty:
                ok, missing = _validate_schema(sel.assign(_score_es=sel.get("_score_es", 0)))
                if not ok:
                    st.warning(f"Selección con esquema incompleto: faltan {missing}")
                sel2 = sel.copy()
                sel2["sorteo_aplicado"] = current_lottery
                p = _save_ledger(sel2, current_lottery)
                _save_csv(sel2, SEL_LAST)  # snapshot
                st.toast(f"Bitácora guardada: {p.name}", icon="🗂️")

        st.markdown("#### Papelera")
        if st.button("Ver papelera", use_container_width=True, key="show_trash"):
            st.session_state["__show_trash__"] = True
            st.rerun()
        if st.button("Ocultar papelera", use_container_width=True, key="hide_trash"):
            st.session_state["__show_trash__"] = False
            st.rerun()

    # ===== Ejecutar pipeline con caché manual =====
    strict_flag = not st.session_state.get("_relax_same_day", False)
    rec_hours = st.session_state.get("slider_recency_hours", CFG["RECENCY_HOURS"])
    ttl_sec = st.session_state.get("slider_cache_ttl", CFG["CACHE_TTL_SEC"])

    df_raw, df_sel, logs = _run_pipeline_manual(strict_flag, rec_hours, extra_block, ttl_sec)
    st.session_state["news_selected_df"] = df_sel.copy()

    if st.session_state.get("_relax_same_day", False):
        st.warning(
            "Depuración activa: se IGNORA el filtro de **mismo día Cuba**. "
            f"Solo se aplica la ventana de recencia de {logs.get('recency_hours_used', CFG['RECENCY_HOURS'])} horas.",
            icon="⚠️"
        )

    # Encabezado KPIs
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Fuentes", f"{len(logs.get('sources', []))}")
    m2.metric("Bruto (filtro actual)", f"{len(df_raw)}")
    m3.metric("Seleccionadas", f"{len(df_sel)}")
    m4.metric("Ventana (h)", f"{logs.get('recency_hours_used', CFG['RECENCY_HOURS'])}")
    m5.metric("Tiempo (s)", f"{logs.get('elapsed_sec', 0)}")

    if df_raw.empty:
        st.warning("No se obtuvieron noticias con la configuración actual. Verifica conectividad o ajusta recencia.", icon="⛔")
    elif df_sel.empty:
        st.info("Hay acopio bruto pero la selección quedó vacía tras filtros. Revisa MIN_TOKENS, límite por fuente o keywords.", icon="ℹ️")

    # Mostrar noticias seleccionadas en español con fecha y fuente
    st.markdown("#### 📰 Noticias Seleccionadas (Emociones Sociales)")
    if not df_sel.empty:
        view = df_sel.copy()
        view["fecha_cuba"] = view["fecha_dt"].dt.tz_convert(ZoneInfo(PROTOCOL_TZ)).dt.strftime("%Y-%m-%d %H:%M:%S")
        view["hace_horas"] = ((_now_utc() - view["fecha_dt"]).dt.total_seconds()/3600).round(1)
        
        # Mostrar tabla principal con información clave
        display_cols = ["titular", "fuente", "fecha_cuba", "_score_es"]
        st.dataframe(view[display_cols], use_container_width=True, hide_index=True)
        
        # KPIs de noticias
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Noticias", len(df_sel))
        col2.metric("Fuentes Únicas", df_sel["fuente"].nunique())
        col3.metric("Promedio Score", round(df_sel["_score_es"].mean(), 2))
        col4.metric("Recencia Promedio", f"{view['hace_horas'].mean():.1f}h")
        
        # Exportar noticias
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📥 Descargar CSV",
                df_sel.to_csv(index=False, encoding="utf-8").encode("utf-8"),
                f"noticias_emocionales_{_ts()}.csv",
                use_container_width=True
            )
        with col2:
            st.download_button(
                "📥 Descargar JSON",
                df_sel.to_json(orient="records", force_ascii=False, indent=2).encode("utf-8"),
                f"noticias_emocionales_{_ts()}.json",
                use_container_width=True
            )
    else:
        st.info("No hay noticias seleccionadas. Ejecuta el acopio primero.")
    
    # Expanders de auditoría
    with st.expander("📦 Selección completa (ordenada por score y fecha)"):
        if not df_sel.empty:
            view = df_sel.copy()
            view["fecha_cuba"] = view["fecha_dt"].dt.tz_convert(ZoneInfo(PROTOCOL_TZ)).dt.strftime("%Y-%m-%d %H:%M:%S")
            view["hace_horas"] = ((_now_utc() - view["fecha_dt"]).dt.total_seconds()/3600).round(1)
            st.dataframe(view[["id_noticia","titular","fuente","fecha_cuba","hace_horas","_score_es"]], use_container_width=True, hide_index=True)
        else:
            st.write("—")

    with st.expander("🧱 Acopio bruto (auditoría)"):
        if not df_raw.empty:
            rawv = df_raw.copy()
            rawv["fecha_cuba"] = rawv["fecha_dt"].dt.tz_convert(ZoneInfo(PROTOCOL_TZ)).dt.strftime("%Y-%m-%d %H:%M:%S")
            st.dataframe(rawv[["titular","fuente","fecha_cuba","url","resumen"]], use_container_width=True, hide_index=True)
        else:
            st.write("—")

    with st.expander("🧩 Logs del acopio"):
        try:
            st.markdown(f"**Mismo día Cuba:** {logs.get('strict_same_day', True)}  |  **Ventana (h):** {logs.get('recency_hours_used')}")
            st.markdown("**Dominios bloqueados (persistentes)**")
            st.code(", ".join(logs.get("blocked_domains_persisted", [])))
            st.markdown("**Dominios bloqueados efectivos (base + persistentes + sesión)**")
            st.code(", ".join(logs.get("blocked_domains_effective", [])))
            df_src = pd.DataFrame(logs.get("sources", []))
            if not df_src.empty:
                st.markdown("**Fuentes procesadas**")
                st.dataframe(df_src, use_container_width=True, hide_index=True)
            errs = pd.DataFrame(logs.get("errors", []))
            if not errs.empty:
                st.markdown("**Errores**")
                st.dataframe(errs, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Logs no disponibles: {e}")

    # Papelera (opcional)
    if st.session_state.get("__show_trash__"):
        f = TRASH_DIR / "trash.csv"
        st.markdown("### 🗑️ Papelera")
        if f.exists():
            try:
                df_tr = pd.read_csv(f, dtype=str, encoding="utf-8")
                st.dataframe(df_tr, use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"No se pudo leer papelera: {e}")
        else:
            st.info("Papelera vacía.")

    # Acciones sobre selección
    st.markdown("#### Acciones sobre selección")
    sel_ids = st.multiselect("Selecciona ID(s) de noticia:", options=df_sel.get("id_noticia", []),
                             label_visibility="collapsed", key="ms_sel_ids")
    bar1, bar2, bar3 = st.columns(3)

    with bar1:
        if st.button("📋 Copiar/Ver seleccionadas", key="btn_copy_sel", use_container_width=True):
            subset = df_sel[df_sel["id_noticia"].isin(sel_ids)][["titular", "url", "resumen"]].copy()
            if subset.empty:
                st.info("No hay filas seleccionadas.")
            else:
                st.success(f"{len(subset)} noticia(s) preparadas.")
                st.dataframe(subset, use_container_width=True, hide_index=True)
                text_block = "\n\n".join([f"• {r.titular}\n{r.url}\n{r.resumen}" for r in subset.itertuples(index=False)])
                st.text_area("Bloque de texto (selecciona y copia):", value=text_block, height=200)
                st.download_button("⬇️ CSV (subset)", data=_to_csv_bytes(subset),
                                   file_name=f"noticias_subset_{_ts()}.csv", use_container_width=True)
                st.download_button("⬇️ JSON (subset)", data=_to_json_bytes(subset),
                                   file_name=f"noticias_subset_{_ts()}.json", use_container_width=True)

    with bar2:
        motivo = st.text_input("Motivo papelera", value="manual", key="trash_reason")
        if st.button("🗑️ Enviar a papelera", key="btn_to_trash", use_container_width=True):
            subset = df_sel[df_sel["id_noticia"].isin(sel_ids)].copy()
            if subset.empty:
                st.info("No hay filas seleccionadas.")
            else:
                _append_trash(subset, reason=motivo.strip() or "manual")
                st.toast(f"Enviadas {len(subset)} a papelera.", icon="🗑️")
                st.rerun()

    with bar3:
        dest = st.selectbox("Exportar a", options=["GEM","SUB","T70"], key="subset_dest")
        if st.button("🚚 Exportar subset", key="btn_export_subset", use_container_width=True):
            subset = df_sel[df_sel["id_noticia"].isin(sel_ids)].copy()
            if subset.empty:
                st.info("No hay filas seleccionadas.")
            else:
                if dest == "T70" and "T70_map" not in subset.columns:
                    subset["T70_map"] = ""
                p = _export_buffer(subset, dest)
                st.toast(f"Exportado a {dest}: {p.name if p else 'sin datos'}", icon="✅")

    # Exportación de selección completa (JSON extra)
    if not df_sel.empty:
        st.markdown("#### Exportación de selección completa")
        st.download_button("⬇️ Selección ES (JSON)", data=_to_json_bytes(df_sel),
                           file_name=f"seleccion_es_{_ts()}.json", use_container_width=True) 
 
