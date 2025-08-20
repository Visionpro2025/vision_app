# app.py — Visión (Streamlit)
from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit as st

# =========================
# Configuración de página
# =========================
st.set_page_config(page_title="Visión", page_icon="🔮", layout="wide")

# =========================
# Título principal
# =========================
st.title("🔮 Sistema Predictivo Visión")

# =========================
# Menú lateral (único)
# =========================
menu = st.sidebar.selectbox(
    "Selecciona un módulo:",
    [
        "Inicio",
        "Visión",
        "Tabla T70",
        "Noticias",
        "Gematría",
        "Análisis del mensaje subliminal",
        "Orquestador",
    ],
)

# =========================
# Rutas auxiliares
# =========================
REPO_ROOT = Path(__file__).resolve().parent
T70_PATH = REPO_ROOT / "T70.csv"
NEWS_PATH = REPO_ROOT / "noticias.csv"


# =========================
# Router de vistas
# =========================
if menu == "Inicio":
    st.write("Bienvenido a la App del sistema Visión 🚀")

elif menu == "Visión":
    st.write("Aquí estará la lógica principal del sistema Visión.")

elif menu == "Tabla T70":
    st.subheader("📊 Tabla T70")
    try:
        if not T70_PATH.exists():
            st.warning("No se encontró **T70.csv** en la raíz del repositorio.")
        else:
            df_t70 = pd.read_csv(T70_PATH, encoding="utf-8")
            st.dataframe(df_t70, use_container_width=True)
    except Exception as e:
        st.error(f"No se pudo cargar T70.csv: {e}")
        st.info("Verifica que el archivo **T70.csv** exista en la carpeta raíz.")

elif menu == "Noticias":
    # Vista modular de Noticias (bitácora)
    from modules.noticias_module import render_noticias
    render_noticias()

elif menu == "Gematría":
    # Vista modular de Gematría
    from modules.gematria import show_gematria
    show_gematria()

elif menu == "Análisis del mensaje subliminal":
    # Vista modular de Subliminal
    from modules.subliminal_module import render_subliminal
    render_subliminal()

elif menu == "Orquestador":
    # Director de orquesta: chequea, ordena y ejecuta capas
    from modules.orchestrator import render_orchestrator
    render_orchestrator()

# =========================
# Pie de página (opcional)
# =========================
st.caption(
    f"© Visión · última recarga: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')}"
)