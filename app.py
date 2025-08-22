# app.py — Edición Pro UI (corregido y depurado)
from __future__ import annotations

from pathlib import Path
from datetime import datetime
import sys

import pandas as pd
import streamlit as st

# === Habilitar imports desde la raíz del repo ===
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# ================================================

# Config de loterías
from modules.lottery_config import LOTTERIES, DEFAULT_LOTTERY

# ========= Config de página =========
st.set_page_config(
    page_title="Sistema Predictivo Visión",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ========= Estilos ligeros (CSS) =========
PRO_CSS = """
<style>
/* contenedor ajustado */
.block-container {padding-top: 1.2rem; padding-bottom: 2.5rem;}
/* tarjetas */
.kpi-card {
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 14px; padding: 16px 16px;
  background: rgba(255,255,255,0.03);
}
.kpi-title {font-size: 0.82rem; opacity: .8;}
.kpi-value {font-size: 1.6rem; font-weight: 700; margin-top: 4px;}
.kpi-sub {font-size: .78rem; opacity:.7;}
/* botones rápidos */
.quick .stButton>button {
  width: 100%; border-radius: 12px; padding: .6rem .8rem; font-weight: 600;
}
hr.sep {border:none; height:1px; background:rgba(255,255,255,.08); margin: .6rem 0 1rem;}
/* footer */
.footer {opacity:.7; font-size:.85rem; margin-top:2rem;}
</style>
"""
st.markdown(PRO_CSS, unsafe_allow_html=True)

# ========= Rutas base y utilidades =========
RUNS = ROOT / "__RUNS"
RUNS.mkdir(parents=True, exist_ok=True)

@st.cache_data(show_spinner=False)
def load_csv_safe(path: Path) -> pd.DataFrame:
    """Lee CSV y SIEMPRE devuelve un DataFrame (vacío si falla)."""
    try:
        return pd.read_csv(path, dtype=str, encoding="utf-8")
    except Exception:
        return pd.DataFrame()

def exists(p: Path) -> bool:
    try:
        return p.exists()
    except Exception:
        return False

def kpi_card(title: str, value: str, sub: str = ""):
    st.markdown(
        f"""
        <div class="kpi-card">
          <div class="kpi-title">{title}</div>
          <div class="kpi-value">{value}</div>
          <div class="kpi-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ========= Sidebar (navegación) =========
with st.sidebar:
    # === Selector de lotería (afecta a toda la app) ===
    lot_keys = list(LOTTERIES.keys())
    default_idx = lot_keys.index(DEFAULT_LOTTERY) if DEFAULT_LOTTERY in lot_keys else 0
    idx = lot_keys.index(st.session_state.get("current_lottery", lot_keys[default_idx]))
    current_key = st.selectbox("Lotería activa", options=lot_keys, index=idx)

    st.session_state["current_lottery"] = current_key
    L = LOTTERIES[current_key]

    # Logo + meta (si hay logo)
    try:
        logo = L.get("logo")
        if logo and Path(logo).exists():
            st.image(str(logo), use_container_width=True)
    except Exception:
        pass

    # Meta de lotería (a prueba de claves faltantes)
    try:
        name = L.get("name", current_key)
        days = ", ".join(L.get("days", [])) if isinstance(L.get("days"), list) else L.get("days", "")
        draw_time_local = L.get("draw_time_local", "")
        tz = L.get("tz", "")
        site = L.get("site", "")

        st.caption(f"**{name}** · Días: {days} · Hora local: {draw_time_local} ({tz})")
        if site:
            st.markdown(f"[🌐 Sitio oficial]({site})")
    except Exception:
        pass

    st.markdown("<hr class='sep'>", unsafe_allow_html=True)
    st.markdown("## 🔮 Visión · Navegación")
    menu = st.radio(
        "Selecciona un módulo",
        [
            "🏠 Inicio",
            "📰 Noticias",
            "🔡 Gematría",
            "🌀 Análisis subliminal",
            "📚 Biblioteca",
            "🧭 Orquestador",
        ],
        index=0,
        label_visibility="collapsed",
    )
    st.markdown("<hr class='sep'>", unsafe_allow_html=True)

    # Acciones rápidas
    st.markdown("#### ⚡ Acciones")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("↻ Recargar", use_container_width=True):
            st.cache_data.clear()
            st.toast("Caché limpiada. Recargando…", icon="♻️")
            st.rerun()
    with c2:
        t70p = ROOT / "T70.csv"
        st.download_button(
            "Descargar T70.csv",
            t70p.read_bytes() if exists(t70p) else b"",
            file_name="T70.csv",
            disabled=not exists(t70p),
            use_container_width=True,
        )

# ========= Cabecera común =========
colA, colB = st.columns([0.78, 0.22])
with colA:
    st.title("🔮 Sistema Predictivo Visión")
    st.caption("Menú maestro para navegar por las capas del sistema.")
with colB:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
    kpi_card("⏱️ Última recarga", now)

# KPI coherente con el selector
kpi_card("🎯 Lotería activa", L.get("name", current_key))

# ========= Inicio =========
if menu == "🏠 Inicio":
    st.subheader("Bienvenido 👋")

    noticias_path = ROOT / "noticias.csv"
    t70_path = ROOT / "T70.csv"

    c1, c2, c3 = st.columns(3)
    with c1:
        if exists(noticias_path):
            df_n = load_csv_safe(noticias_path)
            if df_n.empty:
                kpi_card("📰 noticias.csv", "Vacío ⚠️", "Sin filas legibles")
            else:
                kpi_card("📰 noticias.csv", "OK ✅", f"Filas: {len(df_n)}")
        else:
            kpi_card("📰 noticias.csv", "No encontrado ❌", "Coloca el archivo en la raíz")

    with c2:
        if exists(t70_path):
            df_t = load_csv_safe(t70_path)
            if df_t.empty:
                kpi_card("📊 T70.csv", "Vacío ⚠️", "Sin filas legibles")
            else:
                kpi_card("📊 T70.csv", "OK ✅", f"Filas: {len(df_t)}")
        else:
            kpi_card("📊 T70.csv", "No encontrado ❌", "Coloca el archivo en la raíz")

    with c3:
        runs_g = ROOT / "__RUNS" / "GEMATRIA"
        runs_s = ROOT / "__RUNS" / "SUBLIMINAL"
        count_runs = (len(list(runs_g.glob("*.csv"))) if exists(runs_g) else 0) + \
                     (len(list(runs_s.glob("*.csv"))) if exists(runs_s) else 0)
        kpi_card("📁 Salidas generadas", str(count_runs), "CSV en __RUNS/…")

    st.markdown("<hr class='sep'>", unsafe_allow_html=True)
    st.markdown("### 🚀 Abrir módulos")
    q1, q2, q3, q4, q5 = st.columns(5)
    if q1.button("📰 Noticias", use_container_width=True):
        st.session_state["_nav"] = "📰 Noticias"; st.rerun()
    if q2.button("🔡 Gematría", use_container_width=True):
        st.session_state["_nav"] = "🔡 Gematría"; st.rerun()
    if q3.button("🌀 Subliminal", use_container_width=True):
        st.session_state["_nav"] = "🌀 Análisis subliminal"; st.rerun()
    if q4.button("📚 Biblioteca", use_container_width=True):
        st.session_state["_nav"] = "📚 Biblioteca"; st.rerun()
    if q5.button("🧭 Orquestador", use_container_width=True):
        st.session_state["_nav"] = "🧭 Orquestador"; st.rerun()

# ========= Noticias =========
elif menu == "📰 Noticias" or st.session_state.get("_nav") == "📰 Noticias":
    st.session_state["_nav"] = "📰 Noticias"
    try:
        from modules.noticias_module import render_noticias
        with st.spinner("Cargando noticias…"):
            render_noticias()
    except Exception as e:
        st.error("No se pudo cargar el módulo de **Noticias**.")
        st.exception(e)

# ========= Gematría =========
elif menu == "🔡 Gematría" or st.session_state.get("_nav") == "🔡 Gematría":
    st.session_state["_nav"] = "🔡 Gematría"
    try:
        from modules.gematria import show_gematria
        with st.spinner("Abriendo Gematría…"):
            show_gematria()
    except Exception as e:
        st.error("No se pudo cargar el módulo de **Gematría**.")
        st.exception(e)

# ========= Subliminal =========
elif menu == "🌀 Análisis subliminal" or st.session_state.get("_nav") == "🌀 Análisis subliminal":
    st.session_state["_nav"] = "🌀 Análisis subliminal"
    try:
        from modules.subliminal_module import render_subliminal
        with st.spinner("Analizando mensajes subliminales…"):
            render_subliminal()
    except Exception as e:
        st.error("No se pudo cargar el módulo **Subliminal**.")
        st.exception(e)

# ========= Biblioteca =========
elif menu == "📚 Biblioteca" or st.session_state.get("_nav") == "📚 Biblioteca":
    st.session_state["_nav"] = "📚 Biblioteca"
    try:
        from modules.library import render_library
        with st.spinner("Abriendo Biblioteca…"):
            render_library()
    except Exception as e:
        st.error("No se pudo cargar el módulo **Biblioteca**.")
        st.exception(e)

# ========= Orquestador =========
elif menu == "🧭 Orquestador" or st.session_state.get("_nav") == "🧭 Orquestador":
    st.session_state["_nav"] = "🧭 Orquestador"
    try:
        from modules.orchestrator import render_orchestrator
        with st.spinner("Iniciando orquestador…"):
            render_orchestrator()
    except Exception as e:
        st.error("No se pudo cargar el **Orquestador**.")
        st.exception(e)

# ========= Footer =========
st.markdown(
    f"<div class='footer'>© Visión · última recarga: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')}</div>",
    unsafe_allow_html=True,
  )
