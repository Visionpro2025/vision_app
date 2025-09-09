

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import numpy as np

st.set_page_config(
    page_title="Calidad de Datos - VISION Premium",
    page_icon="",
    layout="wide"
)

st.title(" **CALIDAD DE DATOS**")
st.markdown("---")

# Simulacion de datos para demostracion
@st.cache_data
def get_sample_data():
    """Genera datos de muestra para demostrar la funcionalidad."""
    np.random.seed(42)
    
    # Generar noticias de muestra (USA)
    titles = [
        "Economia estadounidense muestra signos de recuperacion",
        "Nuevas politicas economicas en Estados Unidos",
        "Inversiones extranjeras en el pais",
        "Desarrollo tecnologico en Nueva York",
        "Turismo en Estados Unidos: tendencias actuales"
    ]
    
    sources = ["Reuters", "Associated Press", "Bloomberg", "Wall Street Journal", "CNN"]
    categories = ["Economia", "Politica", "Tecnologia", "Turismo", "Cultura"]
    
    data = []
    for i in range(100):
        data.append({
            'id': f"news_{i:03d}",
            'title': random.choice(titles),
            'url': f"https://example.com/news/{i}",
            'published_at': datetime.now() - timedelta(hours=random.randint(1, 72)),
            'source': random.choice(sources),
            'category': random.choice(categories),
            'emotion': round(random.uniform(-1, 1), 3)
        })
    
    return pd.DataFrame(data)

# Obtener datos de muestra
df = get_sample_data()

# Metricas principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(" Total Noticias", len(df))
    
with col2:
    # Simular duplicados
    duplicates = random.randint(5, 15)
    st.metric(" Duplicados Encontrados", duplicates)
    
with col3:
    # Simular noticias frescas
    fresh_news = len(df) - random.randint(10, 25)
    st.metric(" Noticias Frescas", fresh_news)
    
with col4:
    # Simular score de calidad
    quality_score = round(random.uniform(0.85, 0.98), 3)
    st.metric(" Score Calidad", quality_score)

st.markdown("---")

# Analisis de calidad
st.subheader(" **ANALISIS DE CALIDAD**")

# Grafico de distribucion por fuente
col1, col2 = st.columns(2)

with col1:
    st.subheader(" Distribucion por Fuente")
    source_counts = df['source'].value_counts()
    st.bar_chart(source_counts)
    
    # Tabla de estadisticas por fuente
    st.subheader(" Estadisticas por Fuente")
    source_stats = df.groupby('source').agg({
        'id': 'count',
        'emotion': ['mean', 'std']
    }).round(3)
    source_stats.columns = ['Cantidad', 'Emocion Promedio', 'Desv. Emocion']
    st.dataframe(source_stats)

with col2:
    st.subheader(" Distribucion por Categoria")
    category_counts = df['category'].value_counts()
    st.bar_chart(category_counts)
    
    # Analisis temporal
    st.subheader(" Analisis Temporal")
    df['hour'] = df['published_at'].dt.hour
    hourly_counts = df['hour'].value_counts().sort_index()
    st.line_chart(hourly_counts)

# Detalles de calidad
st.markdown("---")
st.subheader(" **DETALLES DE CALIDAD**")

# Simular reporte de calidad
quality_report = {
    "timestamp": datetime.now().isoformat(),
    "total_records": len(df),
    "valid_records": len(df) - duplicates,
    "invalid_records": duplicates,
    "quality_score": quality_score,
    "issues": [
        {"type": "duplicate", "count": duplicates, "severity": "medium"},
        {"type": "missing_title", "count": 0, "severity": "low"},
        {"type": "invalid_url", "count": 0, "severity": "low"}
    ],
    "recommendations": [
        "Implementar deduplicacion automatica",
        "Validar URLs antes del procesamiento",
        "Establecer umbrales de calidad minima"
    ]
}

# Mostrar reporte
col1, col2 = st.columns(2)

with col1:
    st.subheader(" Reporte de Calidad")
    st.json(quality_report)
    
with col2:
    st.subheader(" Problemas Detectados")
    for issue in quality_report["issues"]:
        if issue["count"] > 0:
            severity_color = {
                "high": "",
                "medium": "", 
                "low": ""
            }.get(issue["severity"], "")
            
            st.write(f"{severity_color} **{issue['type'].title()}**: {issue['count']} registros")

# Recomendaciones
st.markdown("---")
st.subheader(" **RECOMENDACIONES**")

for i, rec in enumerate(quality_report["recommendations"], 1):
    st.write(f"{i}. {rec}")

# Acciones
st.markdown("---")
st.subheader(" **ACCIONES**")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button(" Re-ejecutar Validacion", use_container_width=True):
        st.success(" Validacion completada")
        st.rerun()

with col2:
    if st.button(" Exportar Reporte", use_container_width=True):
        # Simular exportacion
        st.success(" Reporte exportado a CSV")

with col3:
    if st.button(" Configurar Reglas", use_container_width=True):
        st.info(" Panel de configuracion abierto")

# Footer
st.markdown("---")
st.caption(" Modulo de Calidad de Datos - VISION Premium")
