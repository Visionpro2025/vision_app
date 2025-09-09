# app_vision/modules/florida_pick3_ui.py
"""
UI Components para Florida Pick 3 → Bolita Cubana
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, List
import json

def show_florida_pick3_header():
    """Muestra el header del protocolo Florida Pick 3"""
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(90deg, #1e3c72, #2a5298); border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0;">🎰 FLORIDA PICK 3 → BOLITA CUBANA</h1>
        <p style="color: #e0e0e0; margin: 5px 0 0 0;">Protocolo Determinista con Análisis Gematría</p>
    </div>
    """, unsafe_allow_html=True)

def show_window_status():
    """Muestra el estado de las ventanas de tiempo"""
    from app_vision.modules.draw_windows import get_window_status, get_operational_schedule
    
    now = datetime.now()
    status = get_window_status(now)
    schedule = get_operational_schedule()
    
    st.markdown("### 🕐 Estado de Ventanas (ET)")
    
    col1, col2, col3 = st.columns(3)
    
    for i, (block, info) in enumerate(schedule.items()):
        with [col1, col2, col3][i]:
            is_current = status["current_block"] == block
            is_open = status["windows"][block]["is_open"]
            
            color = "#4CAF50" if is_current else "#2196F3" if is_open else "#757575"
            icon = "🟢" if is_current else "🔵" if is_open else "⚪"
            
            st.markdown(f"""
            <div style="padding: 15px; border: 2px solid {color}; border-radius: 8px; text-align: center;">
                <h4 style="color: {color}; margin: 0;">{icon} {block}</h4>
                <p style="margin: 5px 0;">{info['description']}</p>
                <p style="margin: 0; font-size: 0.9em;">Cierra: {info['close']}</p>
            </div>
            """, unsafe_allow_html=True)

def show_candado_rule():
    """Muestra la regla fija del CANDADO"""
    st.markdown("### 🎯 Regla Fija del CANDADO")
    
    st.markdown("""
    <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; border-left: 4px solid #2196F3;">
        <h4 style="margin: 0 0 10px 0; color: #1976D2;">Construcción Determinista:</h4>
        <ol style="margin: 0; padding-left: 20px;">
            <li><strong>FIJO_2D</strong> = últimos 2 del Pick3 del bloque</li>
            <li><strong>CORRIDO_2D</strong> = últimos 2 del Pick4 del mismo bloque (si existe)</li>
            <li><strong>TERCERO</strong> = últimos 2 del Pick3 del otro bloque (opcional)</li>
        </ol>
        <p style="margin: 10px 0 0 0; font-style: italic; color: #666;">
            Nada se inventa. Si falta Pick4 del bloque, candado mínimo de 2 elementos.
        </p>
    </div>
    """, unsafe_allow_html=True)

def show_prev_day_candados(prev_day_data: Dict[str, Any]):
    """Muestra los candados del día anterior en formato de tarjetas"""
    if not prev_day_data or "candados" not in prev_day_data:
        st.warning("No hay datos de candados del día anterior")
        return
    
    st.markdown("### 📅 Candados del Día Anterior")
    
    candados = prev_day_data["candados"]
    summary = prev_day_data.get("summary", {})
    
    # Mostrar resumen
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Completos", summary.get("complete", 0))
    with col2:
        st.metric("Faltantes", summary.get("missing", 0))
    with col3:
        st.metric("Total Parlés", len(summary.get("all_parles_string", "").split(", ")) if summary.get("all_parles_string") else 0)
    
    # Mostrar tarjetas de candados
    cols = st.columns(len(candados))
    
    for i, candado in enumerate(candados):
        with cols[i]:
            slot = candado.get("slot", "N/A")
            status = candado.get("status", "missing")
            candado_list = candado.get("candado", [])
            parles_list = candado.get("parles", [])
            
            if status == "complete":
                color = "#4CAF50"
                icon = "✅"
            else:
                color = "#F44336"
                icon = "❌"
            
            st.markdown(f"""
            <div style="padding: 15px; border: 2px solid {color}; border-radius: 8px; text-align: center; margin-bottom: 10px;">
                <h4 style="color: {color}; margin: 0;">{icon} {slot}</h4>
                <p style="margin: 5px 0; font-size: 1.2em; font-weight: bold;">{' - '.join(candado_list)}</p>
                <p style="margin: 0; font-size: 0.9em; color: #666;">Parlés: {len(parles_list)}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if status == "complete" and parles_list:
                parles_str = ", ".join([f"{p[0]}-{p[1]}" for p in parles_list])
                if st.button(f"📋 Copiar Parlés {slot}", key=f"copy_{slot}"):
                    st.code(parles_str)
                    st.success(f"Parlés {slot} copiados al portapapeles")

def show_current_candado(candado_data: Dict[str, Any]):
    """Muestra el candado actual"""
    if not candado_data:
        st.warning("No hay datos del candado actual")
        return
    
    st.markdown("### 🎲 Candado Actual")
    
    mode = candado_data.get("mode", "")
    date = candado_data.get("date", "")
    block = candado_data.get("block", "")
    candado = candado_data.get("candado", [])
    parles = candado_data.get("parles", [])
    fuente = candado_data.get("fuente", {})
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; text-align: center;">
        <h3 style="margin: 0 0 10px 0;">🎯 CANDADO ACTUAL</h3>
        <p style="margin: 0 0 15px 0; font-size: 1.1em;">{date} - {block}</p>
        <div style="font-size: 2em; font-weight: bold; margin: 15px 0;">{' - '.join(candado)}</div>
        <p style="margin: 10px 0 0 0; font-size: 0.9em;">Parlés: {len(parles)} combinaciones</p>
    </div>
    """, unsafe_allow_html=True)
    
    if parles:
        st.markdown("#### 📋 Parlés Disponibles")
        parles_str = ", ".join([f"{p[0]}-{p[1]}" for p in parles])
        st.code(parles_str)
        
        if st.button("📋 Copiar Todos los Parlés"):
            st.code(parles_str)
            st.success("Parlés copiados al portapapeles")
    
    # Mostrar fuente
    if fuente:
        st.markdown("#### 🔍 Fuente de Datos")
        col1, col2 = st.columns(2)
        with col1:
            st.text(f"Pick3: {fuente.get('pick3_block', 'N/A')}")
        with col2:
            st.text(f"Pick4: {fuente.get('pick4_block', 'N/A')}")

