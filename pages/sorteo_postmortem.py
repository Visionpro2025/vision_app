#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Página de Post-Mortem de Sorteos - VISIÓN Premium
Analiza resultados, métricas y genera propuestas automáticas
"""

import streamlit as st
import pandas as pd
import json
import yaml
from pathlib import Path
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Importar servicios SLL
try:
    from services.sll_metrics import SLLMetrics
    from services.sll_proposals import SLLProposalGenerator
    from services.lexicon import CorpusLexiconBuilder
    from services.news_enricher import NewsEnricher
except ImportError as e:
    st.error(f"Error importando servicios SLL: {e}")
    st.stop()

# Configuración de la página
st.set_page_config(
    page_title="Post-Mortem de Sorteos - VISIÓN Premium",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("📊 Post-Mortem de Sorteos - VISIÓN Premium")
st.markdown("---")

# Inicializar servicios
@st.cache_resource
def init_services():
    """Inicializa servicios SLL"""
    try:
        metrics_service = SLLMetrics()
        proposal_generator = SLLProposalGenerator()
        lexicon_builder = CorpusLexiconBuilder()
        news_enricher = NewsEnricher(lexicon_builder)
        
        return {
            "metrics": metrics_service,
            "proposals": proposal_generator,
            "lexicon": lexicon_builder,
            "enricher": news_enricher
        }
    except Exception as e:
        st.error(f"Error inicializando servicios: {e}")
        return None

services = init_services()
if not services:
    st.stop()

# Sidebar para configuración
st.sidebar.header("⚙️ Configuración")

# Selector de sorteo
st.sidebar.subheader("Seleccionar Sorteo")
sorteo_date = st.sidebar.date_input(
    "Fecha del Sorteo",
    value=datetime.now().date(),
    max_value=datetime.now().date()
)

# Botón para cargar datos
if st.sidebar.button("🔄 Cargar Datos del Sorteo"):
    st.session_state.load_data = True

# Función para cargar datos del sorteo
def load_sorteo_data(date_str: str):
    """Carga datos del sorteo desde archivos"""
    try:
        date_path = Path(f"data/sorteos/{date_str}")
        
        if not date_path.exists():
            return None, "Directorio del sorteo no encontrado"
        
        # Cargar snapshot
        snapshot_path = date_path / "snapshot.yml"
        snapshot = None
        if snapshot_path.exists():
            with open(snapshot_path, 'r', encoding='utf-8') as f:
                snapshot = yaml.safe_load(f)
        
        # Cargar features
        features_path = date_path / "features.jsonl"
        features = []
        if features_path.exists():
            with open(features_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        features.append(json.loads(line))
        
        # Cargar scores
        scores_path = date_path / "scores.json"
        scores = None
        if scores_path.exists():
            with open(scores_path, 'r', encoding='utf-8') as f:
                scores = json.load(f)
        
        # Cargar propuestas
        propuestas_path = date_path / "propuestas.jsonl"
        propuestas = []
        if propuestas_path.exists():
            with open(propuestas_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        propuestas.append(json.loads(line))
        
        return {
            "snapshot": snapshot,
            "features": features,
            "scores": scores,
            "propuestas": propuestas
        }, None
        
    except Exception as e:
        return None, f"Error cargando datos: {e}"

# Función para simular datos de ejemplo
def generate_sample_data():
    """Genera datos de ejemplo para demostración"""
    try:
        # Métricas simuladas
        scores = {
            "hit@1": 0.0,
            "hit@3": 0.33,
            "hit@5": 0.67,
            "brier_score": 0.28,
            "ece": 0.15,
            "coverage_confidence": {
                "coverage": 0.45,
                "accuracy": 0.62,
                "confidence": 0.58
            },
            "total_predictions": 10,
            "total_real": 5,
            "hits_total": 3
        }
        
        # Ablación simulada
        ablation = [
            {
                "family": "S_gematria",
                "impact_percentage": 25.5,
                "status": "positive"
            },
            {
                "family": "S_news_sem",
                "impact_percentage": -12.3,
                "status": "negative"
            },
            {
                "family": "S_frame",
                "impact_percentage": 8.7,
                "status": "positive"
            }
        ]
        
        # Propuestas simuladas
        propuestas = [
            {
                "id": "PROP-20250831-001",
                "tipo": "ajuste_peso",
                "target": "S_gematria",
                "action": "aumentar_peso",
                "delta": 0.15,
                "justification": "Ablación S_gematria: +25.5% impacto, aumentar peso en 0.15",
                "impact": "medium",
                "category": "weight_adjustment",
                "priority": 0.75
            },
            {
                "id": "PROP-20250831-002",
                "tipo": "ajuste_peso",
                "target": "S_news_sem",
                "action": "reducir_peso",
                "delta": -0.10,
                "justification": "Ablación S_news_sem: -12.3% impacto, reducir peso en 0.10",
                "impact": "medium",
                "category": "weight_adjustment",
                "priority": 0.65
            }
        ]
        
        return {
            "scores": scores,
            "ablation": ablation,
            "propuestas": propuestas
        }
        
    except Exception as e:
        st.error(f"Error generando datos de ejemplo: {e}")
        return None

# Cargar o generar datos
if 'load_data' in st.session_state and st.session_state.load_data:
    # Intentar cargar datos reales
    date_str = sorteo_date.strftime("%Y-%m-%d")
    data, error = load_sorteo_data(date_str)
    
    if data is None:
        st.warning(f"No se encontraron datos para {date_str}. Generando datos de ejemplo...")
        data = generate_sample_data()
        if data:
            st.session_state.sorteo_data = data
            st.session_state.load_data = False
    else:
        st.session_state.sorteo_data = data
        st.session_state.load_data = False

# Mostrar datos si están disponibles
if 'sorteo_data' in st.session_state:
    data = st.session_state.sorteo_data
    
    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Métricas", "🔍 Ablación", "💡 Propuestas", "📚 Léxicos"])
    
    with tab1:
        st.header("📈 Métricas del Sorteo")
        
        if data.get("scores"):
            scores = data["scores"]
            
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Hit@1", f"{scores.get('hit@1', 0):.2f}")
            
            with col2:
                st.metric("Hit@3", f"{scores.get('hit@3', 0):.2f}")
            
            with col3:
                st.metric("Hit@5", f"{scores.get('hit@5', 0):.2f}")
            
            with col4:
                st.metric("Brier Score", f"{scores.get('brier_score', 0):.3f}")
            
            # Gráfico de Hit@k
            hit_data = {
                "k": [1, 3, 5],
                "hit_rate": [
                    scores.get("hit@1", 0),
                    scores.get("hit@3", 0),
                    scores.get("hit@5", 0)
                ]
            }
            
            df_hit = pd.DataFrame(hit_data)
            fig_hit = px.bar(df_hit, x="k", y="hit_rate", 
                           title="Hit Rate por Top-K",
                           labels={"k": "Top-K", "hit_rate": "Hit Rate"})
            fig_hit.update_yaxis(range=[0, 1])
            st.plotly_chart(fig_hit, use_container_width=True)
            
            # Cobertura vs Confianza
            if "coverage_confidence" in scores:
                cc = scores["coverage_confidence"]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📊 Cobertura vs Confianza")
                    st.metric("Cobertura", f"{cc.get('coverage', 0):.2f}")
                    st.metric("Precisión", f"{cc.get('accuracy', 0):.2f}")
                    st.metric("Confianza", f"{cc.get('confidence', 0):.2f}")
                
                with col2:
                    # Gráfico de radar para cobertura
                    fig_radar = go.Figure()
                    fig_radar.add_trace(go.Scatterpolar(
                        r=[cc.get('coverage', 0), cc.get('accuracy', 0), cc.get('confidence', 0)],
                        theta=['Cobertura', 'Precisión', 'Confianza'],
                        fill='toself',
                        name='Métricas'
                    ))
                    fig_radar.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                        showlegend=False,
                        title="Métricas de Cobertura"
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)
            
            # Estadísticas generales
            st.subheader("📋 Estadísticas Generales")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Predicciones", scores.get("total_predictions", 0))
            
            with col2:
                st.metric("Total Real", scores.get("total_real", 0))
            
            with col3:
                st.metric("Hits Totales", scores.get("hits_total", 0))
    
    with tab2:
        st.header("🔍 Análisis de Ablación")
        
        if data.get("ablation"):
            ablation = data["ablation"]
            
            # Tabla de ablación
            df_ablation = pd.DataFrame(ablation)
            
            # Colorear por impacto
            def color_impact(val):
                if val > 0:
                    return 'background-color: lightgreen'
                elif val < 0:
                    return 'background-color: lightcoral'
                return ''
            
            st.dataframe(
                df_ablation.style.applymap(color_impact, subset=['impact_percentage']),
                use_container_width=True
            )
            
            # Gráfico de impacto
            fig_ablation = px.bar(
                df_ablation, 
                x="family", 
                y="impact_percentage",
                color="status",
                title="Impacto por Familia de Señales",
                labels={"family": "Familia", "impact_percentage": "Impacto (%)"}
            )
            fig_ablation.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_ablation, use_container_width=True)
            
            # Resumen de ablación
            positive_impact = [a for a in ablation if a.get("impact_percentage", 0) > 0]
            negative_impact = [a for a in ablation if a.get("impact_percentage", 0) < 0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Señales Positivas", len(positive_impact))
                if positive_impact:
                    st.write("**Top señales positivas:**")
                    for signal in sorted(positive_impact, key=lambda x: x.get("impact_percentage", 0), reverse=True)[:3]:
                        st.write(f"- {signal['family']}: +{signal['impact_percentage']:.1f}%")
            
            with col2:
                st.metric("Señales Negativas", len(negative_impact))
                if negative_impact:
                    st.write("**Top señales negativas:**")
                    for signal in sorted(negative_impact, key=lambda x: abs(x.get("impact_percentage", 0)), reverse=True)[:3]:
                        st.write(f"- {signal['family']}: {signal['impact_percentage']:.1f}%")
    
    with tab3:
        st.header("💡 Propuestas Automáticas")
        
        if data.get("propuestas"):
            propuestas = data["propuestas"]
            
            # Resumen de propuestas
            total_prop = len(propuestas)
            high_impact = len([p for p in propuestas if p.get("impact") == "high"])
            medium_impact = len([p for p in propuestas if p.get("impact") == "medium"])
            low_impact = len([p for p in propuestas if p.get("impact") == "low"])
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Propuestas", total_prop)
            
            with col2:
                st.metric("Alto Impacto", high_impact)
            
            with col3:
                st.metric("Medio Impacto", medium_impact)
            
            with col4:
                st.metric("Bajo Impacto", low_impact)
            
            # Tabla de propuestas con botones de acción
            st.subheader("📋 Lista de Propuestas")
            
            for i, prop in enumerate(propuestas):
                with st.expander(f"🔸 {prop['id']} - {prop['tipo']}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Target:** {prop['target']}")
                        st.write(f"**Acción:** {prop['action']}")
                        st.write(f"**Impacto:** {prop['impact']}")
                        st.write(f"**Categoría:** {prop['category']}")
                        st.write(f"**Prioridad:** {prop['priority']:.2f}")
                        st.write(f"**Justificación:** {prop['justification']}")
                        
                        if "delta" in prop:
                            st.write(f"**Delta:** {prop['delta']:.2f}")
                        if "cap" in prop:
                            st.write(f"**Cap:** {prop['cap']:.2f}")
                    
                    with col2:
                        if st.button(f"✅ Aplicar", key=f"apply_{i}"):
                            st.success(f"Propuesta {prop['id']} aplicada")
                        
                        if st.button(f"📝 Revisar", key=f"review_{i}"):
                            st.info(f"Propuesta {prop['id']} marcada para revisión")
                        
                        if st.button(f"❌ Descartar", key=f"discard_{i}"):
                            st.warning(f"Propuesta {prop['id']} descartada")
            
            # Gráfico de propuestas por categoría
            if propuestas:
                categories = {}
                for prop in propuestas:
                    cat = prop.get("category", "unknown")
                    categories[cat] = categories.get(cat, 0) + 1
                
                df_cat = pd.DataFrame(list(categories.items()), columns=["Categoría", "Cantidad"])
                fig_cat = px.pie(df_cat, values="Cantidad", names="Categoría", 
                               title="Propuestas por Categoría")
                st.plotly_chart(fig_cat, use_container_width=True)
    
    with tab4:
        st.header("📚 Léxicos del Corpus")
        
        # Construir léxicos
        if st.button("🔍 Construir Léxicos"):
            with st.spinner("Construyendo léxicos..."):
                try:
                    lexicons = services["lexicon"].build_lexicons()
                    st.session_state.lexicons = lexicons
                    st.success("Léxicos construidos exitosamente")
                except Exception as e:
                    st.error(f"Error construyendo léxicos: {e}")
        
        # Mostrar léxicos si están disponibles
        if 'lexicons' in st.session_state:
            lexicons = st.session_state.lexicons
            
            # Selector de dominio
            domain = st.selectbox(
                "Seleccionar Dominio",
                ["jung", "subliminal", "gematria"]
            )
            
            if domain in lexicons:
                st.subheader(f"📖 Léxico: {domain.upper()}")
                
                # Mostrar categorías
                for category, terms in lexicons[domain].items():
                    with st.expander(f"📁 {category}"):
                        st.write(f"**Términos ({len(terms)}):**")
                        st.write(", ".join(terms))
                
                # Estadísticas del dominio
                total_terms = sum(len(terms) for terms in lexicons[domain].values())
                st.metric(f"Total Términos {domain.upper()}", total_terms)
                
                # Búsqueda en léxicos
                st.subheader("🔍 Buscar Términos")
                search_query = st.text_input("Query de búsqueda:")
                
                if search_query:
                    results = services["lexicon"].search_terms(search_query, domain)
                    if results and domain in results:
                        st.write(f"**Términos encontrados en {domain}:**")
                        st.write(", ".join(results[domain]))
                    else:
                        st.info(f"No se encontraron términos para '{search_query}' en {domain}")
        
        # Demostración de enriquecimiento de noticias
        st.subheader("📰 Demostración: Enriquecimiento de Noticias")
        
        sample_text = st.text_area(
            "Texto de ejemplo para análisis:",
            value="Este documento aborda aspectos de psicología analítica y operaciones psicológicas en el contexto de defensa nacional.",
            height=100
        )
        
        if st.button("🔍 Analizar Texto"):
            if sample_text:
                with st.spinner("Analizando texto..."):
                    try:
                        # Detectar frames
                        frame_analysis = services["enricher"].detect_frames(sample_text)
                        
                        # Mostrar resultados
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Análisis de Frames:**")
                            if "frames" in frame_analysis:
                                for frame_type, info in frame_analysis["frames"].items():
                                    status = "✅" if info["detected"] else "❌"
                                    st.write(f"{status} {frame_type}: {info['confidence']:.2f}")
                        
                        with col2:
                            st.write("**Estadísticas:**")
                            st.write(f"Frames detectados: {frame_analysis.get('total_frames_detected', 0)}")
                            st.write(f"Confianza general: {frame_analysis.get('overall_confidence', 0):.2f}")
                            st.write(f"Longitud del texto: {frame_analysis.get('text_length', 0)}")
                        
                    except Exception as e:
                        st.error(f"Error analizando texto: {e}")

else:
    # Estado inicial
    st.info("👆 Usa el sidebar para cargar datos de un sorteo específico")
    
    # Información del sistema
    st.subheader("ℹ️ Información del Sistema SLL")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Funcionalidades:**")
        st.write("- 📊 Métricas de rendimiento (Hit@k, Brier, ECE)")
        st.write("- 🔍 Análisis de ablación por familia de señales")
        st.write("- 💡 Generación automática de propuestas")
        st.write("- 📚 Léxicos especializados del corpus")
        st.write("- 📰 Enriquecimiento de noticias")
    
    with col2:
        st.write("**Beneficios:**")
        st.write("- 🔄 Aprendizaje continuo por sorteo")
        st.write("- 🎯 Mejora automática del sistema")
        st.write("- 📈 Transparencia en resultados")
        st.write("- 🛡️ Seguridad y estabilidad")
        st.write("- 📖 Integración con corpus de libros")

# Footer
st.markdown("---")
st.markdown("*Sistema de Aprendizaje por Sorteo (SLL) - VISIÓN Premium*")








