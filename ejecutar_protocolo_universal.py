#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 EJECUTOR DEL PROTOCOLO UNIVERSAL FLORIDA LOTTO
Ejecuta paso a paso con visualización completa
"""

import streamlit as st
import sys
from pathlib import Path

# Configurar el entorno
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# Configuración de la página
st.set_page_config(
    page_title="🎯 PROTOCOLO UNIVERSAL FLORIDA LOTTO",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Función principal del Protocolo Universal"""
    
    # Header principal
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(90deg, #1e3c72, #2a5298); border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0;">🎯 PROTOCOLO UNIVERSAL FLORIDA LOTTO</h1>
        <p style="color: #e0e0e0; margin: 5px 0 0 0;">Ejecución paso a paso con visualización completa de todos los detalles</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Importar el visualizador
    from modules.universal_protocol_visualizer import UniversalProtocolVisualizer
    
    # Crear instancia del visualizador
    visualizer = UniversalProtocolVisualizer()
    
    # Ejecutar el protocolo completo
    visualizer.execute_complete_protocol()

if __name__ == "__main__":
    main()