def show_gematria_analysis(gematria_data: Dict[str, Any]):
    """Muestra el análisis gematría"""
    if not gematria_data or "per_candado" not in gematria_data:
        st.warning("No hay datos de análisis gematría")
        return
    
    st.markdown("### 🔮 Análisis Gematría")
    
    per_candado = gematria_data["per_candado"]
    
    for item in per_candado:
        slot = item.get("slot", "N/A")
        topics = item.get("topics", [])
        keywords = item.get("keywords", [])
        poem = item.get("poem", "")
        families = item.get("families", [])
        
        with st.expander(f"📊 Análisis {slot}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Topics:**")
                for topic in topics[:5]:  # Mostrar solo los primeros 5
                    st.markdown(f"• {topic}")
            
            with col2:
                st.markdown("**Keywords:**")
                for keyword in keywords[:5]:  # Mostrar solo los primeros 5
                    st.markdown(f"• {keyword}")
            
            if families:
                st.markdown("**Familias:**")
                st.markdown(", ".join(families))
            
            if poem:
                st.markdown("**Poema:**")
                st.markdown(f"*{poem}*")

def show_guide_message(guide_data: Dict[str, Any]):
    """Muestra el mensaje guía fusionado"""
    if not guide_data or "guide" not in guide_data:
        st.warning("No hay datos del mensaje guía")
        return
    
    guide = guide_data["guide"]
    topics = guide.get("topics", [])
    keywords = guide.get("keywords", [])
    message = guide.get("message", "")
    for_block = guide.get("for_block", "")
    
    st.markdown("### 📰 Mensaje Guía para Noticias")
    
    st.markdown(f"""
    <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; border-left: 4px solid #4CAF50;">
        <h4 style="margin: 0 0 10px 0; color: #2E7D32;">Bloque: {for_block}</h4>
        <p style="margin: 0; font-size: 1.1em; font-weight: bold;">{message}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Topics Principales:**")
        for topic in topics:
            st.markdown(f"• {topic}")
    
    with col2:
        st.markdown("**Keywords Clave:**")
        for keyword in keywords:
            st.markdown(f"• {keyword}")

def show_sefirotic_analysis(sefirotic_data: Dict[str, Any]):
    """Muestra el análisis sefirótico"""
    if not sefirotic_data:
        st.warning("No hay datos de análisis sefirótico")
        return
    
    st.markdown("### 🌟 Análisis Sefirótico")
    
    # Aquí puedes agregar la visualización específica del análisis sefirótico
    # Por ahora, mostramos los datos en formato JSON
    st.json(sefirotic_data)

def show_florida_pick3_analysis():
    """Función principal para mostrar el análisis completo de Florida Pick 3"""
    show_florida_pick3_header()
    
    # Estado de ventanas
    show_window_status()
    
    # Regla del candado
    show_candado_rule()
    
    # Aquí se integrarían los datos del pipeline
    # Por ahora mostramos placeholders
    
    st.markdown("### 📊 Análisis en Tiempo Real")
    st.info("Ejecuta el protocolo para ver los análisis completos")
    
    if st.button("🚀 Ejecutar Protocolo Florida Pick 3", type="primary"):
        st.success("Protocolo ejecutado (simulación)")
        # Aquí se ejecutaría el pipeline real


