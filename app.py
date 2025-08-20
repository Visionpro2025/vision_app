
# ============================
# 🔮 Aplicación Visión — app.py
# ============================

from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit as st

# ──────────────────────────────────────────────────────────────────────────────
# Configuración de página
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Visión", page_icon="🔮", layout="wide")

# ──────────────────────────────────────────────────────────────────────────────
# Utilidades mínimas (cacheadas)
# ──────────────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent

@st.cache_data(show_spinner=False)
def _read_csv_safe(path: Path) -> pd.DataFrame | None:
    try:
        return pd.read_csv(path, dtype=str, encoding="utf-8")
    except Exception as e:
        st.error(f"No se pudo leer {path.name}: {e}")
        return None

# ──────────────────────────────────────────────────────────────────────────────
# Título
# ──────────────────────────────────────────────────────────────────────────────
st.title("🔮 Sistema Predictivo Visión")
st.caption("Menú maestro para navegar por las capas del sistema.")

# ──────────────────────────────────────────────────────────────────────────────
# Menú lateral (único)
# ──────────────────────────────────────────────────────────────────────────────
menu = st.sidebar.selectbox(
    "Selecciona un módulo:",
    [
        "🏠 Inicio",
        "👁️ Visión",
        "📊 Tabla T70",
        "📰 Noticias",
        "🔤 Gematría",
        "🌀 Análisis del mensaje subliminal",
        "🧭 Orquestador de capas",
        "📚 Biblioteca",
    ],
)

# ──────────────────────────────────────────────────────────────────────────────
# Router de vistas (cada elif llama a su módulo)
# ──────────────────────────────────────────────────────────────────────────────
if menu == "🏠 Inicio":
    st.subheader("Bienvenido 👋")
    st.write(
        "Usa el menú de la izquierda para abrir **Noticias**, **Gematría**, "
        "**Análisis del mensaje subliminal**, **📚 Biblioteca** o el **🧭 Orquestador**."
    )
    # Estado rápido de archivos base
    col1, col2 = st.columns(2)
    with col1:
        news_path = ROOT / "noticias.csv"
        ok = news_path.exists()
        st.metric("noticias.csv", "OK ✅" if ok else "Falta ⚠️")
        if ok:
            df = _read_csv_safe(news_path)
            if df is not None:
                st.caption(f"Filas: {len(df)}")
    with col2:
        t70_path = ROOT / "T70.csv"
        ok = t70_path.exists()
        st.metric("T70.csv", "OK ✅" if ok else "Falta ⚠️")
        if ok:
            df = _read_csv_safe(t70_path)
            if df is not None:
                st.caption(f"Filas: {len(df)}")

elif menu == "👁️ Visión":
    st.subheader("Visión (placeholder)")
    st.info("Aquí irá la lógica principal de series/estrategia de la app.")

elif menu == "📊 Tabla T70":
    st.subheader("📊 Tabla T70")
    path = ROOT / "T70.csv"
    if not path.exists():
        st.warning("No encuentro **T70.csv** en la raíz del repositorio.")
    else:
        df = _read_csv_safe(path)
        if df is not None:
            st.dataframe(df, use_container_width=True)

elif menu == "📰 Noticias":
    try:
        from modules.noticias_module import render_noticias
        render_noticias()
    except Exception as e:
        st.error(f"Error al cargar Noticias: {e}")

elif menu == "🔤 Gematría":
    try:
        from modules.gematria import show_gematria
        show_gematria()
    except Exception as e:
        st.error(f"Error en módulo Gematría: {e}")

elif menu == "🌀 Análisis del mensaje subliminal":
    try:
        from modules.subliminal_module import render_subliminal
        render_subliminal()
    except Exception as e:
        st.error(f"Error en módulo Subliminal: {e}")

elif menu == "🧭 Orquestador de capas":
    try:
        from modules.orchestrator import render_orchestrator
        render_orchestrator()
    except Exception as e:
        st.error(f"Error en módulo Orquestador: {e}")

elif menu == "📚 Biblioteca":
    try:
        from modules.library import render_library
        render_library()
    except Exception as e:
        st.error(f"Error en módulo Biblioteca: {e}")

else:
    st.error("Opción de menú no reconocida.")

# ──────────────────────────────────────────────────────────────────────────────
# Pie de página
# ──────────────────────────────────────────────────────────────────────────────
st.caption(
    f"© Visión · última recarga: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')}"
        )
