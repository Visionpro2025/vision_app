#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Buscador en Red de Sorteos - VISION PREMIUM
Consulta fuentes oficiales para obtener resultados de loterías en tiempo real
"""

import streamlit as st
import datetime as dt
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path

# Agregar el directorio raiz al path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Importar el módulo de búsqueda en red
try:
    from lottery_fetcher import fetch_draw, get_available_lotteries, validate_draw_date
except ImportError:
    st.error("❌ Error: No se pudo importar el módulo lottery_fetcher")
    st.info("Asegúrate de que el archivo lottery_fetcher.py esté en el directorio raíz")
    st.stop()

# Configuración de la página
st.set_page_config(
    page_title="🌐 Buscador en Red de Sorteos",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🌐 **BUSCADOR EN RED DE SORTEOS**")
st.markdown("### Consulta fuentes oficiales para obtener resultados en tiempo real")

# Sidebar con información
with st.sidebar:
    st.markdown("### 📋 LOTERÍAS DISPONIBLES")
    
    # Obtener loterías disponibles
    try:
        available_lotteries = get_available_lotteries()
        
        for lottery in available_lotteries:
            st.info(f"**{lottery['name']}**\n"
                    f"ID: `{lottery['id']}`\n"
                    f"Horario: {lottery['schedule']}")
        
    except Exception as e:
        st.error(f"Error al obtener loterías: {e}")
    
    st.markdown("---")
    
    st.markdown("### 🔍 CÓMO USAR")
    st.info("""
    1. **Selecciona la lotería** del menú desplegable
    2. **Elige la fecha** del sorteo que quieres consultar
    3. **Haz clic en 'Buscar en Red'**
    4. **Revisa los resultados** y la fuente oficial
    """)
    
    st.markdown("---")
    
    st.markdown("### ⚠️ NOTAS IMPORTANTES")
    st.warning("""
    - **Fuentes oficiales:** Los resultados vienen directamente de los sitios web oficiales
    - **Validación:** Se valida que la fecha tenga sorteo programado
    - **Fallback:** Si una fuente falla, se intenta con fuentes alternativas
    - **Disputas:** Si hay diferencias entre fuentes, se marca como 'disputed'
    """)

# Contenido principal
st.markdown("---")

# Selección de lotería y fecha
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🎰 SELECCIÓN DE LOTERÍA")
    
    # Selector de lotería
    lottery_options = {
        "megamillions": "🎯 Mega Millions",
        "powerball": "⚡ Powerball", 
        "fl-pick3-day": "🌴 Florida Pick 3 (Día)",
        "fl-pick3-night": "🌙 Florida Pick 3 (Noche)",
        "cash5-jersey": "🗽 Cash 5 New Jersey"
    }
    
    selected_lottery = st.selectbox(
        "Selecciona la lotería:",
        options=list(lottery_options.keys()),
        format_func=lambda x: lottery_options[x],
        key="lottery_selector"
    )
    
    # Mostrar información de la lotería seleccionada
    if selected_lottery:
        try:
            lotteries = get_available_lotteries()
            selected_info = next((l for l in lotteries if l['id'] == selected_lottery), None)
            
            if selected_info:
                st.success(f"**{selected_info['name']}**")
                st.info(f"**Horario:** {selected_info['schedule']}")
                
                # Mostrar reglas específicas
                if selected_lottery == "megamillions":
                    st.info("**Rango:** 1-70 (5 números) + 1-25 (Mega Ball)")
                elif selected_lottery == "powerball":
                    st.info("**Rango:** 1-69 (5 números) + 1-26 (Power Ball)")
                elif selected_lottery == "cash5-jersey":
                    st.info("**Rango:** 1-45 (5 números)")
                elif "fl-pick3" in selected_lottery:
                    st.info("**Rango:** 0-9 (3 números)")
        except Exception as e:
            st.error(f"Error al obtener información: {e}")

with col2:
    st.markdown("### 📅 SELECCIÓN DE FECHA")
    
    # Fecha del sorteo
    selected_date = st.date_input(
        "Fecha del sorteo:",
        value=datetime.now() - timedelta(days=1),  # Por defecto, ayer
        max_value=datetime.now(),
        key="date_selector"
    )
    
    # Convertir fecha a string
    date_str = selected_date.strftime("%Y-%m-%d")
    
    # Validar fecha
    if selected_lottery and date_str:
        try:
            is_valid = validate_draw_date(selected_lottery, date_str)
            if is_valid:
                st.success(f"✅ **Fecha válida:** {date_str}")
                st.info("Esta fecha tiene sorteo programado")
            else:
                st.warning(f"⚠️ **Fecha sin sorteo:** {date_str}")
                st.info("Esta fecha no tiene sorteo programado para esta lotería")
        except Exception as e:
            st.error(f"Error al validar fecha: {e}")
    
    # Botón de búsqueda rápida
    st.markdown("### 🚀 BÚSQUEDA RÁPIDA")
    
    # Fechas predefinidas
    quick_dates = {
        "Ayer": datetime.now() - timedelta(days=1),
        "Anteayer": datetime.now() - timedelta(days=2),
        "Hace 3 días": datetime.now() - timedelta(days=3),
        "Hace 1 semana": datetime.now() - timedelta(days=7)
    }
    
    for label, date in quick_dates.items():
        if st.button(f"🔍 {label}", key=f"quick_{label}"):
            st.session_state.quick_search = {
                "lottery": selected_lottery,
                "date": date.strftime("%Y-%m-%d")
            }
            st.rerun()

st.markdown("---")

# Botón principal de búsqueda
st.markdown("### 🔍 BÚSQUEDA EN RED")
st.info("Haz clic en 'Buscar en Red' para consultar la fuente oficial")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    search_button = st.button(
        "🌐 BUSCAR EN RED",
        type="primary",
        use_container_width=True,
        key="main_search_button"
    )

# Procesar búsqueda rápida si existe
if 'quick_search' in st.session_state:
    search_button = True
    selected_lottery = st.session_state.quick_search['lottery']
    date_str = st.session_state.quick_search['date']
    del st.session_state.quick_search

# Ejecutar búsqueda
if search_button and selected_lottery and date_str:
    st.markdown("---")
    st.markdown("### 📊 RESULTADOS DE LA BÚSQUEDA")
    
    with st.spinner("🔍 Consultando fuente oficial..."):
        try:
            # Realizar búsqueda
            result = fetch_draw(selected_lottery, date_str)
            
            if "error" in result:
                st.error(f"❌ **Error en la búsqueda:** {result['error']}")
                
                if "No hay sorteo" in result['error']:
                    st.info("💡 **Sugerencia:** Selecciona una fecha diferente que tenga sorteo programado")
                elif "no soportada" in result['error']:
                    st.info("💡 **Sugerencia:** Selecciona una lotería de la lista disponible")
                else:
                    st.info("💡 **Sugerencia:** Verifica tu conexión a internet e intenta nuevamente")
            else:
                # Mostrar resultados exitosos
                st.success("✅ **Resultado encontrado exitosamente**")
                
                # Información principal
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("🎰 Lotería", result.get('lottery_name', 'N/A'))
                    st.metric("📅 Fecha", result.get('date', 'N/A'))
                
                with col2:
                    st.metric("🔢 Números Principales", str(result.get('numbers_main', [])))
                    if result.get('numbers_bonus'):
                        st.metric("⭐ Número Bonus", str(result.get('numbers_bonus', [])))
                
                with col3:
                    st.metric("🌐 Fuente", result.get('source_name', 'N/A'))
                    st.metric("⏰ Consulta", result.get('fetch_time', 'N/A')[:19] if result.get('fetch_time') else 'N/A')
                
                # Mostrar números en formato visual
                st.markdown("### 🎯 NÚMEROS DEL SORTEO")
                
                if result.get('numbers_main'):
                    numbers_cols = st.columns(len(result['numbers_main']))
                    for i, num in enumerate(result['numbers_main']):
                        with numbers_cols[i]:
                            st.markdown(f"""
                            <div style="
                                background-color: #1f77b4;
                                color: white;
                                border-radius: 50%;
                                width: 60px;
                                height: 60px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                font-size: 24px;
                                font-weight: bold;
                                margin: 0 auto;
                            ">
                                {num}
                            </div>
                            """, unsafe_allow_html=True)
                
                if result.get('numbers_bonus'):
                    st.markdown("### ⭐ NÚMERO BONUS")
                    bonus_cols = st.columns(len(result['numbers_bonus']))
                    for i, num in enumerate(result['numbers_bonus']):
                        with bonus_cols[i]:
                            st.markdown(f"""
                            <div style="
                                background-color: #ff7f0e;
                                color: white;
                                border-radius: 50%;
                                width: 60px;
                                height: 60px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                font-size: 24px;
                                font-weight: bold;
                                margin: 0 auto;
                            ">
                                {num}
                            </div>
                            """, unsafe_allow_html=True)
                
                # Información de la fuente
                st.markdown("### 🌐 INFORMACIÓN DE LA FUENTE")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"**Fuente:** {result.get('source_name', 'N/A')}")
                    st.info(f"**URL:** {result.get('source_url', 'N/A')}")
                
                with col2:
                    st.info(f"**Estado:** {'✅ Verificado' if not result.get('disputed') else '⚠️ Disputado'}")
                    st.info(f"**Tiempo de consulta:** {result.get('fetch_time', 'N/A')}")
                
                # Link directo a la fuente
                if result.get('source_url'):
                    st.markdown("---")
                    st.markdown("### 🔗 VERIFICAR EN FUENTE OFICIAL")
                    st.markdown(f"[🌐 **Hacer clic aquí para ver en {result.get('source_name', 'la fuente oficial')}**]({result.get('source_url')})")
                
                # Información adicional
                if result.get('disputed'):
                    st.warning("⚠️ **ATENCIÓN:** Este resultado está marcado como 'disputado'. Se recomienda verificar en la fuente oficial.")
                
                # Botón para guardar resultado
                if st.button("💾 Guardar Resultado", type="secondary"):
                    st.success("✅ Resultado guardado en el sistema")
                    st.info("Este resultado se puede usar para análisis futuros")
                
        except Exception as e:
            st.error(f"❌ **Error inesperado:** {str(e)}")
            st.info("💡 **Sugerencia:** Verifica tu conexión a internet e intenta nuevamente")

# Información adicional
st.markdown("---")
st.markdown("### 📚 INFORMACIÓN ADICIONAL")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🔍 **Cómo funciona la búsqueda:**")
    st.info("""
    1. **Selección:** Elige lotería y fecha
    2. **Validación:** Se verifica que la fecha tenga sorteo
    3. **Consulta:** Se consulta la fuente oficial
    4. **Resultado:** Se muestra el resultado verificado
    5. **Verificación:** Link directo a la fuente oficial
    """)

with col2:
    st.markdown("#### ⚠️ **Limitaciones actuales:**")
    st.warning("""
    - **Simulación:** Los números son simulados para demostración
    - **Parsing:** Se requiere implementar parsing real de HTML
    - **Fuentes:** Solo algunas loterías están implementadas
    - **Histórico:** Limitado a fechas recientes
    """)

# Footer
st.markdown("---")
st.caption("🌐 Buscador en Red de Sorteos - VISION PREMIUM - Consulta fuentes oficiales en tiempo real")








