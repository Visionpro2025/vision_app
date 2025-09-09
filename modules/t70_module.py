# modules/t70_module.py — Mapeo T70 de Noticias a Equivalencias Numéricas
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import json
import pandas as pd
import streamlit as st
from typing import List, Dict, Tuple, Optional
import re
import logging

# =================== Configuración de Logging ===================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =================== CLASE PRINCIPAL T70 MODULE ===================

class T70Module:
    """Módulo principal de mapeo T70 de noticias a equivalencias numéricas."""
    
    def __init__(self):
        """Inicializa el módulo T70."""
        self.ROOT = Path(__file__).resolve().parent.parent
        self.T70_PATH = self.ROOT / "T70.csv"
        self.CONFIG_PATH = self.ROOT / "__CONFIG" / "t70_mapping.json"
        
        # Mapeo de temas emocionales a números T70 (1-70)
        self.T70_MAPPING = {
            # Protestas y disturbios sociales
            "protesta": [7, 14, 21, 28, 35, 42, 49, 56, 63, 70],
            "huelga": [3, 10, 17, 24, 31, 38, 45, 52, 59, 66],
            "disturbios": [5, 12, 19, 26, 33, 40, 47, 54, 61, 68],
            "saqueo": [2, 9, 16, 23, 30, 37, 44, 51, 58, 65],
            "manifestación": [8, 15, 22, 29, 36, 43, 50, 57, 64],
            
            # Crisis y emergencias
            "desabasto": [11, 18, 25, 32, 39, 46, 53, 60, 67],
            "apagón": [4, 11, 18, 25, 32, 39, 46, 53, 60, 67],
            "toque de queda": [6, 13, 20, 27, 34, 41, 48, 55, 62, 69],
            "evacuación": [1, 8, 15, 22, 29, 36, 43, 50, 57, 64],
            "emergencia": [9, 16, 23, 30, 37, 44, 51, 58, 65],
            
            # Violencia y seguridad
            "tiroteo": [13, 20, 27, 34, 41, 48, 55, 62, 69],
            "violencia": [7, 14, 21, 28, 35, 42, 49, 56, 63, 70],
            "homicidio": [5, 12, 19, 26, 33, 40, 47, 54, 61, 68],
            "secuestro": [3, 10, 17, 24, 31, 38, 45, 52, 59, 66],
            "asalto": [11, 18, 25, 32, 39, 46, 53, 60, 67],
            
            # Crisis económica
            "inflación": [2, 9, 16, 23, 30, 37, 44, 51, 58, 65],
            "desempleo": [6, 13, 20, 27, 34, 41, 48, 55, 62, 69],
            "despidos": [4, 11, 18, 25, 32, 39, 46, 53, 60, 67],
            "recesión": [8, 15, 22, 29, 36, 43, 50, 57, 64],
            "crisis": [1, 8, 15, 22, 29, 36, 43, 50, 57, 64],
            
            # Desastres naturales
            "huracán": [12, 19, 26, 33, 40, 47, 54, 61, 68],
            "terremoto": [5, 12, 19, 26, 33, 40, 47, 54, 61, 68],
            "inundación": [3, 10, 17, 24, 31, 38, 45, 52, 59, 66],
            "incendio": [7, 14, 21, 28, 35, 42, 49, 56, 63, 70],
            "tornado": [9, 16, 23, 30, 37, 44, 51, 58, 65],
            
            # Salud pública
            "epidemia": [4, 11, 18, 25, 32, 39, 46, 53, 60, 67],
            "brote": [6, 13, 20, 27, 34, 41, 48, 55, 62, 69],
            "hospital": [2, 9, 16, 23, 30, 37, 44, 51, 58, 65],
            "vacuna": [8, 15, 22, 29, 36, 43, 50, 57, 64],
            "muerte": [1, 8, 15, 22, 29, 36, 43, 50, 57, 64],
            
            # Política y corrupción
            "corrupción": [10, 17, 24, 31, 38, 45, 52, 59, 66],
            "escándalo": [6, 13, 20, 27, 34, 41, 48, 55, 62, 69],
            "fraude": [4, 11, 18, 25, 32, 39, 46, 53, 60, 67],
            "investigación": [2, 9, 16, 23, 30, 37, 44, 51, 58, 65],
            "juicio": [7, 14, 21, 28, 35, 42, 49, 56, 63, 70],
            
            # Tecnología y ciberseguridad
            "hackeo": [13, 20, 27, 34, 41, 48, 55, 62, 69],
            "ciberataque": [5, 12, 19, 26, 33, 40, 47, 54, 61, 68],
            "datos": [3, 10, 17, 24, 31, 38, 45, 52, 59, 66],
            "privacidad": [11, 18, 25, 32, 39, 46, 53, 60, 67],
            "redes": [7, 14, 21, 28, 35, 42, 49, 56, 63, 70],
            
            # Transporte y accidentes
            "accidente": [9, 16, 23, 30, 37, 44, 51, 58, 65],
            "choque": [2, 9, 16, 23, 30, 37, 44, 51, 58, 65],
            "avión": [6, 13, 20, 27, 34, 41, 48, 55, 62, 69],
            "tren": [4, 11, 18, 25, 32, 39, 46, 53, 60, 67],
            "carretera": [8, 15, 22, 29, 36, 43, 50, 57, 64],
            
            # Educación y juventud
            "estudiantes": [1, 8, 15, 22, 29, 36, 43, 50, 57, 64],
            "universidad": [5, 12, 19, 26, 33, 40, 47, 54, 61, 68],
            "escuela": [3, 10, 17, 24, 31, 38, 45, 52, 59, 66],
            "jóvenes": [7, 14, 21, 28, 35, 42, 49, 56, 63, 70],
            "adolescentes": [11, 18, 25, 32, 39, 46, 53, 60, 67],
            
            # Familia y comunidad
            "familia": [2, 9, 16, 23, 30, 37, 44, 51, 58, 65],
            "niños": [6, 13, 20, 27, 34, 41, 48, 55, 62, 69],
            "mujeres": [4, 11, 18, 25, 32, 39, 46, 53, 60, 67],
            "hombres": [8, 15, 22, 29, 36, 43, 50, 57, 64],
            "comunidad": [1, 8, 15, 22, 29, 36, 43, 50, 57, 64]
        }
        
        # Palabras clave emocionales en inglés (para noticias en inglés)
        self.ENGLISH_MAPPING = {
            "protest": [7, 14, 21, 28, 35, 42, 49, 56, 63, 70],
            "strike": [3, 10, 17, 24, 31, 38, 45, 52, 59, 66],
            "riot": [5, 12, 19, 26, 33, 40, 47, 54, 61, 68],
            "looting": [2, 9, 16, 23, 30, 37, 44, 51, 58, 65],
            "demonstration": [8, 15, 22, 29, 36, 43, 50, 57, 64],
            "shortage": [11, 18, 25, 32, 39, 46, 53, 60, 67],
            "blackout": [4, 11, 18, 25, 32, 39, 46, 53, 60, 67],
            "curfew": [6, 13, 20, 27, 34, 41, 48, 55, 62, 69],
            "evacuation": [1, 8, 15, 22, 29, 36, 43, 50, 57, 64],
            "emergency": [9, 16, 23, 30, 37, 44, 51, 58, 65],
            "shooting": [13, 20, 27, 34, 41, 48, 55, 62, 69],
            "violence": [7, 14, 21, 28, 35, 42, 49, 56, 63, 70],
            "murder": [5, 12, 19, 26, 33, 40, 47, 54, 61, 68],
            "kidnapping": [3, 10, 17, 24, 31, 38, 45, 52, 59, 66],
            "assault": [11, 18, 25, 32, 39, 46, 53, 60, 67],
            "inflation": [2, 9, 16, 23, 30, 37, 44, 51, 58, 65],
            "unemployment": [6, 13, 20, 27, 34, 41, 48, 55, 62, 69],
            "layoffs": [4, 11, 18, 25, 32, 39, 46, 53, 60, 67],
            "recession": [8, 15, 22, 29, 36, 43, 50, 57, 64],
            "hurricane": [12, 19, 26, 33, 40, 47, 54, 61, 68],
            "earthquake": [5, 12, 19, 26, 33, 40, 47, 54, 61, 68],
            "flood": [3, 10, 17, 24, 31, 38, 45, 52, 59, 66],
            "fire": [7, 14, 21, 28, 35, 42, 49, 56, 63, 70],
            "tornado": [9, 16, 23, 30, 37, 44, 51, 58, 65],
            "epidemic": [4, 11, 18, 25, 32, 39, 46, 53, 60, 67],
            "outbreak": [6, 13, 20, 27, 34, 41, 48, 55, 62, 69],
            "vaccine": [8, 15, 22, 29, 36, 43, 50, 57, 64],
            "death": [1, 8, 15, 22, 29, 36, 43, 50, 57, 64],
            "corruption": [10, 17, 24, 31, 38, 45, 52, 59, 66],
            "scandal": [6, 13, 20, 27, 34, 41, 48, 55, 62, 69],
            "fraud": [4, 11, 18, 25, 32, 39, 46, 53, 60, 67],
            "investigation": [2, 9, 16, 23, 30, 37, 44, 51, 58, 65],
            "trial": [7, 14, 21, 28, 35, 42, 49, 56, 63, 70],
            "hacking": [13, 20, 27, 34, 41, 48, 55, 62, 69],
            "cyberattack": [5, 12, 19, 26, 33, 40, 47, 54, 61, 68],
            "data": [3, 10, 17, 24, 31, 38, 45, 52, 59, 66],
            "privacy": [11, 18, 25, 32, 39, 46, 53, 60, 67],
            "networks": [7, 14, 21, 28, 35, 42, 49, 56, 63, 70],
            "accident": [9, 16, 23, 30, 37, 44, 51, 58, 65],
            "crash": [2, 9, 16, 23, 30, 37, 44, 51, 58, 65],
            "plane": [6, 13, 20, 27, 34, 41, 48, 55, 62, 69],
            "train": [4, 11, 18, 25, 32, 39, 46, 53, 60, 67],
            "highway": [8, 15, 22, 29, 36, 43, 50, 57, 64],
            "students": [1, 8, 15, 22, 29, 36, 43, 50, 57, 64],
            "university": [5, 12, 19, 26, 33, 40, 47, 54, 61, 68],
            "school": [3, 10, 17, 24, 31, 38, 45, 52, 59, 66],
            "youth": [7, 14, 21, 28, 35, 42, 49, 56, 63, 70],
            "teenagers": [11, 18, 25, 32, 39, 46, 53, 60, 67],
            "family": [2, 9, 16, 23, 30, 37, 44, 51, 58, 65],
            "children": [6, 13, 20, 27, 34, 41, 48, 55, 62, 69],
            "women": [4, 11, 18, 25, 32, 39, 46, 53, 60, 67],
            "men": [8, 15, 22, 29, 36, 43, 50, 57, 64],
            "community": [1, 8, 15, 22, 29, 36, 43, 50, 57, 64]
        }
        
        logger.info("📊 Módulo T70 inicializado")
    
    def map_to_T70(self, df_news: pd.DataFrame) -> pd.DataFrame:
        """Mapea noticias a equivalencias T70."""
        if df_news.empty:
            return pd.DataFrame()
        
        results = []
        
        for _, row in df_news.iterrows():
            titular = str(row.get("titular", ""))
            resumen = str(row.get("resumen", ""))
            fuente = str(row.get("fuente", ""))
            fecha = str(row.get("fecha", ""))
            
            # Extraer palabras clave
            texto_completo = f"{titular} {resumen}".lower()
            keywords = []
            t70_numbers = set()
            
            # Buscar coincidencias en español
            for keyword, numbers in self.T70_MAPPING.items():
                if keyword in texto_completo:
                    keywords.append(keyword)
                    t70_numbers.update(numbers)
            
            # Buscar coincidencias en inglés
            for keyword, numbers in self.ENGLISH_MAPPING.items():
                if keyword in texto_completo:
                    keywords.append(keyword)
                    t70_numbers.update(numbers)
            
            # Determinar categoría principal
            categoria = "general"
            if any(k in keywords for k in ["protesta", "huelga", "disturbios", "protest", "strike", "riot"]):
                categoria = "protestas_sociales"
            elif any(k in keywords for k in ["tiroteo", "violencia", "shooting", "violence", "murder"]):
                categoria = "violencia_seguridad"
            elif any(k in keywords for k in ["inflación", "desempleo", "inflation", "unemployment", "layoffs"]):
                categoria = "crisis_economica"
            elif any(k in keywords for k in ["huracán", "terremoto", "hurricane", "earthquake", "flood"]):
                categoria = "desastres_naturales"
            elif any(k in keywords for k in ["epidemia", "hospital", "epidemic", "outbreak"]):
                categoria = "salud_publica"
            elif any(k in keywords for k in ["corrupción", "escándalo", "corruption", "scandal"]):
                categoria = "politica_corrupcion"
            
            results.append({
                "id_noticia": row.get("id_noticia", ""),
                "titular": titular,
                "fuente": fuente,
                "fecha": fecha,
                "palabras_clave": ", ".join(keywords),
                "t70_numbers": ", ".join(map(str, sorted(t70_numbers))),
                "categoria": categoria,
                "intensidad_emocional": len(keywords),
                "cobertura_t70": len(t70_numbers)
            })
        
        return pd.DataFrame(results)
    
    def analyze_news_batch(self, news_list: List[Dict]) -> Dict:
        """Analiza un lote de noticias para mapeo T70."""
        try:
            logger.info(f"📊 Analizando {len(news_list)} noticias para mapeo T70")
            
            if not news_list:
                return {
                    "success": False,
                    "error": "No hay noticias para analizar"
                }
            
            # Convertir a DataFrame si es necesario
            if isinstance(news_list, list):
                df_news = pd.DataFrame(news_list)
            else:
                df_news = news_list
            
            # Realizar mapeo T70
            results_df = self.map_to_T70(df_news)
            
            if results_df.empty:
                return {
                    "success": False,
                    "error": "No se pudieron mapear las noticias"
                }
            
            # Resumen del análisis
            summary = {
                "total_news": len(results_df),
                "categories": results_df['categoria'].value_counts().to_dict(),
                "avg_intensity": results_df['intensidad_emocional'].mean(),
                "avg_coverage": results_df['cobertura_t70'].mean(),
                "dominant_category": results_df['categoria'].mode().iloc[0] if not results_df['categoria'].mode().empty else "general"
            }
            
            result = {
                "success": True,
                "message": f"✅ Mapeo T70 completado: {len(results_df)} noticias mapeadas",
                "results": results_df.to_dict('records'),
                "summary": summary,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Mapeo T70 completado exitosamente")
            return result
            
        except Exception as e:
            error_msg = f"❌ Error en mapeo T70: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def get_analysis_status(self) -> Dict:
        """Obtiene el estado del módulo T70."""
        return {
            "module": "T70Module",
            "status": "active",
            "version": "1.0.0",
            "capabilities": [
                "t70_mapping",
                "category_classification",
                "emotional_intensity_analysis",
                "batch_news_analysis"
            ],
            "timestamp": datetime.now().isoformat()
        }
    
    def _load_t70_mapping(self) -> Dict:
        """Carga el mapeo T70 desde archivo de configuración."""
        try:
            if self.CONFIG_PATH.exists():
                with open(self.CONFIG_PATH, 'r', encoding="utf-8") as f:
                    return json.load(f)
            else:
                # Crear archivo de configuración por defecto
                default_config = {
                    "mapping": self.T70_MAPPING,
                    "english_mapping": self.ENGLISH_MAPPING,
                    "last_updated": datetime.now().isoformat()
                }
                self.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
                with open(self.CONFIG_PATH, 'w', encoding="utf-8") as f:
                    json.dump(default_config, f, ensure_ascii=False, indent=2)
                return default_config
        except Exception as e:
            logger.error(f"Error cargando configuración T70: {e}")
            return self.T70_MAPPING

# =================== FUNCIONES DE COMPATIBILIDAD ===================

# Mantener funciones existentes para compatibilidad
ROOT = Path(__file__).resolve().parent.parent
T70_PATH = ROOT / "T70.csv"
CONFIG_PATH = ROOT / "__CONFIG" / "t70_mapping.json"

# Funciones de compatibilidad
def map_to_T70(df_news: pd.DataFrame) -> pd.DataFrame:
    """Función de compatibilidad - usar T70Module.map_to_T70()"""
    module = T70Module()
    return module.map_to_T70(df_news)

def _load_t70_mapping() -> Dict:
    """Función de compatibilidad - usar T70Module._load_t70_mapping()"""
    module = T70Module()
    return module._load_t70_mapping()

# =================== FUNCIONES DE INTERFAZ STREAMLIT ===================

def render_t70_ui():
    """Renderiza UI del módulo T70."""
    st.subheader("📊 Análisis T70 - Equivalencias Numéricas")
    
    # Cargar noticias si están disponibles
    df_news = st.session_state.get("NEWS_SEL", pd.DataFrame())
    
    if df_news.empty:
        st.warning("⚠️ No hay noticias disponibles. Acopia noticias primero.")
        return
    
    # Generar T70
    if st.button("🔢 Generar Equivalencias T70", type="primary", use_container_width=True):
        with st.spinner("Analizando equivalencias T70..."):
            df_t70 = map_to_T70(df_news)
            st.session_state["T70"] = df_t70
            st.success(f"✅ {len(df_t70)} equivalencias T70 generadas")
            st.toast("T70 generado")
    
    # Mostrar resultados si existen
    df_t70 = st.session_state.get("T70", pd.DataFrame())
    if not df_t70.empty:
        st.markdown("#### 📈 KPIs de T70")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Noticias procesadas", len(df_t70))
        col2.metric("Categorías únicas", df_t70["categoria"].nunique())
        col3.metric("Promedio intensidad", round(df_t70["intensidad_emocional"].mean(), 1))
        col4.metric("Promedio cobertura", round(df_t70["cobertura_t70"].mean(), 1))
        
        # Análisis por categoría
        st.markdown("#### 📊 Análisis por Categoría")
        cat_stats = df_t70.groupby("categoria").agg({
            "intensidad_emocional": ["count", "mean"],
            "cobertura_t70": "mean"
        }).round(2)
        st.dataframe(cat_stats, use_container_width=True)
        
        # Tabla detallada
        st.markdown("#### 📋 Equivalencias Detalladas")
        st.dataframe(df_t70, use_container_width=True, hide_index=True)
        
        # Exportar
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📥 Descargar CSV",
                df_t70.to_csv(index=False, encoding="utf-8").encode("utf-8"),
                "t70_equivalencias.csv",
                use_container_width=True
            )
        with col2:
            st.download_button(
                "📥 Descargar JSON",
                df_t70.to_json(orient="records", force_ascii=False, indent=2).encode("utf-8"),
                "t70_equivalencias.json",
                use_container_width=True
            )
    
    # Configuración de mapeo
    with st.expander("⚙️ Configuración de Mapeo T70"):
        st.markdown("#### Palabras Clave y Números T70")
        
        mapping = _load_t70_mapping()
        
        # Mostrar mapeo actual
        for keyword, numbers in list(mapping.items())[:20]:  # Mostrar primeros 20
            st.write(f"**{keyword}**: {numbers}")
        
        st.info("Para editar el mapeo completo, modifica el archivo __CONFIG/t70_mapping.json")

