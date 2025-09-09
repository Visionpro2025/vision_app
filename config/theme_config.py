# config/theme_config.py — Configuración de Temas para VISION PREMIUM

"""
Configuración de temas para la aplicación VISION PREMIUM.
Incluye temas claro, oscuro y personalizados.
"""

# =================== TEMAS PREDEFINIDOS ===================

LIGHT_THEME = {
    "primaryColor": "#1f77b4",           # Azul principal
    "backgroundColor": "#ffffff",         # Fondo blanco
    "secondaryBackgroundColor": "#f0f2f6", # Fondo secundario gris claro
    "textColor": "#262730",              # Texto oscuro
    "font": "sans serif"                 # Fuente sans serif
}

DARK_THEME = {
    "primaryColor": "#00ff88",           # Verde neón
    "backgroundColor": "#0e1117",        # Fondo oscuro
    "secondaryBackgroundColor": "#262730", # Fondo secundario oscuro
    "textColor": "#fafafa",              # Texto claro
    "font": "sans serif"                 # Fuente sans serif
}

PREMIUM_THEME = {
    "primaryColor": "#ff6b35",           # Naranja premium
    "backgroundColor": "#ffffff",        # Fondo blanco
    "secondaryBackgroundColor": "#f8f9fa", # Fondo gris muy claro
    "textColor": "#2c3e50",             # Texto azul oscuro
    "font": "sans serif"                 # Fuente sans serif
}

PROFESSIONAL_THEME = {
    "primaryColor": "#2c3e50",          # Azul profesional
    "backgroundColor": "#ffffff",        # Fondo blanco
    "secondaryBackgroundColor": "#ecf0f1", # Fondo gris claro
    "textColor": "#34495e",             # Texto gris oscuro
    "font": "sans serif"                 # Fuente sans serif
}

# =================== FUNCIÓN PARA OBTENER TEMA ===================

def get_theme(theme_name: str = "light") -> dict:
    """
    Obtiene la configuración del tema especificado.
    
    Args:
        theme_name (str): Nombre del tema ("light", "dark", "premium", "professional")
        
    Returns:
        dict: Configuración del tema
    """
    themes = {
        "light": LIGHT_THEME,
        "dark": DARK_THEME,
        "premium": PREMIUM_THEME,
        "professional": PROFESSIONAL_THEME
    }
    
    return themes.get(theme_name.lower(), LIGHT_THEME)

def get_theme_names() -> list:
    """
    Obtiene la lista de nombres de temas disponibles.
    
    Returns:
        list: Lista de nombres de temas
    """
    return ["light", "dark", "premium", "professional"]

def get_theme_display_names() -> dict:
    """
    Obtiene los nombres de visualización de los temas.
    
    Returns:
        dict: Mapeo de nombres internos a nombres de visualización
    """
    return {
        "light": "🌞 Tema Claro",
        "dark": "🌙 Tema Oscuro", 
        "premium": "⭐ Tema Premium",
        "professional": "💼 Tema Profesional"
    }

# =================== CONFIGURACIÓN DE COLORES ADICIONALES ===================

# Colores para métricas y KPIs
METRIC_COLORS = {
    "success": "#00ff88",      # Verde para métricas positivas
    "warning": "#ffaa00",      # Amarillo para advertencias
    "error": "#ff4444",        # Rojo para errores
    "info": "#00aaff",         # Azul para información
    "neutral": "#888888"       # Gris para valores neutros
}

# Colores para gráficos y visualizaciones
CHART_COLORS = {
    "primary": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
    "light": ["#aec7e8", "#ffbb78", "#98df8a", "#ff9896", "#c5b0d5"],
    "dark": ["#0e1117", "#262730", "#4a4a4a", "#6b6b6b", "#8a8a8a"]
}

# =================== FUNCIÓN PARA APLICAR TEMA ===================

def apply_theme_config():
    """
    Aplica la configuración del tema a la aplicación.
    Esta función debe ser llamada después de st.set_page_config()
    """
    import streamlit as st
    
    # Crear selector de tema en la barra lateral
    with st.sidebar:
        st.markdown("### 🎨 Configuración de Tema")
        
        # Obtener tema actual de la sesión
        current_theme = st.session_state.get("current_theme", "light")
        
        # Selector de tema
        theme_names = get_theme_names()
        display_names = get_theme_display_names()
        
        selected_theme = st.selectbox(
            "Seleccionar Tema:",
            options=theme_names,
            format_func=lambda x: display_names[x],
            index=theme_names.index(current_theme),
            key="theme_selector"
        )
        
        # Aplicar tema si cambió
        if selected_theme != current_theme:
            st.session_state.current_theme = selected_theme
            st.rerun()
        
        # Mostrar información del tema actual
        st.info(f"Tema actual: {display_names[current_theme]}")
        
        # Botón para resetear tema
        if st.button("🔄 Resetear Tema", use_container_width=True):
            st.session_state.current_theme = "light"
            st.rerun()

# =================== USO EN LA APLICACIÓN ===================

"""
Para usar este sistema de temas en tu aplicación:

1. Importar el módulo:
   from config.theme_config import get_theme, apply_theme_config

2. Aplicar en st.set_page_config():
   theme_config = get_theme("light")  # o el tema que prefieras
   st.set_page_config(
       page_title="Tu App",
       theme=theme_config
   )

3. Llamar apply_theme_config() después de la configuración de página para
   mostrar el selector de temas en la barra lateral.

4. Para cambiar el tema dinámicamente, usar:
   st.session_state.current_theme = "dark"  # o cualquier otro tema
   st.rerun()
"""







