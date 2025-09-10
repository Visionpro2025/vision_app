#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERSIÓN DE PRUEBA SIMPLIFICADA - VISION PREMIUM
Para identificar problemas de carga
"""

import streamlit as st

# Configuración básica
st.set_page_config(
    page_title="VISION PREMIUM - TEST",
    page_icon="🚀",
    layout="wide"
)

# Título simple
st.title("🚀 VISION PREMIUM - VERSIÓN DE PRUEBA")
st.markdown("### Sistema de Prueba para Diagnóstico")

# Información básica
st.info("✅ Esta es una versión simplificada para verificar que Streamlit funciona")

# Métricas básicas
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Estado", "✅ FUNCIONANDO")
    
with col2:
    st.metric("Versión", "1.0 TEST")
    
with col3:
    st.metric("Módulos", "1/1")

# Mensaje de éxito
st.success("🎉 ¡La aplicación está funcionando correctamente!")
st.info("Si puedes ver este mensaje, Streamlit está funcionando perfectamente.")

# Información del sistema
st.markdown("---")
st.subheader("📊 Información del Sistema")

# Verificar módulos disponibles
try:
    import pandas as pd
    st.success("✅ Pandas disponible")
except:
    st.error("❌ Pandas no disponible")

try:
    import plotly
    st.success("✅ Plotly disponible")
except:
    st.error("❌ Plotly no disponible")

try:
    import psutil
    st.success("✅ Psutil disponible")
except:
    st.error("❌ Psutil no disponible")

# Footer
st.markdown("---")
st.caption("VISION Premium - Versión de Prueba - Todos los sistemas funcionando")