# =================== EJEMPLO DE USO ===================

if __name__ == "__main__":
    # Ejemplo de uso del módulo
    print("📊 MÓDULO T70 - MAPEO DE EQUIVALENCIAS NUMÉRICAS")
    print("=" * 60)
    
    # Crear instancia del módulo
    t70_module = T70Module()
    
    # Ejemplo de noticia
    noticia_ejemplo = {
        "titular": "Protestas masivas contra la inflación en la ciudad",
        "resumen": "Miles de personas salieron a las calles para protestar contra el aumento de precios y la crisis económica",
        "fuente": "Reuters",
        "fecha": "2024-01-15"
    }
    
    print(f"📝 Noticia de ejemplo: {noticia_ejemplo['titular']}")
    
    # Crear DataFrame de ejemplo
    df_ejemplo = pd.DataFrame([noticia_ejemplo])
    
    # Mapeo T70
    resultado_t70 = t70_module.map_to_T70(df_ejemplo)
    
    if not resultado_t70.empty:
        row = resultado_t70.iloc[0]
        print(f"🔢 Palabras clave detectadas: {row['palabras_clave']}")
        print(f"📊 Números T70: {row['t70_numbers']}")
        print(f"🏷️ Categoría: {row['categoria']}")
        print(f"⚡ Intensidad emocional: {row['intensidad_emocional']}")
        print(f"📈 Cobertura T70: {row['cobertura_t70']}")
    
    # Estado del módulo
    status = t70_module.get_analysis_status()
    print(f"📊 Estado: {status['status']} - Versión: {status['version']}")
    
    print("\n✅ Módulo T70 funcionando correctamente")








