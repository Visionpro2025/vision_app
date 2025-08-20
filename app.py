# app.py — Visión (UI Pro)
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import importlib
import streamlit as st
import pandas as pd

# =========================
# Configuración de página
# =========================
st.set_page_config(
    page_title="Sistema Predictivo Visión",
    page_icon="🔮",
    layout="wide",
    menu_items={
        "Get help": None,
        "Report a bug": None,
        "About": "Visión · Plataforma modular para análisis predictivo.",
    },
)

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "__RUNS"
RUNS.mkdir(parents=True, exist_ok=True)

# =========================
# Utilidades de UI
# =========================
def kpi_card(title: str, value: str | int | float, help_text: str = ""):
    st.markdown(
        f"""
        <div style="padding:14px;border-radius:14px;border:1px solid rgba(255,255,255,.1);
                    background:rgba(255,255,255,.03);">
            <div style="opacity:.75;font-size:.9rem">{title}</div>
            <div style="font-weight:700;font-size:1.6rem;line-height:1.2">{value}</div>
            <div style="opacity:.55;font-size:.85rem">{help_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

@st.cache_data(show_spinner=False)
def _safe_read_csv(path: Path) -> pd.DataFrame | None:
    try:
        return pd.read_csv(path, dtype=str, encoding="utf-8")
    except Exception:
        return None

def file_badge(path: Path) -> str:
    return "✅" if path.exists() else "❌"

# =========================
# Sidebar pro
# =========================
with st.sidebar:
    # Si tienes un logo, ponlo en la raíz y descomenta:
    # st.image("logo.png", use_container_width=True)
    st.markdown("### 🔮 Visión")
    st.caption("Suite de análisis modular")

    section = st.radio(
        "Navegación",
        [
            "🏠 Inicio",
            "📰 Noticias",
            "🔤 Gematría",
            "🌀 Análisis del mensaje subliminal",
            "📚 Biblioteca",
            "🧭 Orquestador de capas",
        ],
        index=0,
    )

    st.markdown("---")
    st.caption(
        "© Visión · " + datetime.utcnow().strftime("última recarga: %Y-%m-%d %H:%M:%SZ")
    )

# =========================
# Portada
# =========================
if section == "🏠 Inicio":
    st.title("🔮 Sistema Predictivo Visión")
    st.write(
        "Menú maestro para navegar por las capas del sistema. "
        "Usa la barra lateral para abrir cada módulo."
    )

    # chequeos rápidos
    news_p = ROOT / "noticias.csv"
    t70_p = ROOT / "T70.csv"

    c1, c2, c3 = st.columns([1.2, 1, 1])
    with c1:
        st.subheader("Estado de insumos")
        col_a, col_b = st.columns(2)
        with col_a:
            kpi_card("noticias.csv", file_badge(news_p), "bitácora")
        with col_b:
            kpi_card("T70.csv", file_badge(t70_p), "Tabla de tendencias")

        # detalles
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if news_p.exists():
            df_n = _safe_read_csv(news_p) or pd.DataFrame()
            st.success(f"noticias.csv OK {len(df_n)} filas")
        else:
            st.warning("Falta **noticias.csv** en la raíz del repo.")

        if t70_p.exists():
            df_t = _safe_read_csv(t70_p) or pd.DataFrame()
            st.success(f"T70.csv OK {len(df_t)} filas")
        else:
            st.warning("Falta **T70.csv** en la raíz del repo.")

    with c2:
        st.subheader("Métricas")
        total_mods = 4
        ready = int(news_p.exists()) + int(t70_p.exists())
        kpi_card("Módulos", total_mods, "Noticias · Gematría · Subliminal · Biblioteca")
        kpi_card("Insumos listos", f"{ready}/2")

    with c3:
        st.subheader("Acciones")
        if st.button("↻ Re-cargar datos"):
            st.cache_data.clear()
            st.experimental_rerun()
        st.caption("Limpia caché y recarga el estado de archivos.")

# =========================
# Noticias
# =========================
elif section == "📰 Noticias":
    try:
        mod = importlib.import_module("modules.noticias_module")
        st.title("📰 Noticias — bitácora del sorteo")
        mod.render_noticias()
    except Exception as e:
        st.error("No se pudo cargar el módulo de noticias.")
        st.exception(e)

# =========================
# Gematría
# =========================
elif section == "🔤 Gematría":
    try:
        mod = importlib.import_module("modules.gematria")
        st.title("🔤 Gematría")
        mod.show_gematria()
    except Exception as e:
        st.error("No se pudo cargar el módulo de gematría.")
        st.exception(e)

# =========================
# Subliminal
# =========================
elif section == "🌀 Análisis del mensaje subliminal":
    try:
        mod = importlib.import_module("modules.subliminal_module")
        st.title("🌀 Análisis del mensaje subliminal")
        mod.render_subliminal()
    except Exception as e:
        st.error("No se pudo cargar el módulo de subliminal.")
        st.exception(e)

# =========================
# Biblioteca
# =========================
elif section == "📚 Biblioteca":
    try:
        mod = importlib.import_module("modules.library")
        st.title("📚 Biblioteca")
        mod.render_library()
    except Exception as e:
        st.error("No se pudo cargar el módulo de biblioteca.")
        st.exception(e)

# =========================
# Orquestador
# =========================
elif section == "🧭 Orquestador de capas":
    try:
        mod = importlib.import_module("modules.orchestrator")
        st.title("🧭 Orquestador de capas")
        mod.render_orchestrator()
    except Exception as e:
        st.error("No se pudo cargar el módulo de orquestador.")
        st.exception(e)

# =========================
# Footer
# =========================
st.markdown("---")
st.caption("Hecho con ❤️ y Streamlit · Visión")
