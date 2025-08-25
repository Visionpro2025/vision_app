# modules/diagnostics.py — Panel de propiedades y diagnóstico (blindado)
from __future__ import annotations
from pathlib import Path
import os, sys, platform, json
import importlib
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "__RUNS"
NEWS_CSV = ROOT / "noticias.csv"

SAFE_ENV_PREFIXES = ["STREAMLIT_", "PYTHON", "PIP_", "GIT_", "REPLIT_"]

# -------- Placeholders (DOM estable) --------
if "__diag_paths_slot" not in st.session_state:
    st.session_state["__diag_paths_slot"] = st.empty()
if "__diag_versions_slot" not in st.session_state:
    st.session_state["__diag_versions_slot"] = st.empty()
if "__diag_secrets_slot" not in st.session_state:
    st.session_state["__diag_secrets_slot"] = st.empty()
if "__diag_env_slot" not in st.session_state:
    st.session_state["__diag_env_slot"] = st.empty()
if "__diag_ss_slot" not in st.session_state:
    st.session_state["__diag_ss_slot"] = st.empty()
if "__diag_modules_slot" not in st.session_state:
    st.session_state["__diag_modules_slot"] = st.empty()
if "__diag_utils_slot" not in st.session_state:
    st.session_state["__diag_utils_slot"] = st.empty()

# -------- Flags (acciones disciplinadas) --------
def _flag(name: str):
    st.session_state[name] = True
def _consume_flag(name: str) -> bool:
    if st.session_state.get(name):
        st.session_state[name] = False
        return True
    return False

# -------- Utilidades --------
def _exists(p: Path) -> bool:
    try:
        return p.exists()
    except Exception:
        return False

def _size(p: Path) -> int:
    try:
        return p.stat().st_size
    except Exception:
        return 0

def _read_csv_rows(p: Path) -> int:
    try:
        df = pd.read_csv(p, dtype=str, encoding="utf-8")
        return len(df)
    except Exception:
        return 0

def _pkg_ver(name: str) -> str:
    try:
        m = importlib.import_module(name)
        return getattr(m, "__version__", "desconocida")
    except Exception:
        return "no instalado"

def _safe_env():
    data = {}
    for k, v in os.environ.items():
        if any(k.startswith(pref) for pref in SAFE_ENV_PREFIXES):
            s = str(v)
            data[k] = (s if len(s) <= 120 else s[:117] + "…")
    return data

def _safe_secrets():
    try:
        keys = list(st.secrets.keys())
        out = {"_top_level_keys": keys}
        for k in keys:
            try:
                sub = st.secrets[k]
                if isinstance(sub, dict):
                    out[k] = list(sub.keys())
                else:
                    out[k] = "(valor oculto)"
            except Exception:
                out[k] = "(no accesible)"
        return out
    except Exception:
        return {"_info": "secrets no disponible"}

def _folder_counts():
    out = {}
    try:
        g = RUNS / "GEMATRIA"
        s = RUNS / "SUBLIMINAL"
        n = RUNS / "NEWS"
        out["__RUNS/GEMATRIA (*.csv)"] = len(list(g.glob("*.csv"))) if _exists(g) else 0
        out["__RUNS/SUBLIMINAL (*.csv)"] = len(list(s.glob("*.csv"))) if _exists(s) else 0
        out["__RUNS/NEWS (*.csv)"] = len(list(n.glob("*.csv"))) if _exists(n) else 0
    except Exception:
        pass
    return out

# -------- UI principal --------
def render_diagnostics():
    st.header("🧪 Diagnóstico de la aplicación")

    # Acciones diferidas (antes de pintar layout)
    if _consume_flag("__diag_clear_cache__"):
        try:
            st.cache_data.clear()
        except Exception:
            pass

    # ===== Rutas y archivos =====
    with st.session_state["__diag_paths_slot"].container():
        st.subheader("📁 Rutas y archivos")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Raíz del proyecto**:", str(ROOT))
            st.write("**Archivo principal esperado**:", "app.py")
            st.write("**Carpeta modules/**:", str(ROOT / "modules"))
            st.write("**__RUNS/**:", str(RUNS))
        with col2:
            if _exists(NEWS_CSV):
                st.write(
                    "**noticias.csv**:",
                    "Sí ✅",
                    f"· filas: {_read_csv_rows(NEWS_CSV)} · tamaño: {_size(NEWS_CSV)} bytes",
                )
            else:
                st.write("**noticias.csv**:", "No ❌")
            for k, v in _folder_counts().items():
                st.write(f"**{k}**: {v}")

    # ===== Versiones =====
    with st.session_state["__diag_versions_slot"].container():
        st.subheader("⚙️ Versiones")
        st.json({
            "python": platform.python_version(),
            "streamlit": _pkg_ver("streamlit"),
            "pandas": _pkg_ver("pandas"),
            "requests": _pkg_ver("requests"),
            "feedparser": _pkg_ver("feedparser"),
            "platform": f"{platform.system()} {platform.release()}",
        }, expanded=False)

    # ===== Secrets (solo claves) =====
    with st.session_state["__diag_secrets_slot"].container():
        st.subheader("🔐 Secrets (solo claves, sin valores)")
        st.json(_safe_secrets(), expanded=False)

    # ===== Variables de entorno seguras =====
    with st.session_state["__diag_env_slot"].container():
        st.subheader("🌐 Variables de entorno (seguras)")
        st.json(_safe_env(), expanded=False)

    # ===== Session state (resumen) =====
    with st.session_state["__diag_ss_slot"].container():
        st.subheader("🧠 Session state (resumen)")
        ss = {}
        for k, v in st.session_state.items():
            try:
                sv = v if isinstance(v, (str, int, float, bool, type(None))) else type(v).__name__
                ss[k] = sv
            except Exception:
                ss[k] = "(no serializable)"
        st.json(ss, expanded=False)

    # ===== modules/ presentes =====
    with st.session_state["__diag_modules_slot"].container():
        st.subheader("📦 modules/ presentes")
        try:
            mods = [p.name for p in (ROOT / "modules").glob("*.py")]
            st.write(mods or "(vacío)")
        except Exception as e:
            st.write(f"No se pudo listar modules/: {e}")

    # ===== Utilidades rápidas (botones con keys y bandera) =====
    with st.session_state["__diag_utils_slot"].container():
        st.subheader("🛠 Utilidades")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔁 Limpiar caché de datos", key="btn_diag_clear_cache", use_container_width=True):
                _flag("__diag_clear_cache__")
                st.stop()  # cortamos el ciclo actual; se limpia antes del siguiente render
        with c2:
            st.caption("Consejo: usa este panel para verificar repo, entorno y archivos antes de depurar.")
